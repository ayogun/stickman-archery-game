#!/bin/bash
# Simple script to run the Stickman Archery Game

echo "Starting Stickman Archery Game..."
echo "Make sure you have Python 3 installed!"
echo ""

# Check if virtual environment exists
if [ ! -d "game_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv game_env
    echo "Installing pygame..."
    source game_env/bin/activate
    pip install pygame
else
    echo "Using existing virtual environment..."
    source game_env/bin/activate
fi

echo "Launching game..."
python stickman_archery.py
