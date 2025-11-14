#!/usr/bin/env python3
"""
Quick script to verify Twilio setup
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Verifying Twilio Setup...")
print("=" * 50)

# Check credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
police_number = os.getenv("POLICE_NUMBER")
base_url = os.getenv("BASE_URL")

print(f"✅ Account SID: {account_sid[:10]}..." if account_sid else "❌ Account SID: Missing")
print(f"✅ Auth Token: {'*' * 20}..." if auth_token else "❌ Auth Token: Missing")
print(f"✅ Twilio Number: {twilio_number}" if twilio_number else "❌ Twilio Number: Missing (get from Twilio Console)")
print(f"✅ Police Number: {police_number}")
print(f"✅ Base URL: {base_url}")

print("\n" + "=" * 50)

# Test Twilio connection
if account_sid and auth_token:
    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        
        if twilio_number:
            print("\n🧪 Testing Twilio connection...")
            # Try to fetch account info
            account = client.api.accounts(account_sid).fetch()
            print(f"✅ Twilio connected! Account: {account.friendly_name}")
        else:
            print("\n⚠️  Twilio credentials OK, but phone number missing!")
            print("   Get your number from: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
    except Exception as e:
        print(f"\n❌ Twilio connection failed: {e}")
        print("   Check your credentials in .env file")
else:
    print("\n⚠️  Missing Twilio credentials in .env file")

print("\n📋 Next Steps:")
if not twilio_number:
    print("   1. Get Twilio phone number from console")
    print("   2. Add to .env: TWILIO_PHONE_NUMBER=+15551234567")
if base_url == "http://localhost:8000":
    print("   3. Set up ngrok: ngrok http 8000")
    print("   4. Update BASE_URL in .env with ngrok URL")
print("   5. Configure webhook in Twilio Console")
print("   6. Test: curl http://localhost:8000/api/police-call/test")

