import sqlite3
import os
import sys

#db file name
dbfile = "wordslist.db"

path_to_files = None
if len(sys.argv) > 1:
    path_to_files = sys.argv[1]
else:
    print("Usage: python3 gen_db_from_wordslist.py <path to files>")
    print("     <path to files> is the path to the directory containing the wordslist files")
    print("     Expects file names to be in the format: <year>-week<week>.txt (ie: ce1-week03.txt)")
    sys.exit(1)
    
#delete old db file
try:
    os.remove(dbfile)
except Exception as e:
    pass


con = sqlite3.connect("wordslist.db")
cur = con.cursor()
cur.execute("CREATE TABLE word(word TEXT, language TEXT, year TEXT, week int)")

for root, dirs, files in os.walk(path_to_files):
    for file in files:
        if file.endswith(".txt"):
            with open(os.path.join(root, file), "r") as f:
                for line in f:
                    line = line.strip()
                    if len(line) > 0:
                        word = line
                        language = "fr"
                        year = file.split("-")[0]
                        week = int(file.split("-")[1].split(".")[0].replace("week", ""))
                        cur.execute("INSERT INTO word(word, language, year, week) VALUES(?, ?, ?, ?)", (word, language, year, week))

con.commit()
con.close()
print("Done")
