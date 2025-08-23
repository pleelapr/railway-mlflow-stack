from os import getenv

from example_run import example_run


def main() -> None:
	"""Main entry point for the MLflow example.

	Reads environment variables for MLflow configuration and runs the example.
	"""
	tracking_url = getenv("MLFLOW_TRACKING_URL")
	tracking_username = getenv("MLFLOW_TRACKING_USERNAME")
	tracking_password = getenv("MLFLOW_TRACKING_PASSWORD")

	if tracking_password:
		tracking_password_censored = "".join(["*" for c in tracking_password])
		print(
			f"using tracking url {tracking_username}:{tracking_password_censored}@{tracking_url}"
		)
	else:
		print("No MLflow tracking credentials set, using local tracking")

	example_run(tracking_url)


if __name__ == "__main__":
	main()
