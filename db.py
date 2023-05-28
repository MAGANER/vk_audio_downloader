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

            req = '''
            CREATE TABLE {}_RANGE(
                  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                  begin INTEGER,
                  end INTEGER);'''
            db.execute(req.format("TRACKS"))
            db.execute(req.format("ALBUMS"))
            
    return db

def add(db,data,table):
    req = "INSERT INTO {}(id,title,artist,url) values(?,?,?,?)".format(table)
    with db:
        db.executemany(req,data)

def get_max_id(db,table):
    req = "SELECT id FROM {} ORDER BY id DESC LIMIT 1".format(table)
    with db:
        data = db.execute(req)
        for row in data:
            return row[0]
def get_range(db, table):
    req = "SELECT begin, end FROM {}".format(table)
    with db:
        data = db.execute(req)
        for row in data:
            return row[0], row[1]
def set_range(db, data,table):
    req = "INSERT INTO {}(id, begin, end) values(?,?,?)".format(table)
    with db:
        db.executemany(req,data)
def get_range(db, table):
    req = "SELECT begin, end FROM {}".format(table)

    ranges = []
    with db:
        data = db.execute(req)
        for row in data:
            ranges.append(row)
    return ranges

def is_table_empty(db, table):
    req = "SELECT COUNT(id) from {} LIMIT 1".format(table)
    with db:
        data = db.execute(req)
        for row in data:
            return row[0] == 0
