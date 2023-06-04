from os.path import isfile
import sqlite3 as sl

def open_db():
    '''create table if it's not created yet and also create special tables,
       otherwise just open it and return its object'''
    create_table = False
    if not isfile("music.db"):
        create_table = True
        print("music data base will be created at the directory of app!")

    db = sl.connect("music.db")
    if not create_table:
        return db
    else:
        with db:
            '''
            there are 4 tables:
               TRACKS/ALBUMS tables contain data, shown below in request to data base.
               TRACKS_RANGE/ALBUMS_RANGE tables contain range of request ranges to
               prevent optionally wasteless loading of data already loaded. 
            '''
            
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
    '''add tracks albums'''
    req = "INSERT INTO {}(id,title,artist,url) values(?,?,?,?)".format(table)
    with db:
        db.executemany(req,data)

def get_max_id(db,table):
    '''get max id of any table'''
    req = "SELECT id FROM {} ORDER BY id DESC LIMIT 1".format(table)
    with db:
        data = db.execute(req)
        for row in data:
            return row[0]


def set_range(db, data,table):
    '''add new ranges into associated table'''
    req = "INSERT INTO {}(id, begin, end) values(?,?,?)".format(table)
    with db:
        db.executemany(req,data)
def get_range(db, table):
    '''get list of ranges tuples'''
    req = "SELECT begin, end FROM {}".format(table)

    ranges = []
    with db:
        data = db.execute(req)
        for row in data:
            ranges.append(row)
    return ranges

def is_table_empty(db, table):
    '''check is any table passed as argument is empty'''
    req = "SELECT COUNT(id) from {} LIMIT 1".format(table)
    with db:
        data = db.execute(req)
        for row in data:
            return row[0] == 0

def get_size(db, table):
    '''get number of elements in table'''
    req = "SELECT COUNT(id) FROM {}".format(table)
    with db:
        data = db.execute(req)
        for row in data:
            return row[0]
        
def get_elements(db,table, substr="",case=0,field=""):
    req = "SELECT title,artist,url FROM {}".format(table)
    if substr:
        title = field if case == 0 else "LOWER({})".format(field)
        req += " WHERE {} like '%{}%'".format(title,substr)

    elements = []
    with db:
        data = db.execute(req)
        for row in data:
            elements.append(row)
    return elements
