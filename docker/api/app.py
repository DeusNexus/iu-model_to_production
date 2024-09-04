from flask import Flask, jsonify, request
from cassandra.cluster import Cluster
import pandas as pd
import joblib
import os
import subprocess
import numpy as np
from datetime import datetime, timedelta
import mlflow.pyfunc
import mlflow

# Initialize Flask app
app = Flask(__name__)

# Connect to Cassandra
cluster = Cluster(['localhost'], port=9042)  # Update with the correct host IP if needed
session = cluster.connect('iot_stations')  # Connect to your keyspace

def load_latest_model():
    # Determine the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the paths relative to the script directory
    model_dir = os.path.join(script_dir, 'mlruns', '0')

    # Load the latest run ID
    try:
        with open(os.path.join(model_dir, 'latest_id.txt'), 'r') as file:
            latest_id = file.read().strip()
    except Exception as e:
        print('Error occured getting run ID: ',e)
        # Try to use default (first model id)
        latest_id = 'be37c6b65f08460ab4ac5b0055a2368f'

    # Load the model and scaler from MLflow
    model_uri = f'runs:/{latest_id}/isolation_forest_model'
    loaded_model = mlflow.pyfunc.load_model(model_uri)

    # Load the scaler artifact from the MLflow run
    scaler_path = mlflow.artifacts.download_artifacts(
        artifact_path="scaler.joblib",
        run_id=f'{latest_id}'
    )
    scaler = joblib.load(scaler_path)

    # Retrieve model version information
    model_version_info = mlflow.get_run(f'{latest_id}').info.run_id

    return loaded_model, scaler, model_version_info

# Function to fetch the latest anomalies
def get_latest_anomalies(limit=10):
    # Fetch a larger set of data and sort in Python
    query = "SELECT * FROM spark_stream;"
    rows = session.execute(query)
    data = [dict(row._asdict()) for row in rows]
    df = pd.DataFrame(data)
    if not df.empty:
        df['record_time'] = pd.to_datetime(df['record_time'])
        df = df[df['is_outlier'] == True].sort_values(by='record_time', ascending=False).head(limit)  # Sort by 'record_time' and limit
    return df

# Endpoint to fetch the latest predictions
@app.route('/api/latest_anomalies', methods=['GET'])
def latest_anomalies():
    try:
        limit = int(request.args.get('limit', 10))
        df = get_latest_anomalies(limit)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Endpoint to check for drift and retrain if present, will update the model to use the latest new model in the docker/api/mlruns/0 folder using latest_id.txt
@app.route('/api/check_drift_retrain', methods=['GET'])
def check_drift_retrain():
    try:
        # Run detect_drift.py script and capture its output
        result = subprocess.run(['python3', 'detect_drift.py'], capture_output=True, text=True)
        
        # Capture the stdout and stderr
        stdout = result.stdout
        stderr = result.stderr

        # Return stdout in the response; you might want to include stderr for debugging
        if result.returncode == 0:
            return jsonify({'msg': stdout})
        else:
            return jsonify({'error': stderr}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/outliers_count', methods=['GET'])
def get_outliers_count():
    try:
        # Read 'time_range' parameter from request (e.g., '5m', '60m', '1d')
        time_range = request.args.get('time_range')
        
        # Validate the input time range
        if not time_range:
            return jsonify({'error': 'time_range parameter is required. Examples: 5m, 60m, 1d'}), 400

        # Convert time range into a timedelta object
        time_value = int(time_range[:-1])  # Get the number part (e.g., '5', '60', '1')
        time_unit = time_range[-1]  # Get the unit part (e.g., 'm', 'd')

        # Determine the time delta
        if time_unit == 'm':  # Minutes
            delta = timedelta(minutes=time_value)
        elif time_unit == 'h':  # Hours
            delta = timedelta(hours=time_value)
        elif time_unit == 'd':  # Days
            delta = timedelta(days=time_value)
        else:
            return jsonify({'error': 'Invalid time range unit. Use "m" for minutes, "h" for hours, or "d" for days.'}), 400
        
        # Calculate the start time for filtering
        end_time = datetime.utcnow()
        start_time = end_time - delta
        
        # Query to get the count of outliers in the specified time range
        query = """
            SELECT COUNT(*) FROM spark_stream 
            WHERE is_outlier = true 
            AND record_time >= %s AND record_time <= %s ALLOW FILTERING;
        """
        
        rows = session.execute(query, (start_time, end_time))
        outliers_count = rows.one()[0]  # Get the count
        
        # Respond with the count of outliers
        return jsonify({'time_range': time_range, 'outliers_count': outliers_count})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to make a new prediction
@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        # Load the latest model and get the info
        loaded_model, scaler, model_version_info = load_latest_model()
        
        # Receive the input data as JSON
        data = request.json
        
        # Define expected features
        features = ['humidity', 'noise_level', 'temperature']
        
        # Check if all required features are in the input JSON
        if not all(feature in data for feature in features):
            return jsonify({'error': 'Invalid input data. Required fields: humidity, noise_level, temperature'}), 400
        
        # Validate that all features are numbers and not null
        for feature in features:
            if data[feature] is None or not isinstance(data[feature], (int, float)):
                return jsonify({'error': f'Invalid value for {feature}. It must be a number and not null.'}), 400
        
        # Create DataFrame with the correct column names
        X = pd.DataFrame([[
            data['humidity'], 
            data['noise_level'], 
            data['temperature']
        ]], columns=features)
        
        # Scale the features
        X_scaled = scaler.transform(X)
        
        # Predict using the MLflow model
        prediction = loaded_model.predict(X_scaled)
        is_anomaly = bool(prediction[0] == -1)  # Ensure it's a proper JSON-serializable boolean
        
        # Respond with the prediction and model version
        return jsonify({'is_anomaly': is_anomaly, 'features': data, 'model_version': model_version_info})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Main block to run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
