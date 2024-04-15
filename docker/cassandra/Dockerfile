# Use the official Cassandra 3.11 image
FROM cassandra:3.11

# Set environment variables to tune Cassandra
# For example, to adjust the heap size, you might use:
ENV MAX_HEAP_SIZE="512M"
ENV HEAP_NEWSIZE="256M"

# Copy custom configurations if you have them
# Note: Ensure your cassandra.yaml file is properly configured before copying
# COPY cassandra.yaml /etc/cassandra/cassandra.yaml

# Expose the ports Cassandra uses
# 9042: CQL port for client connections
# 7000: Cassandra inter-node cluster communication (not encrypted)
# 7001: Cassandra inter-node cluster communication (SSL encrypted)
# 7199: JMX port (used for operations and monitoring)
EXPOSE 9042 7000 7001 7199

# The ENTRYPOINT and CMD from the base image are used to start Cassandra,
# so we don't need to specify them unless we have custom startup scripts.
