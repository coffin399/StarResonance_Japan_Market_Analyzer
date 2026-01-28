#!/bin/bash
set -e

echo "Waiting for database to be ready..."
until pg_isready -h postgres -U bpsr_user; do
    sleep 1
done

echo "Database is ready. Running migrations..."
python -m src.database.setup

echo "Starting API server..."
exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000
