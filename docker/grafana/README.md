# Building
No need to build since we're pulling external image and include the files inside the folder as volumes.

## Run manual grafana
sudo docker run -itd --name grafana --network host grafana

# Other
sudo docker-compose up -d # Run X containers as specified in docker-compose.yml
sudo docker stop $(sudo docker ps -q) # Stop all containers
sudo docker rm -f $(sudo docker ps -aq) # Remove all unused docker container labels