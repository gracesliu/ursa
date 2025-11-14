#!/bin/bash

# Start Ursa backend server

echo "🚀 Starting Ursa Backend Server..."
echo ""

cd "$(dirname "$0")/backend"

# Check if port 8000 is already in use
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is already in use"
    echo "   Stopping existing server..."
    kill $(lsof -ti:8000) 2>/dev/null
    sleep 2
fi

echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

python main.py

