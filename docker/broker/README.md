# Building
cd docker/broker
sudo docker build -t broker .

## Run manual broker
sudo docker run -itd --name broker --network iotnet -p 9092:9092 -p 7072:7072 broker

# Other
sudo docker-compose up -d # Run X containers as specified in docker-compose.yml
sudo docker stop $(sudo docker ps -q) # Stop all containers
sudo docker rm -f $(sudo docker ps -aq) # Remove all unused docker container labels