#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Change to the script directory
cd "$SCRIPT_DIR"

# Activate virtual environment and run server
echo "Activating virtual environment and starting server..."
source "$SCRIPT_DIR/venv/bin/activate"
python server.py
