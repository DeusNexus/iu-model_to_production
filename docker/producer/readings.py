import time
import numpy as np

class Sensor:
    def __init__(self, mean, std_dev, name, keep_readings=100, recalibration_rate=0.1):
        self.mean = mean
        self.std_dev = std_dev
        self.keep_readings = keep_readings
        self.name = name
        self.past_readings = []
        self.recalibration_rate = recalibration_rate  # Probability to recalibrate towards mean

    def generate_reading(self):
        n = len(self.past_readings)
        weights = np.linspace(1, 1.5, n) if n > 0 else np.array([1.0])
        average_past = np.average(self.past_readings[-self.keep_readings:], weights=weights) if n > 0 else self.mean

        new_reading = average_past + np.random.normal(0, self.std_dev)

        # With a certain probability, recalibrate towards the mean
        if np.random.random() < self.recalibration_rate:
            new_reading = self.mean + (new_reading - self.mean) * np.random.uniform(0.9, 1.1)

        self.past_readings.append(new_reading)
        self.past_readings = self.past_readings[-self.keep_readings:]

        return self.name,new_reading

class Station:
    def __init__(self,station_id='default_id'):
        self.station_id = station_id
        self.sensors = [
            Sensor(mean=25,std_dev=2,name='temperature',keep_readings=300,recalibration_rate=0.2),
            Sensor(mean=60,std_dev=3,name='humidity',keep_readings=300,recalibration_rate=0.2),
            Sensor(mean=1013,std_dev=2,name='pressure',keep_readings=300,recalibration_rate=0.2),
            Sensor(mean=200,std_dev=20,name='air_quality',keep_readings=300,recalibration_rate=0.2),
            Sensor(mean=30,std_dev=2,name='particulate_matter',keep_readings=300,recalibration_rate=0.2),
            Sensor(mean=50,std_dev=3,name='noise_level',keep_readings=300,recalibration_rate=0.2),
            Sensor(mean=500,std_dev=50,name='illuminance',keep_readings=300,recalibration_rate=0.2),
            Sensor(mean=5,std_dev=20,name='wind_speed',keep_readings=300,recalibration_rate=0.2),
            Sensor(mean=0,std_dev=3,name='rainfall',keep_readings=300,recalibration_rate=0.2),
        ]

    def generate_station_readings(self):
        timestamp = int(time.time())
        station_readings = {"timestamp": timestamp, "station_id": self.station_id}

        for sensor in self.sensors:
            sensor_name, reading = sensor.generate_reading()
            station_readings[sensor_name] = abs(reading)
        
        # Return the final updated list
        return [station_readings]

    def generate_and_collect_data(self):
        # Initialize the dictionary with station_id.
        station_sensor_data = {'station_id': self.station_id}
        
        # Generate sensor readings.
        station_readings = self.generate_station_readings()

        # Iterate through each reading and assign the value to the respective sensor key.
        for reading in station_readings:
            for sensor_name, value in reading.items():
                # Make sure we're only dealing with sensor data, not metadata like 'timestamp' or 'station_id'.
                if sensor_name not in ['timestamp', 'station_id']:
                    station_sensor_data[sensor_name] = value  # Assigning the scalar value directly.

        return station_sensor_data

