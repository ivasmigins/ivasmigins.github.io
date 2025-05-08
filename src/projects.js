export const projects = [
    {
        title: "The Mimic",
        featured: true,
        description: "Lead Programmer for this horror game in Roblox with over <b>1 billion plays</b>.<br>Features boss fights, AI monsters, tons of puzzles, scripted sequences, and that's just a few.<br>For more information about this game, it can be easily found online!<br>This is one of the most widely known games on the platform and always talked about for it's quality. Coded using Luau.",
        videoId: "aK7AnPmdD-s",
        links: [{
            label: "Play",
            url: "https://www.roblox.com/games/6243699076/The-Mimic"
        },
        {
            label: "Group",
            url: "https://www.roblox.com/communities/9482918/CTStudio#!/about"
        }
        ],
        stats: [{
            label: "Difficulty",
            percentage: 70
        },
        {
            label: "Completion",
            percentage: 100
        }
        ]
    },
    {
        title: "ScaryPlay",
        featured: true,
        description: "Co-created and programmed a multiplayer game in Roblox with <b>10,000+ community members</b>.<br>The game isn't out yet. Trailer received over <b>850k views</b> and TikToks hit <b>11M+ views</b>.<br>Features randomly generated worlds, AI monsters, item interactions, and more!<br>Coded using Luau.",
        videoId: "vw4dz7sL7KE",
        links: [{
            label: "TikTok",
            url: "https://www.tiktok.com/@scaryplayofficial"
        },
        {
            label: "Group",
            url: "https://www.roblox.com/communities/32538104/ScaryPlay#!/about"
        }
        ],
        stats: [{
            label: "Difficulty",
            percentage: 80
        },
        {
            label: "Completion",
            percentage: 85
        }
        ]
    },
    {
        title: "Sensor connected to arduino",
        featured: true,
        description: "Code written in C where I connect to a temperature sensor using I2C, then communicate from the arduino to my PC using UART and store the data in a database. The data is then shown live on a website with different graphs! The code directly handles addresses and registers.",
        videoFile: "../videos/arduinosensor_preview.mp4",
        links: [{
            label: "Code",
            url: "https://github.com/ivasmigins/ivasmigins.github.io/tree/main/public_projects/ArduinoSensor"
        },
        {
            label: "Hardware image",
            url: "https://raw.githubusercontent.com/ivasmigins/ivasmigins.github.io/main/images/tempproject.png"
        }
        ],
        stats: [{
            label: "Difficulty",
            percentage: 65
        },
        {
            label: "Completion",
            percentage: 100
        }
        ]
    },
    {
        title: "Python MQTT Broker",
        description: "A MQTT Broker written in python which uses the paho library for MQTT connection, maria-db to connect and change a database, and dotenv files for security.<br>It grabs data from two different type of sensors, then formats it and saves it into a datastore!",
        image: "../images/mqttexplorer.png",
        links: [{
            label: "Code",
            url: "https://github.com/ivasmigins/ivasmigins.github.io/tree/main/public_projects/MQTTBroker"
        }
        ],
        stats: [{
            label: "Difficulty",
            percentage: 20
        },
        {
            label: "Completion",
            percentage: 100
        }
        ]
    },
    {
        title: "Graph generator via Lua console app",
        description: "A console application written in Lua which gets data from an API and generates graph .png files based on the requested data.<br> Uses oocairo to draw pixels onto an image!",
        image: "../images/ConsoleGraphOutputExample.png",
        links: [{
            label: "Code",
            url: "https://github.com/ivasmigins/ivasmigins.github.io/tree/main/public_projects/LuaConsoleGraphImg"
        }
        ],
        stats: [{
            label: "Difficulty",
            percentage: 50
        },
        {
            label: "Completion",
            percentage: 100
        }
        ]
    },
    {
        title: "Assembly x86-64 calculator",
        featured: true,
        description: "A console calculator written in assembly that uses floating point arithmetic to do addition, subtraction, multiplication, and division with negatives included.",
        image: "../images/calculator.png",
        links: [{
            label: "Code",
            url: "https://github.com/ivasmigins/ivasmigins.github.io/tree/main/public_projects/AssemblyCalculator"
        }
        ],
        stats: [{
            label: "Difficulty",
            percentage: 90
        },
        {
            label: "Completion",
            percentage: 100
        }
        ]
    },
    {
        title: "Monster Mayhem",
        description: "Created and programmed a game in Roblox where you play as a monster that destroys different maps, eats scared humans, gets stronger, and fights the military!<br>I have this project in an <b>indefinite hold</b> at the moment. Coded using Luau.",
        videoId: "CLwO-2jHnJ4",
        stats: [{
            label: "Difficulty",
            percentage: 50
        },
        {
            label: "Completion",
            percentage: 95
        }
        ]
    },
    {
        title: "WiFi Manager for ESP32",
        featured: true,
        description: "A singleton class written in C++ that connects to a wifi network, attempts to reconnect if connection is lost, and features POST and GET requests to a given URL.<br>The received data from a server is read in chunks with a modifiable limit to prevent issues!",
        image: "../images/esp32.png",
        links: [{
            label: "Code",
            url: "https://github.com/ivasmigins/ivasmigins.github.io/tree/main/public_projects/WifiManagerESP32"
        }
        ],
        stats: [{
            label: "Difficulty",
            percentage: 45
        },
        {
            label: "Completion",
            percentage: 100
        }
        ]
    },
    {
        title: "Tide Riders",
        description: "Created a retro-style physics based jetski racing game in Roblox where players complete stunts, customize their rider and jetski, earn achievements, and compete to be the best!<br>There are multiple maps, a queue/matchmaking system, and cool jetski physics!<br>This project was made around 2020. It is in an <b>indefinite hold</b> at the moment. Coded using Luau.",
        videoId: "BNv6ldoxjxs",
        stats: [{
            label: "Difficulty",
            percentage: 50
        },
        {
            label: "Completion",
            percentage: 80
        }
        ]
    },
    {
        title: "Roblox in-game catalog system",
        description: "Made it by using a proxy to connect to the official catalog page, and then retrieve data from it using GET requests. Features a cache to reduce requests and <b>smooth UI!</b>. Coded using Luau. Note: video is not mine, this was a commission.",
        videoFile: "../videos/catalog_preview.mp4",
        stats: [{
            label: "Difficulty",
            percentage: 40
        },
        {
            label: "Completion",
            percentage: 100
        }
        ]
    },
    {
        title: "Simple Recipe Finder App",
        description: "App written in C#/XAML that uses two APIs; one to get recipes and one to calculate the macronutrients for that recipe.",
        videoFile: "../videos/recipeapp_preview.mp4",
        links: [{
            label: "Code",
            url: "https://github.com/ivasmigins/ivasmigins.github.io/tree/main/public_projects/CsharpApp"
        }
        ],
        stats: [{
            label: "Difficulty",
            percentage: 15
        },
        {
            label: "Completion",
            percentage: 100
        }
        ]
    },
    {
        title: "This website",
        description: "I made the website you are seeing <b>right now!</b><br>It is written using JavaScript, HTML, and CSS.",
        image: "../images/fanartofme.png",
        links: [{
            label: "Link",
            url: "https://ivasmigins.github.io/"
        },
        {
            label: "Repository",
            url: "https://github.com/ivasmigins/ivasmigins.github.io"
        }
        ],
        stats: [{
            label: "Difficulty",
            percentage: 30
        },
        {
            label: "Completion",
            percentage: 100
        }
        ]
    }
];