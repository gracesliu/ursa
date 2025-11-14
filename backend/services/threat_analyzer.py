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
    """Threat categories based on use cases"""
    KIDNAPPING = "kidnapping"
    ASSAULT = "assault"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    BEHAVIORAL_ABNORMALITY = "behavioral_abnormality"
    FIRE = "fire"
    CAR_PROWING = "car_prowling"
    LOITERING = "loitering"
    UNKNOWN = "unknown"

class ThreatAnalyzer:
    """Analyzes threats to determine severity and appropriate response"""
    
    def __init__(self):
        self.call_threshold = 0.75  # Confidence threshold for calling police
        self.critical_activities = [
            "kidnapping",
            "assault",
            "fire",
            "violent_activity"
        ]
        self.high_severity_activities = [
            "car_prowling",
            "suspicious_movement",
            "break_in_attempt"
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
        
        # Determine if police should be called
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
        
        if "kidnap" in activity_lower or "abduction" in activity_lower:
            return ThreatCategory.KIDNAPPING
        elif "assault" in activity_lower or "attack" in activity_lower or "violence" in activity_lower:
            return ThreatCategory.ASSAULT
        elif "fire" in activity_lower or "smoke" in activity_lower:
            return ThreatCategory.FIRE
        elif "car_prowl" in activity_lower or "vehicle" in activity_lower:
            return ThreatCategory.CAR_PROWING
        elif "loiter" in activity_lower:
            return ThreatCategory.LOITERING
        elif "child" in activity_lower or "alone" in activity_lower:
            return ThreatCategory.BEHAVIORAL_ABNORMALITY
        elif "suspicious" in activity_lower:
            return ThreatCategory.SUSPICIOUS_ACTIVITY
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
        if category in [ThreatCategory.KIDNAPPING, ThreatCategory.ASSAULT, ThreatCategory.FIRE]:
            return ThreatSeverity.CRITICAL
        
        # High severity - significant risk
        if category == ThreatCategory.CAR_PROWING and confidence > 0.8:
            return ThreatSeverity.HIGH
        if category == ThreatCategory.SUSPICIOUS_ACTIVITY and confidence > 0.85:
            return ThreatSeverity.HIGH
        if category == ThreatCategory.BEHAVIORAL_ABNORMALITY and confidence > 0.75:
            return ThreatSeverity.HIGH
        
        # Medium severity - moderate risk
        if confidence > 0.7:
            return ThreatSeverity.MEDIUM
        if category == ThreatCategory.CAR_PROWING:
            return ThreatSeverity.MEDIUM
        if category == ThreatCategory.SUSPICIOUS_ACTIVITY:
            return ThreatSeverity.MEDIUM
        
        # Low severity - minor concern
        return ThreatSeverity.LOW
    
    def _should_call_police(
        self, 
        severity: ThreatSeverity, 
        confidence: float,
        category: ThreatCategory
    ) -> bool:
        """Determine if police should be called"""
        # Always call for critical threats
        if severity == ThreatSeverity.CRITICAL:
            return True
        
        # Call for high severity with high confidence
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
            actions.append("Immediate police dispatch required")
            actions.append("Alert all nearby cameras")
            actions.append("Notify community immediately")
        elif severity == ThreatSeverity.HIGH:
            actions.append("Contact police dispatch")
            actions.append("Monitor with nearby cameras")
            actions.append("Notify community")
        elif severity == ThreatSeverity.MEDIUM:
            actions.append("Monitor situation")
            actions.append("Notify community if pattern continues")
        
        if category == ThreatCategory.FIRE:
            actions.append("Contact fire department")
        elif category == ThreatCategory.BEHAVIORAL_ABNORMALITY:
            actions.append("Check for guardian presence")
            actions.append("Monitor child safety")
        
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

