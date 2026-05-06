#!/bin/sh
set -e

echo "Starting Ollama server..."
echo "Note: Model qwen2.5-coder:7b should be available (pulled previously)"
echo "If not available, the agent will handle pulling it when needed"

# Start Ollama server
export OLLAMA_HOST=0.0.0.0
exec ollama serve