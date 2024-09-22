import sqlite3
import random

__DB_FILE = "wordslist.db"

#Initiate the database utility
def init(db_file):
    global __DB_FILE
    __DB_FILE = db_file

#Get a random word from the database
# Params:
# year: The year of the word
# week: The week of the word (for the single revision)
# lang: The language of the word
# maxweek: The maximum week (included) to get the word from (for the revision)
# Return: (word, year, week, language)
def random_word(year, week=None, lang=None, maxweek=None):
    words = all_words(year, week, lang, maxweek)

    if len(words) > 0:
        return words[random.randint(0, len(words)-1)]
    return None


#Get ALL words from the database according to the parameters
# Params:
# year: The year of the word
# week: The week of the word (for the single revision)
# lang: The language of the word
# maxweek: The maximum week (included) to get the word from (for the revision)
# Return: (word, year, week, language)
def all_words(year, week=None, lang=None, maxweek=None):
    con = sqlite3.connect(__DB_FILE)
    cur = con.cursor()

    cur.execute("""
SELECT 
    word, year, week, language 
FROM 
    word 
WHERE 
    year=?1 
    and (?2 IS NULL OR ?2 IS NOT NULL AND week=?2) 
    and (?3 IS NULL OR ?3 IS NOT NULL AND language=?3)
    and (?4 IS NULL OR ?4 IS NOT NULL AND week <= ?4);""", (year, week, lang, maxweek))

    words = cur.fetchall()
    con.close()

    return words


#returns useful stats about the database
def db_stats():
    con = sqlite3.connect(__DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT count(*) FROM word")
    wc = cur.fetchone()
    cur.execute("SELECT count(*) FROM word WHERE language='fr'")
    wcfr = cur.fetchone()
    cur.execute("SELECT year, count(1) FROM word group by year")
    wcyears = cur.fetchall()
    cur.execute("SELECT DISTINCT year, week FROM word ORDER BY year, week")
    wcweeksperyear = cur.fetchall()
    con.close()
    
    return wc[0], wcfr[0], wcyears, wcweeksperyear


#----------------------------------------------------------
# Test the dbutils.py
#----------------------------------------------------------
if __name__ == '__main__':
    init("db/wordslist.db")

    print("All words for a week")
    print(all_words("ce1", 2, 'fr'))
    print("All words UP TO a week")
    print(all_words("ce1", lang='fr', maxweek=3))

    print("Random word with all params")
    print(random_word("ce1", 1, 'fr'))
    print("Random word with minimal params only")
    print(random_word("ce1"))
    print("Random word with some params")
    print(random_word("ce1", lang='fr'))

    print("Stats")
    print(db_stats())