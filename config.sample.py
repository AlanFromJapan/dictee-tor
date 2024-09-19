
import logging

myconfig = {

    "language" : "fr",

    "session secret key" : "you can really put whatever you want, it's just to encrypt the thingy!",

    #Normally this should be True, but in case you use this where someone misconfigured the CA check settings then make this False.
    "SSL_CHECK" : True,

    #Block, Cursive or mix
    "letterstyle" : "block",

    #uppercase or lowercase
    "lettercase" : "lowercase",

    #VoiceRSS key for speech to text
    "VoiceRSS key" : "your key here",

    #where is the logfile
    "logfile" : "/tmp/poke-trainer.log",

    #log level
    "loglevel" : logging.INFO,

    #TCP port number to listen to
    "port" : 56788,

    
}