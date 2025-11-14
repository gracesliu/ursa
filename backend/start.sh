#!/bin/bash
# Quick start script for Constellation backend

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the server
python main.py

