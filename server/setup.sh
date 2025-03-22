#!/bin/bash

echo "Setting up EasyOCR server environment..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "Script directory: $SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it and try again."
    exit 1
fi

# Verify if requirements.txt exists
if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "Error: requirements.txt not found at $SCRIPT_DIR/requirements.txt"
    # Create a basic requirements file if it doesn't exist
    echo "Creating a basic requirements file..."
    cat > "$SCRIPT_DIR/requirements.txt" << EOL
flask>=2.0.0
flask-cors>=3.0.10
easyocr>=1.6.2
numpy>=1.20.0
opencv-python>=4.5.0
Werkzeug>=2.0.0
EOL
    echo "Created requirements.txt file."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Make sure you have python3-venv installed."
        echo "On Ubuntu/Debian: sudo apt install python3-venv"
        exit 1
    fi
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

# Install dependencies using the full path to requirements.txt
echo "Installing dependencies from $SCRIPT_DIR/requirements.txt..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi

echo "Setup completed successfully!"
echo ""
echo "To start the server:"
echo "1. Activate the virtual environment (if not already activated):"
echo "   source $SCRIPT_DIR/venv/bin/activate"
echo "2. Run the server:"
echo "   python $SCRIPT_DIR/server.py"
echo ""
echo "To deactivate the virtual environment when done:"
echo "   deactivate"

# Ask if user wants to start the server now
read -p "Do you want to start the server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting EasyOCR server..."
    python "$SCRIPT_DIR/server.py"
fi
