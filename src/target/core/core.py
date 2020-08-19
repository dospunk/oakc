from typing import List

class Machine:
	def __init__(self, capacity: int) -> None:
		self.capacity : int         = capacity
		self.memory   : List[float] = [0.0] * capacity
		self.allocated: List[bool]  = [False] * capacity
		self.stack_ptr: int         = 0
		self.base_ptr : int         = 0


#########################################
############## Error codes ##############
#########################################
STACK_HEAP_COLLISION = 1
NO_FREE_MEMORY       = 2
STACK_UNDERFLOW      = 3

def panic(code: int) -> None:
	'''Fatal error handler. Always exits program.'''

	message = "panic: "
	messages = {
		1: "stack and heap collision during push",
		2: "no free memory left",
		3: "stack underflow"
	}
	try:
		message += messages[code]
	except KeyError as _:
		message += "unknown error code"
	print(message)
	raise SystemExit

def machine_new(vars: int, capacity: int) -> Machine:
	'''Create new virtual Machine'''

	result = Machine(capacity)
	
	#initialize the memory and allocated arrays
	for i in range(capacity):
		result.memory[i] = 0
		result.allocated[i] = False

	for i in range(vars):
		machine_push(result, 0)

	return result

def machine_dump(vm: Machine) -> None:
	'''Print out the state of the virtual Machine's stack and heap'''

	print("stack: [ ", end='')
	for i in range (vm.stack_ptr):
		print(vm.memory[i], end='')
	for i in range(vm.stack_ptr, vm.capacity):
		print("  ", end='')
	print("]\nheap:  [ ", end='')
	for i in range (vm.stack_ptr):
		print("  ", end='')
	for i in range(vm.stack_ptr, vm.capacity):
		print(vm.memory[i], end=' ')
	print("]\nalloc: [ ", end='')
	for i in range(vm.capacity):
		print(vm.allocated[i], end=' ')
	print("]")
	total = 0
	for i in range(vm.capacity):
		total += vm.allocated[i]
	print("STACK SIZE	", vm.stack_ptr)
	print("TOTAL ALLOC'D ", total)

def machine_drop(vm: Machine) -> None:
	'''
	Free the virtual Machine's memory. This is called at the end of the program.
	Python doesn't have manual memory management, so this function does nothing
	'''
	#free(vm.memory)
	#free(vm.allocated)

def machine_load_base_ptr(vm: Machine) -> None:
    '''Get the virtual Machine's current base pointer value and push it onto the stack.'''
    machine_push(vm, vm.base_ptr)

def machine_establish_stack_frame(vm: Machine, arg_size: int, local_scope_size: int) -> None:
    #Allocate some space to store the arguments' cells for later
    args = [0.0] * arg_size

    # Pop the arguments' values off of the stack
    for i in reversed(range(arg_size)):
        args[i] = machine_pop(vm)

    # Push the current base pointer onto the stack so that
    # when this function returns, it will be able to resume
    # the current stack frame
    machine_load_base_ptr(vm)

    # Set the base pointer to the current stack pointer to 
    # begin the stack frame at the current position on the stack.
    vm.base_ptr = vm.stack_ptr

    # Allocate space for all the variables used in the local scope on the stack
    for i in range(local_scope_size):
        machine_push(vm, 0)

    # Push the arguments back onto the stack for use by the current function
    for i in range(arg_size):
        machine_push(vm, args[i])

def machine_end_stack_frame(vm: Machine, return_size: int, local_scope_size: int) -> None:
    # Allocate some space to store the returned cells for later
    return_val = [0.0] * return_size
    # Pop the returned values off of the stack
    for i in reversed(range(return_size)):
        return_val[i] = machine_pop(vm)

    # Discard the memory setup by the stack frame
    for i in range(local_scope_size):
        machine_pop(vm)
    
    # Retrieve the parent function's base pointer to resume the function
    vm.base_ptr = machine_pop(vm)

    # Finally, push the returned value back onto the stack for use by
    # the parent function.
    for i in range(return_size):
        machine_push(vm, return_val[i])

def machine_push(vm: Machine, n: float) -> None:
	'''Push a number onto the stack'''
	if vm.allocated[vm.stack_ptr]:
		panic(STACK_HEAP_COLLISION)
	vm.stack_ptr += 1
	vm.memory[vm.stack_ptr] = n

def machine_pop(vm: Machine) -> float:
	'''Pop a number from the stack'''
	if vm.stack_ptr == 0:
		panic(STACK_UNDERFLOW)
	result = vm.memory[vm.stack_ptr-1]
	vm.stack_ptr -= 1
	vm.memory[vm.stack_ptr] = 0
	return result

def machine_allocate(vm: Machine) -> int:
	'''Pop the `size` parameter off of the stack, and return a pointer to `size` number of free
	cells.'''
	size = machine_pop(vm)
	addr = 0
	consecutive_free_cells = 0

	for i in reversed(range(vm.stack_ptr, vm.capacity)):
		if not vm.allocated[i]:
			consecutive_free_cells += 1
		else:
			consecutive_free_cells = 0

		if consecutive_free_cells == size:
			addr = i
			break

	if addr <= vm.stack_ptr:
		panic(NO_FREE_MEMORY)
	
	for i in range(size):
		vm.allocated[addr+i] = True

	machine_push(vm, addr)
	return addr

def machine_free(vm: Machine) -> None:
	'''
	Pop the `address` and `size` parameters off of the stack, and free the memory at
	`address` with size `size`.
	'''
	addr = machine_pop(vm)
	size = machine_pop(vm)

	for i in range(size):
		vm.allocated[addr+i] = False
		vm.memory[addr+i] = 0

def machine_store(vm: Machine, size: int) -> None:
	'''
	Pop an `address` parameter off of the stack, and a `value` parameter with size `size`.
	Then store the `value` parameter at the memory address `address`.
	'''
	addr = machine_pop(vm)
	for i in reversed(range(size)):
		vm.memory[addr+i] = machine_pop(vm)

def machine_load(vm: Machine, size: int) -> None:
	'''
	Pop an `address` parameter off of the stack, and push the value at `address` with size
	`size` onto the stack.
	'''
	addr = machine_pop(vm)
	for i in range(size):
		machine_push(vm, vm.memory[addr+i])

def machine_add(vm: Machine) -> None:
	'''Add the topmost numbers on the stack'''
	machine_push(vm, machine_pop(vm) + machine_pop(vm))

def machine_subtract(vm: Machine) -> None:
	'''Subtract the topmost number on the stack from the second topmost number on the stack'''
	b = machine_pop(vm)
	a = machine_pop(vm)
	machine_push(vm, a-b)

def machine_multiply(vm: Machine) -> None:
	'''Multiply the topmost numbers on the stack'''
	machine_push(vm, machine_pop(vm) * machine_pop(vm))

def machine_divide(vm: Machine) -> None:
	'''Divide the second topmost number on the stack by the topmost number on the stack'''
	b = machine_pop(vm)
	a = machine_pop(vm)
	machine_push(vm, a/b)

def machine_sign(vm: Machine) -> None:
    x = machine_pop(vm)
    if x >= 0:
        machine_push(vm, 1)
    else:
        machine_push(vm, -1)