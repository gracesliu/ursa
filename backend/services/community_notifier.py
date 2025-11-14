"""
Community Notifier - Sends SMS alerts to people in a 50-mile radius
"""

import math
from typing import Dict, Any, List, Optional
from services.twilio_service import TwilioService
from datetime import datetime

class CommunityNotifier:
    """Notifies community members within 50 miles of an incident"""
    
    def __init__(self, twilio_service: TwilioService):
        self.twilio_service = twilio_service
        self.notification_radius_miles = 50.0
        
        # Demo community members (in production, this would be from a database)
        # Format: {phone_number: {"lat": float, "lng": float, "name": str}}
        # Default: Add the demo user at the first camera location
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get police number (which is the demo user's number)
        police_num = os.getenv("POLICE_NUMBER", "+13022151083")
        # Ensure E.164 format
        if not police_num.startswith("+"):
            if len(police_num) == 10:
                police_num = f"+1{police_num}"
            elif len(police_num) == 11 and police_num.startswith("1"):
                police_num = f"+{police_num}"
        
        self.community_members = {
            police_num: {"lat": 37.7749, "lng": -122.4194, "name": "Demo User"},
            # Add more community members here for testing
            # "+1234567890": {"lat": 37.7750, "lng": -122.4195, "name": "Neighbor 1"},
        }
    
    def notify_community(
        self,
        threat_info: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Notify all community members within 50 miles of the incident
        
        Args:
            threat_info: Threat detection information
            analysis: Threat analysis
            nearby_cameras: Nearby cameras that detected the incident
            
        Returns:
            Notification results
        """
        incident_location = threat_info.get("location", {})
        incident_lat = incident_location.get("lat")
        incident_lng = incident_location.get("lng")
        
        if not incident_lat or not incident_lng:
            return {"error": "Invalid incident location", "notified": []}
        
        # Find community members within radius
        nearby_members = self._find_nearby_members(incident_lat, incident_lng)
        
        # Generate message
        message = self._generate_community_message(threat_info, analysis, nearby_cameras)
        
        # Send notifications
        results = []
        for phone_number, member_info in nearby_members.items():
            result = self.twilio_service.send_sms(phone_number, message)
            if result:
                results.append({
                    "phone_number": phone_number,
                    "name": member_info.get("name", "Unknown"),
                    "distance_miles": member_info.get("distance", 0),
                    "status": result.get("status", "unknown")
                })
        
        return {
            "incident_location": {"lat": incident_lat, "lng": incident_lng},
            "notified_count": len(results),
            "notified": results,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    def _find_nearby_members(
        self, 
        incident_lat: float, 
        incident_lng: float
    ) -> Dict[str, Dict[str, Any]]:
        """Find community members within notification radius"""
        nearby = {}
        
        for phone_number, member_info in self.community_members.items():
            member_lat = member_info.get("lat")
            member_lng = member_info.get("lng")
            
            if not member_lat or not member_lng:
                continue
            
            # Calculate distance using Haversine formula
            distance = self._calculate_distance(
                incident_lat, incident_lng,
                member_lat, member_lng
            )
            
            if distance <= self.notification_radius_miles:
                nearby[phone_number] = {
                    **member_info,
                    "distance": distance
                }
        
        return nearby
    
    def _calculate_distance(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calculate distance between two points using Haversine formula
        Returns distance in miles
        """
        # Earth's radius in miles
        R = 3959.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def _generate_community_message(
        self,
        threat_info: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Generate AI-generated message for community notification"""
        activity_type = threat_info.get("type", "suspicious activity")
        location = threat_info.get("location", {})
        severity = analysis.get("severity", "unknown")
        category = analysis.get("category", "unknown")
        timestamp = threat_info.get("timestamp", datetime.now().isoformat())
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%I:%M %p")
        except:
            time_str = "recently"
        
        message = f"🚨 URSA SECURITY ALERT 🚨\n\n"
        message += f"Incident detected: {activity_type.replace('_', ' ').title()}\n"
        message += f"Severity: {severity.upper()}\n"
        message += f"Time: {time_str}\n\n"
        
        # Add category-specific guidance
        if category == "car_prowling":
            message += "⚠️ Be alert: Someone may be checking vehicles in your area. "
            message += "Please check your vehicles and report any suspicious activity.\n\n"
        elif category == "suspicious_activity":
            message += "⚠️ Unusual activity detected in your neighborhood. "
            message += "Please remain vigilant and report any concerns.\n\n"
        elif category == "behavioral_abnormality":
            message += "⚠️ Behavioral concern detected. "
            message += "Please check on neighbors if safe to do so.\n\n"
        elif category == "fire":
            message += "🔥 FIRE DETECTED. Evacuate if necessary and call 911 immediately.\n\n"
        elif category in ["assault", "kidnapping"]:
            message += "🚨 CRITICAL INCIDENT. Stay indoors, lock doors, and call 911 if you see anything.\n\n"
        
        # Add location info
        if location.get("lat") and location.get("lng"):
            message += f"Location: {location['lat']:.4f}, {location['lng']:.4f}\n"
        
        # Add camera info
        if nearby_cameras and len(nearby_cameras) > 0:
            message += f"Multiple cameras monitoring the area.\n"
        
        message += "\nStay safe. Updates will be sent as the situation develops."
        
        return message
    
    def add_community_member(
        self, 
        phone_number: str, 
        lat: float, 
        lng: float, 
        name: str = "Community Member"
    ):
        """Add a community member to the notification list"""
        self.community_members[phone_number] = {
            "lat": lat,
            "lng": lng,
            "name": name
        }
    
    def get_community_members(self) -> Dict[str, Dict[str, Any]]:
        """Get all community members (for testing/admin)"""
        return self.community_members.copy()

