# Use the official Cassandra 3.11 image
FROM cassandra:3.11

# Set environment variables to tune Cassandra
# For example, to adjust the heap size, you might use:
ENV MAX_HEAP_SIZE="4G"
ENV HEAP_NEWSIZE="2G"

#########
# Create the Prometheus directory and copy the JMX Exporter and configuration file
RUN mkdir -p /opt/cassandra/prometheus

# Copy necessary files from the build context
COPY jmx_prometheus_javaagent-0.20.0.jar /opt/cassandra/prometheus/jmx_prometheus_javaagent-0.20.0.jar
COPY cassandra-1_0_0.yml /opt/cassandra/prometheus/cassandra-1_0_0.yml

# Set environment variables for Cassandra
ENV CASSANDRA_HOME=/opt/cassandra
ENV PATH="${CASSANDRA_HOME}/bin:${PATH}:${CASSANDRA_HOME}/sbin"
#ENV CASSANDRA_OPTS="-javaagent:/opt/cassandra/prometheus/jmx_prometheus_javaagent-0.20.0.jar=7200:/opt/cassandra/prometheus/cassandra-1_0_0.yml"

# Set JVM options to enable JMX Exporter
ENV JVM_OPTS="-Xmx2G -Xms2G"
ENV JVM_OPTS="$JVM_OPTS -javaagent:/opt/cassandra/prometheus/jmx_prometheus_javaagent-0.20.0.jar=7200:/opt/cassandra/prometheus/cassandra-1_0_0.yml"
###############

# Copy custom configurations if you have them
# Note: Ensure your cassandra.yaml file is properly configured before copying
# COPY cassandra.yaml /etc/cassandra/cassandra.yaml

# Expose the ports Cassandra uses
# 9042: CQL port for client connections
# 7000: Cassandra inter-node cluster communication (not encrypted)
# 7001: Cassandra inter-node cluster communication (SSL encrypted)
# 7199: JMX port (used for operations and monitoring)
EXPOSE 9042 7200
#7000 7001

# The ENTRYPOINT and CMD from the base image are used to start Cassandra,
# so we don't need to specify them unless we have custom startup scripts.
