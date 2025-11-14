"""
Threat Severity Analyzer - Determines threat severity and appropriate response
"""

from typing import Dict, Any, Optional
from datetime import datetime
import enum

class ThreatSeverity(enum.Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatCategory(enum.Enum):
    """Threat categories for wildlife and wildfire detection"""
    WILDFIRE = "wildfire"
    WILDLIFE = "wildlife"
    WILDLIFE_BEAR = "wildlife_bear"
    WILDLIFE_DEER = "wildlife_deer"
    WILDLIFE_COYOTE = "wildlife_coyote"
    WILDLIFE_DETECTED = "wildlife_detected"
    LOST_PET = "lost_pet"
    UNKNOWN = "unknown"

class ThreatAnalyzer:
    """Analyzes threats to determine severity and appropriate response"""
    
    def __init__(self):
        self.call_threshold = 0.75  # Confidence threshold for calling emergency services
        self.critical_activities = [
            "wildfire",
            "fire"
        ]
        self.high_severity_activities = [
            "wildlife_bear",
            "wildlife_coyote",
            "wildlife_detected"
        ]
        self.lost_pet_activities = [
            "lost_pet"
        ]
    
    def analyze_threat(self, threat: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a threat and determine severity, category, and response
        
        Args:
            threat: Threat dictionary with detection information
            
        Returns:
            Analysis dict with severity, category, should_call_police, etc.
        """
        activity_type = threat.get("type", "").lower()
        confidence = threat.get("confidence", 0.0)
        details = threat.get("details", {})
        
        # Determine threat category
        category = self._categorize_threat(activity_type, details)
        
        # Determine severity
        severity = self._determine_severity(activity_type, confidence, details, category)
        
        # Determine if emergency services should be called
        should_call_police = self._should_call_police(severity, confidence, category)
        
        # Determine if community should be notified
        should_notify_community = self._should_notify_community(severity, category)
        
        # Generate response summary
        response_summary = self._generate_response_summary(threat, severity, category)
        
        return {
            "threat_id": threat.get("id"),
            "severity": severity.value,
            "category": category.value,
            "confidence": confidence,
            "should_call_police": should_call_police,
            "should_notify_community": should_notify_community,
            "priority": self._get_priority(severity),
            "response_summary": response_summary,
            "recommended_actions": self._get_recommended_actions(severity, category),
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _categorize_threat(self, activity_type: str, details: Dict[str, Any]) -> ThreatCategory:
        """Categorize threat based on activity type"""
        activity_lower = activity_type.lower()
        
        if "wildfire" in activity_lower or "fire" in activity_lower or "smoke" in activity_lower:
            return ThreatCategory.WILDFIRE
        elif "wildlife_bear" in activity_lower or "bear" in activity_lower:
            return ThreatCategory.WILDLIFE_BEAR
        elif "wildlife_coyote" in activity_lower or "coyote" in activity_lower:
            return ThreatCategory.WILDLIFE_COYOTE
        elif "wildlife_deer" in activity_lower or "deer" in activity_lower:
            return ThreatCategory.WILDLIFE_DEER
        elif "lost_pet" in activity_lower or "lost pet" in activity_lower:
            return ThreatCategory.LOST_PET
        elif "wildlife" in activity_lower:
            return ThreatCategory.WILDLIFE
        else:
            return ThreatCategory.UNKNOWN
    
    def _determine_severity(
        self, 
        activity_type: str, 
        confidence: float, 
        details: Dict[str, Any],
        category: ThreatCategory
    ) -> ThreatSeverity:
        """Determine threat severity level"""
        activity_lower = activity_type.lower()
        
        # Critical threats - immediate danger
        if category == ThreatCategory.WILDFIRE:
            return ThreatSeverity.CRITICAL
        
        # High severity - significant risk (dangerous wildlife)
        if category == ThreatCategory.WILDLIFE_BEAR and confidence > 0.7:
            return ThreatSeverity.HIGH
        if category == ThreatCategory.WILDLIFE_COYOTE and confidence > 0.7:
            return ThreatSeverity.HIGH
        if category == ThreatCategory.WILDLIFE and confidence > 0.8:
            return ThreatSeverity.HIGH
        
        # Medium severity - moderate risk (lost pets)
        if category == ThreatCategory.LOST_PET:
            return ThreatSeverity.MEDIUM
        if confidence > 0.7:
            return ThreatSeverity.MEDIUM
        if category in [ThreatCategory.WILDLIFE, ThreatCategory.WILDLIFE_DEER]:
            return ThreatSeverity.MEDIUM
        
        # Low severity - minor concern
        return ThreatSeverity.LOW
    
    def _should_call_police(
        self, 
        severity: ThreatSeverity, 
        confidence: float,
        category: ThreatCategory
    ) -> bool:
        """Determine if emergency services should be called (fire dept for wildfires, wildlife authorities for dangerous wildlife, animal control for lost pets)"""
        # Always call for critical threats (wildfires)
        if severity == ThreatSeverity.CRITICAL:
            return True
        
        # Call animal control for lost pets (medium confidence threshold)
        if category == ThreatCategory.LOST_PET and confidence >= 0.7:
            return True
        
        # Call for high severity with high confidence (dangerous wildlife like bears)
        if severity == ThreatSeverity.HIGH and confidence >= self.call_threshold:
            return True
        
        # Call for medium severity with very high confidence
        if severity == ThreatSeverity.MEDIUM and confidence >= 0.9:
            return True
        
        return False
    
    def _should_notify_community(
        self, 
        severity: ThreatSeverity,
        category: ThreatCategory
    ) -> bool:
        """Determine if community should be notified"""
        # Notify for medium and above
        if severity in [ThreatSeverity.MEDIUM, ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]:
            return True
        
        # Always notify for lost pets (to help find owner)
        if category == ThreatCategory.LOST_PET:
            return True
        
        # Always notify for behavioral abnormalities (child alone, etc.)
        if category == ThreatCategory.BEHAVIORAL_ABNORMALITY:
            return True
        
        return False
    
    def _get_priority(self, severity: ThreatSeverity) -> int:
        """Get priority level (1-10, higher = more urgent)"""
        priority_map = {
            ThreatSeverity.CRITICAL: 10,
            ThreatSeverity.HIGH: 7,
            ThreatSeverity.MEDIUM: 5,
            ThreatSeverity.LOW: 2
        }
        return priority_map.get(severity, 1)
    
    def _get_recommended_actions(
        self, 
        severity: ThreatSeverity,
        category: ThreatCategory
    ) -> list:
        """Get recommended actions based on severity and category"""
        actions = []
        
        if severity == ThreatSeverity.CRITICAL:
            actions.append("Immediate fire department dispatch required")
            actions.append("Alert all nearby cameras")
            actions.append("Notify community immediately")
        elif severity == ThreatSeverity.HIGH:
            actions.append("Contact wildlife authorities or fire department")
            actions.append("Monitor with nearby cameras")
            actions.append("Notify community")
        elif severity == ThreatSeverity.MEDIUM:
            actions.append("Monitor situation")
            actions.append("Notify community if pattern continues")
        
        if category == ThreatCategory.WILDFIRE:
            actions.append("Contact fire department immediately")
            actions.append("Alert nearby residents")
        elif category == ThreatCategory.WILDLIFE_BEAR:
            actions.append("Alert wildlife authorities")
            actions.append("Warn nearby residents")
        elif category == ThreatCategory.WILDLIFE_COYOTE:
            actions.append("Alert wildlife authorities")
            actions.append("Monitor situation")
        elif category == ThreatCategory.LOST_PET:
            actions.append("Contact animal control")
            actions.append("Notify nearby residents")
            actions.append("Monitor pet movement across cameras")
        
        return actions
    
    def _generate_response_summary(
        self, 
        threat: Dict[str, Any],
        severity: ThreatSeverity,
        category: ThreatCategory
    ) -> str:
        """Generate a summary of the threat for communication"""
        activity_type = threat.get("type", "unknown activity")
        location = threat.get("location", {})
        confidence = threat.get("confidence", 0.0)
        timestamp = threat.get("timestamp", datetime.now().isoformat())
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%I:%M %p on %B %d")
        except:
            time_str = timestamp
        
        summary = f"Detected {activity_type.replace('_', ' ')} "
        summary += f"at {location.get('lat', 'unknown')}, {location.get('lng', 'unknown')} "
        summary += f"at {time_str}. "
        summary += f"Confidence: {confidence:.0%}. "
        summary += f"Severity: {severity.value.upper()}. "
        
        if category != ThreatCategory.UNKNOWN:
            summary += f"Category: {category.value.replace('_', ' ')}. "
        
        return summary

