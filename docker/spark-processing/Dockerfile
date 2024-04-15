# Stage 1: Build stage for downloading and unpacking Spark and its dependencies
FROM openjdk:11-jdk-slim as builder

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Download and unpack Spark
RUN wget --no-verbose "https://dlcdn.apache.org/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz" && \
    tar -xzf spark-3.5.1-bin-hadoop3.tgz && \
    rm spark-3.5.1-bin-hadoop3.tgz

# Use Spark's dependency downloader to pre-download the Kafka connector and Cassandra connector
RUN ./spark-3.5.1-bin-hadoop3/bin/spark-shell --packages "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.0.0"

# Stage 2: Final stage to setup the Spark environment
FROM openjdk:11-jdk-slim

# Copy the Spark installation from the builder stage
COPY --from=builder /tmp/spark-3.5.1-bin-hadoop3 /usr/local/spark
# Copy the downloaded jars from the builder stage
COPY --from=builder /root/.ivy2 /root/.ivy2
# Copy the downloaded jars from the builder stage to Spark's jars directory
COPY --from=builder /root/.ivy2/jars/*.jar /usr/local/spark/jars/

# Set environment variables
ENV SPARK_HOME=/usr/local/spark
ENV PATH=$PATH:$SPARK_HOME/bin:${SPARK_HOME}/sbin

# Install procps, Python, pip, and wget
RUN apt-get update && \
    apt-get install -y procps python3 python3-pip wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/local/spark/script
# Copy the outlier script into the container
COPY outlier_detection.py /usr/local/spark/script/outlier_detection.py
COPY log4j2.properties /usr/local/spark/conf/log4j2.properties

# Start the outlier script
WORKDIR /usr/local/spark
# CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1", "./script/outlier_detection.py"]
CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.0.0", "./script/outlier_detection.py"]

