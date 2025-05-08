local io = require("io")
local out_r = require("outputresponses")
local commands = require("commands")

print(out_r.welcome)

while true do
    io.write("> ")
    local line = io.read()
    local command, rest = string.match(line, "(%S+)%s*(.*)")
    if command then
        local args = {}
        for arg in string.gmatch(rest, "%S+") do
            table.insert(args, arg)
        end

        if commands[command] then
            local result = commands[command](args)
            if result == "exit" then break end
        else
            print(out_r.invalid_command)
        end
    else
        print(out_r.invalid_command)
    end
end