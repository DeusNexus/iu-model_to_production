import time
import random
import uuid
from kafka import KafkaProducer
from readings import Station

# Kafka configuration
kafka_broker = "broker:9092"  # Replace with your Kafka broker address
topic_name = "iot-sensor-stream"
station_id = f'station_{uuid.uuid4().hex[:9]}'

# Initialize Kafka producer
producer = KafkaProducer(bootstrap_servers=[kafka_broker])

# Create a new sensor station
station = Station(station_id=station_id)

def generate_sensor_data():
    while True:
        # Simulate sensor data
        data = station.generate_and_collect_data()
        print(f"Sending data: {data}")
        
        # Send data to Kafka
        producer.send(topic_name, str(data).encode())
        producer.flush()

        # Wait for a second before next data point
        time.sleep(1)

if __name__ == "__main__":
    generate_sensor_data()
