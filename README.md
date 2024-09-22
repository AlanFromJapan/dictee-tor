# dictee-tor
A web application using speech to text to have your kids practice "dictee" (dictation).

![Homepage](/images/home.png?raw=true) ![Results](/images/result.png?raw=true)

## Name 
Dictee is French for dictation so ... "Dicta-tor" ... got it? Mwahaha ! 🤣 Yeah it s*cks but I was short on nice name.

## Motivation
I have young kids learning French, and my son wanted to be able to run his weekly dication by himself. Once I explained him that him *reading* the words would not make sense in a dictation exercise, I got to think of how I could help him. 

I already input all the words of the year (2024) in the **seyes-wordlist** https://github.com/AlanFromJapan/seyes-wordlist project that generates caligraphy script version of the words to practice. So moved all to a DB file, reused the Text-to-speech I used in **poke-trainer** https://github.com/AlanFromJapan/poke-trainer, and voila.

## Modes
### Dictee de la semaine (dictation of the week)
Pick one week and practice the words of *that week only*.

### Dictee de revision (review dictation)
Pick one week and practice the words of *the begining of the year until that week included*. Will be limited to 10 words by default (edit config to change that).

# Installation
## Mandatory - Need to get you key for Voice RSS
The Text-to-Speech API used is **Voice RSS API**. Go to the Login page https://voicerss.org/login.aspx, create a free account, and get your *token*. The free account allows for 350 calls per day, which should be enough, but feel free to subscribe!

Then update your *config.py* (copied from *config.sample.py*): "VoiceRSS key" : "*your key here*"

**OR**

You can set the environment variable *VOICERSS_KEY* on the server or the Docker container.

## Manual install
1. git clone https://github.com/AlanFromJapan/dictee-tor
1. python3 -m venv .
1. source bin/activate
1. python -m pip install -r requirements.txt
1. copy config.sample.py config.py
1. EDIT YOUR Voice RSS token (see above↑) + other values of config.py
1. deactivate
1. bin/python dictee-tor.py

## Docker container version
Assuming you have Docker working on your PC:
1. `git clone https://github.com/AlanFromJapan/dictee-tor`
1. `copy config.sample.py config.py`
1. EDIT YOUR Voice RSS token (see above↑) + other values of config.py
1. `docker build -t dictee-tor .`
1. `docker run --name dictee-container --env VOICERSS_KEY=<your_voicerss_token> -d dictee-tor`
    - In case you provide the environment variable, it will override whatever is in the config file. Pick according your usecase.

