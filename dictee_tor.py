import logging
import os
import requests
import random

from flask import Flask, redirect, render_template, current_app, session, request
#running behind proxy?                                                                                            
from werkzeug.middleware.proxy_fix import ProxyFix

from config import myconfig
import dbutils

########################################################################################
## Flask vars
#
app = Flask(__name__, static_url_path='')
app.secret_key = myconfig["session secret key"]

#if behind a proxy set the WSGI properly 
# see http://electrogeek.tokyo/setup%20flask%20behind%20nginx%20proxy.html
if myconfig.get("BehindProxy", False):
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'ico'])

########################################################################################
## Other non-web related functions
#
#-----------------------------------------------------------------------
#Indirection so I can keep the API key on server side (useless, but I don't want to expose it)
@app.route("/api/text2speech/<lang>/<message>", methods=['GET'])
def text_to_speech(lang, message):
    logging.info(f"S2T: {lang} - '{message}'")
    
    #The API expects a specific locale "fr-fr", "ja-jp", "ko-kr" and not just a language code on 2 letters
    locale =  "fr-fr" if lang == "fr" else "ja-jp" if lang == "jp" else "ko-kr"

    try:
        speed_factor = myconfig.get("VoiceRSS speed", 0)
        url = f"https://api.voicerss.org/?key={myconfig['VoiceRSS key']}&hl={locale}&c=MP3&v=Zola&f=16khz_16bit_mono&r={speed_factor}&src={message}"
        logging.debug(f"URL for S2T: {url}")
        req = requests.Request('GET', url)
        prepared = req.prepare()
        resp = requests.Session().send(prepared, stream=True, verify=myconfig["SSL_CHECK"])
    
        return resp.raw.read(), resp.status_code, resp.headers.items()
    except Exception as e:
        logging.error(f"Error in text_to_speech: {str(e)}")
        return None, 500, None

########################################################################################
## Web related functions
#
#-----------------------------------------------------------------------
#Landing page, not much to see here but at least if API connectivity doesn't you will know immediately

@app.before_request
def init_session():
    if "language" not in session:
        session["language"] = myconfig["language"]
    if "letterstyle" not in session:
        session["letterstyle"] = myconfig["letterstyle"]
    if "lettercase" not in session:
        session["lettercase"] = myconfig["lettercase"]

        


@app.route('/')
@app.route('/home')
def homepage():
    wc_total, _, wc_years, wc_weeksperyear = dbutils.db_stats()

    return render_template("home01.html", pagename="Home", stats=(wc_total, wc_years, wc_weeksperyear), **current_app.global_render_template_params)


@app.before_request
def set_global_variables():
    current_app.global_render_template_params = {} 


@app.route("/new_dictee")
def new_dictee_page():
    #get the words list
    words = None
    mode = request.args.get("mode", "single")
    year, week = request.args.get("weekid", "ce1-1").split("-")

    if mode == "single":
        #get a word from the selected week
        words = dbutils.all_words(year, week=week, lang=session["language"])
    else:
        #get a word from the selected year UP TO the selected week included
        words = dbutils.all_words(year, maxweek=week,lang=session["language"])

    #How many words to ask: the minimum between the number of words in the list and the number of words to ask (no duplicates)
    session["max word count"] = min(len(words), myconfig["dictee word count"])
    session["current word count"] = session["max word count"]

    #shorten the list if too long (after mixing)
    random.shuffle(words)  
    words = words[:session["current word count"]]

    #the words list is stored in the session
    session["wordslist"] = words

    session["dictee mode"] = mode
    session["dictee year"] = year
    session["dictee week"] = week

    session.modified = True

    return redirect(f"/dictee")


@app.route("/dictee")
def dictee_page():
    if session["current word count"] < 1:
        #finished
        return redirect("/dictee_result")

    #dec
    session["current word count"] -= 1
    #pop and requeue (assume already shuffled) => processed words are requeued so they can be shown in order at the end
    word = session["wordslist"].pop(0)
    session["wordslist"].append(word)

    session.modified = True

    mode = session["dictee mode"]
    return render_template("dictee01.html",  title="Dictée de la semaine" if mode == "single" else "Dictée de révision", word=word, **current_app.global_render_template_params)


@app.route("/dictee_result")
def dictee_result_page():
    content = ""
    content += f"Mode: {session['dictee mode']}<br/>"
    content += f"Annee: {session['dictee year']}<br/>"
    content += f"Semaine: {session['dictee week']}<br/>"
    content += f"Langue: {session['language']}<br/>"

    mode = session["dictee mode"]
    return render_template("results01.html", title="Dictée de la semaine" if mode == "single" else "Dictée de révision", pagecontent=content, results=session["wordslist"], **current_app.global_render_template_params)    


@app.route("/help")
def help_page():
    return render_template("help01.html", pagename="Help", **current_app.global_render_template_params)

########################################################################################
## Main entry point
#
if __name__ == '__main__':
    try:
        #logging
        directory = os.path.dirname(myconfig.get("logfile", "/tmp/dictee-tor.log"))
        if directory != "" and not os.path.exists(directory):
            os.makedirs(directory)

        logging.basicConfig(filename=myconfig.get("logfile", "/tmp/dictee-tor.log"), level=myconfig.get("loglevel", logging.INFO))

        app.logger.warning("Starting the app")

        #init the database
        dbutils.init(myconfig["database"])

        #start web interface
        app.debug = True
        app.run(host='0.0.0.0', port=myconfig.get("port", 12345), threaded=True)

    except Exception as e:
        print("Error in main: %s" % str(e))
        app.logger.error("Error in main: %s" % str(e))
        raise