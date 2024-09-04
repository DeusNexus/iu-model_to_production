import os
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, wasserstein_distance
from cassandra.cluster import Cluster
import joblib  # To save and load the model
import matplotlib
import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Load training data
training_df = pd.read_csv('spark_stream_data.csv')
training_df['record_time'] = pd.to_datetime(training_df['record_time'])
latest_training_time = training_df['record_time'].max()

###################################################
##### Get current data from Cassandra database ####
###################################################

# Connect to Cassandra
cluster = Cluster(['localhost'], port=9042)  # Replace 'localhost' with the appropriate host IP if needed
session = cluster.connect('iot_stations')  # Connect to your keyspace

# Convert `latest_training_time` to an ISO format string
latest_training_time_str = latest_training_time.strftime('%Y-%m-%dT%H:%M:%S')

# Query to select only new data after the latest record_time in training data
query = "SELECT * FROM spark_stream WHERE record_time > %s ALLOW FILTERING"
rows = session.execute(query, [latest_training_time_str])

# Convert the query result to a list of dictionaries
data = [dict(row._asdict()) for row in rows]

# Convert to a pandas DataFrame
new_df = pd.DataFrame(data)
new_df['record_time'] = pd.to_datetime(new_df['record_time'])

# Check if the DataFrame is not empty
if new_df.empty:
    print("No new data to process.")
else:
    # Continue with the drift detection
    print("New data loaded for drift detection.")

###################################################
##### Drift Detection Using Statistical Tests  ####
###################################################

# Features to monitor
features = ['humidity', 'noise_level', 'temperature']

def check_distribution_drift(training_df, new_df, features):
    drift_results = {}
    drift_detected = False
    for feature in features:
        train_values = training_df[feature].values
        new_values = new_df[feature].values

        # KS Test
        ks_stat, ks_p_value = ks_2samp(train_values, new_values)
        
        # Wasserstein Distance
        wd = wasserstein_distance(train_values, new_values)
        
        # Record results
        drift_results[feature] = {
            'KS Statistic': ks_stat,
            'KS p-value': ks_p_value,
            'Wasserstein Distance': wd
        }
        
        # Output drift warning if p-value is low (indicating drift)
        if ks_p_value < 0.05:  # Common threshold for statistical significance
            print(f"Warning: Drift detected in feature '{feature}' (KS p-value = {ks_p_value})")
            drift_detected = True  # Set the flag if drift is detected
    
    return pd.DataFrame(drift_results).T, drift_detected

# Run the drift check
if not new_df.empty:
    drift_report, drift_detected = check_distribution_drift(training_df, new_df, features)
    print(drift_report)

    # If drift is detected, retrain the model
    if drift_detected:
        print("Drift detected. Retraining the model...")

        # Determine the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Define the paths relative to the script directory
        model_dir = os.path.join(script_dir, 'mlruns', '0')

        # Load the latest run ID
        with open(os.path.join(model_dir, 'latest_id.txt'), 'r') as file:
            latest_id = file.read().strip()

        # Define paths for the existing model and scaler
        model_path = os.path.join(model_dir, latest_id, 'artifacts','isolation_forest_model', 'model.pkl')
        scaler_path = os.path.join(model_dir, latest_id,'artifacts', 'scaler.joblib')

        print(f"Model path: {model_path}")
        print(f"Scaler path: {scaler_path}")

        print("OS PATH ISFILE MODEL_PATH: ",os.path.isfile(model_path))
        print("OS PATH ISFILE SCALER_PATH: ",os.path.isfile(scaler_path))

        # Check if the files exist before loading
        if os.path.isfile(model_path) and os.path.isfile(scaler_path):
            # Enhanced error handling for model loading
            try:
                iso_forest = joblib.load(model_path)
                scaler = joblib.load(scaler_path)
                print("Loaded existing model and scaler.")
            except FileNotFoundError as e:
                print(f"File not found: {e}. Retraining the model from scratch.")
                iso_forest = None
                scaler = None
            except Exception as e:
                print(f"Unexpected error occurred: {e}. Retraining the model from scratch.")
                iso_forest = None
                scaler = None
        else:
            print(f"No existing model or scaler found at {model_path} or {scaler_path}. Training from scratch.")
            iso_forest = None
            scaler = None

        # Start a new MLflow run for retraining
        with mlflow.start_run() as new_run:
            # Retrain the model
            if iso_forest is None or scaler is None:
                # Ensure `new_df` contains only numeric features for scaling and model training
                data = new_df[features].astype('float64')  # Convert all to float64

                # Fit the StandardScaler on a DataFrame to keep feature names
                scaler = StandardScaler()
                
                # Fit and transform using DataFrame
                data_scaled = scaler.fit_transform(data)
                
                # Train the Isolation Forest model using DataFrame directly
                iso_forest = IsolationForest()
                iso_forest.fit(data_scaled)

            else:
                # Apply the scaler to new data using DataFrame to keep feature names
                data = new_df[features].astype('float64')  # Convert all to float64

                # Transform the data using the fitted scaler and retain column names
                data_scaled = scaler.fit_transform(data)
                
                # Retrain the Isolation Forest model using DataFrame directly
                iso_forest.fit(data_scaled)

            # Define the input example and infer the signature
            data_for_signature = data_scaled[:5] # Use a subset of data for signature inference
            signature = infer_signature(data_for_signature, iso_forest.predict(data_scaled[:5]))

            # Ensure input example matches the expected schema without integer warnings
            input_example = pd.DataFrame({
                'humidity': [50.1],
                'noise_level': [30.5],
                'temperature': [22.6]
            }).astype('float64')  # Convert all columns to float64 to avoid schema enforcement issues


            # Log the model and scaler
            mlflow.sklearn.log_model(iso_forest, "isolation_forest_model", input_example=input_example, signature=signature)
            joblib.dump(scaler, "scaler.joblib")
            mlflow.log_artifact("scaler.joblib")

            # Plot and log PCA results
            pca = PCA(n_components=3)
            pca_result = pca.fit_transform(data_scaled)

            # 2D Plot
            plt.figure()
            plt.scatter(pca_result[:, 0], pca_result[:, 1], c='blue', label='Normal')
            plt.xlabel('PCA Component 1')
            plt.ylabel('PCA Component 2')
            plt.title('2D PCA of Data with Isolation Forest Outliers')
            plt.legend()
            plt.savefig("pca_2d_plot.png")
            mlflow.log_artifact("pca_2d_plot.png")
            plt.close()

            # 3D Plot
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(pca_result[:, 0], pca_result[:, 1], pca_result[:, 2], c='blue', label='Normal')
            ax.set_xlabel('PCA Component 1')
            ax.set_ylabel('PCA Component 2')
            ax.set_zlabel('PCA Component 3')
            ax.set_title('3D PCA of Data with Isolation Forest Outliers')
            ax.legend()
            plt.savefig("pca_3d_plot.png")
            mlflow.log_artifact("pca_3d_plot.png")
            plt.close()

            # Get the new run ID
            new_run_id = new_run.info.run_id
            print(f"New MLflow run ID: {new_run_id}")

            # Update latest_id.txt with the new run ID
            with open(os.path.join(model_dir, 'latest_id.txt'), 'w') as file:
                file.write(new_run_id)
                print(f"Updated latest_id.txt with run ID: {new_run_id}")

        print("Model retraining completed and artifacts logged.")
    else:
        print("No new data to process.")
