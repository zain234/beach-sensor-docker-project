import time
import json
import requests
import datetime
from kafka import KafkaProducer, KafkaClient
from websocket import create_connection


def get_sensor_data_stream():
    try:
        url = 'http://localhost:5000/sensordata'
        r = requests.get(url)
        return r.text
    except:
        return "Error in Connection"

# kafka producer
producer = KafkaProducer(bootstrap_servers=['kafka:9093'])

# raw sensor data is sent to kafka producer topic 'SensorData'
while True:
    msg =  get_sensor_data_stream()
    print(msg)
    producer.send("SensorData", msg.encode('utf-8'))
    time.sleep(1)
