# Define the Kafka version as a build-time argument
ARG KAFKA_VERSION=3.7.0

# Stage 1: Build stage
FROM ubuntu:22.04 as builder

# Set environment variables to avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Re-declare ARG after FROM to use it in the build stage
ARG KAFKA_VERSION

# Install Java JDK and necessary tools for the build
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

# Re-declare ARG after FROM to use it in the build stage
ARG KAFKA_VERSION

# Copy only the necessary Kafka client binaries, libs, and config from the build stage
COPY --from=builder /tmp/kafka_2.13-${KAFKA_VERSION}/bin /usr/local/kafka/bin
COPY --from=builder /tmp/kafka_2.13-${KAFKA_VERSION}/libs /usr/local/kafka/libs
COPY --from=builder /tmp/kafka_2.13-${KAFKA_VERSION}/config /usr/local/kafka/config


# Set environment variables for Kafka
ENV KAFKA_HOME=/usr/local/kafka
ENV PATH="${KAFKA_HOME}/bin:${PATH}"

# Set the working directory
WORKDIR /usr/local/kafka/bin

# Default command to create a topic as an example
CMD ["kafka-topics.sh", "--create", "--topic", "iot-sensor-stream", "--bootstrap-server", "broker:9092", "--replication-factor", "1", "--partitions", "1"]
