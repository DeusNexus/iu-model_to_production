## Building 
cd docker/prometheus
sudo docker build -t prometheus .

## Run manual prometheus
sudo docker run -itd --name prometheus --network iotnet -p 9090:9090 prometheus

# Other
sudo docker stop $(sudo docker ps -q) # Stop all containers
sudo docker rm -f $(sudo docker ps -aq) # Remove all unused docker container labels