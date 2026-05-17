#!/bin/sh
set -e

# SECURED_NETWORK="${SECURED_NETWORK:-true}"
MODEL="${OLLAMA_MODEL:-llama3.2:3b}"
HOST="0.0.0.0"

echo "Starting Ollama server on $HOST"
echo "Configured model: $MODEL"

export OLLAMA_HOST="$HOST"

ollama serve &
SERVER_PID=$!

cleanup() {
  echo "Shutting down Ollama (PID $SERVER_PID)..."
  kill "$SERVER_PID" 2>/dev/null || true
}
trap cleanup INT TERM

echo "Waiting for Ollama API..."
until ollama list >/dev/null 2>&1; do
  sleep 1
done

echo "Ollama ready"

# if [ "$SECURED_NETWORK" != "true" ]; then
#   echo "Running in open network mode. Ollama will be accessible on all interfaces."

# else
#   echo "Running in secured network mode. Ollama will be accessible only within the Docker network."
# fi


  if ! ollama show "$MODEL" >/dev/null 2>&1; then
    echo "Pulling $MODEL..."
    ollama pull "$MODEL"
    echo "Model ready"
  else
    echo "Model $MODEL already available"
  fi

echo "Ollama startup complete"
wait "$SERVER_PID"