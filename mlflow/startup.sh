#!/bin/bash
echo 'Running database migration (safe to run every time)...'
mlflow db upgrade $DB_URL

echo 'Starting mlflow server...'
exec mlflow server \
    --backend-store-uri $DB_URL \
    --artifacts-destination s3://bucket \
    --host :: \
    --port ${PORT:-5000} \
    --allowed-hosts "*.up.railway.app,localhost:*"