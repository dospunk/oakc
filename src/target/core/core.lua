--[[typedef struct machine {
    double* memory
    bool*   allocated
    int     capacity
    int     stack_ptr
    int     base_ptr
} machine
]]--


-----------------------------------------------------------------------
----------------------------- Error codes -----------------------------
-----------------------------------------------------------------------
local const STACK_HEAP_COLLISION = 1
local const NO_FREE_MEMORY       = 2
local const STACK_UNDERFLOW      = 3

-- Fatal error handler. Always exits program.
function panic(code)
    io.write("panic: ")
    if     code==STACK_HEAP_COLLISION then io.write("stack and heap collision during push")
    elseif code==NO_FREE_MEMORY       then io.write("no free memory left")
    elseif code==STACK_UNDERFLOW      then io.write("stack underflow")
    else                                   io.write("unknown error code")
    end
    io.write("\n")
    os.exit(code)
end

-----------------------------------------------------------------------
----------------------------- Debug Info ------------------------------
-----------------------------------------------------------------------
-- Print out the state of the virtual machine's stack and heap
function machine_dump(vm)
    io.write("stack: [ ")
    for i = 0, vm.stack_ptr-1 do
        io.write(string.format("%g ", vm.memory[i]))
    end
    for i = vm.stack_ptr, vm.capacity-1 do
        io.write("  ")
    end
    io.write("]\nheap:  [ ")
    for i = 0, vm.stack_ptr-1 do
        io.write("  ")
    end
    for i = vm.stack_ptr, vm.capacity-1 do
        io.write(string.format("%g ", vm.memory[i]))
    end
    io.write("]\nalloc: [ ")
    for i = 0, vm.capacity-1 do
        io.write(string.format("%d ", vm.allocated[i]))
    end
    io.write("]\n")
    local total = 0
    for i = 0, vm.capacity-1 do
        if vm.allocated[i] then
            total = total + 1
        end
    end
    io.write(string.format("STACK SIZE    %d\n", vm.stack_ptr))
    io.write(string.format("TOTAL ALLOC'D %d\n", total))
end


-------------------------------------------------------------------------
--------------------- Stack manipulation operations ---------------------
-------------------------------------------------------------------------
-- Push a number onto the stack
function machine_push(vm, n)
    -- If the memory at the stack pointer is allocated on the heap,
    -- then the stack pointer has collided with the heap.
    -- The program cannot continue without undefined behaviour,
    -- so the program must panic.
    if vm.allocated[vm.stack_ptr] then
        panic(STACK_HEAP_COLLISION)
    end
    
    -- If the memory isn't allocated, simply push the value onto the stack.
    vm.memory[vm.stack_ptr] = n
    vm.stack_ptr = vm.stack_ptr + 1
end

-- Pop a number from the stack
function machine_pop(vm)
    -- If the stack pointer can't decrement any further,
    -- the stack has underflowed.

    -- It is not possible for pure Oak to generate code that will
    -- cause a stack underflow. Foreign functions, or errors in
    -- the virtual machine implementation are SOLELY responsible
    -- for a stack underflow.
    if vm.stack_ptr == 0 then
        panic(STACK_UNDERFLOW)
    end
    -- Get the popped value
    vm.stack_ptr = vm.stack_ptr - 1
    local result = vm.memory[vm.stack_ptr]
    -- Overwrite the position on the stack with a zero
    vm.memory[vm.stack_ptr] = 0
    return result
end

------------------------------------------------------------------------
---------------------- Constructor and destructor ----------------------
------------------------------------------------------------------------
-- Create new virtual machine
function machine_new(global_scope_size, capacity)
    local result = {}
    result.capacity  = capacity
    result.memory    = {}
    result.allocated = {}
    result.stack_ptr = 0

    for i = 0, capacity-1 do
        result.memory[i] = 0
        result.allocated[i] = false
    end

    for i = 0, global_scope_size-1 do
        machine_push(result, 0)
    end

    result.base_ptr = 0

    return result
end

-- Free the virtual machine's memory. This is called at the end of the program.
-- lua has automatic memory management
function machine_drop(vm)
    -- machine_dump(vm)
    -- free(vm.memory)
    -- free(vm.allocated)
end

------------------------------------------------------------------------
---------------------- Function memory management ----------------------
------------------------------------------------------------------------
-- Push the base pointer onto the stack
function machine_load_base_ptr(vm)
    -- Get the virtual machine's current base pointer value,
    -- and push it onto the stack.
    machine_push(vm, vm.base_ptr)
end

-- Establish a new stack frame for a function with `arg_size`
-- number of cells as arguments.
function machine_establish_stack_frame(vm, arg_size, local_scope_size)
    -- Allocate some space to store the arguments' cells for later
    local args = {}
    -- Pop the arguments' values off of the stack
    for i = arg_size-1, 0, -1 do
        args[i] = machine_pop(vm)
    end
    -- Push the current base pointer onto the stack so that
    -- when this function returns, it will be able to resume
    -- the current stack frame
    machine_load_base_ptr(vm)

    -- Set the base pointer to the current stack pointer to 
    -- begin the stack frame at the current position on the stack.
    vm.base_ptr = vm.stack_ptr

    -- Allocate space for all the variables used in the local scope on the stack
    for i = 0, local_scope_size-1 do
        machine_push(vm, 0)
    end

    -- Push the arguments back onto the stack for use by the current function
    for i = 0, arg_size-1 do
        machine_push(vm, args[i])
    end

    -- Free the space used to temporarily store the supplied arguments.
    -- lua has automatic memory management 
    -- free(args)
end

-- End a stack frame for a function with `return_size` number of cells
-- to return, and resume the parent stack frame.
function machine_end_stack_frame(vm, return_size, local_scope_size)
    -- Allocate some space to store the returned cells for later
    local return_val = {}
    -- Pop the returned values off of the stack
    for i = return_size-1, 0, -1 do
        return_val[i] = machine_pop(vm)
    end

    -- Discard the memory setup by the stack frame
    for i = 0, local_scope_size-1 do
        machine_pop(vm)
    end
    
    -- Retrieve the parent function's base pointer to resume the function
    vm.base_ptr = machine_pop(vm)

    -- Finally, push the returned value back onto the stack for use by
    -- the parent function.
    for i = 0, return_size-1 do
        machine_push(vm, return_val[i])
    end

    -- Free the space used to temporarily store the returned value.
    -- lua has automatic memory management
    -- free(return_val)
end


-------------------------------------------------------------------------
--------------------- Pointer and memory operations ---------------------
-------------------------------------------------------------------------
-- Pop the `size` parameter off of the stack, and return a pointer to `size` number of free cells.
function machine_allocate(vm)    
    -- Get the size of the memory to allocate on the heap
    local size = machine_pop(vm)
    local addr = 0
    local consecutive_free_cells = 0

    -- Starting at the end of the memory tape, find `size`
    -- number of consecutive cells that have not yet been
    -- allocated.
    for i = vm.capacity-1, vm.stack_ptr+1, -1 do
        -- If the memory hasn't been allocated, increment the counter.
        -- Otherwise, reset the counter.
        if not vm.allocated[i] then 
            consecutive_free_cells = consecutive_free_cells + 1
        else
            consecutive_free_cells = 0
        end

        -- After we've found an address with the proper amount of memory left,
        -- return the address.
        if consecutive_free_cells == size then
            addr = i
            break
        end
    end

    -- If the address is less than the stack pointer,
    -- the the heap must be full.
    -- The program cannot continue without undefined behavior in this state.
    if addr <= vm.stack_ptr then
        panic(NO_FREE_MEMORY)
    end
    
    -- Mark the address as allocated
    for i = 0, size-1 do
        vm.allocated[addr+i] = true
    end

    -- Push the address onto the stack
    machine_push(vm, addr)
    return addr
end

-- Pop the `address` and `size` parameters off of the stack, and free the memory at `address` with size `size`.
function machine_free(vm)
    -- Get the address and size to free from the stack
    local addr = machine_pop(vm)
    local size = machine_pop(vm)

    -- Mark the memory as unallocated, and zero each of the cells
    for i = 0, size-1 do
        vm.allocated[addr+i] = false
        vm.memory[addr+i] = 0
    end
end

-- Pop an `address` parameter off of the stack, and a `value` parameter with size `size`.
-- Then store the `value` parameter at the memory address `address`.
function machine_store(vm, size)
    -- Pop an address off of the stack
    local addr = machine_pop(vm)

    -- Pop `size` number of cells from the stack,
    -- and store them at the address in the same order they were
    -- pushed onto the stack.
    for i = size-1, 0, -1 do
        vm.memory[addr+i] = machine_pop(vm)
    end
end

-- Pop an `address` parameter off of the stack, and push the value at `address` with size `size` onto the stack.
function machine_load(vm, size)
    local addr = machine_pop(vm)
    for i = 0, size-1 do
        machine_push(vm, vm.memory[addr+i])
    end
end

-- Add the topmost numbers on the stack
function machine_add(vm)
    machine_push(vm, machine_pop(vm) + machine_pop(vm))
end

-- Subtract the topmost number on the stack from the second topmost number on the stack
function machine_subtract(vm)
    local b = machine_pop(vm)
    local a = machine_pop(vm)
    machine_push(vm, a-b)
end

-- Multiply the topmost numbers on the stack
function machine_multiply(vm)
    machine_push(vm, machine_pop(vm) * machine_pop(vm))
end

-- Divide the second topmost number on the stack by the topmost number on the stack
function machine_divide(vm)
    local b = machine_pop(vm)
    local a = machine_pop(vm)
    machine_push(vm, a/b)
end

function machine_sign(vm)
    local x = machine_pop(vm)
    if x >= 0 then
        machine_push(vm, 1)
    else
        machine_push(vm, -1)
    end
end


