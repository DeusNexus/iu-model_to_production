# Define the Kafka version as a build-time argument
ARG KAFKA_VERSION=3.7.0

# Stage 1: Build stage
FROM ubuntu:22.04 as builder

# Set environment variables to avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Re-declare ARG after FROM to use it in the build stage
ARG KAFKA_VERSION

# Install Java Development Kit (JDK) and other necessary tools
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Define Kafka base URL for downloading
ENV KAFKA_BASE_URL=https://downloads.apache.org/kafka

# Download and extract Kafka
RUN wget ${KAFKA_BASE_URL}/${KAFKA_VERSION}/kafka_2.13-${KAFKA_VERSION}.tgz \
    && tar -xzf kafka_2.13-${KAFKA_VERSION}.tgz -C /tmp \
    && rm kafka_2.13-${KAFKA_VERSION}.tgz

# Stage 2: Final stage
FROM openjdk:11-jre-slim

# Re-declare ARG before using it in the COPY command
ARG KAFKA_VERSION

# Copy Kafka from the build stage
COPY --from=builder /tmp/kafka_2.13-${KAFKA_VERSION} /usr/local/kafka

# Create the Prometheus directory and copy the JMX Exporter and configuration file
RUN mkdir -p /usr/local/kafka/prometheus

# Copy necessary files from the build context
COPY jmx_prometheus_javaagent-0.20.0.jar /usr/local/kafka/prometheus/jmx_prometheus_javaagent-0.20.0.jar
COPY kafka-2_0_0.yml /usr/local/kafka/prometheus/kafka-2_0_0.yml
COPY server.properties /usr/local/kafka/config/server.properties

# Set environment variables for Kafka
ENV KAFKA_HOME=/usr/local/kafka
ENV PATH="${KAFKA_HOME}/bin:${PATH}:${KAFKA_HOME}/sbin"
ENV KAFKA_OPTS="-javaagent:/usr/local/kafka/prometheus/jmx_prometheus_javaagent-0.20.0.jar=7072:/usr/local/kafka/prometheus/kafka-2_0_0.yml"

# Expose ports for Kafka broker and JMX
EXPOSE 9092 7072

# Command to start Kafka
CMD ["kafka-server-start.sh", "/usr/local/kafka/config/server.properties"]
