#!/bin/bash
# Copyright (c) 2026 Brothertown Language

# Script to start Streamlit in a persistent background process
# This ensures it continues running even after the Junie session exits.

LOG_FILE="tmp/streamlit.log"

echo "Starting Streamlit in the background..."
mkdir -p tmp
nohup uv run streamlit run src/frontend/app.py --server.address 0.0.0.0 --server.port 8501 > "$LOG_FILE" 2>&1 &

PID=$!
echo "Streamlit started with PID: $PID"
echo "Logs are being written to $LOG_FILE"
