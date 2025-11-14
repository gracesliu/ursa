#!/bin/bash

# Script to start ngrok for Ursa backend

echo "🚀 Starting ngrok for Ursa backend..."
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "⚠️  Backend server doesn't appear to be running on port 8000"
    echo "   Start it with: cd backend && python main.py"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Starting ngrok tunnel..."
echo "📋 Once ngrok starts, copy the HTTPS URL and:"
echo "   1. Update backend/.env: BASE_URL=https://your-url.ngrok.io"
echo "   2. Update Twilio webhook: https://your-url.ngrok.io/api/twilio/voice"
echo ""

ngrok http 8000

