# Build stage for compiling and installing dependencies
FROM python:3.8-slim as builder

# Set the working directory in the builder stage
WORKDIR /build

# Upgrade pip and install dependencies in a virtual environment
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install kafka-python uuid numpy

# Runtime stage which uses the slim base image
FROM python:3.8-slim

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set environment variables to ensure the virtual environment is used
ENV PATH="/opt/venv/bin:$PATH"

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the Python scripts into the container
COPY producer.py .
COPY readings.py .

# Command to run the producer script
CMD ["python", "./producer.py"]
