#include "WiFiManager.hpp"

WiFiManager& WiFiManager::getInstance() {
    static WiFiManager instance;
    return instance;
}

WiFiManager::WiFiManager() {
    ESP_LOGI(_debugTag, "[Init] Initializing wifi events and configuration.");
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_LOGW(_debugTag, "[Init] Cleaning NVS.");
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    _wifiEventGroup = xEventGroupCreate();
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &WiFiManager::eventsCallback, this, nullptr));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &WiFiManager::eventsCallback, this, nullptr));

    ESP_LOGI(_debugTag, "[Init] WiFiManager initialized");
}

bool WiFiManager::connect() {
    ESP_LOGI(_debugTag, "[Connection] Setting WiFi credentials");

    wifi_config_t wifi_config = {};
    strncpy((char*)wifi_config.sta.ssid, CONFIG_WIFI_SSID, sizeof(wifi_config.sta.ssid));
    strncpy((char*)wifi_config.sta.password, CONFIG_WIFI_PASS, sizeof(wifi_config.sta.password));

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_LOGI(_debugTag, "[Connection] Starting WiFi");
    ESP_ERROR_CHECK(esp_wifi_start());

    // This would usually go inside the eventsCallback, however, I had problems, probably a race condition between the connection
    // of the eventsCallback and the event.
    ESP_ERROR_CHECK(esp_wifi_connect());

    ESP_LOGI(_debugTag, "[Connection] Waiting for connection.");
    if (waitForConnection()) {
        ESP_LOGI(_debugTag, "[Connection] Connected. Returning.");
        return true;
    } else {
        ESP_LOGE(_debugTag, "[Connection] Failed.");
        return false;
    }
}

void WiFiManager::eventsCallback(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data) {
    // Automatically reconnect if something happens
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        if (_retryCount < RECONNECTION_ATTEMPTS) {
            _retryCount++;
            ESP_LOGW(_debugTag, "[Connection] Retrying. (%d/%d)", _retryCount, RECONNECTION_ATTEMPTS);
            esp_wifi_connect();
        } else {
            ESP_LOGE(_debugTag, "[Connection] Connection failed.");
            xEventGroupSetBits(_wifiEventGroup, WIFI_FAIL_BIT);
        }
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        _retryCount = 0;
        ESP_LOGI(_debugTag, "[Connection] Connected.");
        xEventGroupSetBits(_wifiEventGroup, WIFI_CONNECTED_BIT);
    }
}

bool WiFiManager::waitForConnection() {
    EventBits_t bits = xEventGroupWaitBits(
        _wifiEventGroup,
        WIFI_CONNECTED_BIT | WIFI_FAIL_BIT, // Bits to wait
        pdTRUE, // Clear bits when returning
        pdFALSE, // Wait for just 1 bit to be set
        pdMS_TO_TICKS(40000) // Timeout after 40 seconds
        // All reconnect attempts are probably done by now, it is for sure not connecting
        // During my testing, the timeout sometimes triggered before the reconnect attempts were finished
    );

    return (bits & WIFI_CONNECTED_BIT);
}

esp_err_t WiFiManager::sendDataToServer(const char* url, const char* data) {
    esp_http_client_config_t config = {};
    config.url = url;
    config.method = HTTP_METHOD_POST;
    config.timeout_ms = 5000;

    esp_http_client_handle_t client = esp_http_client_init(&config);
    if (!client) {
        ESP_LOGE(_debugTag, "[POST] Failed to initialize HTTP client.");
        return ESP_FAIL;
    }

    esp_http_client_set_header(client, "Content-Type", "application/json");
    esp_http_client_set_post_field(client, data, strlen(data));

    // Perform worked fine here unlike on getDataFromServer, so no need to extend it :D
    esp_err_t err = esp_http_client_perform(client);
    if (err == ESP_OK) ESP_LOGI(_debugTag, "[POST] CODE = %" PRId64 ", CONTENT = %" PRId64, (int64_t)esp_http_client_get_status_code(client), (int64_t)esp_http_client_get_content_length(client));
    else ESP_LOGE(_debugTag, "[POST] Request failed");

    esp_http_client_cleanup(client);
    return err;
}

esp_err_t WiFiManager::getDataFromServer(const char* url, std::string& response) {
    esp_http_client_config_t config = {};
    config.url = url;
    config.method = HTTP_METHOD_GET;
    config.timeout_ms = 5000;

    esp_http_client_handle_t client = esp_http_client_init(&config);
    if (!client) {
        ESP_LOGE(_debugTag, "[GET] Failed to initialize HTTP client");
        return ESP_FAIL;
    }

    // Open the TCP connection
    // For some reason I had problems using esp_http_client_perform(), so I basically did what it does manually
    // which includes opening, fetching headers, and reading. I added chunk reading after I had to do this.
    esp_err_t err = esp_http_client_open(client, 0);
    if (err != ESP_OK) {
        ESP_LOGE(_debugTag, "[GET] Failed to open HTTP connection");
        esp_http_client_cleanup(client);
        return err;
    }

    int content_length = esp_http_client_fetch_headers(client); // Gotta make sure headers are loaded before reading the body
    if (content_length < 0) {
        ESP_LOGE(_debugTag, "[GET] Failed to fetch headers");
        esp_http_client_cleanup(client);
        return ESP_FAIL;
    }

    const size_t bufferSize = _bufferSize;
    char* buffer = new char[bufferSize];
    int total_read = 0;

    while (true) { // Append the data in chunks into the string
        int read_len = esp_http_client_read(client, buffer, bufferSize - 1);
        if (read_len <= 0) break;

        buffer[read_len] = '\0';
        response.append(buffer, read_len);
        total_read += read_len;

        if (total_read > _maxResponseSize) {
            ESP_LOGW(_debugTag, "[GET] Response too large.");
            break;
        }
    }

    delete[] buffer;

    ESP_LOGI(_debugTag, "[GET] CODE = %d, BYTES (read) = %d", esp_http_client_get_status_code(client), total_read);

    esp_http_client_cleanup(client);
    return ESP_OK;
}