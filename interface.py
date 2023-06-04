from secret_input import *
from os import system
import re
def get_data():
    '''input user data to process auth.
       Import note: you set permission at your account settings
       for foreign application to get access to your acount's music 
    '''
    login = secret_input("enter login:","*")
    password = secret_input("enter password:","*")
    return login, password

def get_number(number_input):
    '''get range of objects you will receive'''
    pattern = re.compile("\d*,\d*")
    
    if number_input == "all":
        return None,None

    #correct input is n,n where n is decimal number
    if pattern.match(number_input):
        left, right  = number_input.split(",")
        return int(left), int(right)
    else:
        system("cls")
        print("inccorect input! it must be n,n  where n is decimal number") 
        return -1, -1


def __get_response():
    try:
        response = input(">>")
        return response
    except KeyboardInterrupt:
        print("\n see you later!")
        exit(0)

def check_arguments(args, correct_number):
    if len(args) != correct_number:
        print("incorrect number of arguments")
        return -1
def check_target(target):
    if not target.upper() in ("TRACKS"): #,"ALBUMS"): currently disabled
        print("{} is invalid target!".format(target))
        return -1

def run(functions, mdb, audio):
    '''functions received dict of user commands, data base and audio session object'''
    while True:
        response = __get_response()
        
        head, *arguments = response.split(" ")
        if head in functions.keys():
            if head == "help":
                functions[head](functions)
                continue

            if functions[head](arguments,mdb,audio) == None:
                print("something went wrong with {} function...".format(head))
        else:
            print("{} doesn't exist!".format(head))
