# Use the official Prometheus image as the base
FROM prom/prometheus:v2.50.1

# Set the working directory in the container
WORKDIR /etc/prometheus/

# Copy the Prometheus configuration file into the container
COPY prometheus.yml /etc/prometheus/prometheus.yml

# Expose the port Prometheus listens on
EXPOSE 9090

# Specify the command to run Prometheus with the config file
CMD ["--config.file=/etc/prometheus/prometheus.yml"]