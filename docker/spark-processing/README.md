## Building 
cd docker/spark-processing
sudo docker build -t spark-processing .

## Run manual spark-processing
sudo docker run -itd --name spark-processing --network iotnet -p 7077:7077 spark-processing

# Other
sudo docker stop $(sudo docker ps -q) # Stop all containers
sudo docker rm -f $(sudo docker ps -aq) # Remove all unused docker container labels