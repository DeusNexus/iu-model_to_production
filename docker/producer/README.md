## Building 
cd docker/producer
sudo docker build -t producer .

## Run manual producer
sudo docker run -itd --network="iotnet" producer
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic iot-sensor-stream --from-beginning

# Other
sudo docker-compose up -d # Run X containers as specified in docker-compose.yml
sudo docker stop $(sudo docker ps -q) # Stop all containers
sudo docker rm -f $(sudo docker ps -aq) # Remove all unused docker container labels
