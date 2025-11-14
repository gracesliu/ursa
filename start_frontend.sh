#!/bin/bash

# Start Ursa Frontend

echo "🚀 Starting Ursa Frontend..."
echo ""

cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

echo "Starting frontend development server..."
echo "Frontend will be available at: http://localhost:5173"
echo "Press Ctrl+C to stop"
echo ""

npm run dev

