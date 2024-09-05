# IU INTERNATIONAL UNIVERSITY OF APPLIED SCIENCES

### Project: From Model to Production (DLBDSMTP01)
### Task 1: Anomaly detection in an IoT setting (spotlight: Stream processing)
## Problem Statement
In modern manufacturing environments, especially those involving high-precision components such as wind turbines, the integrity and functionality of the production process are paramount. Unexpected malfunctions or deviations in machine behavior can lead to significant financial losses and safety risks. Currently, the factory utilizes a network of sensors to monitor various aspects of the production cycle. However, there is a critical gap in the system: the ability to automatically detect and respond to anomalies in real-time. The challenge lies in implementing a robust anomaly detection system that can process continuous sensor data and alert the factory management about potential issues before they escalate into more significant problems.

## Approach

Our solution leverages a combination of cutting-edge technologies:

- Apache Kafka for high-throughput, real-time data ingestion

- Apache Spark Streaming for efficient, scalable data processing

- Apache Cassandra for robust, scalable data storage

- MLflow for model versioning and tracking

- Flask for RESTful API implementation


This stack ensures seamless integration, high volume processing, low latency, and high redundancy, making it suitable for enterprise-level production environments.


## Architecture

![Architecture Diagram](/images/uml.jpg)


The system architecture includes:

- IoT sensors (simulated) publishing data to Kafka topics

- Kafka brokers for message queuing

- Spark Streaming for real-time data processing and anomaly detection

- Cassandra for storing processed data

- MLflow for model management

- Flask API for system interaction and model serving

- Prometheus and Grafana for system monitoring


## System Components

### Cassandra
- Primary database for the architecture
- Must be running before all other services start
- Stores rows processed by Spark Streaming, including sensor readings, outlier detection results, and MLflow IDs
- Accessible via CSQL on port 9042
- Integrates with jmx_prometheus_javaagent for Prometheus scraping and Grafana visualization

### Kafka Broker
- Part of the Apache Kafka ecosystem
- Maintains topics and manages broker followers
- One leader broker (port 9092) and two follower brokers (ports 9093 & 9094)
- Facilitates horizontal scaling and redundancy
- Integrates with jmx_prometheus_javaagent for monitoring

### Zookeeper
- Orchestrator for the Apache Kafka ecosystem
- Manages overall health of Kafka
- Provides broker IDs to Spark Streaming for topic access
- Client connections available on port 2181
- Integrates with jmx_prometheus_javaagent for monitoring

### Kafka Client
- Temporary container that creates a Kafka topic
- Runs after all brokers are initialized
- Terminates after topic creation

### Producer (IoT Station)
- Simulates factory IoT stations or sensors
- Generates and publishes messages to Kafka brokers
- Produces approximately one message per second per producer
- Uses probability distribution with minor random walk for realistic data generation
- Default setup: 25 replicas (approx. 25 messages/second)

### Prometheus
- Scrapes JMX metrics from brokers, Zookeeper, Spark Streaming, and Cassandra
- Facilitates collection of logs for Grafana visualization
- Accessible at http://localhost:9090/targets for service status monitoring

### Spark Processing
- Core component of the architecture
- Fetches messages from Kafka topics in real-time
- Uses Pandas UDF and applies MLflow model for outlier detection
- Writes results to Apache Cassandra
- Utilizes JMX (port 4040) for Prometheus metric scraping

### Grafana Dashboard
- Provides comprehensive monitoring of architecture components
- Accessible at http://localhost:3001/ after container start
- Visualizes metrics from Prometheus for all services

### Flask API
- Unifies access to all system components
- Provides RESTful endpoints for interacting with the system
- Handles model loading, prediction, and drift detection
- Facilitates easy integration with external systems and user interfaces

This architecture ensures a robust, scalable, and monitored system for real-time anomaly detection in an IoT setting. Each component plays a crucial role in data ingestion, processing, storage, and analysis, working together to provide timely insights and alerts.


## Installation and Setup


### Prerequisites

- Docker and Docker Compose

- Python 3.7+

## Building Docker Images

### Cassandra
    - 1. `cd docker/cassandra`
    - 2. `docker build -t deusnexus/cassandra .`
    - 3. `docker push deusnexus/cassandra` (not necessary, only for author)

### Broker
    - 1. `cd docker/broker`
    - 2. `docker build -t deusnexus/broker .`
    - 3. `docker push deusnexus/broker` (not necessary, only for author)

### Zookeeper
    - 1. `cd docker/zookeeper`
    - 2. `docker build -t deusnexus/zookeeper .`
    - 3. `docker push deusnexus/zookeeper` (not necessary, only for author)

### Client
    - 1. `cd docker/client`
    - 2. `docker build -t deusnexus/client .`
    - 3. `docker push deusnexus/client` (not necessary, only for author)

### Producer (iot-station)
    - 1. `cd docker/producer`
    - 2. `docker build -t deusnexus/producer .`
    - 3. `docker push deusnexus/producer` (not necessary, only for author)

### Prometheus
    - 1. `cd docker/prometheus`
    - 2. `docker build -t deusnexus/prometheus .`
    - 3. `docker push deusnexus/prometheus` (not necessary, only for author)

### Spark Processing - Will get the latest mlruns model from docker/api/mlruns
    - 1. `cd docker`
    - 2. `docker build -t deusnexus/spark-processing -f ./spark-processing/Dockerfile .`
    - 3. `cd docker/spark-processing`
    - 3. `docker push deusnexus/spark-processing` (not necessary, only for author)

# Install API modules in venv
    - 1. `cd docker/api`
    - 2. `python -m venv venv`
    - 3. `source venv/bin/activate`
    - 4. `pip install -r requirements.txt`

## Running the containers
This requires multiple terminals.

### Create a new docker network
    - `docker networks create iotnet`

### Terminal 1 - Apache Cassandra (always make sure this is running first!):
    - 1. `cd docker/cassandra`
    - 2. `docker compose up`

### Terminal 2 - Broker(s), Zookeeper, Client (temp), Prometheus, Spark-Processing
    - 1. `cd docker`
    - 2. `docker compose up`

### Terminal 3 - Producer(s), these emulate the sensor readings (change the replicas in docker-compose.yaml to your liking - default: 25)
    - 1. `cd docker/producer`
    - 2. `docker compose up`

### Terminal 4 - Grafana (Dashboard that can be opened and connects to scraped JMX from Prometheus - Collects from Broker(s), Zookeeper, Spark and Cassandra)
    - 1. `cd docker/grafana`
    - 2. `docker compose up`
    - 3. `Open http://localhost:3001/`

### Terminal 5 - API (Not containerized)
    - 1. `cd docker/api`
    - 2. `source venv/bin/activate` - Make sure virtual env is used with required installed modules.
    - 3. `python app.py`
    - 4. `Open http://localhost:5000/`

#### Note: Here you can access the following endpoints
- GET /api/latest_anomalies - Fetch the latest predictions (returns latest 10 where is_outlier = True)
- GET /api/check_drift_retrain - Will check for model drift and retrain model, will automatically switch to new model for /api/predict including model_id, Spark-Processing needs to build new image and will automatically use the new one generated by the api.
- GET /api/outliers_count?time_range=1h - You can use m,h,d for example 5m, 4h, 30d.
- POST /api/predict - Example Request Message and Response

```json
Example Message: { "humidity": 5.20311500477099, "noise_level": 17.48891168612748, "temperature": 22.86046518733127 }
```

```json
Example Response: {
    "features": {
        "humidity": 5.20311500477099,
        "noise_level": 17.48891168612748,
        "temperature": 22.86046518733127
    },
    "is_anomaly": true,
    "model_version": "90e6bef02af84f3186e0e068e9fa4e4d"
}
```

## API Endpoints


The Flask API provides the following endpoints:


1. GET /api/latest_anomalies

   - Fetches the latest detected anomalies

   - Example response:

     ```json

     [

       {

         "station_id": "station_123",

         "record_time": "2023-05-20T14:30:00",

         "humidity": 70.5,

         "noise_level": 65.2,

         "temperature": 30.1,

         "is_outlier": true,

         "mlflow_id": "90e6bef02af84f3186e0e068e9fa4e4d"

       }

     ]

     ```


2. GET /api/check_drift_retrain

   - Checks for model drift and retrains if necessary

   - Example response:

     ```json

     {

       "msg": "Model drift detected. Retraining completed. New model ID: 91f7cef13bf95g4297f1f179f0gb5f5e"

     }

     ```


3. GET /api/outliers_count?time_range=1h

   - Returns the count of outliers in a specified time range

   - Example response:

     ```json

     {

       "time_range": "1h",

       "outliers_count": 15

     }

     ```


4. POST /api/predict

   - Makes a new prediction based on input data

   - Example request:

     ```json

     {

       "humidity": 65.2,

       "noise_level": 55.7,

       "temperature": 28.3

     }

     ```

   - Example response:

     ```json

     {

       "is_anomaly": true,

       "features": {

         "humidity": 65.2,

         "noise_level": 55.7,

         "temperature": 28.3

       },

       "model_version": "90e6bef02af84f3186e0e068e9fa4e4d"

     }

     ```


## Sensor Data Overview

The system simulates three types of sensors: humidity, noise level, and temperature. Data is generated using probability distributions with minor random walks, correcting towards the mean to maintain realistic patterns.


## Outlier Detection Model

The system uses an Isolation Forest model with 1000 estimators and a contamination factor of 0.00125. The model is periodically checked for drift and retrained as necessary to maintain accuracy.


## MLflow Integration

MLflow is primarily used for model versioning and artifact tracking. It maintains a record of model versions, training artifacts, and facilitates easy switching between model versions for predictions.


## Monitoring and Metrics

The system uses Prometheus for metrics collection and Grafana for visualization. Key metrics monitored include:

- Kafka: Messages per second, consumer requests, latency, disk usage

- Zookeeper: Disconnects per second, request latency

- Spark: Memory usage, executor metrics, GC time

- Cassandra: Memtable metrics, connections, reads/writes


## Evaluation

The system's success is evaluated based on its ability to:

1. Detect anomalies in real-time with high accuracy

2. Handle increasing data loads through scalable architecture

3. Maintain low latency in data processing and anomaly detection

4. Provide easy access to insights through the API

5. Facilitate model updates and version control


## Reflection

The project presented challenges, particularly in JMX integration. However, it provided valuable insights into creating a scalable production architecture with a focus on version tracking, monitoring, and easy deployment through containerization.


## Conclusion

The project successfully implemented a highly scalable anomaly detection system for IoT sensor data. It meets the initial goals of real-time processing, easy model updates, and comprehensive monitoring. Future directions could include further optimization of the model drift detection process and expansion to handle more diverse sensor types.


## License

This project is licensed under the GNU General Public License.