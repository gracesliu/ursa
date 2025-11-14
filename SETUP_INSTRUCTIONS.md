# Quick Setup Instructions

## Step 1: Install Twilio Package

```bash
cd backend
pip install twilio
```

## Step 2: Create .env File

Create a file called `.env` in the `backend/` directory with this content:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here

# Twilio Phone Number (get this next)
TWILIO_PHONE_NUMBER=

# Your Phone Number
POLICE_NUMBER=+13022151083

# Base URL (we'll update this with ngrok)
BASE_URL=http://localhost:8000

USE_REAL_AI=false
```

## Step 3: Get Your Twilio Phone Number

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. If you don't have a number yet:
   - Click "Buy a number"
   - Select United States
   - Click "Search"
   - Pick any number (they're free on trial)
   - Click "Buy"
3. Copy your phone number (format: +15551234567)
4. Add it to `.env` file: `TWILIO_PHONE_NUMBER=+15551234567`

## Step 4: Set Up ngrok

1. Install ngrok (if not already):
   ```bash
   brew install ngrok
   # OR download from: https://ngrok.com/download
   ```

2. Start your backend:
   ```bash
   cd backend
   python main.py
   ```

3. In another terminal, start ngrok:
   ```bash
   ngrok http 8000
   ```

4. Copy the HTTPS URL (looks like: `https://abc123.ngrok.io`)

5. Update `.env` file:
   ```env
   BASE_URL=https://your-ngrok-url.ngrok.io
   ```

## Step 5: Configure Twilio Webhook

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click on your Twilio phone number
3. Scroll to "Voice & Fax" section
4. Under "A CALL COMES IN", set:
   - **Webhook URL:** `https://your-ngrok-url.ngrok.io/api/twilio/voice`
   - **HTTP Method:** `POST`
5. Click "Save"

## Step 6: Test It!

1. Make sure backend is running: `cd backend && python main.py`
2. Make sure ngrok is running: `ngrok http 8000`
3. In another terminal:
   ```bash
   curl http://localhost:8000/api/police-call/test
   ```
4. Your phone should ring! 📞

## Quick Commands Summary

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start ngrok
ngrok http 8000

# Terminal 3: Test
curl http://localhost:8000/api/police-call/test
```

