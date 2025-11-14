#!/usr/bin/env python3
"""
Check Twilio call status and verify phone number
"""

import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
police_number = os.getenv("POLICE_NUMBER", "+13022151083")

if not account_sid or not auth_token:
    print("❌ Twilio credentials not found in .env")
    exit(1)

client = Client(account_sid, auth_token)

print("🔍 Checking Twilio Status...")
print("=" * 50)

# Check verified numbers
print("\n📱 Verified Phone Numbers:")
try:
    verified_numbers = client.outgoing_caller_ids.list()
    verified_numbers_list = [v.phone_number for v in verified_numbers]
    
    if police_number in verified_numbers_list:
        print(f"✅ {police_number} is VERIFIED")
    else:
        print(f"❌ {police_number} is NOT VERIFIED")
        print("\n⚠️  TRIAL ACCOUNTS CAN ONLY CALL VERIFIED NUMBERS!")
        print("\nTo verify your number:")
        print("1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
        print("2. Click 'Add a new Caller ID'")
        print(f"3. Enter: {police_number}")
        print("4. Twilio will call/text you with a verification code")
        print("5. Enter the code to verify")
except Exception as e:
    print(f"Error checking verified numbers: {e}")

# Check recent calls
print("\n📞 Recent Calls (last 5):")
try:
    calls = client.calls.list(limit=5)
    if calls:
        for call in calls:
            status_emoji = "✅" if call.status == "completed" else "⏳" if call.status in ["queued", "ringing"] else "❌"
            print(f"{status_emoji} {call.to} - Status: {call.status} - {call.date_created}")
            if call.status_message:
                print(f"   Message: {call.status_message}")
    else:
        print("No recent calls found")
except Exception as e:
    print(f"Error checking calls: {e}")

print("\n" + "=" * 50)

