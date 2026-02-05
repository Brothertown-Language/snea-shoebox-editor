#!/bin/bash
# Copyright (c) 2026 Brothertown Language

# Script to kill any existing Streamlit processes to ensure a clean restart
# This is used by the PyCharm Run Configuration.

# Find PIDs of streamlit processes running src/frontend/app.py
PIDS=$(ps aux | grep "streamlit run src/frontend/app.py" | grep -v grep | awk '{print $2}')

if [ -n "$PIDS" ]; then
    echo "Killing existing Streamlit processes: $PIDS"
    kill $PIDS
    # Give it a moment to release ports
    sleep 1
else
    echo "No existing Streamlit processes found."
fi
