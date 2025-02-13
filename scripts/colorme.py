# Print stuff to the console with color

# via:
# https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Error
def adderrorcolor(func):
    def function_wrapper(*args):
        print(bcolors.FAIL, end='')
        func(*args)
        print(bcolors.ENDC, end='')
    return function_wrapper

# Warning
# Use blue as a warning bc yellow is impossible to read!
def addwarncolor(func):
    def function_wrapper(*args):
        print(bcolors.OKBLUE, end='')
        func(*args)
        print(bcolors.ENDC, end='')
    return function_wrapper

# Okay
def addokcolor(func):
    def function_wrapper(*args):
        print(bcolors.OKGREEN, end='')
        func(*args)
        print(bcolors.ENDC, end='')
    return function_wrapper

# https://www.geeksforgeeks.org/decorators-in-python/
def hello_decorator(func): 
    def inner1(*args): 
        print("Hello, this is before function execution") 
        func(*args) 
        print("This is after function execution")
    return inner1

@adderrorcolor
def errorprint(x):
    print(x)

# @addwarncolor
@adderrorcolor
def warnprint(x):
    print(x)

@addokcolor
def okprint(x):
    print(x)