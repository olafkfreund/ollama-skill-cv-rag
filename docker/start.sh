#!/bin/bash

# Wait for Ollama to be ready
OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://localhost:11434}
echo "Waiting for Ollama to be ready at $OLLAMA_BASE_URL..."
until curl -s "$OLLAMA_BASE_URL/api/tags" >/dev/null; do
    echo "Ollama not ready yet, retrying in 5 seconds..."
    sleep 5
done
echo "Ollama is ready!"

# Pull the required model
echo "Pulling the llama3 model..."
curl -X POST "$OLLAMA_BASE_URL/api/pull" -d '{"name": "llama3"}'

# Process documents
echo "Processing documents..."
python -m src.scripts.ingest_data

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000
