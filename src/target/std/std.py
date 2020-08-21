
#do not remove this space at the top

import getch as getchar

def prn(vm: Machine) -> None:
	'''print a number'''
	n = machine_pop(vm)
	print(n)

def prs(vm: Machine) -> None:
	'''print a null-terminated string'''
	addr = machine_pop(vm)
	i = addr
	while vm.memory[i]:
		print(chr(vm.memory[i]), end='')
		i += 1

def prc(vm: Machine) -> None:
	'''print a char'''
	n = machine_pop(vm)
	print(chr(n))


def prend(vm: Machine) -> None:
	'''print a newline'''
	#print inserts a newline
	print("")

def getch(vm: Machine) -> None:
	ch = getchar.getch()
	if ch == '\r':
		ch = getchar.getch()
	machine_push(vm, ch)


