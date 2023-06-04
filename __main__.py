import vk_api
from vk_api.audio import VkAudio
import collections
from itertools import islice
import os
from os import system, path
import db as DB
import interface
from functools import reduce
import re
import audio_downloader as ad
import requests
from secret_input import *

def list_split(main_list, chunk_size):
    splitted_list = list()

    for i in range(0, len(main_list), chunk_size):
        splitted_list.append(main_list[i:i+chunk_size])
    return splitted_list

def get_session():
    '''send request to get main vk api object'''
    login,password = interface.get_data()
    vk_session = vk_api.VkApi(login=login,password=password)
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        exit(-1)
        
    print("get session successfully!")
    return vk_session


#----------------------------------------------
#functions related to process of checking range of request
def ask():
    '''function is used by check range'''
    choice = input("do you want to continue?(y/n):")
    if "n" == choice:
        return -1
    elif "y" == choice:
        return 1
    else:
        ask()
#-------------------------------------------------

#---------------------------------------------------
#section of functions representing user's commands
def scan(arguments,mdb,session):
    '''scan - scan accounts music to receive tracks in specified range. example : scan  10,100'''
    if interface.check_arguments(arguments, 1) == -1:
        return None

    target = "tracks"
    rng = arguments[0]

    #DISABLED FOR SOMETIME
    #if interface.check_target(target) == -1:
    #    return None
    
    begin, end = interface.get_number(rng)
    if begin == -1:
        print("{} is invalid range!".format(rng))
        return None

    run_through_music(begin,end,session.get_iter(),mdb,target)

    return 1


def size(arguments, mdb,session):
    '''size - get size of loaded data. example'''
    if interface.check_arguments(arguments,0) == -1:
        return None

    target = "tracks"

    #DISABLED FOR SOMETIME
    #if interface.check_target(target) == -1:
    #    return None
    
    print("size of {} is {}.".format(target,DB.get_size(mdb,target.upper())))

    return 1#ok

def get(arguments, mdb, session):
    '''get - get list of tracks.'''
    if interface.check_arguments(arguments,0) == -1:
        return None

    target = "tracks"

    #DISABLED FOR SOMETIME
    #if interface.check_target(target) == -1:
    #    return None
    
    elements = DB.get_elements(mdb,target.upper())
    total_size = len(elements)

    counter = 0
    for l in list_split(elements,10):
        for el in l:
            if not el == None:
                print("{} - {}".format(el[0],el[1]))
        print("slice #{}".format(counter))
        q = input("-------------")
        if "q" == q:break
        counter+= 1
            
    return 1#ok

def get_help(functions):
    '''help - show this text'''
    for k, v in functions.items():
        print("{}.".format(str(v.__doc__)))

    return 1#ok
def clear(arguments,mdb,session):
    '''clear - clear the terminal screen.'''
    os.system("clear")
    return 1#ok

def find(arguments, mdb, session):
    '''find - find substring in saved tracks/albums, also specify case sensitivity. example - find "wish yo" artist|track 0
       where 0 means non case sensible'''
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
     
    if interface.check_arguments(arguments,2) == -1:
        return None
    
    #if interface.check_target(arguments[0]) == -1:
    #    return None

    target="tracks"
    field,case = arguments
    if field not in ["track","artist"]:
        print("the third argument must be track or artist!")
        return None

    items = list(set(DB.get_elements(mdb,target,substr[1:-1],case,field)))
    for obj in enumerate(items):
        print("{}: {} - {}".format(obj[0],obj[1][1],obj[1][0]))

    ad.download(items)
    return 1#
    
#------------------------------------------------------------    


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
    try:
        os.chdir("vk_audio_downloader")
    except Exception as e:
        print("error! please move to folder or rename it as vk_audio_downloader")
        exit(-1)
        
    session = get_session()
    vkaudio = VkAudio(session)
    mdb = DB.open_db()

    functions = {
        "scan":scan,
        "size":size,
        "get":get,
        "help":get_help,
        "clear":clear,
        "find":find
        }
    interface.run(functions,mdb,vkaudio)
