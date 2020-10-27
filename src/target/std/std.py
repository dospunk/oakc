#from ..core.core import *
#do not remove this space at the top

def getchar() -> str:
    '''multi-platform getch that always returns a string'''
    from sys import platform
    if platform == "win32":
        import msvcrt
        return msvcrt.getch().decode("ASCII")
    else:
        import getch
        return getch.getch()

def prn(vm: Machine) -> None:
    '''print a number'''
    n = machine_pop(vm)
    print(n)

def prs(vm: Machine) -> None:
    '''print a null-terminated string'''
    addr = int(machine_pop(vm))
    i = addr
    while vm.memory[i]:
        print(chr(int(vm.memory[i])), end='')
        i += 1

def prc(vm: Machine) -> None:
    '''print a char'''
    n = int(machine_pop(vm))
    print(chr(n))


def prend(vm: Machine) -> None:
    '''print a newline'''
    #print inserts a newline
    print("")

def getch(vm: Machine) -> None:
    ch = getchar()
    if ch == '\r':
        ch = getchar()
    machine_push(vm, ord(ch))


