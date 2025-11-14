"""
AI Message Generator - Uses Anthropic Claude to generate dynamic, contextual messages
for emergency calls and community notifications
"""

import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

# Try to import Anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

class AIMessageGenerator:
    """Generates dynamic messages using AI for emergency calls and notifications"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        
        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                print("Anthropic Claude client initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {e}")
                self.client = None
        else:
            if not ANTHROPIC_AVAILABLE:
                print("Warning: Anthropic package not installed. Install with: pip install anthropic")
            if not self.api_key:
                print("Warning: ANTHROPIC_API_KEY not found in .env")
    
    def generate_call_message(
        self,
        threat_info: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate a dynamic call message using AI
        
        Args:
            threat_info: Detection information
            analysis: Threat analysis
            nearby_cameras: Nearby cameras that detected the incident
            
        Returns:
            Generated message string
        """
        if not self.client:
            # Fallback to template-based message if AI not available
            return self._generate_fallback_call_message(threat_info, analysis, nearby_cameras)
        
        try:
            # Build context for AI
            activity_type = threat_info.get("type", "detection")
            location = threat_info.get("location", {})
            confidence = threat_info.get("confidence", 0.0)
            severity = analysis.get("severity", "unknown")
            category = analysis.get("category", "unknown")
            details = threat_info.get("details", {})
            
            # Determine who we're calling
            if category == "wildfire":
                recipient = "fire department"
            elif category == "lost_pet":
                recipient = "animal control"
            elif category in ["wildlife_bear", "wildlife_coyote"]:
                recipient = "wildlife authorities"
            else:
                recipient = "emergency services"
            
            # Build prompt
            prompt = f"""You are an AI assistant for URSA, a wildlife and wildfire detection system. Generate a clear, professional voice message for a phone call to {recipient}.

Detection Details:
- Type: {activity_type.replace('_', ' ')}
- Category: {category.replace('_', ' ')}
- Severity: {severity}
- Confidence: {confidence:.0%}
- Location: {location.get('lat', 'unknown')}, {location.get('lng', 'unknown')}
"""
            
            # Add category-specific details
            if category == "wildfire":
                fire_density = details.get("ai_metrics", {}).get("fire_density", 0)
                smoke_density = details.get("ai_metrics", {}).get("smoke_density", 0)
                prompt += f"- Fire density: {fire_density:.1%}\n- Smoke density: {smoke_density:.1%}\n"
            elif category == "lost_pet":
                pet_type = details.get("pet_type", "pet")
                is_moving = details.get("is_moving_across_streets", False)
                camera_count = details.get("camera_count", 1)
                prompt += f"- Pet type: {pet_type}\n"
                if is_moving:
                    prompt += f"- Detected across {camera_count} camera locations (moving across streets)\n"
            elif category in ["wildlife_bear", "wildlife_coyote"]:
                animal_type = category.replace("wildlife_", "")
                prompt += f"- Animal type: {animal_type}\n"
            
            if nearby_cameras and len(nearby_cameras) > 0:
                prompt += f"- Additional cameras monitoring: {len(nearby_cameras)}\n"
            
            prompt += f"""
Generate a concise, professional voice message (2-3 sentences) that:
1. Identifies the system (URSA Wildlife and Wildfire Detection System)
2. Clearly states what was detected and the severity
3. Provides key details (location, confidence, specific observations)
4. Indicates the appropriate response needed
5. Is suitable for text-to-speech (clear, natural language)

Keep it under 50 words and professional. Start with "Hello, this is Ursa Wildlife and Wildfire Detection System."
"""
            
            # Call Claude
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract message from response
            if message.content and len(message.content) > 0:
                generated_text = message.content[0].text
                return generated_text.strip()
            else:
                return self._generate_fallback_call_message(threat_info, analysis, nearby_cameras)
                
        except Exception as e:
            print(f"Error generating AI message: {e}")
            return self._generate_fallback_call_message(threat_info, analysis, nearby_cameras)
    
    def generate_sms_message(
        self,
        threat_info: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate a dynamic SMS message using AI
        
        Args:
            threat_info: Detection information
            analysis: Threat analysis
            nearby_cameras: Nearby cameras that detected the incident
            
        Returns:
            Generated message string
        """
        if not self.client:
            # Fallback to template-based message if AI not available
            return self._generate_fallback_sms_message(threat_info, analysis, nearby_cameras)
        
        try:
            # Build context for AI
            activity_type = threat_info.get("type", "detection")
            location = threat_info.get("location", {})
            confidence = threat_info.get("confidence", 0.0)
            severity = analysis.get("severity", "unknown")
            category = analysis.get("category", "unknown")
            details = threat_info.get("details", {})
            timestamp = threat_info.get("timestamp", "")
            
            # Build prompt
            prompt = f"""You are an AI assistant for URSA, a wildlife and wildfire detection system. Generate a clear, concise SMS alert message for community members.

Detection Details:
- Type: {activity_type.replace('_', ' ')}
- Category: {category.replace('_', ' ')}
- Severity: {severity}
- Confidence: {confidence:.0%}
- Time: {timestamp}
- Location: {location.get('lat', 'unknown')}, {location.get('lng', 'unknown')}
"""
            
            # Add category-specific details
            if category == "wildfire":
                fire_density = details.get("ai_metrics", {}).get("fire_density", 0)
                smoke_density = details.get("ai_metrics", {}).get("smoke_density", 0)
                prompt += f"- Fire density: {fire_density:.1%}\n- Smoke density: {smoke_density:.1%}\n"
            elif category == "lost_pet":
                pet_type = details.get("pet_type", "pet")
                is_moving = details.get("is_moving_across_streets", False)
                camera_count = details.get("camera_count", 1)
                prompt += f"- Pet type: {pet_type}\n"
                if is_moving:
                    prompt += f"- Detected across {camera_count} camera locations (moving across streets)\n"
            elif category in ["wildlife_bear", "wildlife_coyote"]:
                animal_type = category.replace("wildlife_", "")
                prompt += f"- Animal type: {animal_type}\n"
            
            if nearby_cameras and len(nearby_cameras) > 0:
                prompt += f"- Additional cameras monitoring: {len(nearby_cameras)}\n"
            
            prompt += f"""
Generate a concise SMS alert message that:
1. Has a clear header: "🚨 URSA WILDLIFE & WILDFIRE ALERT 🚨"
2. States what was detected, severity, and time
3. Provides actionable guidance based on the category:
   - Wildfire: Evacuation instructions, call 911
   - Lost pet: How to help, contact animal control
   - Bear: Safety instructions, keep distance
   - Coyote: Keep pets indoors, alert authorities
   - General wildlife: Awareness and safety
4. Includes location information
5. Is under 200 characters for SMS compatibility

Use appropriate emojis and keep it urgent but clear.
"""
            
            # Call Claude
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract message from response
            if message.content and len(message.content) > 0:
                generated_text = message.content[0].text
                return generated_text.strip()
            else:
                return self._generate_fallback_sms_message(threat_info, analysis, nearby_cameras)
                
        except Exception as e:
            print(f"Error generating AI SMS message: {e}")
            return self._generate_fallback_sms_message(threat_info, analysis, nearby_cameras)
    
    def _generate_fallback_call_message(
        self,
        threat_info: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Fallback template-based message if AI is not available"""
        activity_type = threat_info.get("type", "detection")
        location = threat_info.get("location", {})
        confidence = threat_info.get("confidence", 0.0)
        severity = analysis.get("severity", "unknown")
        category = analysis.get("category", "unknown")
        
        message = f"Hello, this is Ursa Wildlife and Wildfire Detection System. "
        message += f"We have detected {activity_type.replace('_', ' ')} "
        message += f"with {severity} severity and {confidence:.0%} confidence. "
        
        if location.get("lat") and location.get("lng"):
            message += f"Location coordinates are {location['lat']:.4f}, {location['lng']:.4f}. "
        
        if nearby_cameras and len(nearby_cameras) > 0:
            message += f"We have {len(nearby_cameras)} additional cameras monitoring the area. "
        
        message += "Please advise on the appropriate response. Thank you."
        return message
    
    def _generate_fallback_sms_message(
        self,
        threat_info: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Fallback template-based SMS if AI is not available"""
        from datetime import datetime
        
        activity_type = threat_info.get("type", "detection")
        location = threat_info.get("location", {})
        severity = analysis.get("severity", "unknown")
        category = analysis.get("category", "unknown")
        timestamp = threat_info.get("timestamp", datetime.now().isoformat())
        details = threat_info.get("details", {})
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%I:%M %p")
        except:
            time_str = "recently"
        
        message = f"🚨 URSA WILDLIFE & WILDFIRE ALERT 🚨\n\n"
        message += f"Detection: {activity_type.replace('_', ' ').title()}\n"
        message += f"Severity: {severity.upper()}\n"
        message += f"Time: {time_str}\n\n"
        
        # Add category-specific guidance
        if category == "wildfire":
            message += "🔥 WILDFIRE DETECTED. Evacuate if necessary and call 911 immediately.\n\n"
        elif category == "lost_pet":
            pet_type = details.get("pet_type", "pet")
            message += f"🐾 LOST PET ALERT: {pet_type.title()} detected without owner nearby.\n\n"
        elif category == "wildlife_bear":
            message += "🐻 BEAR DETECTED. Keep distance and alert wildlife authorities.\n\n"
        elif category == "wildlife_coyote":
            message += "🐺 COYOTE DETECTED. Keep pets indoors.\n\n"
        
        if location.get("lat") and location.get("lng"):
            message += f"Location: {location['lat']:.4f}, {location['lng']:.4f}\n"
        
        return message
