
function prn(vm)
    local n = machine_pop(vm)
    io.write(string.format("%g", n))
end

function prs(vm)
    local addr = machine_pop(vm)
    local i = addr
    while vm.memory[i] ~= 0 do
        io.write(string.format("%c", vm.memory[i]))
        i = i + 1
    end
end

function prc(vm)
    local n = machine_pop(vm)
    io.write(string.format("%c", n))
end

function prend(vm)
    io.write("\n")
end

function getch(vm)
    local ch = read(1)
    if ch == '\r' then
        ch = read(1)
    end
    machine_push(vm, string.byte(ch))
end

