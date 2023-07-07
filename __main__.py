import vk_api
from vk_api.audio import VkAudio
import collections
from itertools import islice
import os
import sys
from os import system, path
import db as DB
import interface
from functools import reduce
import re
import audio_downloader as ad
import requests
from secret_input import *
from WindowMode import *
from create_album_dict import *

def list_split(main_list, chunk_size):
    '''split list into list of equal chunks'''
    splitted_list = list()

    for i in range(0, len(main_list), chunk_size):
        splitted_list.append(main_list[i:i+chunk_size])
    return splitted_list

def get_session(login, password,break_function = lambda error_msg:exit(-1)):
    '''send request to get main vk api object'''
    #weird app id to prevent Auth error
    vk_session = vk_api.VkApi(login=login,password=password,app_id=2685278)
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        break_function(error_msg)
        return None#if it doesn't break, than it will return None
        
    print("get session successfully!")
    return vk_session


#----------------------------------------------
#functions related to process of checking range of request
def ask():
    '''function is used by check range'''
    try:
        choice = input("do you want to continue?(y/n):")
        if "n" == choice:
            return -1
        elif "y" == choice:
            return 1
        else:
            ask()
    except KeyboardInterrupt:
        print("ok...")
#-------------------------------------------------

#---------------------------------------------------
#section of functions representing user's commands

def check_range(begin, end):
    if begin < 0 or end < 0:
        return False
    if begin == end:
        return False
    if begin > end:
        return False
    return True
def scan(arguments,mdb,session):
    '''scan - scan accounts music to receive tracks in specified range. example : scan  10,100 albums'''

    #first argument is range and the second one is table name: artists or tracks
    if interface.check_arguments(arguments, 2) == -1:
        return None
    
    scaning_range = arguments[0]
    target = arguments[1]
    if interface.check_target(target) == -1:
        return None
    
    begin, end = interface.get_number(scaning_range)
    if not check_range(begin,end):
        print("incorrect range {}:{}".format(begin,end))
        return None

    if target == "tracks":
        run_through_music(begin,end,session.get_iter(),mdb)
    else:
        run_through_albums(begin,end,session,mdb)
    return 1


def size(arguments, mdb,session):
    '''size - get size of loaded data, number of tracks or total size of all tracks of all albums'''
    if interface.check_arguments(arguments,1) == -1:
        return None

    target = arguments[0]

    if interface.check_target(target) == -1:
        return None
    
    print("size of {} is {}.".format(target,DB.get_size(mdb,target.upper())))

    return 1#ok

def __print_tracks(elements,non_stop=False):
    counter = 0
    for l in list_split(elements,10):
        for el in l:
            if not el == None:
                print("{} - {}".format(el[0],el[1]))
        if not non_stop:
            print("slice #{}".format(counter))
            try:
                q = input("-------------")
                if "q" == q:break
                counter+= 1
            except KeyboardInterrupt:
                print("")
                return 1
def __print_albums(elements,non_stop=False):

    #create table where key is name of album and its value is list of album's tracks
    albums = cad(elements)#create albums dict

    counter = 0
    for key in albums:
        print("album name:{}".format(key))
        print("*---------------*")
        for el in albums[key]:
            print("{} - {}".format(el[0],el[1]))
        print("album #{}".format(counter))
        counter+=1
        if not non_stop:
            try:
                q = input("------------")
                if "q" == q:break
            except KeyboardInterrupt:
                print("")
                return 1

    #return data for graphical mode
    if non_stop:
        return albums
            
def get(arguments, mdb, session,non_stop=False):
    '''get - get list of tracks or albums with their contents.'''
    if interface.check_arguments(arguments,1) == -1:
        return None

    target = arguments[0]
    if interface.check_target(target) == -1:
        return None
    
    elements = DB.get_elements(mdb,target.upper())
    total_size = len(elements)

    if target.lower() == "tracks":
        __print_tracks(elements,non_stop)
        return elements#for graphical mode
    else:
        result = __print_albums(elements,non_stop)
        return result
            
    return 1#ok

def get_help(functions):
    '''help - show this text'''
    #print docsting of every function that can be invoked by user
    for k, v in functions.items():
        print("{}.".format(str(v.__doc__)))

    return 1#ok
def clear(arguments,mdb,session):
    '''clear - clear the terminal screen.'''
    os.system("clear")
    return 1#ok

def find(arguments, mdb, session,terminal=True):
    '''find - find substring in saved tracks/albums, also specify case sensitivity. example - find "wish yo" artist|track 0
        tracks/albums where 0 means non case sensible'''
    def unite_substr(args):
        #i think there is better solution
        begin, end = -1,-1
        for el in enumerate(args,start=0):
            if el[1].count('"') == 2:#there might argument made of 1 word
                begin = end = el[0]
                break
            if '"' in el[1] and begin ==-1:
                begin = el[0]
            if '"' in el[1] and begin != -1:
                end = el[0]
        
        #incorrect argument
        if begin == -1 or end == -1: return None

        #too boring to explaing set stuff
        arg = set(range(begin,end+1))
        all_ids = set(range(0,len(arguments)))
        save = all_ids.difference(arg)

        another_arguments = list()
        for i in list(save):
            another_arguments.append(args[i])
            
        substr = args[begin] if begin == end else str(reduce(lambda a,b:a+" "+b,args[begin:end+1]))
        return substr, another_arguments


    substr, arguments = unite_substr(arguments)
    if interface.check_arguments(arguments,3) == -1:
        return None

    field,case,target = arguments
    if interface.check_target(target) == -1:
        return None

    if field not in ["track","artist"]:
        print("the third argument must be track or artist!")
        return None

    #tracks mean title
    #we can search matching name of artist
    #or name of track. There is no row called track, so use title instead
    if field == "track": field = "title"

    sub = substr[1:-1]
    items = list(set(DB.get_elements(mdb,target,sub,case,field)))
    for obj in enumerate(items):
        print("{}: {} - {}".format(obj[0],obj[1][1],obj[1][0]))

    if terminal:
        ad.download(items)
    else:
        return items
    
    return 1#
    
#------------------------------------------------------------    

def fetch_album(id,owner_id,session, album_name):
    try:
        tracks = session.get(owner_id=owner_id,album_id=id)
    except vk_api.exceptions.AccessDenied:
        print("it's unable to read '{}' album's data\n\n".format(album_name))
        return None

    return tracks

def run_through_albums(begin,end,session,mdb):
    '''this function runs through albums list'''

    current_user_id = session.user_id

    #get albums and check if everything is ok
    albums = session.get_albums(current_user_id)
    if begin > len(albums) or end > len(albums):
        print("range is out albums' number!")
        return None


    max_id = DB.get_max_id(mdb,"ALBUMS")
    counter = 0 if max_id == None else max_id + 1
    for album in albums[begin:end]:
        print(album['title'])
        print("*{}*\n".format("-"*10))

        #get tracks of albums
        tracks = fetch_album(album["id"],album["owner_id"],session,album["title"])
        if not tracks is None:
            for t in tracks:
                data = [( counter, t['title'], t['artist'], t['url'], album['title'] )]
                DB.add(mdb,data,"ALBUMS")
                counter += 1
                print("-"*20)
                print("title:{}".format(t["title"]))
                print("url:{}".format(t["url"]))
                print("-"*20)
    
def run_through_music(begin,end, mus_iter,mdb):
    '''this function runs through track list'''
    #get iterator for slice or for every item from response(good luck with it)
    #also if begin is None, then end is the same
    try:
        it = mus_iter if begin == None else islice(mus_iter,begin,end,1)
    except Exception as e: #out of range error may appear
        print(str(e))
        return
    
    max_id = DB.get_max_id(mdb,"TRACKS")
    counter = 0 if max_id == None else max_id + 1
    for track in it:
        data = [(counter,str(track.get('title')),str(track.get('artist')),str(track.get('url')),"none")]
        DB.add(mdb,data,"TRACKS")
        counter += 1
        
        print("artist : {}".format(data[0][2]))
        print("title : {}".format(data[0][1]))
        print("link(url) : {}".format(data[0][3]))
        print('-'*10)

def run_terminal_version(functions_table):
    system("cls")
    #try:
    #    os.chdir("vk_audio_downloader")
    #except Exception as e:
    #    print("error! run it as python vk_audio_downloader!")
    #    exit(-1)

    login,password = interface.get_data()
    session = get_session(login,password)
    vkaudio = VkAudio(session)
    mdb = DB.open_db()

    interface.run(functions_table,mdb,vkaudio)

def run_graphical_mode(functions):
    win = Window()
    session = win.run_enter_menu(get_session)
    if session is None:
        exit(0)
    vkaudio = VkAudio(session)
    mdb = DB.open_db()

    win.run_main_menu(functions,mdb,vkaudio)
    
if __name__ == "__main__":
    functions = {
        "scan":scan,
        "size":size,
        "get":get,
        "help":get_help,
        "clear":clear,
        "find":find
    }
    
    run_in_terminal = len(sys.argv) == 2 and sys.argv[1] == "terminal"
    if run_in_terminal:
        run_terminal_version(functions)
    elif not run_in_terminal and len(sys.argv) != 1:
        print("incorrect arguments!")
        exit(-1)
    else:
        del(functions["size"])
        del(functions["help"])
        del(functions["clear"])
        run_graphical_mode(functions)
