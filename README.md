# IU INTERNATIONAL UNIVERSITY OF APPLIED SCIENCES

### Project: From Model to Production (DLBDSMTP01)
### Task 1: Anomaly detection in an IoT setting (spotlight: Stream processing)
## Problem Statement
In modern manufacturing environments, especially those involving high-precision components such as wind turbines, the integrity and functionality of the production process are paramount. Unexpected malfunctions or deviations in machine behavior can lead to significant financial losses and safety risks. Currently, the factory utilizes a network of sensors to monitor various aspects of the production cycle. However, there is a critical gap in the system: the ability to automatically detect and respond to anomalies in real-time. The challenge lies in implementing a robust anomaly detection system that can process continuous sensor data and alert the factory management about potential issues before they escalate into more significant problems.

# Approach
1.1 Task 1: Anomaly Detection in an IoT Setting (Spotlight: Stream Processing)
Conceptual Architecture Design:
The system architecture is designed to handle high-throughput, real-time data streams using Apache Kafka for data ingestion. The data is then processed in real-time through Spark Streaming, which allows for efficient anomaly detection by applying the machine learning model to incoming sensor data streams. Processed data, including anomaly scores, are stored in Apache Cassandra, providing robust and scalable storage solutions for fast reads and writes. A visual representation of this architecture will be developed to illustrate the data flow and component interaction, which aids in the clear understanding and further development of the system.

## Choosing a Data Source:
Given the need for realistic data simulation:

Sensor data is generated using sample distributions with specified mean and standard deviation values.
To simulate natural fluctuations observed in real-world scenarios, the data generation includes a random walk based on the past n points, ensuring some variability in the sensor outputs.
A recalibration rate is implemented to ensure that long-term data readings remain aligned with the initial distribution parameters.
This approach allows for a controlled yet realistic testing environment for the anomaly detection model.
Building the Anomaly Detection Model:
A Python-based anomaly detection model will be developed, utilizing IsolationForest(n_estimators=1000, contamination=0.00125, random_state=42) and determine if the new datapoints is an outlier or not. The model will focus on features identified as crucial by shop floor employees, such as temperature, humidity, and sound volume. While simplicity is key, the model will be robust enough to demonstrate effective anomaly detection in a streamed data environment.

## API Integration and Model Packaging:
The anomaly detection system will be accessible via a RESTful API, which will receive sensor data from Kafka and return anomaly detection results. The integration with Spark Streaming ensures that the data processing is seamless and efficient. The use of Flask or mlflow for developing the API will facilitate easy integration and interaction with the Kafka and Cassandra components.

## Non-Cloud System Implementation:
The system is initially implemented on a local setup to avoid the complexities of cloud deployment. However, the design is inherently scalable and can be migrated to a cloud environment to enhance its capabilities, based on future needs or for academic demonstration purposes.

## Preparation for Final Presentation:
The presentation will cover:

- Technical challenges encountered while integrating streaming data with the predictive model.
- Design considerations for handling high-throughput real-time data.
- Adjustments made to simulate realistic sensor data and their impact on model performance.
- Monitoring strategies for ensuring the system’s reliability and performance in a real-world factory setting.
- Comprehensive system design showcasing the integration of Kafka, Spark Streaming, and Cassandra.
- A link to the GitHub repository will be provided, allowing the audience to access the complete codebase, which includes detailed documentation on the system setup, configuration, and operation.

This refined section will help to clearly communicate the technical depth of your project and the innovative approaches you have employed in developing the anomaly detection system.


# Development Planning - UML Schemas
## UML Diagram
Docker Architecture Diagram
![Design of ](/images/uml.jpg)


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
- POST /api/predict - Using for example { "humidity": 5.20311500477099, "noise_level": 17.48891168612748, "temperature": 22.86046518733127 }


**Docker Deployment with docker-compose (~28mb GIF):**
<!-- ![Docker Deployment with docker-compose (~28mb)](/images/docker_compose.gif) -->

## Sensor Data Overview
...

## Outlier Detection Model
..

## MLFlow (http://127.0.0.1:5000/#/experiments/)
..

## Apache Kafka
...

# Apache Spark Streaming
...

## Apache Cassandra
...

# Docker Deploy Kafka without docker-compose (individually)
...

## Dashboards Metrics
...
## Evaluation
..

## Reflection
..

# How to get started
## Installation instructions
1. Download the Git repo using `git clone https://github.com/DeusNexus/iu-model_to_production`
2. Open folder using `cd iu-model_to_production`
3. Install docker and docker-compose to your the local filesystem.
4. Follow the steps from begin of README.md at the top ('Running the containers')

# Reflection
- What I learned ...
- What challenges occured ...
- What recommendations are suggested ...
- What could be improved ...

# Conclusion
Did we achieve the goal etc and how?

# Disclaimer
The developed application is licensed under the GNU General Public License.
