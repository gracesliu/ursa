# Testing the Police Calling Feature

Quick guide to test the Ursa police calling feature.

## Quick Test (No Twilio Setup Required)

### Option 1: Use the Test Endpoint

1. **Start the backend server:**
   ```bash
   cd backend
   python main.py
   ```

2. **In another terminal, trigger a test threat:**
   ```bash
   curl http://localhost:8000/api/police-call/test
   ```

3. **Check the console output** - You should see:
   - Threat analysis results
   - Simulated police call message (if Twilio not configured)
   - Community notification details

### Option 2: Start a Scenario

1. **Start the backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **In the browser (http://localhost:5173):**
   - Click "Start Scenario" in the Control Panel
   - Watch for threat detections
   - Check backend console for police call attempts

## Testing with Real Twilio (Actual Phone Calls)

### Prerequisites

1. **Get Twilio Account:**
   - Sign up at https://www.twilio.com/try-twilio
   - Get a free trial phone number
   - Get your Account SID and Auth Token from dashboard

2. **Set up ngrok (for local webhooks):**
   ```bash
   # Install ngrok: https://ngrok.com/download
   ngrok http 8000
   ```
   Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

3. **Create `.env` file in `backend/` directory:**
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=+15551234567  # Your Twilio number
   POLICE_NUMBER=+13022151083  # Your phone number (will receive calls)
   BASE_URL=https://abc123.ngrok.io  # Your ngrok URL
   ```

4. **Configure Twilio Webhook:**
   - Go to Twilio Console → Phone Numbers → Manage → Active Numbers
   - Click your Twilio number
   - Under "Voice & Fax", set webhook URL:
     ```
     https://your-ngrok-url.ngrok.io/api/twilio/voice
     ```
   - Set HTTP method to `POST`
   - Save

### Test Steps

1. **Start backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **Trigger test threat:**
   ```bash
   curl http://localhost:8000/api/police-call/test
   ```

3. **Your phone should ring!** (3022151083)
   - Answer the call
   - Listen to the AI-generated message
   - Press 1 for more information
   - Press 2 to end call

4. **Check SMS** - You should receive a text message with incident details

## Testing Different Threat Types

### Test High Severity (Will Trigger Call)

```bash
curl -X POST http://localhost:8000/api/scenarios/start?scenario_name=car_prowler
```

This creates a car prowling incident with high confidence, which should trigger a police call.

### Test Critical Severity (Always Calls)

You can modify the test endpoint or create custom threats. For now, car prowling with confidence > 0.75 will trigger calls.

## What to Look For

### In Console Output:

```
Threat Analyzer Results:
- Severity: HIGH
- Category: car_prowling
- Should call police: True
- Should notify community: True

Police called for threat <id>: queued
Community notified for threat <id>: 1 members
```

### In Phone Call:

You should hear:
- "Hello, this is Ursa security system calling to report a HIGH severity incident..."
- Incident details, location, confidence level
- Option to press 1 for more info

### In SMS:

You should receive:
```
🚨 URSA SECURITY ALERT 🚨

Incident detected: Car Prowling
Severity: HIGH
Time: [timestamp]

⚠️ Be alert: Someone may be checking vehicles in your area...
Location: [coordinates]
Multiple cameras monitoring the area.

Stay safe. Updates will be sent as the situation develops.
```

## Troubleshooting

### "Twilio not configured" message
- Check your `.env` file exists in `backend/` directory
- Verify environment variable names are correct
- Restart the server after changing `.env`

### No phone call received
- Check ngrok is running and URL is correct in `.env`
- Verify Twilio webhook URL is set correctly
- Check Twilio console for call logs
- Ensure `POLICE_NUMBER` is in E.164 format (+1XXXXXXXXXX)

### Webhook errors
- Make sure ngrok is running
- Check `BASE_URL` in `.env` matches ngrok URL
- Verify webhook endpoint is accessible: `curl https://your-ngrok-url.ngrok.io/api/twilio/voice`

### SMS not received
- Check community member is added in `community_notifier.py`
- Verify phone number is in E.164 format
- Check Twilio console for message logs
- Ensure location is within 50 miles of incident

## Manual Testing via Python

You can also test directly in Python:

```python
from agents.coordinator import AgentCoordinator
from datetime import datetime

coordinator = AgentCoordinator()

# Create a test threat
test_threat = {
    "type": "car_prowling",
    "camera_id": "cam_001",
    "location": {"lat": 37.7749, "lng": -122.4194},
    "confidence": 0.85,
    "timestamp": datetime.now().isoformat(),
    "details": {
        "description": "Test car prowling",
        "severity": "high",
        "action_required": True
    }
}

# Add threat (will trigger analysis and calls)
coordinator.add_threat(test_threat)

# Wait a moment for async processing
import time
time.sleep(2)

# Check results
threats = coordinator.get_active_threats()
if threats:
    threat = threats[-1]
    print("Analysis:", threat.get("analysis"))
    print("Police call:", threat.get("police_call"))
    print("Community notification:", threat.get("community_notification"))
```

## Next Steps

1. **Test with real scenarios** - Start the car prowler scenario and watch it trigger
2. **Add more community members** - Edit `community_notifier.py` to add test numbers
3. **Test different severities** - Modify threat confidence to test thresholds
4. **Check webhook responses** - Monitor ngrok logs to see Twilio requests

Happy testing! 🚨📞

