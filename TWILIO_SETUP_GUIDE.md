# Twilio Setup Guide for Ursa

Complete guide to getting free Twilio credentials for testing the police calling feature.

## 🆓 Is Twilio Free?

**Yes!** Twilio offers a **free trial** that includes:
- ✅ $15.50 in free credit (enough for testing)
- ✅ Free phone number for making calls and sending SMS
- ✅ No credit card required initially
- ✅ Perfect for demos and testing

**Limitations:**
- Trial account has some restrictions (can only call verified numbers initially)
- After trial, you pay per call/SMS (very cheap: ~$0.01-0.02 per call/SMS)

## Step-by-Step Setup

### Step 1: Sign Up for Twilio

1. Go to: **https://www.twilio.com/try-twilio**
2. Click "Start Free Trial"
3. Fill out the form:
   - Email address
   - Password
   - Phone number (for verification)
4. Verify your email and phone number

### Step 2: Get Your Credentials

Once logged into the Twilio Console:

1. **Account SID & Auth Token:**
   - Go to: https://console.twilio.com/
   - Your **Account SID** is shown on the dashboard (starts with `AC...`)
   - Click "Show" next to Auth Token to reveal it
   - **Copy both** - you'll need them for `.env`

2. **Get a Phone Number:**
   - Go to: Phone Numbers → Manage → Buy a Number
   - Click "Buy a number"
   - Select your country (United States)
   - Click "Search"
   - Pick any available number (they're all the same)
   - Click "Buy" (it's free on trial)
   - **Copy the phone number** (format: +15551234567)

### Step 3: Verify Your Phone Number (For Testing)

Since you're on a trial account, you need to verify the number you want to receive calls at:

1. Go to: Phone Numbers → Manage → Verified Caller IDs
2. Click "Add a new Caller ID"
3. Enter your phone number (format: +15551234567)
4. Twilio will call/text you with a verification code
5. Enter the code to verify

**Note:** Trial accounts can only call verified numbers. After verifying, you can receive calls!

### Step 4: Set Up Your `.env` File

Create `backend/.env` file:

```env
# Twilio Credentials (from Step 2)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here

# Your Twilio Phone Number (from Step 2)
TWILIO_PHONE_NUMBER=+15551234567

# Your Phone Number (the one you verified in Step 3)
POLICE_NUMBER=  # Format: +15551234567

# Base URL for webhooks (see Step 5)
BASE_URL=https://your-ngrok-url.ngrok.io
```

### Step 5: Set Up ngrok (For Local Development)

Twilio needs a public URL to send webhooks to your local server:

1. **Install ngrok:**
   ```bash
   # Mac
   brew install ngrok
   
   # Or download from: https://ngrok.com/download
   ```

2. **Start your backend:**
   ```bash
   cd backend
   python main.py
   ```

3. **In another terminal, start ngrok:**
   ```bash
   ngrok http 8000
   ```

4. **Copy the HTTPS URL:**
   - You'll see something like: `https://abc123.ngrok.io`
   - Copy this URL
   - Update `BASE_URL` in your `.env` file

### Step 6: Configure Twilio Webhook

1. Go to: Phone Numbers → Manage → Active Numbers
2. Click on your Twilio phone number
3. Scroll to "Voice & Fax" section
4. Under "A CALL COMES IN", set:
   - **Webhook URL:** `https://your-ngrok-url.ngrok.io/api/twilio/voice`
   - **HTTP Method:** `POST`
5. Click "Save"

### Step 7: Test It!

1. **Make sure backend is running:**
   ```bash
   cd backend
   python main.py
   ```

2. **Make sure ngrok is running:**
   ```bash
   ngrok http 8000
   ```

3. **Trigger a test:**
   ```bash
   curl http://localhost:8000/api/police-call/test
   ```

4. **Your phone should ring!** 📞

## Cost Breakdown

### Free Trial (What You Get)
- $15.50 free credit
- ~775 phone calls (at $0.02/call)
- ~1,550 SMS messages (at $0.01/SMS)
- Free phone number

### After Trial (If You Continue)
- Phone calls: ~$0.01-0.02 per minute
- SMS: ~$0.0075 per message
- Phone number: ~$1/month
- **Very affordable for demos!**

## Troubleshooting

### "Trial account can only call verified numbers"
- Solution: Verify your phone number in Step 3 above

### "Webhook error" or "404 Not Found"
- Solution: Make sure ngrok is running and URL in `.env` matches ngrok URL
- Update Twilio webhook URL if ngrok URL changed

### "Invalid phone number format"
- Solution: Use E.164 format: `+1XXXXXXXXXX` (include country code)

### "Call not received"
- Check Twilio console → Monitor → Logs → Calls
- Verify your number is verified
- Check ngrok is running
- Verify webhook URL is correct

## Quick Reference

**Where to find things in Twilio Console:**
- Account SID & Auth Token: Dashboard (home page)
- Phone Numbers: Phone Numbers → Manage → Active Numbers
- Verified Numbers: Phone Numbers → Manage → Verified Caller IDs
- Call Logs: Monitor → Logs → Calls
- SMS Logs: Monitor → Logs → Messages

## Security Notes

⚠️ **Never commit your `.env` file to git!**
- It contains sensitive credentials
- Add `.env` to `.gitignore`
- Use `.env.example` for sharing structure

## Next Steps

Once set up, you can:
1. Test the police calling feature
2. Test community SMS notifications
3. Customize the voice messages
4. Add more community members

Happy testing! 🚨📞

