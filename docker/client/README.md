# Building
cd docker/client
sudo docker build -t client .

## Run manual client
sudo docker run -itd --name client --network iotnet client

# Other
sudo docker stop $(sudo docker ps -q) # Stop all containers
sudo docker rm -f $(sudo docker ps -aq) # Remove all unused docker container labels