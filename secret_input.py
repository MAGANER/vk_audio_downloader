import msvcrt
import sys

def __clear():
    print("\033[D",end="")
    print(" ",end="")
    print("\033[D",end="")
    sys.stdout.flush()
    
def secret_input(prompt,char=""):
    '''get terminal input without showing the input'''
    fb = lambda n: int.from_bytes(n,byteorder="big")# lambda to convert bytes into int

    #show prompt, then flush buffer to redraw
    print(prompt,end="")
    sys.stdout.flush()

    backspace_counter = 0
    
    #get input untill ENTER key is pressed
    result_value = ""
    while (pressed := msvcrt.getch()) and  fb(pressed) != 13:#until enter
        if fb(pressed) == 8 and  not backspace_counter == 0: #backspace
            __clear()
            result_value = result_value[:len(result_value)-1]
            backspace_counter-= 1
            continue
        
        if char != ""  and fb(pressed) != 8:# if there is specific character, show it instead of input
            print(char,end="")
            sys.stdout.flush()
            backspace_counter+=1
        result_value = result_value +chr(fb(pressed))

    print("")
    return result_value
