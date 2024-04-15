CREATE KEYSPACE IF NOT EXISTS iot_stations
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': '1'  -- Change to 1 if using a single-node cluster
};

CREATE TABLE IF NOT EXISTS iot_stations.spark_stream (
    station_id text,
    record_time timestamp,
    temperature double,
    humidity double,
    pressure double,
    air_quality double,
    particulate_matter double,
    noise_level double,
    illuminance double,
    wind_speed double,
    rainfall double,
    temperature_outlier boolean,
    humidity_outlier boolean,
    pressure_outlier boolean,
    air_quality_outlier boolean,
    particulate_matter_outlier boolean,
    noise_level_outlier boolean,
    illuminance_outlier boolean,
    wind_speed_outlier boolean,
    rainfall_outlier boolean,
    PRIMARY KEY (station_id, record_time)
) WITH CLUSTERING ORDER BY (record_time DESC);