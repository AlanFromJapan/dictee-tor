
import logging

myconfig = {
    #This is the path to the database file. It should be a sqlite3 file.
    "database" : "db/wordslist.db",

    #This is the number of words in a dictation session
    "dictee word count" : 10,

    #This is the language of the words in the database
    "language" : "fr",

    #Session secret key to encrypt the session cookie
    "session secret key" : "you can really put whatever you want, it's just to encrypt the thingy!",

    #Normally this should be True, but in case you use this where someone misconfigured the CA check settings then make this False.
    "SSL_CHECK" : True,

    #Block, Cursive or mix
    "letterstyle" : "block",

    #uppercase or lowercase
    "lettercase" : "lowercase",

    #VoiceRSS key for speech to text [https://voicerss.org/api/]
    "VoiceRSS key" : "your key here",

    #VoiceRSS speed: The speech rate (speed). Allows values: from -10 (slowest speed) up to 10 (fastest speed). Default value: 0 (normal speed).
    "VoiceRSS speed" : -3,

    #where is the logfile
    "logfile" : "/tmp/dictee-tor.log",

    #log level
    "loglevel" : logging.INFO,

    #TCP port number to listen to
    "port" : 56788,

    
}