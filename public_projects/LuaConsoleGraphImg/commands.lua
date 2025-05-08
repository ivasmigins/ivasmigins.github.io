local out_r = require("outputresponses")
local https = require("ssl.https")
local json = require("cjson")
local cairo = require("oocairo")

-- Public Members

local commands = {}

-- Private Members

local attr_to_unit = {
    temperature_inside = "°C",
    temperature_outside = "°C",
    humidity = "%",
    light = "%",
    snr = "dB",
    signal_strength = "dBm",
    pressure = "hPa",
    battery_voltage = "V",
}

local defaultColors = {
    {1, 0, 0},{0.9, 0.1, 0.1},
    {0, 1, 0},{0.1, 0.9, 0.1},
    {0, 0, 1},{0.1, 0.1, 0.9},
    {1, 1, 0},{0.9, 0.9, 0.1},
    {1, 0, 1},{0.9, 0.1, 0.9},
    {0, 1, 1},{0.1, 0.9, 0.9},
}

-- Private functions

local function GetData(url)
    local response_body, code = https.request(url)
    if code == 200 then
        local decoded = json.decode(response_body)
        if decoded then
            return decoded
        else
            print(out_r.error_decoding_json)
        end
    else
        print(out_r.invalid_http_request, code)
    end
end

local function draw_text(cr, x, y, text, font, size, rotation)
    cr:save() -- cool
    cr:translate(x, y)
    if rotation then
        cr:rotate(rotation)
    end
    cr:select_font_face(font, "normal")
    cr:set_font_size(size)
    cr:move_to(0, 0)
    cr:show_text(text)
    cr:restore()
end

local function randomColor(index)
    if index > #defaultColors then
        return {math.random(), math.random(), math.random()}
    else
        return defaultColors[index]
    end
end

local function plotToImage(cr, plotTable, device, spaceY, colorIndex)
    local plotSize = #plotTable

    local pointColor = randomColor(colorIndex)
    local lineColor = randomColor(colorIndex + 1)
    for i,v in ipairs(plotTable) do
        -- points
        cr:set_source_rgb(pointColor[1], pointColor[2], pointColor[3])
        cr:arc(v[1], v[2], 4, 0, math.pi*2)
        cr:fill()

        -- lines
        cr:set_source_rgb(lineColor[1], lineColor[2], lineColor[3]);
        cr:move_to(plotTable[i][1], plotTable[i][2])
        if plotSize >= i+1 then
            cr:line_to(plotTable[i+1][1], plotTable[i+1][2])
            cr:stroke()
        end
    end

    cr:set_source_rgb(lineColor[1], lineColor[2], lineColor[3])
    draw_text(cr, 1450, spaceY, device, "Arial", 20, -math.pi/2)
end

-- Public functions

commands.help = function()
    print(out_r.help)
end

commands.exit = function()
    print(out_r.exit)
    return "exit"
end

commands.list = function()
    print("Listing all available devices...")
    local data = GetData("https://project-software.codestate.nl/api/nodes")
    if data then
        for i, v in ipairs(data) do
            print(v.node_id)
        end
    else
        print(out_r.invalid_data)
    end
end

commands.stats = function(args)
    if args[1] == nil then
        print(out_r.invalid_argument)
        return
    end
    print("Getting the current basic stats for "..args[1].."...")
    local data = GetData("https://project-software.codestate.nl/api/get/"..args[1].."?limit=2") -- so I can treat as table
    if data and data[1] then
        for i,v in pairs(data[1]) do
            if type(v) == "userdata" then
                v = "N/A"
            end
            print(i..": "..v)
        end
    else
        print(out_r.invalid_data)
    end
end

commands.graph = function(args)
    if args[1] == nil or args[2] == nil or args[3] == nil or args[4] == nil then
        print(out_r.invalid_argument)
        return
    end
    local time = string.lower(args[1])
    local attribute = args[2]
    local file_name = args[3]
    local devices = {}
    for i = 4, #args do
        table.insert(devices, args[i])
    end
    if not attr_to_unit[attribute] then
        print(out_r.invalid_argument)
        print("ALL available attributes (some depend on device):")
        for i,v in pairs(attr_to_unit) do
            print(i)
        end
        return
    end

    print("Making a graph of the desired stat...")
    local surface = cairo.image_surface_create("rgb24", 1500, 1500)
    local cr = cairo.context_create(surface)

    -- Canvas
    cr:rectangle(0, 0, 1500, 1500)
    cr:set_source_rgb(1, 1, 1)
    cr:fill()

    -- Grid
    local grid_lines = 16
    cr:set_source_rgb(0.8, 0.8, 0.8)
    for i = 0, grid_lines do
        cr:rectangle(100, 100+(1300/grid_lines)*i, 1300, 3)
        cr:fill()
        cr:rectangle(100+(1300/grid_lines)*i, 100, 3, 1300)
        cr:fill()
    end

    -- Y axis
    cr:rectangle(100, 100, 5, 1300)
    cr:set_source_rgb(0, 0, 0)
    cr:fill()
    draw_text(cr, 25, 785, "data ("..attr_to_unit[attribute]..")", "Arial", 20, -math.pi/2)

    -- X axis
    cr:rectangle(100, 1400, 1300, 5)
    cr:set_source_rgb(0, 0, 0)
    cr:fill()

    local current_time, past_time, xLabel
    if string.find(time, "-") then
        --more stuff to avoid useless requests; the string could just be split and sent but why not
        local t_date = {}
        for d in string.gmatch(time, "([^-]+)") do
            for w in string.gmatch(d, "([^/]+)") do
                table.insert(t_date, w)
            end
        end

        for i,v in pairs(t_date) do
            local num = tonumber(v)
            if not num then
                print(out_r.invalid_date)
                return
            end
        end
        if not #t_date == 6 then
            print(out_r.invalid_date)
            return
        end

        past_time = t_date[3].."-"..t_date[2].."-"..t_date[1]
        current_time = t_date[6].."-"..t_date[5].."-"..t_date[4]
        xLabel = time
    else
        local date1 = os.time()
        local date2 = date1 - 3600
        if time == "day" then
            date2 = date1 - 86400
        elseif time == "week" then
            date2 = date1 - 604800
        elseif time ~= "hour" then
            print(out_r.invalid_argument)
            return
        end

        current_time = os.date("%Y-%m-%d %H:%M:%S", date1)
        past_time = os.date("%Y-%m-%d %H:%M:%S", date2)
        xLabel = "last "..time
    end

    draw_text(cr, 750, 1450, xLabel, "Arial", 20)
    draw_text(cr, 250, 50, attribute.." for "..table.concat(devices, " & "), "Arial", 25)
    draw_text(cr, 250, 75, "from "..past_time.." to "..current_time, "Arial", 25)

    -- data
    local devicesData = {}
    local hasData = false
    for i,v in pairs(devices) do
        local data = GetData("https://project-software.codestate.nl/api/graph/"..v.."?start="..past_time.."&end="..current_time)
        if data then
            devicesData[v] = data
            hasData = true
        end
    end

    if hasData then
        local max = -math.huge
        local min = math.huge

        for o, p in pairs(devicesData) do -- Find max and min from all data
            for i, v in pairs(p) do
                if v[attribute] and type(v[attribute]) == "number" then
                    if v[attribute] > max then
                        max = v[attribute]
                    elseif v[attribute] < min then
                        min = v[attribute]
                    end
                else
                    print("\nAttribute not found on device: "..o, out_r.invalid_argument)
                    return
                end
            end
        end

        if (max == -math.huge and min == math.huge) then
            print(out_r.invalid_data)
            return
        end

        if max == min then --edge case, usually on hour requests.
            max = max + 10
            min = min - 10
        end

        local diff = max - min
        local currDevice = 0;
        local colorIndex = 1;
        for o, p in pairs(devicesData) do
            local plotTable = {}
            for i, v in ipairs(p) do
                local x = 100 + ((i - 1) * 1300 / math.max(#p - 1, 1)) -- if there was 1 entry it would error without math.max
                local y = 1400 - ((v[attribute] - min) * 1300 / diff)
                table.insert(plotTable, {x, y})
            end
            local heightRoom = (1500 / #devices)
            plotToImage(cr, plotTable, o, currDevice * heightRoom + heightRoom/2, colorIndex)
            colorIndex = colorIndex + 2
            currDevice = currDevice + 1
        end

        -- y axis markers
        cr:set_source_rgb(0, 0, 0)
        local intervals = 6
        for i = 0, intervals - 1 do
            local value = min + i * (diff / (intervals - 1))
            local y_position = 1400 + i * ((100 - 1400) / (intervals - 1))
            draw_text(cr, 10, y_position, tostring(value), "Arial", 20)
        end

        surface:write_to_png(file_name..".png")
        print("Graph saved as "..file_name..".png in the project directory.")
    else
        print(out_r.invalid_data)
        return
    end
end

return commands;