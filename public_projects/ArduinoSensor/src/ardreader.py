import serial
import time
from db import TemperatureData, session

# Connect to arduino
ser = serial.Serial('COM8', 9600) # 9600 baudrate

store_interval = 10 # How often I store repeated data

def storeTemperature(data):
    temp = TemperatureData(value=float(data))
    print(f"Storing temperature: {temp.value} °C")
    session.add(temp)
    session.commit()

def read():
    lastTemp = 999999
    lastStoreTime = 0
    while True:
        if ser.in_waiting > 0:
            raw = ser.readline()
            # Sometimes the data is not properly decoded as something goes wrong during the communication
            # Often when the program starts running after the Arduino has been running for a while
            try:
                data = raw.decode('utf-8').strip() # Decode the data using utf-8 and remove any leading/trailing whitespaces
                temperature = float(data.split(":")[1].strip().replace("°C", "")) # Extract the temperature value from the data
                current_time = time.time()
                # Cut some repeated data as it is not necessary to store it
                if temperature != lastTemp or (current_time - lastStoreTime) >= store_interval:
                    storeTemperature(temperature)
                    lastTemp = temperature
                    lastStoreTime = current_time
            except (UnicodeDecodeError) as e:
                print(f"Error decoding: {e}")
        time.sleep(0.5) # Needed, picked 0.5 because it filters some entries but still allows steady data flow

read()
