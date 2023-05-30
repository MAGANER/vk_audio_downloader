import vk_api
from vk_api.audio import VkAudio
import collections
from itertools import islice
from os import system
import db as DB
import interface

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
def check_is_range_already_exist(begin,end,ranges):
    for r in ranges:
        check1 = begin in r or end in r
        check2 = lambda n: r[0] <= n <= r[1]
        if check1 or check2(begin) or check2(end):
            print("there is similar or the same range already:{} !".format(r))
            if ask() == -1:
                return None
    return 1
def check_range(db,table, begin, end):
    if not DB.is_table_empty(db,table):
        ranges = DB.get_range(db,table)
        if check_is_range_already_exist(begin,end,ranges) == None:
            return None

    max_id = DB.get_max_id(db,table)
    max_id = 0 if max_id == None else max_id
    
    DB.set_range(db,[(max_id+1,begin,end)],table)
#-------------------------------------------------

#---------------------------------------------------
#section of functions representing user's commands
def scan(arguments,mdb,session):
    if interface.check_arguments(arguments, 2) == -1:
        return None

    target, rng = arguments
    if interface.check_target(target) == -1:
        return None

    begin, end = interface.get_number(rng)
    if begin == -1:
        print("{} is invalid range!".format(rng))
        return None

    if check_range(mdb,target+"_RANGE",begin,end) == None:
        print("{} won't be scanned.".format(target))
        return None

    run_through_music(begin,end,session.get_iter(),mdb,target)

    return 1


def size(arguments, mdb,session):
    '''get size of tables'''
    if interface.check_arguments(arguments,1) == -1:
        return None

    target = arguments[0]
    if interface.check_target(target) == -1:
        return None
    
    print("size of {} is {}.".format(target,DB.get_size(mdb,target.upper())))

    return 1#ok

def get(arguments, mdb, session):
    if interface.check_arguments(arguments,1) == -1:
        return None

    target = arguments[0]
    if interface.check_target(target) == -1:
        return None

    elements = DB.get_elements(mdb,target.upper())

    return 1#ok
    
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
    
    session = get_session()
    vkaudio = VkAudio(session)
    mdb = DB.open_db()

    functions = {
        "scan":scan,
        "size":size,
        "get":get
        }
    interface.run(functions,mdb,vkaudio)
