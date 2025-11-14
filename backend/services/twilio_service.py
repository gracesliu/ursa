"""
Twilio Service - Handles phone calls and SMS via Twilio
"""

import os
from typing import Dict, Any, Optional, List
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv
import json

load_dotenv()

class TwilioService:
    """Service for making phone calls and sending SMS via Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")  # Your Twilio number
        # Default to user's number for demo (3022151083)
        police_num = os.getenv("POLICE_NUMBER", "+13022151083")
        # Ensure E.164 format
        if not police_num.startswith("+"):
            if len(police_num) == 10:
                police_num = f"+1{police_num}"
            elif len(police_num) == 11 and police_num.startswith("1"):
                police_num = f"+{police_num}"
        self.police_number = police_num
        
        # Initialize Twilio client if credentials are available
        self.client = None
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                print("Twilio client initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize Twilio client: {e}")
        else:
            print("Warning: Twilio credentials not found. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env")
    
    def call_police(
        self, 
        threat_info: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: List[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Call the configured number (NOT actual police/911 - this is for demo purposes)
        
        NOTE: This calls POLICE_NUMBER from .env (defaults to 3022151083 for demo).
        This is YOUR number, not emergency services. In production, this would
        call a police dispatch non-emergency line or your security monitoring service.
        
        Args:
            threat_info: Original threat detection information
            analysis: Threat analysis from ThreatAnalyzer
            nearby_cameras: List of nearby cameras that also detected the incident
            
        Returns:
            Call status information or None if call failed
        """
        if not self.client:
            print("Twilio not configured - simulating call")
            return self._simulate_call(threat_info, analysis, nearby_cameras)
        
        try:
            # Generate call message
            call_message = self._generate_call_message(threat_info, analysis, nearby_cameras)
            
            # Make the call
            call = self.client.calls.create(
                to=self.police_number,
                from_=self.phone_number,
                url=f"{os.getenv('BASE_URL', 'http://localhost:8000')}/api/twilio/voice",
                method='POST',
                status_callback=f"{os.getenv('BASE_URL', 'http://localhost:8000')}/api/twilio/call-status",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method='POST'
            )
            
            print(f"Calling {self.police_number} - Call SID: {call.sid}")
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "to": self.police_number,
                "from": self.phone_number,
                "message": call_message,
                "timestamp": call.date_created.isoformat() if call.date_created else None
            }
        except Exception as e:
            print(f"Error making call: {e}")
            return None
    
    def send_sms(
        self, 
        to_number: str,
        message: str
    ) -> Optional[Dict[str, Any]]:
        """
        Send SMS message
        
        Args:
            to_number: Phone number to send to (E.164 format)
            message: Message content
            
        Returns:
            Message status or None if failed
        """
        if not self.client:
            print(f"Twilio not configured - simulating SMS to {to_number}")
            return {"status": "simulated", "to": to_number, "message": message}
        
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )
            
            return {
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "to": to_number,
                "from": self.phone_number,
                "timestamp": message_obj.date_created.isoformat() if message_obj.date_created else None
            }
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return None
    
    def _generate_call_message(
        self,
        threat_info: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Generate the message to speak during the call"""
        activity_type = threat_info.get("type", "suspicious activity")
        location = threat_info.get("location", {})
        confidence = threat_info.get("confidence", 0.0)
        severity = analysis.get("severity", "unknown")
        category = analysis.get("category", "unknown")
        
        message = f"Hello, this is Ursa security system calling to report a {severity} severity incident. "
        message += f"We have detected {activity_type.replace('_', ' ')} "
        message += f"with {confidence:.0%} confidence. "
        message += f"The incident is categorized as {category.replace('_', ' ')}. "
        
        # Add location info
        if location.get("lat") and location.get("lng"):
            message += f"Location coordinates are {location['lat']:.4f}, {location['lng']:.4f}. "
        
        # Add nearby camera info
        if nearby_cameras and len(nearby_cameras) > 0:
            message += f"We have {len(nearby_cameras)} additional cameras monitoring the area. "
        
        message += "Please advise on the appropriate response. Thank you."
        
        return message
    
    def _simulate_call(
        self,
        threat_info: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Simulate a call when Twilio is not configured"""
        message = self._generate_call_message(threat_info, analysis, nearby_cameras)
        print(f"\n{'='*60}")
        print("SIMULATED POLICE CALL")
        print(f"{'='*60}")
        print(f"To: {self.police_number}")
        print(f"Message: {message}")
        print(f"{'='*60}\n")
        
        return {
            "status": "simulated",
            "to": self.police_number,
            "message": message,
            "note": "Twilio not configured - this is a simulation"
        }
    
    def generate_voice_response(
        self,
        threat_info: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: Optional[List[Dict[str, Any]]]
    ) -> str:
        """
        Generate TwiML XML for voice response
        
        This is called by the webhook when Twilio connects the call
        """
        message = self._generate_call_message(threat_info, analysis, nearby_cameras)
        
        response = VoiceResponse()
        
        # Speak the message
        response.say(message, voice='alice', language='en-US')
        
        # Optionally gather input (press 1 for more info, etc.)
        gather = Gather(num_digits=1, timeout=10, action='/api/twilio/gather')
        gather.say("Press 1 for more information, or press 2 to end the call.", voice='alice')
        response.append(gather)
        
        # If no input, say goodbye
        response.say("Thank you for your attention. Goodbye.", voice='alice')
        response.hangup()
        
        return str(response)

