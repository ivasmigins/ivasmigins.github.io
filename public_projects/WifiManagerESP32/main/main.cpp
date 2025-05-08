#include "WiFiManager.hpp"

static const char *TAG = "main";

extern "C" void app_main() {
    WiFiManager& wifi = WiFiManager::getInstance();
    if (wifi.connect()) {
        ESP_LOGI(TAG, "Calling POST");
        esp_err_t postResult = wifi.sendDataToServer("http://httpbin.org/post", "{\"message\":\"Test\"}");
        ESP_LOGI(TAG, "Calling GET");
        std::string getResponse;
        esp_err_t getResult = wifi.getDataFromServer("http://httpbin.org/get", getResponse);
        if (getResult == ESP_OK) {
            ESP_LOGI(TAG, "Response:\n%s", getResponse.c_str());
        }
    }
}
