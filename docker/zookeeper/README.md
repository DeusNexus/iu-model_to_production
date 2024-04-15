## Building 
cd docker/zookeeper
sudo docker build -t zookeeper .

## Run manual zookeeper
sudo docker run -itd --name zookeeper --network iotnet -p 2181:2181 -p 5555:5555 zookeeper

# Other
sudo docker stop $(sudo docker ps -q) # Stop all containers
sudo docker rm -f $(sudo docker ps -aq) # Remove all unused docker container labels