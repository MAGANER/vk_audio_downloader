import msvcrt
import sys

def secret_input(prompt,char=""):
    '''get terminal input without showing the input'''
    fb = lambda n: int.from_bytes(n,byteorder="big")# lambda to convert bytes into int

    #show prompt, then flush buffer to redraw
    print(prompt,end="")
    sys.stdout.flush()

    #get input untill ENTER key is pressed
    result_value = ""
    while (pressed := msvcrt.getch()) and  fb(pressed) != 13:
        if char != "":# if there is specific character, show it instead of input
            print(char,end="")
            sys.stdout.flush()
        result_value = result_value +chr(fb(pressed))

    print("")
    return result_value
