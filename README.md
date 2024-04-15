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
A Python-based anomaly detection model will be developed, utilizing basic statistical methods to calculate anomaly scores. The model will focus on features identified as crucial by shop floor employees, such as temperature, humidity, and sound volume. While simplicity is key, the model will be robust enough to demonstrate effective anomaly detection in a streamed data environment.

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

## Running the containers
...

**Docker Deployment with docker-compose (~28mb GIF):**
![Docker Deployment with docker-compose (~28mb)](/images/docker_compose.gif)



## Sensor Data Overview
...

**IoT Sensor Producers (~23mb GIF):**
![IoT Sensor Producers (~23mb)](/images/station_sensor_generation.gif)

...

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
1. Download the Git repo using `git clone https://github.com/DeusNexus/iu-data-engineer-stream-processing`
2. Open folder using `cd iu-data-engineer-stream-processing`
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
