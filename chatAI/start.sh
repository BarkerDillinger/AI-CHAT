#!/bin/bash

cd /mnt/AI/Development/Projects/chatAI || exit 1

# Optional: create logs directory
mkdir -p logs

# Activate virtual environment
source chatai/venv/bin/activate

# Start Ollama in the background and log output
ollama serve > logs/ollama.log 2>&1 &
OL_PID=$!

echo "Ollama started with PID $OL_PID"
sleep 2

# Ensure Ollama is running before starting the app
if ! ps -p $OL_PID > /dev/null; then
    echo "Failed to start Ollama. Exiting."
    exit 1
fi

# Trap to kill Ollama on script exit
trap "echo 'Stopping Ollama...'; kill $OL_PID" EXIT

# Start the chatAI app
PYTHONPATH=. uvicorn chat.main:app --reload --port 4242