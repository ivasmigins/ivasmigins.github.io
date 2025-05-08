import logging
import paho.mqtt.client as mqtt
import json
import mariadb
import sensors
import threading
import os
from dotenv import load_dotenv

load_dotenv()

# The Things Network MQTT broker settings
_mqtt_host = os.getenv('MQTT_HOST')
_mqtt_port = int(os.getenv('MQTT_PORT'))
_mqtt_username = os.getenv('MQTT_USERNAME')
_mqtt_password = os.getenv('MQTT_PASSWORD')

# Database connection settings
_db_host = os.getenv('DB_HOST')
_db_port = int(os.getenv('DB_PORT'))
_db_user = os.getenv('DB_USER')
_db_password = os.getenv('DB_PASSWORD')
_db_name = os.getenv('DB_NAME')

# Device MQTT broker settings
_mqtt2_host = os.getenv('MQTT2_HOST')
_mqtt2_port = int(os.getenv('MQTT2_PORT'))
_mqtt2_username = os.getenv('MQTT2_USERNAME')
_mqtt2_password = os.getenv('MQTT2_PASSWORD')

# Set the logging level to DEBUG to see all messages (from https://stackoverflow.com/q/50714316)
logger = logging.getLogger('m_logger')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Create the MQTT client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "main")
# Create the 2nd MQTT client
mqtt2c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "arduino")
# Connect to the database
connection = mariadb.connect(user=_db_user,password=_db_password,host=_db_host,port=_db_port,database=_db_name)
cursor = connection.cursor()
# Connect to the broker
mqttc.username_pw_set(_mqtt_username,_mqtt_password)
mqttc.enable_logger()
mqttc.connect(_mqtt_host, _mqtt_port, 60)
# Connect to the 2nd broker
mqtt2c.username_pw_set(_mqtt2_username,_mqtt2_password)
mqtt2c.enable_logger()
mqtt2c.connect(_mqtt2_host, _mqtt2_port, 60)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    logger.debug(f'Connected with result code {reason_code} to {client.username}')
    if client.username == _mqtt_username:
        client.subscribe('v3/project-software-engineering@ttn/devices/+/up', qos = 1)
    else:
        client.subscribe('v3/group14-secondyear@ttn/devices/mkr-wan-1310/up', qos = 1)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    decoded = msg.payload.decode('utf-8')
    data = json.loads(decoded)
    logger.debug(f'Received {data}')

    # Extract the data from the message
    metadata = data['uplink_message']['rx_metadata']
    device = data['end_device_ids']['device_id']
    info = data['uplink_message']['decoded_payload']

    if device.startswith('mkr-'):
        sensors.mkr_sensor(info, metadata, device, cursor, connection)
    elif device.startswith('lht-'):
        sensors.lht_sensor(info, metadata, device, cursor, connection)

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        logger.debug(f"[CLIENT]: {client.username} - Broker rejected you subscription: {reason_code_list[0]}")
    else:
        logger.debug(f"[CLIENT]: {client.username} - Broker granted you subscription: {reason_code_list[0]}")

# Set the callbacks
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_subscribe = on_subscribe
mqtt2c.on_connect = on_connect
mqtt2c.on_message = on_message
mqtt2c.on_subscribe = on_subscribe

# Start listening
thread = threading.Thread(target=mqttc.loop_forever, args=[])
thread.start()
thread2 = threading.Thread(target=mqtt2c.loop_forever, args=[])
thread2.start()