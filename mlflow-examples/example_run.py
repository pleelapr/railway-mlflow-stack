import mlflow

import numpy as np
import pandas as pd

from mlflow.models import infer_signature

from sklearn import datasets
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def run_training_and_prediction() -> tuple[
	dict, float, np.ndarray, np.ndarray, np.ndarray, LogisticRegression
]:
	"""Train a logistic regression model on the iris dataset.

	Returns:
		Tuple containing:
		- params: Model hyperparameters dictionary
		- accuracy: Model accuracy on test set
		- X_train: Training features
		- X_test: Test features
		- y_test: Test labels
		- lr: Trained LogisticRegression model
	"""
	# Load the Iris dataset
	X, y = datasets.load_iris(return_X_y=True)

	# Split the data into training and test sets
	X_train, X_test, y_train, y_test = train_test_split(
		X, y, test_size=0.2, random_state=42
	)

	# Define the model hyperparameters
	params = {
		"solver": "lbfgs",
		"max_iter": 1000,
		"multi_class": "auto",
		"random_state": 8888,
	}

	# Train the model
	lr = LogisticRegression(**params)
	lr.fit(X_train, y_train)

	# Predict on the test set
	y_pred = lr.predict(X_test)

	# Calculate accuracy as a target loss metric
	accuracy = accuracy_score(y_test, y_pred)

	return params, accuracy, X_train, X_test, y_test, lr


def log_results_in_mlflow(
	params: dict, accuracy: float, X_train: np.ndarray, lr: LogisticRegression
):
	"""Log model parameters, metrics, and artifacts to MLflow.

	Args:
		params: Model hyperparameters to log
		accuracy: Model accuracy metric to log
		X_train: Training data for model signature inference
		lr: Trained LogisticRegression model to log

	Returns:
		ModelInfo object containing model metadata
	"""
	# Start an MLflow run
	try:
		with mlflow.start_run():
			# Log the hyperparameters
			mlflow.log_params(params)

			# Log the loss metric
			mlflow.log_metric("accuracy", accuracy)

			# Set tags that we can use to organize and find runs later
			mlflow.set_tag("Training Info", "Basic LR model for iris data")
			mlflow.set_tag("model_type", "LogisticRegression")
			mlflow.set_tag("dataset", "iris")
			mlflow.set_tag("framework", "scikit-learn")

			# Infer the model signature
			signature = infer_signature(X_train, lr.predict(X_train))

			# Log the model
			model_info = mlflow.sklearn.log_model(
				sk_model=lr,
				artifact_path="model",
				signature=signature,
				input_example=X_train,
				registered_model_name="tracking-quickstart",
			)

			return model_info
	except Exception as e:
		print(f"Error logging to MLflow: {e}")
		print("This might be due to connectivity issues with the MLflow server.")
		raise


def example_run(tracking_url: str | None) -> pd.DataFrame:
	"""Run a complete MLflow experiment with model training and logging.

	Args:
		tracking_url: MLflow tracking server URL, None for local tracking

	Returns:
		DataFrame containing model predictions vs actual values
	"""
	# Set the tracking URL
	if tracking_url:
		mlflow.set_tracking_uri(tracking_url)
		try:
			# Test connectivity by trying to get the tracking URI
			current_uri = mlflow.get_tracking_uri()
			print(f"Connected to MLflow tracking server: {current_uri}")
		except Exception as e:
			print(f"Warning: Could not verify connection to MLflow server: {e}")
			print("Continuing with local tracking...")
			mlflow.set_tracking_uri("")
	else:
		print("Using local MLflow tracking (mlruns/ directory)")

	# Train and run the model
	params, accuracy, X_train, X_test, y_test, lr = run_training_and_prediction()

	# Set the active experiment in MLflow
	experiment_name = "MLFlow Quickstart"
	print(f"\nSetting up experiment: {experiment_name}")
	mlflow.set_experiment(experiment_name)

	# Log and tag the results in MLflow for review
	# This all stores the trained model in MLflow
	print(f"Training accuracy: {accuracy:.3f}")
	print("Logging model and metrics to MLflow...")
	model_info = log_results_in_mlflow(params, accuracy, X_train, lr)

	print(f"Model logged successfully! Model URI: {model_info.model_uri}")
	print(f"Model run ID: {model_info.run_id}")

	# Load the model to use it
	print("\nLoading model for inference...")
	loaded_model = mlflow.pyfunc.load_model(model_info.model_uri)

	# Use the model and output results
	predictions = loaded_model.predict(X_test)
	iris_feature_names = datasets.load_iris().feature_names
	iris_target_names = datasets.load_iris().target_names

	# Convert X_test validation feature data to a Pandas DataFrame
	result = pd.DataFrame(X_test, columns=iris_feature_names)

	# Add the actual classes to the DataFrame (both numeric and names)
	result["actual_class"] = y_test
	result["actual_class_name"] = [iris_target_names[i] for i in y_test]

	# Add the model predictions to the DataFrame (both numeric and names)
	result["predicted_class"] = predictions.astype(int)
	result["predicted_class_name"] = [iris_target_names[int(i)] for i in predictions]

	# Add a column showing if the prediction was correct
	result["correct_prediction"] = result["actual_class"] == result["predicted_class"]

	print("\n=== Model Predictions vs Actual Values ===")
	print(result)

	# Calculate and display accuracy
	accuracy_percentage = (result["correct_prediction"].sum() / len(result)) * 100
	print("\n=== Model Performance ===")
	print(
		f"Test set accuracy: {accuracy_percentage:.1f}% ({result['correct_prediction'].sum()}/{len(result)} correct)"
	)

	# Show any misclassifications
	misclassifications = result[~result["correct_prediction"]]
	if not misclassifications.empty:
		print(f"\nMisclassified samples: {len(misclassifications)}")
		print(misclassifications[["actual_class_name", "predicted_class_name"]])
	else:
		print("\n🎉 Perfect classification! All predictions were correct.")

	return result
