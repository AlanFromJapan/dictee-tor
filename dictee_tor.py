import random
import logging
import os

from flask import Flask, redirect, render_template, current_app, session
#running behind proxy?                                                                                            
from werkzeug.middleware.proxy_fix import ProxyFix

from config import myconfig


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
    return render_template("home01.html", pagename="Home", **current_app.global_render_template_params)


@app.before_request
def set_global_variables():
    current_app.global_render_template_params = {} 




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

        #start web interface
        app.debug = True
        app.run(host='0.0.0.0', port=myconfig.get("port", 12345), threaded=True)

    except Exception as e:
        print("Error in main: %s" % str(e))
        app.logger.error("Error in main: %s" % str(e))
        raise