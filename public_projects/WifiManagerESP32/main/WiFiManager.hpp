#ifndef WiFiManagerHpp
#define WiFiManagerHpp

#include <iostream>
#include <string>
#include <cstring>

extern "C" {
    #include "freertos/FreeRTOS.h"
    #include "freertos/task.h"
    #include "freertos/event_groups.h"
    #include "esp_wifi.h"
    #include "esp_event.h"
    #include "esp_log.h"
    #include "nvs_flash.h"
    #include "esp_netif.h"
    #include "esp_http_client.h"
    #include "sdkconfig.h"
}

// How many times it can retry connecting to WiFi
#define RECONNECTION_ATTEMPTS 10
// Event group
#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT BIT1

class WiFiManager { // Singleton class that handles connection to WiFi and GET/POST requests
    public:
        static WiFiManager& getInstance();
        bool connect(); // Yields until connection is stablished or not
        // I designed it in mind to be used after creating the class, like checking if (wifiInstance:connect()) then ...

        esp_err_t sendDataToServer(const char* url, const char* data); // POST request
        esp_err_t getDataFromServer(const char* url, std::string& response); // GET request (data stored on the response)

        // Allows to change the buffer for the GET request. Use with caution, make sure requests aren't overlapping.
        void setBufferSize(size_t size) { _bufferSize = size; }
        void setMaxResponseSize(size_t size) { _maxResponseSize = size; }

    private:
        WiFiManager();

        // Make it clear this is a singleton, so it shouldn't be copied or moved.
        WiFiManager(const WiFiManager&) = delete;
        WiFiManager& operator=(const WiFiManager&) = delete;
        WiFiManager(WiFiManager&&) = delete;
        WiFiManager& operator=(WiFiManager&&) = delete;

        // Callback for events related to the WiFi connection.
        static void eventsCallback(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data);
        bool waitForConnection(); // Wait for the _wifiEventGroup bits to be set.

        // I am enforcing C++17 (in the cmake) to enable the use of inline, otherwise I would have had to define these in the .cpp file
        // which is a bit unorganized.
        inline static const char *_debugTag = "WiFiManager";
        inline static EventGroupHandle_t _wifiEventGroup = nullptr; // Must be created at runtime since it is a RTOS object
        inline static int _retryCount = 0;

        size_t _bufferSize = 256; // Bytes
        size_t _maxResponseSize = 8192; // 8 KB
};

#endif