#!/bin/bash

# Quick test script for police calling feature

echo "🚨 Testing Ursa Police Calling Feature"
echo "======================================"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/ > /dev/null; then
    echo "❌ Backend server is not running!"
    echo "   Start it with: cd backend && python main.py"
    exit 1
fi

echo "✅ Backend server is running"
echo ""

# Trigger test threat
echo "📞 Triggering test threat..."
response=$(curl -s http://localhost:8000/api/police-call/test)

echo "Response: $response"
echo ""

# Check threats
echo "🔍 Checking active threats..."
threats=$(curl -s http://localhost:8000/api/threats)
echo "$threats" | python3 -m json.tool 2>/dev/null || echo "$threats"

echo ""
echo "✅ Test complete! Check the backend console for:"
echo "   - Threat analysis results"
echo "   - Police call status (simulated if Twilio not configured)"
echo "   - Community notification status"
echo ""
echo "If Twilio is configured, you should receive:"
echo "   📞 A phone call to 3022151083"
echo "   📱 An SMS with incident details"

