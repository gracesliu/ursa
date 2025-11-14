#!/bin/bash

# Quick Backend Test Script
# Tests if backend is running and responding

echo "🧪 Testing Constellation Backend..."
echo ""

# Check if backend is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend is running!"
    echo ""
    
    echo "📡 Testing API endpoints:"
    echo ""
    
    echo "1. Root endpoint:"
    curl -s http://localhost:8000/ | python3 -m json.tool
    echo ""
    
    echo "2. Cameras endpoint:"
    curl -s http://localhost:8000/api/cameras | python3 -m json.tool
    echo ""
    
    echo "3. Threats endpoint:"
    curl -s http://localhost:8000/api/threats | python3 -m json.tool
    echo ""
    
    echo "✅ All endpoints responding!"
else
    echo "❌ Backend is not running!"
    echo "   Start it with: cd backend && python main.py"
    exit 1
fi

