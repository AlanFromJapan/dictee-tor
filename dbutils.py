import sqlite3
import random

__DB_FILE = "wordslist.db"

#Initiate the database utility
def init(db_file):
    global __DB_FILE
    __DB_FILE = db_file

#Get a random word from the database
# Return: (word, year, week, language)
def random_word(year, week=None, lang=None):
    con = sqlite3.connect(__DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT word, year, week, language FROM word WHERE year=?1 and (?2 IS NULL OR ?2 IS NOT NULL AND week=?2) and (?3 IS NULL OR ?3 IS NOT NULL AND language=?3)", (year, week, lang))
    words = cur.fetchall()
    con.close()

    if len(words) > 0:
        return words[random.randint(0, len(words)-1)]
    return None


#----------------------------------------------------------
# Test the dbutils.py
#----------------------------------------------------------
if __name__ == '__main__':
    init("db/wordslist.db")

    print("Random word with all params")
    print(random_word("ce1", 1, 'fr'))
    print("Random word with minimal params only")
    print(random_word("ce1"))
    print("Random word with some params")
    print(random_word("ce1", lang='fr'))

