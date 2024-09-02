from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, udf, pandas_udf
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, BooleanType
import mlflow.pyfunc
import pandas as pd
import joblib

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("KafkaOutlierDetectionWithMLflow") \
    .getOrCreate()

# Set the MLflow tracking URI to the path where the `mlruns` folder is located in the container
mlflow.set_tracking_uri("file:/mlruns")

# Load the Isolation Forest model from MLflow using its run ID
model_uri = 'runs:/be37c6b65f08460ab4ac5b0055a2368f/isolation_forest_model'
loaded_model = mlflow.pyfunc.load_model(model_uri)

# Load the scaler artifact from the MLflow run
scaler_path = mlflow.artifacts.download_artifacts(
    artifact_path="scaler.joblib",
    run_id='be37c6b65f08460ab4ac5b0055a2368f'
)

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

# Query to print results to the console
console_query = outliers_df.writeStream.outputMode("append").format("console").start()

# Wait for the streaming query to terminate
console_query.awaitTermination()
