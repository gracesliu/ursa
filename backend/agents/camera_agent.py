"""
Camera Agent - Individual camera agent for threat detection
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import os

# Import video analyzer for real AI mode
try:
    import cv2
    import numpy as np
    from agents.video_analyzer import VideoAnalyzer
    AI_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    AI_AVAILABLE = False
    VideoAnalyzer = None
    cv2 = None
    np = None

class CameraAgent:
    """Individual camera agent that processes video feeds"""
    
    def __init__(self, camera_id: str, coordinator: 'AgentCoordinator', use_real_ai: bool = False):
        self.agent_id = f"agent_{camera_id}"
        self.camera_id = camera_id
        self.coordinator = coordinator
        self.status = "active"
        self.last_detection = None
        self.reasoning_log: List[Dict[str, Any]] = []
        self.use_real_ai = use_real_ai and AI_AVAILABLE
        self.video_analyzer = VideoAnalyzer() if (self.use_real_ai and VideoAnalyzer) else None
        self.previous_frame = None
    
    def process_frame(self, frame_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a video frame and detect threats"""
        if self.use_real_ai and self.video_analyzer:
            # Real AI mode: analyze actual video frame
            return self._process_frame_real_ai(frame_data)
        else:
            # Simulated mode: return None (scenarios will trigger detections)
            return None
    
    def _process_frame_real_ai(self, frame_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process frame using real AI/computer vision"""
        if not self.video_analyzer or not np:
            return None
        
        # frame_data can be a numpy array (OpenCV frame) or path to video
        if isinstance(frame_data, np.ndarray):
            # Direct frame analysis
            detection = self.video_analyzer.process_live_frame(
                frame_data, 
                self.camera_id,
                self.previous_frame
            )
            self.previous_frame = frame_data.copy()
        elif isinstance(frame_data, str) and os.path.exists(frame_data):
            # Video file path - analyze video
            detections = self.video_analyzer.analyze_video_file(
                frame_data,
                self.camera_id
            )
            detection = detections[0] if detections else None
        else:
            return None
        
        if detection:
            self.last_detection = detection
            self._log_reasoning(detection, is_real_ai=True)
            return detection
        
        return None
    
    def analyze_video_file(self, video_path: str) -> List[Dict[str, Any]]:
        """
        Analyze a video file using real AI (if enabled)
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of detections
        """
        if self.use_real_ai and self.video_analyzer and os.path.exists(video_path):
            return self.video_analyzer.analyze_video_file(video_path, self.camera_id)
        return []
    
    def detect_suspicious_activity(self, activity_type: str, confidence: float = 0.85) -> Dict[str, Any]:
        """Manually trigger a detection (used by scenarios)"""
        camera = next((c for c in self.coordinator.get_all_cameras() if c["id"] == self.camera_id), None)
        
        if not camera:
            return None
        
        detection = {
            "camera_id": self.camera_id,
            "activity_type": activity_type,
            "confidence": confidence,
            "location": {"lat": camera["lat"], "lng": camera["lng"]},
            "timestamp": datetime.now().isoformat(),
            "behavior": activity_type,
            "details": self._get_activity_details(activity_type)
        }
        
        self.last_detection = detection
        self._log_reasoning(detection)
        
        return detection
    
    def _get_activity_details(self, activity_type: str) -> Dict[str, Any]:
        """Get details for activity type"""
        details_map = {
            "car_prowling": {
                "description": "Individual checking car door handles",
                "severity": "medium",
                "action_required": True
            },
            "loitering": {
                "description": "Person loitering near vehicles",
                "severity": "low",
                "action_required": False
            },
            "suspicious_movement": {
                "description": "Unusual movement pattern detected",
                "severity": "medium",
                "action_required": True
            }
        }
        return details_map.get(activity_type, {
            "description": "Unknown activity",
            "severity": "low",
            "action_required": False
        })
    
    def _log_reasoning(self, detection: Dict[str, Any], is_real_ai: bool = False):
        """Log AI reasoning for visualization"""
        if is_real_ai and detection.get('details', {}).get('ai_metrics'):
            # Real AI reasoning with metrics
            metrics = detection['details']['ai_metrics']
            reasoning = {
                "timestamp": datetime.now().isoformat(),
                "camera_id": self.camera_id,
                "step": "ai_detection",
                "reasoning": f"AI analyzed video frame: detected {detection['activity_type']} with {detection['confidence']:.0%} confidence",
                "evidence": [
                    f"Computer vision analysis completed",
                    f"Edge density: {metrics.get('edge_density', 0):.2%}",
                    f"Motion intensity: {metrics.get('motion_intensity', 0):.2f}",
                    f"Detection method: {metrics.get('detection_method', 'unknown')}",
                    f"Confidence: {detection['confidence']:.0%}"
                ],
                "conclusion": f"AI threat identified: {detection['activity_type']}"
            }
        else:
            # Simulated reasoning
            reasoning = {
                "timestamp": datetime.now().isoformat(),
                "camera_id": self.camera_id,
                "step": "detection",
                "reasoning": f"Detected {detection['activity_type']} with {detection['confidence']:.0%} confidence",
                "evidence": [
                    f"Motion detected at {detection['location']['lat']:.4f}, {detection['location']['lng']:.4f}",
                    f"Behavior pattern matches: {detection['behavior']}",
                    f"Confidence threshold exceeded: {detection['confidence']:.0%}"
                ],
                "conclusion": f"Threat identified: {detection['activity_type']}"
            }
        
        self.reasoning_log.append(reasoning)
        return reasoning
    
    def get_reasoning_log(self) -> List[Dict[str, Any]]:
        """Get reasoning log for visualization"""
        return self.reasoning_log[-10:]  # Last 10 entries

