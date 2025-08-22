# Deploy and Host MLFlow on Railway

MLflow is an open-source platform for managing ML/AI lifecycles. It handles experiment tracking, model packaging, and deployment with a combination of online services and local Python tooling. MLFlow standardizes workflows across tools and frameworks, making collaboration, reproducibility, and scaling ML systems easier in both research and production environments.

## About Hosting MLFlow

Hosting MLFlow on Railway is easy! This tempalte makes it a 1-click deploy. Once all the service's are deployed and reporting healthy, you'll just need to configure your local environment using the username/password automatically generate for you by Railway and you're good to start building production ready ML/AI systems.

This template was based on MLFlow's ["Remote Experiment Tracking with MLFlow Tracking Server"](https://mlflow.org/docs/latest/ml/tracking/tutorials/remote-server/) guide that allows you to remotely access the MLFlow Artifact Store, Backend Store, and a shared Tracking server for easy collaboration across your ML/AI teams.

## Common Use Cases

- **Track and compare experiments**: Log parameters, metrics, and outputs from every training run. Quickly compare results to see which models perform best and why.
- **Centralized artifact storage**: Store models, plots, logs, and other outputs in MinIO, making them easy to retrieve, share, and keep organized.
- **Manage model lifecycles**: Use the model registry to version, annotate, and promote models from experimentation through staging and into production.
- **Keep data reproducible**: Record dataset versions or URIs so you always know exactly which data was used to train a model—even if the raw data itself lives elsewhere.
- **Package models for reuse**: PAutomatically capture dependencies and package models into portable formats like Docker images or Conda environments, ensuring consistent results everywhere.
- **Deploy models with ease**: Serve trained models locally or via Docker containers that you can push up to a registry, and deploy back to Railway!

## Dependencies for MLFlow Hosting

The Railway template includes all required dependencies:

- a Caddy HTTP Gateway / Reverse proxy that provides authentication and HTTP logging.
- a MLFlow "tracking" server that acts as a primary API connects everything together.
- a PostgreSQL database which acts as an MLFlow Backend Store.
- a Minio S3 compatible file store which acts as an MLFlow Artifact Store.

### Deployment Dependencies

The MLFlow documentation is crucial for understanding how to best utilize all of the great tooling MLFlow can provide. 
Here are some links to get you started:

- [Getting started with ML](https://mlflow.org/docs/latest/ml/getting-started/): a getting started guide for MLOps on MLFlow.
- [Getting Started with GenAI](https://mlflow.org/docs/latest/genai/getting-started/): a getting started guide for LLMOps on MLFlow.
- [MLFlow v3](https://mlflow.org/docs/latest/genai/mlflow-3): release notes for the latest major release of MLFlow.

### Implementation Details

#### Pinning MLFlow versions

Just provide a `MLFOW_VERSION` environment variable on the MLFlow Service to pin a version! by default, it's pinned to v3.3.1.

#### Authentication via Caddy

MLFlow has a few experimental authentication features right now, but nothing stable.

By using basic authentication via Caddy, we're following MLFlow's best practice on deploying a production system behind a reverse proxy and using a stable and reliable form of authentication that their Python tooling already supports.

To make sure your authentication works locally, make sure you export your MLFlow credentials

```bash
# set your credentials
export MLFLOW_TRACKING_URI=https://your-mlflow-deployment.up.railway.app
export MLFLOW_TRACKING_USERNAME=username
export MLFLOW_TRACKING_PASSWORD=your-generated-password

# any MLFlow code will pick those credentials up... 
python example.py
```

#### Extending the default MLFlow dockerfile

The default dockerfile provided by mlflow just includes the bare minimum setup.  

By creating a custom dockerfile that extends the default image, and following the best practices outlined on the MLFlow docsite, We were able to make this template a 1-click-deploy and ensure that it would still be heavily extensible to suit your needs after deployment.

#### Deploying your MLFlow trained models on Railway

You can easily deploy your MLFlow trained models on Railway by reading through the [MLFlow Serving docs](https://mlflow.org/docs/latest/ml/deployment/) and adapting the ["deploy MLFlow model to k8s" guide](https://mlflow.org/docs/latest/ml/deployment/deploy-model-to-kubernetes/). To summarize, they outline the following:

- how to [generate a docker image based on an MLFlow trained model](https://mlflow.org/docs/latest/api_reference/cli.html#mlflow-models-build-docker).
- how to push that docker image to your docker repository of choice.

From there, you can follow this Railway guide on deploying docker images ([public](https://docs.railway.com/guides/services#deploying-a-public-docker-image), or [private](https://docs.railway.com/guides/services#deploying-a-private-docker-image)) on Railway to serve your deployed images!

_With a little bit of custom automation code, you could use this template as the core of an MLOps deployment pipeline!_

## Why Deploy MLFlow on Railway?

Railway is a singular platform to deploy your infrastructure stack. Railway will host your infrastructure so you don't have to deal with configuration, while allowing you to vertically and horizontally scale it.

By deploying MLFlow on Railway, you are one step closer to supporting a complete full-stack application with minimal burden. Host your servers, databases, AI agents, and more on Railway.