from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, lit, udf, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, BooleanType

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("KafkaOutlierDetection") \
    .config("spark.cassandra.connection.host", "cassandra") \
    .config("spark.cassandra.connection.port", "9042") \
    .config("spark.cassandra.auth.username", "cassandra") \
    .config("spark.cassandra.auth.password", "cassandra") \
    .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.1.0") \
    .getOrCreate()


# Define the schema matching the structure of the JSON messages
schema = StructType([
    StructField("station_id", StringType()),
    StructField("temperature", DoubleType()),
    StructField("humidity", DoubleType()),
    StructField("pressure", DoubleType()),
    StructField("air_quality", DoubleType()),
    StructField("particulate_matter", DoubleType()),
    StructField("noise_level", DoubleType()),
    StructField("illuminance", DoubleType()),
    StructField("wind_speed", DoubleType()),
    StructField("rainfall", DoubleType()),
])

# Read data from Kafka
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "broker:9092") \
    .option("subscribe", "iot-sensor-stream") \
    .load()

# Parse the JSON data from Kafka
parsed_df = kafka_df.selectExpr("CAST(value AS STRING)").select(from_json(col("value"), schema).alias("data")).select("data.*")

# Distribution parameters for each sensor type
dist_parameters = {
    'temperature': {'mean': 25, 'std_dev': 2},
    'humidity': {'mean': 60, 'std_dev': 3},
    'pressure': {'mean': 1013, 'std_dev': 2},
    'air_quality': {'mean': 200, 'std_dev': 20},
    'particulate_matter': {'mean': 30, 'std_dev': 2},
    'noise_level': {'mean': 50, 'std_dev': 3},
    'illuminance': {'mean': 500, 'std_dev': 50},
    'wind_speed': {'mean': 5, 'std_dev': 20},
    'rainfall': {'mean': 0, 'std_dev': 3}
}

# UDF to check if a value is an outlier based on the 0.01th and 99.99th percentiles
def is_outlier(value, mean, std_dev):
    z_score_9999th = 3.72
    z_score_001st = -3.72
    lower_bound = mean + z_score_001st * std_dev
    upper_bound = mean + z_score_9999th * std_dev
    return value < lower_bound or value > upper_bound

is_outlier_udf = udf(is_outlier, BooleanType())

# Initialize outliers_df as a copy of parsed_df
outliers_df = parsed_df

# Apply the outlier detection to each sensor column
for sensor, params in dist_parameters.items():
    outliers_df = outliers_df.withColumn(f"{sensor}_outlier", is_outlier_udf(col(sensor), lit(params['mean']), lit(params['std_dev'])))

# Query to print results to the console
console_query = outliers_df.writeStream.outputMode("update").format("console").start()

# Define the query to write the streaming data to Cassandra
def write_to_cassandra(batch_df, epoch_id):
    # Add a timestamp column to the DataFrame
    batch_with_timestamp = batch_df.withColumn("record_time", current_timestamp())
    
    batch_with_timestamp.write \
        .format("org.apache.spark.sql.cassandra") \
        .mode("append") \
        .option("keyspace", "iot_stations") \
        .option("table", "spark_stream") \
        .save()

cassandra_query = outliers_df \
    .writeStream \
    .outputMode("update") \
    .foreachBatch(write_to_cassandra) \
    .start()

# Wait for both streaming queries to terminate
console_query.awaitTermination()
cassandra_query.awaitTermination()