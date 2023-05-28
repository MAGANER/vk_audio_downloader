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


def run(functions, mdb, audio):
    while True:
        response = input(">>")
        head, *arguments = response.split(" ")

        if head in functions.keys():
            if functions[head](arguments,mdb,audio) == None:
                print("something went wrong with {} function...".format(head))
        else:
            print("{} doesn't exist!".format(head))
