#!/bin/bash

# Check ngrok status

echo "🔍 Checking ngrok status..."
echo ""

# Check if ngrok is running
if pgrep -f "ngrok http" > /dev/null; then
    echo "✅ ngrok is running"
    echo ""
    
    # Try to get URL from ngrok API
    URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); tunnels = data.get('tunnels', []); print(tunnels[0]['public_url'] if tunnels else '')" 2>/dev/null)
    
    if [ -n "$URL" ]; then
        echo "📋 Your ngrok URL: $URL"
        echo ""
        echo "✅ Everything is set up! You can:"
        echo "   1. Test: curl http://localhost:8000/api/police-call/test"
        echo "   2. View ngrok dashboard: http://localhost:4040"
    else
        echo "⚠️  ngrok is running but URL not accessible"
        echo "   Try opening: http://localhost:4040"
    fi
else
    echo "❌ ngrok is not running"
    echo ""
    echo "Start it with:"
    echo "  ./start_ngrok.sh"
    echo "  OR"
    echo "  ngrok http 8000"
fi

