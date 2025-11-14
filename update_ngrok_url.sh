#!/bin/bash

# Script to update .env with ngrok URL

if [ -z "$1" ]; then
    echo "Usage: ./update_ngrok_url.sh https://your-url.ngrok.io"
    echo ""
    echo "Or get URL from ngrok web interface: http://localhost:4040"
    exit 1
fi

NGROK_URL=$1

# Update .env file
if [ -f "backend/.env" ]; then
    # Check if BASE_URL exists
    if grep -q "BASE_URL=" backend/.env; then
        # Update existing BASE_URL
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s|BASE_URL=.*|BASE_URL=$NGROK_URL|" backend/.env
        else
            # Linux
            sed -i "s|BASE_URL=.*|BASE_URL=$NGROK_URL|" backend/.env
        fi
        echo "✅ Updated BASE_URL in backend/.env to: $NGROK_URL"
    else
        # Add BASE_URL
        echo "BASE_URL=$NGROK_URL" >> backend/.env
        echo "✅ Added BASE_URL to backend/.env: $NGROK_URL"
    fi
    
    echo ""
    echo "📋 Next step: Update Twilio webhook:"
    echo "   1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming"
    echo "   2. Click your number: +18608645576"
    echo "   3. Set webhook URL to: $NGROK_URL/api/twilio/voice"
    echo "   4. Set HTTP method to: POST"
    echo "   5. Save"
else
    echo "❌ backend/.env file not found!"
    exit 1
fi

