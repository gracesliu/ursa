#!/bin/bash

# Setup script to create .env file with your Twilio credentials

echo "🔧 Setting up Ursa .env file..."
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Overwrite? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 1
    fi
fi

# Create .env file
cat > .env << 'EOF'
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here

# Twilio Phone Number (get this from Twilio Console → Phone Numbers)
# Format: +15551234567
TWILIO_PHONE_NUMBER=

# Your Phone Number (already verified)
POLICE_NUMBER=+13022151083

# Base URL for webhooks (use ngrok URL when running)
BASE_URL=http://localhost:8000

# AI Mode
USE_REAL_AI=false
EOF

echo "✅ .env file created!"
echo ""
echo "📋 Next steps:"
echo "1. Get your Twilio phone number from: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming"
echo "2. Add it to .env: TWILIO_PHONE_NUMBER=+15551234567"
echo "3. Set up ngrok and update BASE_URL"
echo ""

