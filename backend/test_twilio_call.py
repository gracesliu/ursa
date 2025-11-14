#!/usr/bin/env python3
"""
Test script to directly test Twilio calling
"""

import os
from dotenv import load_dotenv
from services.twilio_service import TwilioService
from services.threat_analyzer import ThreatAnalyzer
from datetime import datetime

load_dotenv()

print("🧪 Testing Twilio Call Directly...")
print("=" * 50)

# Initialize services
twilio_service = TwilioService()
analyzer = ThreatAnalyzer()

# Create test threat
test_threat = {
    'id': 'test-123',
    'type': 'car_prowling',
    'camera_id': 'cam_001',
    'location': {'lat': 37.7749, 'lng': -122.4194},
    'confidence': 0.85,
    'timestamp': datetime.now().isoformat(),
    'details': {'description': 'Test', 'severity': 'high', 'action_required': True}
}

# Analyze
analysis = analyzer.analyze_threat(test_threat)
print(f"Analysis: should_call_police = {analysis.get('should_call_police')}")
print(f"Severity: {analysis.get('severity')}")
print()

# Check Twilio config
print("Twilio Configuration:")
print(f"  Client initialized: {twilio_service.client is not None}")
print(f"  Phone number: {twilio_service.phone_number}")
print(f"  Police number: {twilio_service.police_number}")
print(f"  Base URL: {os.getenv('BASE_URL', 'NOT SET')}")
print()

if not twilio_service.client:
    print("❌ Twilio client not initialized!")
    print("   Check your .env file for TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN")
elif not analysis.get('should_call_police'):
    print("❌ Threat analysis says don't call police")
    print(f"   Severity: {analysis.get('severity')}, Confidence: {test_threat['confidence']}")
else:
    print("✅ Attempting to make call...")
    result = twilio_service.call_police(test_threat, analysis, [])
    
    if result:
        print(f"✅ Call initiated!")
        print(f"   Status: {result.get('status')}")
        print(f"   Call SID: {result.get('call_sid', 'N/A')}")
        if result.get('status') == 'simulated':
            print("\n⚠️  This is a simulation (BASE_URL is localhost)")
            print("   Set up ngrok and update BASE_URL in .env to make real calls")
    else:
        print("❌ Call failed - check error messages above")

