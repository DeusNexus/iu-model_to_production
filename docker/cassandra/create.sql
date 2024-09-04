CREATE KEYSPACE IF NOT EXISTS iot_stations
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': '1'  -- Change to 1 if using a single-node cluster
};

CREATE TABLE IF NOT EXISTS iot_stations.spark_stream (
    station_id text,
    record_time timestamp,
    humidity double,    
    noise_level double,
    temperature double,
    is_outlier boolean,
    mlflow_id text,
    PRIMARY KEY (station_id, record_time)
) WITH CLUSTERING ORDER BY (record_time DESC);