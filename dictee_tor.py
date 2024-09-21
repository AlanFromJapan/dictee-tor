import logging
import os
import requests

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
@app.route("/api/speech2text/<lang>/<message>", methods=['GET'])
def speech_to_text(lang, message):
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
        logging.error(f"Error in speech_to_text: {str(e)}")
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
    if "dictee word count" not in session:
        session["dictee word count"] = myconfig["dictee word count"]

        


@app.route('/')
@app.route('/home')
def homepage():
    wc_total, _, wc_years, wc_weeksperyear = dbutils.db_stats()

    #ensure next dictation will start from the beginning
    session["dictee word count"] <= -1

    return render_template("home01.html", pagename="Home", stats=(wc_total, wc_years, wc_weeksperyear), **current_app.global_render_template_params)


@app.before_request
def set_global_variables():
    current_app.global_render_template_params = {} 


@app.route("/dictee")
def dictee_page():
    if session["dictee word count"] == 0:
        #finished
        session["dictee word count"] = -1
        content = "Resultat de la dictee ..."
        return render_template("template01.html", title="dictee xyz", pagecontent=content, **current_app.global_render_template_params)    

    if session["dictee word count"] <= -1:
        #restart
        session["dictee word count"] = myconfig["dictee word count"]

    #dec
    session["dictee word count"] -= 1

    #get a word
    word = None
    mode = request.args.get("mode", "single")
    year, week = request.args.get("weekid", "ce1-1").split("-")

    if mode == "single":
        #get a word from the selected week
        word = dbutils.random_word(year, week=week, lang=session["language"])
    else:
        #get a word from the selected year UP TO the selected week included
        word = dbutils.random_word(year, maxweek=week,lang=session["language"])
    
    return render_template("dictee01.html", title="Dictee de la semaine" if mode == "single" else "Dictee de revision", word=word, **current_app.global_render_template_params)


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