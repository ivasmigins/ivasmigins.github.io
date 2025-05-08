Console app that grabs data from the website API. Info is displayed on the console, while graphs are put into images.

# Dependencies (install in order):
- lua (https://www.lua.org/)
- OpenSSL (https://www.openssl.org/)
    - libssl-dev also needed
- luasec (https://github.com/lunarmodules/luasec)
    - luasocket *might* be needed, I installed it before luasec but *in theory* it doesn't need it. If you have errors using the https request then install it.
        (https://github.com/lunarmodules/luasocket)
- cairo (https://www.cairographics.org/download/)
    - libcairo2-dev also needed
- oocairo (https://github.com/awesomeWM/oocairo)
    - documentation (https://geoffrichards.co.uk/lua/oocairo/)
- cjson (https://github.com/openresty/lua-cjson)

Some of these are installed easier using LuaRocks (https://luarocks.org/)

# How to run:
    - Install the dependencies
    - Run the following command while in the root directory of the project:
        ```
        lua main.lua
        ```