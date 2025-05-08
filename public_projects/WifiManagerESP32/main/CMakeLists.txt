idf_component_register(
    SRCS "main.cpp" "wifi_manager.cpp"
    INCLUDE_DIRS "."
    PRIV_REQUIRES spi_flash esp_wifi esp_event nvs_flash esp_netif esp_http_client
)