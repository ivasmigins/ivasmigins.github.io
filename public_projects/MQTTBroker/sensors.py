import logging
import math
from datetime import datetime, timezone, timedelta

logger = logging.getLogger('m_logger')

# Process the data for mkr- type sensors
def mkr_sensor(info, metadata, device, cursor, connection):
    humidity = info['humidity']
    light = ((int(info['light'])/255)* 100)
    pressure = info['pressure']
    temperature = info['temperature']


    # Convert the time to a readable format
    dt = datetime.fromisoformat(metadata[0]['time'].replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=1)))
    time = dt.strftime('%Y-%m-%d %H:%M:%S')
    timestamp = dt.timestamp()
    latitude = metadata[0]['location']['latitude']
    longitude = metadata[0]['location']['longitude']
    snr = metadata[0]['snr']
    signal_strength = metadata[0]['rssi']

    # Create a new node if it does not exist
    cursor.execute(f'SELECT * FROM nodes WHERE node_id = ?', (device,))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO nodes (node_id, latitude, longitude) VALUES (?, ?, ?)', (device, latitude, longitude))
        connection.commit()
        logger.debug(f'Node {device} created')
    
    # Insert the data into the database
    cursor.execute('''INSERT INTO data 
                   (node_id, temperature_inside, temperature_outside, humidity, light, pressure, time, timestamp, battery_voltage, battery_status, snr, signal_strength) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (device, temperature, None, humidity, light, pressure, time, timestamp, None, None, snr, signal_strength))
    connection.commit()
    logger.debug(f'Data Entered: \nDevice: {device}, humidity: {humidity}, light: {light}, pressure: {pressure}, temperature: {temperature}, time: {time}, timestamp: {timestamp}, longitude: {longitude}, latitude: {latitude}, snr: {snr}, signal_strength: {signal_strength}')

# Process the data for lht- type sensors
def lht_sensor(info, metadata, device, cursor, connection):
    humidity = info['Hum_SHT']
    temperature_inside = None
    temperature_outside = None
    light = None
    if info['Bat_status'] == 3:
        battery_status = 'Good'
    elif info['Bat_status'] == 2:
        battery_status = 'Ok'
    elif info['Bat_status'] == 1:
        battery_status = 'Low'
    else:
        battery_status = 'Ultra Low'
    battery_voltage = info['BatV']
    if device.startswith('lht-s'):
        temperature_inside = info['TempC_SHT']
        temperature_outside = info['TempC_DS']
    elif device.startswith('lht-t'):
        temperature_inside = info['TempC_SHT']
    else:
        temperature_outside = info['TempC_SHT']
        if info['ILL_lx'] <= 0:
            light = 0
        else:
            light = ((math.log(int(info['ILL_lx'])) * 0.9) * 10)

    # Convert the time to a readable format
    dt = datetime.fromisoformat(metadata[0]['time'].replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=1)))
    time = dt.strftime('%Y-%m-%d %H:%M:%S')
    timestamp = dt.timestamp()
    latitude = metadata[0]['location']['latitude']
    longitude = metadata[0]['location']['longitude']
    snr = metadata[0]['snr']
    signal_strength = metadata[0]['rssi']

    # Create a new node if it does not exist
    cursor.execute(f'SELECT * FROM nodes WHERE node_id = ?', (device,))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO nodes (node_id, latitude, longitude) VALUES (?, ?, ?)', (device, latitude, longitude))
        connection.commit()
        logger.debug(f'Node {device} created')
    
    # Insert the data into the database
    cursor.execute('''INSERT INTO data 
                   (node_id, temperature_inside, temperature_outside, humidity, light, pressure, time, timestamp, battery_voltage, battery_status, snr, signal_strength) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (device, temperature_inside, temperature_outside, humidity, light, None, time, timestamp, battery_voltage, battery_status, snr ,signal_strength))
    connection.commit()
    logger.debug(f'Data Entered: \nDevice: {device}, humidity: {humidity}, light: {light}, temperature_inside: {temperature_inside}, temperature_outside: {temperature_outside}, time: {time}, timestamp: {timestamp}, longitude: {longitude}, latitude: {latitude}, snr: {snr}, signal_strength: {signal_strength}, battery_voltage: {battery_voltage}, battery_status: {battery_status}')