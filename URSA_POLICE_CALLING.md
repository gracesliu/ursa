# Ursa Police Calling Feature

This document describes the police calling and community notification features implemented for Ursa.

## Overview

Ursa now includes an AI-powered system that:
1. **Analyzes threat severity** to determine when police should be called
2. **Calls your demo number** (NOT actual police/911) with AI-generated voice messages
3. **Notifies community members** within a 50-mile radius via SMS
4. **Gathers information** from nearby cameras in the network

**⚠️ IMPORTANT: This system calls YOUR phone number (3022151083) for demo purposes. It does NOT call 911 or actual emergency services.**

## Features

### 1. Threat Severity Analyzer

The `ThreatAnalyzer` class evaluates threats and determines:
- **Severity levels**: LOW, MEDIUM, HIGH, CRITICAL
- **Threat categories**: Kidnapping, Assault, Fire, Car Prowling, Suspicious Activity, Behavioral Abnormality
- **Whether to call police**: Based on severity and confidence thresholds
- **Whether to notify community**: For medium+ severity threats

### 2. Twilio Integration

#### Phone Calls
- Uses Twilio's voice API to make calls
- AI-generated voice messages describe the incident
- Interactive voice response (IVR) allows dispatchers to:
  - Press 1 for more information
  - Press 2 to end the call

#### SMS Notifications
- Sends AI-generated text messages to community members
- Includes incident details, location, and safety guidance
- Only notifies people within 50 miles of the incident

### 3. Community Notifier

- Finds community members within 50-mile radius using Haversine formula
- Sends personalized SMS alerts with:
  - Incident type and severity
  - Location coordinates
  - Category-specific safety guidance
  - Updates from nearby cameras

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Twilio

Create a `.env` file in the `backend/` directory:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890  # Your Twilio phone number

# Police/Demo Number (your number for testing)
POLICE_NUMBER=  # Format: +1 followed by 10 digits (e.g., +15551234567)

# Base URL for Twilio webhooks (use ngrok for local dev)
BASE_URL=http://localhost:8000
```

### 3. Get Twilio Credentials

1. Sign up at https://www.twilio.com/
2. Get your Account SID and Auth Token from the dashboard
3. Get a phone number from Twilio (for making calls and sending SMS)
4. For local development, use ngrok to expose your server:
   ```bash
   ngrok http 8000
   ```
   Then set `BASE_URL` in `.env` to your ngrok URL

### 4. Add Community Members

Edit `backend/services/community_notifier.py` to add community members:

```python
self.community_members = {
    "+15551234567": {"lat": 37.7749, "lng": -122.4194, "name": "Your Name"},
    # Add more members here
}
```

## How It Works

### Threat Detection Flow

1. **Camera detects incident** → Threat is added to coordinator
2. **Threat Analyzer evaluates** → Determines severity and category
3. **If high severity** → Police is called automatically
4. **If medium+ severity** → Community is notified via SMS
5. **Nearby cameras** → Information is gathered from cameras within 5 miles

### Police Call Flow

1. System calls `POLICE_NUMBER` (your number for demo - **NOT 911 or emergency services**)
2. Twilio connects to `/api/twilio/voice` webhook
3. AI-generated message is spoken:
   - Incident type and severity
   - Location coordinates
   - Confidence level
   - Nearby camera information
4. You can press 1 for more info or 2 to end (simulating dispatcher interaction)

### Community Notification Flow

1. System finds all community members within 50 miles
2. Calculates distance using Haversine formula
3. Sends SMS to each member with:
   - Incident alert
   - Safety guidance based on category
   - Location information
   - Camera monitoring status

## API Endpoints

### Test Police Call
```bash
GET http://localhost:8000/api/police-call/test
```
Creates a test threat and triggers police call (if severity is high enough)

### Twilio Webhooks
- `POST /api/twilio/voice` - Handles incoming call, generates TwiML
- `POST /api/twilio/gather` - Handles user input during call
- `POST /api/twilio/call-status` - Receives call status updates

## Threat Severity Thresholds

### Police Call Triggers
- **CRITICAL** threats: Always call
- **HIGH** severity + confidence ≥ 75%: Call
- **MEDIUM** severity + confidence ≥ 90%: Call

### Community Notification Triggers
- **MEDIUM, HIGH, CRITICAL** severity: Always notify
- **Behavioral abnormalities**: Always notify (e.g., child alone)

## Use Cases Supported

✅ **Kidnapping** - CRITICAL, immediate police call
✅ **Assault** - CRITICAL, immediate police call  
✅ **Fire** - CRITICAL, immediate police call
✅ **Car Prowling** - HIGH/MEDIUM, police call if confidence ≥ 75%
✅ **Suspicious Activity** - HIGH/MEDIUM, police call if confidence ≥ 75%
✅ **Behavioral Abnormalities** - HIGH/MEDIUM, community notification

## Demo Mode

If Twilio credentials are not configured, the system will:
- **Simulate calls** - Print call information to console
- **Simulate SMS** - Print SMS content to console
- Still perform threat analysis and severity determination

This allows testing the logic without Twilio setup.

## Notes

- The system prevents duplicate calls/notifications for the same threat
- Phone numbers must be in E.164 format (+1XXXXXXXXXX)
- For production, use a proper database for community members
- Consider rate limiting for SMS notifications
- Webhook URLs must be publicly accessible (use ngrok for local dev)

## Future Enhancements

- [ ] AI voice agent that can have conversations with dispatchers
- [ ] Real-time updates to community as situation develops
- [ ] Integration with emergency services APIs
- [ ] Multi-language support for community notifications
- [ ] Incident documentation website (optional feature)

