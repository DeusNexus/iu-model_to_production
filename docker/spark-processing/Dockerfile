# Stage 1: Build stage for downloading and unpacking Spark and its dependencies
FROM openjdk:11-jdk-slim AS builder

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Download and unpack Spark
RUN wget --no-verbose "https://dlcdn.apache.org/spark/spark-3.5.2/spark-3.5.2-bin-hadoop3.tgz" && \
    tar -xzf spark-3.5.2-bin-hadoop3.tgz && \
    rm spark-3.5.2-bin-hadoop3.tgz

# Use Spark's dependency downloader to pre-download the Kafka connector and Cassandra connector
RUN ./spark-3.5.2-bin-hadoop3/bin/spark-shell --packages "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2,com.datastax.spark:spark-cassandra-connector_2.12:3.0.0"

# Stage 2: Final stage to setup the Spark environment
FROM openjdk:11-jdk-slim

# Copy the Spark installation from the builder stage
COPY --from=builder /tmp/spark-3.5.2-bin-hadoop3 /usr/local/spark
# Copy the downloaded jars from the builder stage
COPY --from=builder /root/.ivy2 /root/.ivy2
# Copy the downloaded jars from the builder stage to Spark's jars directory
COPY --from=builder /root/.ivy2/jars/*.jar /usr/local/spark/jars/

# Set environment variables
ENV SPARK_HOME=/usr/local/spark
ENV PATH=$PATH:$SPARK_HOME/bin:${SPARK_HOME}/sbin

# Install procps, Python, pip, and wget
RUN apt-get update && \
    apt-get install -y procps python3.10 python3-venv python3-dev python3-pip wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install specific versions of Python packages
RUN pip install --upgrade pip && \
    pip install \
    mlflow==2.16.0 \
    cloudpickle==3.0.0 \
    psutil==5.9.5 \
    scipy==1.13.0 \
    joblib==1.4.2 \
    pandas==2.2.2 \
    numpy==1.26.2 \
    scikit-learn==1.4.2 \
    matplotlib==3.9.0

RUN mkdir -p /usr/local/spark/script

####################################
######## BUILD INSTRUCTIONS ########
####################################
# 1. cd iu-model_to_production_anomaly_iot/docker
# 2. docker build -t deusnexus/spark-processing -f ./spark-processing/Dockerfile .
#
# Copy the outlier script and other necessary files into the container
COPY spark-processing/outlier_detection.py /usr/local/spark/script/outlier_detection.py
COPY spark-processing/log4j2.properties /usr/local/spark/conf/log4j2.properties
COPY spark-processing/metrics.properties /usr/local/spark/conf/metrics.properties
COPY spark-processing/mlruns /mlruns

# Expose Prometheus metrics port
EXPOSE 4040

# Start the outlier script
WORKDIR /usr/local/spark
# CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2", "./script/outlier_detection.py"]
CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2,com.datastax.spark:spark-cassandra-connector_2.12:3.0.0", "./script/outlier_detection.py"]

