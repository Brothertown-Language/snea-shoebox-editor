#!/bin/bash
# Copyright (c) 2026 Brothertown Language

# Script to kill any existing Streamlit processes to ensure a clean restart
# This is used by the PyCharm Run Configuration.

# Ensure we are in the project root using git
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
if [ -z "$PROJECT_ROOT" ]; then
    echo "Error: Could not find project root via git."
    exit 1
fi
cd "$PROJECT_ROOT" || exit 1

# Stop local PostgreSQL if it is running
echo "Stopping local PostgreSQL server..."
uv run python scripts/manage_local_db.py stop

# Kill any remaining pgserver processes if necessary
PG_PIDS=$(ps aux | grep "pgserver/pginstall/bin/postgres" | grep -v grep | awk '{print $2}')
if [ -n "$PG_PIDS" ]; then
    echo "Killing remaining pgserver processes: $PG_PIDS"
    kill $PG_PIDS
fi

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
