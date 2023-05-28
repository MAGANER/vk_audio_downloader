from os.path import isfile
import sqlite3 as sl

def open_db():
    create_table = False
    if not isfile("music.db"):
        create_table = True
        print("music data base will be created at the directory of app!")

    db = sl.connect("music.db")
    if not create_table:
        return db
    else:
        with db:
            req = '''
            CREATE TABLE {}(
                  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                  title Text,
                  artist Text,
                  url Text);
            '''
            db.execute(req.format("TRACKS"))
            db.execute(req.format("ALBUMS"))
    return db

def add(db,data,table):
    req = "INSERT INTO {}(id,title,artist,url) values(?,?,?,?)".format(table)
    with db:
        db.executemany(req,data)
