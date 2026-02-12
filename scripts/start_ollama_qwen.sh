#!/bin/bash
# Copyright (c) 2026 Brothertown Language

# Script to start Ollama and pull the Qwen2.5-Coder-14B model
# Designed for use by PyCharm or manual execution.

# Ensure we are in the project root using git
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
if [ -z "$PROJECT_ROOT" ]; then
    echo "Error: Could not find project root via git."
    exit 1
fi
cd "$PROJECT_ROOT" || exit 1

LOG_FILE="tmp/ollama_start.log"
MODEL_NAME="qwen2.5-coder:14b"

mkdir -p tmp
echo "--- Starting Ollama Startup Sequence: $(date) ---" > "$LOG_FILE"

# 1. Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Error: 'ollama' command not found. Please install Ollama first." | tee -a "$LOG_FILE"
    exit 1
fi

# 2. Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Ollama server not responding. Attempting to start..." | tee -a "$LOG_FILE"
    # Note: On many systems Ollama is a systemd service. 
    # If it's not running, we try to start it in the background as a fallback.
    nohup ollama serve > tmp/ollama_serve.log 2>&1 &
    
    # Wait for server to wake up
    MAX_RETRIES=10
    COUNT=0
    while ! curl -s http://localhost:11434/api/tags > /dev/null; do
        [ $COUNT -eq $MAX_RETRIES ] && echo "Error: Ollama server failed to start after $MAX_RETRIES seconds." && exit 1
        echo "Waiting for Ollama server... ($((COUNT+1))/$MAX_RETRIES)" | tee -a "$LOG_FILE"
        sleep 1
        COUNT=$((COUNT+1))
    done
    echo "Ollama server started successfully." | tee -a "$LOG_FILE"
else
    echo "Ollama server is already running." | tee -a "$LOG_FILE"
fi

# 3. Pull the model if not present
echo "Ensuring model '$MODEL_NAME' is available..." | tee -a "$LOG_FILE"
ollama pull "$MODEL_NAME" 2>&1 | tee -a "$LOG_FILE"

echo "Ollama is ready. Model: $MODEL_NAME" | tee -a "$LOG_FILE"
echo "--- Startup Sequence Complete: $(date) ---" >> "$LOG_FILE"
