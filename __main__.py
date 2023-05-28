import vk_api
from vk_api.audio import VkAudio
from secret_input import *
import collections
from itertools import islice
import re
from os import system
import db as DB

def get_data():
    '''input user data to process auth.
       Import note: you set permission at your account settings
       for foreign application to get access to your acount's music 
    '''
    login = secret_input("enter login:","*")
    password = secret_input("enter password:","*")
    return login, password

def get_session():
    '''send request to get main vk api object'''
    login,password = get_data()
    vk_session = vk_api.VkApi(login=login,password=password)
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        exit(-1)
    print("get session successfully!")
    return vk_session

def get_number():
    '''get range of objects you will receive'''
    number = input("enter range of tracks/albums to search:")
    pattern = re.compile("\d*,\d*")
    
    if number == "all":
        return None,None

    #correct input is n,n where n is decimal number
    if pattern.match(number):
        left, right  = number.split(",")
        return int(left), int(right)
    else:
        system("cls")
        print("inccorect input! it must be n,n  where n is decimal number") 
        get_number()
def check_range(db,table, begin, end):
    if not DB.is_table_empty(db,table):
        ranges = DB.get_range(db,table)
        for r in ranges:
            if begin in r or end in r:
                print("there is similar or the same range already:{} !".format(r))

    max_id = DB.get_max_id(db,table)
    max_id = 0 if max_id == None else max_id
    
    DB.set_range(db,[(max_id+1,begin,end)],table)
def process(session):
    mdb = DB.open_db()
    vkaudio = VkAudio(session)
        
    choice = input("what do you want to scan:ls tracks/ls albums/search(1,2,3)?:")
    
    if "1" == choice:
        begin, end = get_number()
        check_range(mdb,"TRACKS_RANGE",begin,end)
        
        run_through_music(begin,end,vkaudio.get_iter(),mdb,"TRACKS")
    elif "2" == choice:
        begin, end = get_number()
        check_range(mdb,"ALBUMS_RANGE",begin,end)
        
        run_through_music(begin, end, vkaudio.get_albums_iter(),mdb,"ALBUMS")
    elif "3" == choice:
        pass
    else:
        system("cls")
        process(session)
def run_through_music(begin,end, mus_iter,mdb,table):
    #get iterator for slice or for every item from response(good luck with it)
    #also if begin is None, then end is the same
    try:
        it = mus_iter if begin == None else islice(mus_iter,begin,end,1)
    except Exception as e: #out of range error may appear
        print(str(e))
        return
    
    max_id = DB.get_max_id(mdb,table)
    counter = 0 if max_id == None else max_id + 1
    for track in it:
        data = [(counter,str(track.get('title')),str(track.get('artist')),str(track.get('url')))]
        DB.add(mdb,data,table)
        counter += 1
        
        print("artist : {}".format(data[0][2]))
        print("title : {}".format(data[0][1]))
        print("link(url) : {}".format(data[0][3]))
        print('-'*10)
        
if __name__ == "__main__":
    system("cls")
    process(get_session())




