from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, udf, pandas_udf, current_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, BooleanType
import mlflow.pyfunc
import pandas as pd
import joblib
import os

# Initialize Spark Session with Cassandra configurations
spark = SparkSession.builder \
    .appName("KafkaOutlierDetectionWithMLflow") \
    .config("spark.cassandra.connection.host", "cassandra") \
    .config("spark.cassandra.connection.port", "9042") \
    .config("spark.cassandra.auth.username", "cassandra") \
    .config("spark.cassandra.auth.password", "cassandra") \
    .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.1.0") \
    .getOrCreate()

# Set the MLflow tracking URI to the path where the `mlruns` folder is located in the container
mlflow.set_tracking_uri("file:/mlruns")

# Define the paths relative to the script directory
model_dir = '/mlruns/0'

# Load the latest run ID
try: 
    with open(os.path.join(model_dir, 'latest_id.txt'), 'r') as file:
        latest_id = file.read().strip()
except Exception as e:
    print('Failed to read file: ',e)
    # Use default model
    latest_id = 'be37c6b65f08460ab4ac5b0055a2368f'

# Define paths for the existing model and scaler
model_path = os.path.join(model_dir, latest_id, 'artifacts','isolation_forest_model', 'model.pkl')
scaler_path = os.path.join(model_dir, latest_id,'artifacts', 'scaler.joblib')

# Check if the files exist before loading
if os.path.isfile(model_path) and os.path.isfile(scaler_path):
    # Enhanced error handling for model loading
    try:
        loaded_model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        print("Loaded existing model and scaler.")
        print(f"Mlruns latest_id: {latest_id}")
    except FileNotFoundError as e:
        print(f"File not found: {e}. Retraining the model from scratch.")
        loaded_model = None
        scaler = None
    except Exception as e:
        print(f"Unexpected error occurred: {e}. Retraining the model from scratch.")
        loaded_model = None
        scaler = None
else:
    print(f"No existing model or scaler found at {model_path} or {scaler_path}. Training from scratch.")
    loaded_model = None
    scaler = None

# Load the scaler using joblib
scaler = joblib.load(scaler_path)

# Define the schema matching the structure of the JSON messages
schema = StructType([
    StructField("station_id", StringType()),
    StructField("humidity", DoubleType()),
    StructField("noise_level", DoubleType()),
    StructField("temperature", DoubleType()),
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

# Define a Pandas UDF to apply the MLflow model to the streaming data
@pandas_udf(BooleanType())
def detect_outliers(humidity: pd.Series, noise_level: pd.Series, temperature: pd.Series) -> pd.Series:
    # Combine the input columns into a DataFrame with the correct feature order
    pdf = pd.DataFrame({
        'humidity': humidity,
        'noise_level': noise_level,
        'temperature': temperature
    })
    # Scale the features
    scaled_features = scaler.transform(pdf.values)
    # Convert DataFrame to NumPy array (no feature names)
    pdf_values = scaled_features
    # Predict using the loaded model
    predictions = loaded_model.predict(pdf_values)
    # Return predictions as boolean: True for 'Outlier', False for 'Normal'
    return pd.Series(predictions == -1)

# Apply the MLflow model to each row in the parsed DataFrame
outliers_df = parsed_df.withColumn('is_outlier', detect_outliers(col('humidity'), col('noise_level'), col('temperature')))

# Add the latest_id as a new column
outliers_df = outliers_df.withColumn("mlflow_id", lit(latest_id))

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

# Write the outliers to Cassandra
cassandra_query = outliers_df \
    .writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_cassandra) \
    .start()

# Optionally, you can still print to console for debugging purposes
console_query = outliers_df.writeStream.outputMode("append").format("console").start()

# Wait for both streaming queries to terminate
console_query.awaitTermination()
cassandra_query.awaitTermination()
