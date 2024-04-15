# Building
cd docker/cassandra
sudo docker build -t cassandra .

## Run manual cassandra
sudo docker run -itd --name cassandra --network iotnet -p 9042:9042 -p 7000:7000 -p 7001:7001 -p 7199:7199 cassandra

## Make sure iotnet is created as docker network (driver=bridge)

1. Run the cassandra database on iotnet using `docker/cassandra/docker-compose up`.

2. After cassandra has been initialized, all other docker containers can be started. It is important that cassandra is up and running or we will get connection error!

3. Then start zookeeper, brokers, prometheus and spark-processing using `docker/docker-compose up` which will also be launched in iotnet.

4. Now producers can start to generate streaming data for the brokers, start producers (iot stations) using `docker/producer/docker-compose up`.

5. Query the database using docker exec -it cassandra cqlsh:
- USE iot_stations;
- SELECT * FROM spark_stream LIMIT 10;
- SELECT COUNT(*) FROM spark_stream;
- SELECT COUNT(*) FROM spark_stream WHERE station_id = 'station_...';

# Other
sudo docker-compose up -d # Run X containers as specified in docker-compose.yml
sudo docker stop $(sudo docker ps -q) # Stop all containers
sudo docker rm -f $(sudo docker ps -aq) # Remove all unused docker container labels