from typing import List
MemList = List[float]

class Machine:
	def __init__(self, capacity: int) -> Machine:
		self.capacity = capacity
		self.memory = [0.0] * capacity
		self.allocated = [False] * capacity
		self.stack_ptr = 0
		self.base_ptr = 0


#########################################
############## Error codes ##############
#########################################
STACK_HEAP_COLLISION = 1;
NO_FREE_MEMORY       = 2;
STACK_UNDERFLOW      = 3;

# Fatal error handler. Always exits program.
def panic(code: int) -> void:
	message = "panic: ";
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

# Create new virtual machine
def machine_new(vars: int, capacity: int) -> Machine:
	result = Machine(capacity)
	
	#initialize the memory and allocated arrays
	for i in range(capacity):
		result.memory[i] = 0;
		result.allocated[i] = false;

	for (let i = 0; i < vars; i++)
		machine_push(result, 0);

	return result;
}

# Print out the state of the virtual machine's stack and heap
def machine_dump(vm: machine): void {
	let i:number;
	console.log("stack: [ ");
	for (i=0; i<vm.stack_ptr; i++)
	console.log(vm.memory[i]);
	for (i=vm.stack_ptr; i<vm.capacity; i++)
	console.log("  ");
	console.log("]\nheap:  [ ");
	for (i=0; i<vm.stack_ptr; i++)
		console.log("  ");
	for (i=vm.stack_ptr; i<vm.capacity; i++)
		console.log(`${vm.memory[i]} `);
	console.log("]\nalloc: [ ");
	for (i=0; i<vm.capacity; i++)
		console.log(`${vm.allocated[i]} `);
	console.log("]\n");
	let total: number = 0;
	for (i=0; i<vm.capacity; i++)
		total += vm.allocated[i] ? 1 : 0;
	console.log(`STACK SIZE	${vm.stack_ptr}\n`);
	console.log(`TOTAL ALLOC'D ${total}\n`);
}

# Free the virtual machine's memory. This is called at the end of the program.
def machine_drop(vm: machine): void {
	#JS doesn't have manual memory management, so this function does nothing
	#free(vm.memory);
	#free(vm.allocated);
}

def machine_load_base_ptr(vm: machine): void {
    # Get the virtual machine's current base pointer value,
    # and push it onto the stack.
    machine_push(vm, vm.base_ptr);
}

def machine_establish_stack_frame(
	vm: machine, 
	arg_size: number, 
	local_scope_size: number
): void {
    # Allocate some space to store the arguments' cells for later
    let args = Array<number>(arg_size);
    let i: number;
    # Pop the arguments' values off of the stack
    for (i=arg_size-1; i>=0; i--)
        args[i] = machine_pop(vm);

    # Push the current base pointer onto the stack so that
    # when this function returns, it will be able to resume
    # the current stack frame
    machine_load_base_ptr(vm);

    # Set the base pointer to the current stack pointer to 
    # begin the stack frame at the current position on the stack.
    vm.base_ptr = vm.stack_ptr;

    # Allocate space for all the variables used in the local scope on the stack
    for (i=0; i<local_scope_size; i++)
        machine_push(vm, 0);

    # Push the arguments back onto the stack for use by the current function
    for (i=0; i<arg_size; i++)
        machine_push(vm, args[i]);
}

def machine_end_stack_frame(
	vm: machine, 
	return_size: number, 
	local_scope_size: number
): void {
    # Allocate some space to store the returned cells for later
    let return_val = Array<number>(return_size);
    let i: number;
    # Pop the returned values off of the stack
    for (i=return_size-1; i>=0; i--)
        return_val[i] = machine_pop(vm);

    # Discard the memory setup by the stack frame
    for (i=0; i<local_scope_size; i++)
        machine_pop(vm);
    
    # Retrieve the parent function's base pointer to resume the function
    vm.base_ptr = machine_pop(vm);

    # Finally, push the returned value back onto the stack for use by
    # the parent function.
    for (i=0; i<return_size; i++)
        machine_push(vm, return_val[i]);
}

# Push a number onto the stack
def machine_push(vm: machine, n: number): void {
	if (vm.allocated[vm.stack_ptr])
		panic(STACK_HEAP_COLLISION);
	vm.memory[vm.stack_ptr++] = n;
}

# Pop a number from the stack
def machine_pop(vm: machine): number {
	if (vm.stack_ptr === 0) {
		panic(STACK_UNDERFLOW);
	}
	let result: number = vm.memory[vm.stack_ptr-1];
	vm.memory[--vm.stack_ptr] = 0;
	#--vm.stack_ptr;
	return result;
}

# Pop the `size` parameter off of the stack, and return a pointer to `size` number of free cells.
def machine_allocate(vm: machine): number {	
	let size = machine_pop(vm);
	let addr = 0;
	let consecutive_free_cells = 0;

	for (let i = vm.capacity-1; i > vm.stack_ptr; i--) {
		if (!vm.allocated[i]) consecutive_free_cells++;
		else consecutive_free_cells = 0;

		if (consecutive_free_cells === size) {
			addr = i;
			break;
		}
	}

	if (addr <= vm.stack_ptr)
		panic(NO_FREE_MEMORY);
	
	for (let i = 0; i < size; i++)
		vm.allocated[addr+i] = true;

	machine_push(vm, addr);
	return addr;
}

# Pop the `address` and `size` parameters off of the stack, and free the memory at `address` with size `size`.
def machine_free(vm: machine): void {
	let addr = machine_pop(vm);
	let size = machine_pop(vm);

	for (let i=0; i<size; i++) {
		vm.allocated[addr+i] = false;
		vm.memory[addr+i] = 0;
	}
}

# Pop an `address` parameter off of the stack, and a `value` parameter with size `size`.
# Then store the `value` parameter at the memory address `address`.
def machine_store(vm: machine, size: number): void {
	let addr = machine_pop(vm);

	for (let i = size-1; i >= 0; i--) vm.memory[addr+i] = machine_pop(vm);
}

# Pop an `address` parameter off of the stack, and push the value at `address` with size
#`size` onto the stack.
def machine_load(vm: machine, size: number): void {
	let addr = machine_pop(vm);

	for (let i=0; i<size; i++) machine_push(vm, vm.memory[addr+i]);
}

# Add the topmost numbers on the stack
def machine_add(vm: machine): void {
	machine_push(vm, machine_pop(vm) + machine_pop(vm));
}

# Subtract the topmost number on the stack from the second topmost number on the stack
def machine_subtract(vm: machine): void {
	let b = machine_pop(vm);
	let a = machine_pop(vm);
	machine_push(vm, a-b);
}

# Multiply the topmost numbers on the stack
def machine_multiply(vm: machine): void {
	machine_push(vm, machine_pop(vm) * machine_pop(vm));
}

# Divide the second topmost number on the stack by the topmost number on the stack
def machine_divide(vm: machine): void {
	let b = machine_pop(vm);
	let a = machine_pop(vm);
	machine_push(vm, a/b);
}

def machine_sign(vm: machine): void {
    let x = machine_pop(vm);
    if (x >= 0) {
        machine_push(vm, 1);
    } else {
        machine_push(vm, -1);
    }
}