# Quick Test Guide

## ✅ Everything is Set Up!

Your system is ready. Here's how to test:

### Test the Police Call Feature

```bash
curl http://localhost:8000/api/police-call/test
```

**What happens:**
1. Creates a test threat (car prowling, 85% confidence)
2. Analyzes threat → Determines HIGH severity
3. Calls your phone (configured in `.env` as `POLICE_NUMBER`)
4. When you answer, you'll hear an AI-generated message

### What You'll Hear

The call will say something like:
> "Hello, this is Ursa security system calling to report a HIGH severity incident. We have detected car prowling with 85% confidence. The incident is categorized as car prowling. Location coordinates are 37.7749, -122.4194. We have X additional cameras monitoring the area. Please advise on the appropriate response. Thank you."

Then you can:
- Press **1** for more information
- Press **2** to end the call

### Troubleshooting

**If you don't receive a call:**
- Check your phone isn't on Do Not Disturb
- Verify the number in `.env`: `POLICE_NUMBER=+15551234567` (your actual number)
- Check Twilio console for call logs: https://console.twilio.com/us1/monitor/logs/calls

**If the call doesn't have voice:**
- Make sure Twilio webhook is configured:
  - URL: `https://dissociable-perlucidus-odilia.ngrok-free.dev/api/twilio/voice`
  - Method: `POST`

### View ngrok Traffic

See all requests: http://localhost:4040

### View Twilio Logs

See call status: https://console.twilio.com/us1/monitor/logs/calls

---

**You're all set! 🎉**

