import vk_api
from vk_api.audio import VkAudio
from secret_input import *
import collections
from itertools import islice
import re
from os import system
import db

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
    pattern = re.compile("\d,\d")
    
    if number == "all":
        return None,None

    #correct input is n,n where n is decimal number
    if pattern.match(number):
        left, right  = number.split(",")
        return int(left), int(right)
    else:
        system("cls")
        get_number()
        
def process(db,session):
    vkaudio = VkAudio(session)
        
    choice = input("what do you want to scan:ls tracks/ls albums/search(1,2,3)?:")
    
    if "1" == choice:
        begin, end = get_number()
        run_through_music(begin,end,vkaudio.get_iter(),db,"TRACKS")
    elif "2" == choice:
        begin, end = get_number()
        run_through_music(begin, end, vkaudio.get_albums_iter(),db,"ALBUMS")
    elif "3" == choice:
        pass
    else:
        system("cls")
        process()
def run_through_music(begin,end, mus_iter,mdb,table):
    it = mus_iter if begin == None else islice(mus_iter,begin,end,1)
    for track in it:
        data = [(0,str(track.get('title')),str(track.get('artist')),str(track.get('url')))]
        db.add(mdb,data,table)
        
        print("artist : {}".format(data[0][2]))
        print("title : {}".format(data[0][1]))
        print("link(url) : {}".format(data[0][3]))
        print('-'*10)
        
if __name__ == "__main__":
    system("cls")
    mdb = db.open_db()
    process(mdb,get_session())




