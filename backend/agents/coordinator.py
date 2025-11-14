"""
Agent Coordinator - Manages multi-agent coordination via MCP
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import asyncio

# Import services for emergency calling and community notifications
try:
    from services.threat_analyzer import ThreatAnalyzer
    from services.twilio_service import TwilioService
    from services.community_notifier import CommunityNotifier
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False
    ThreatAnalyzer = None
    TwilioService = None
    CommunityNotifier = None

class AgentCoordinator:
    """Coordinates multiple camera agents for wildlife and wildfire detection"""
    
    def __init__(self, use_real_ai: bool = False):
        self.agents: Dict[str, 'CameraAgent'] = {}
        self.threats: List[Dict[str, Any]] = []
        self.patterns: List[Dict[str, Any]] = []
        self.cameras: List[Dict[str, Any]] = []
        self.use_real_ai = use_real_ai
        self._initialize_cameras()
        
        # Initialize services for emergency calling and notifications
        self.threat_analyzer = ThreatAnalyzer() if SERVICES_AVAILABLE and ThreatAnalyzer else None
        self.twilio_service = TwilioService() if SERVICES_AVAILABLE and TwilioService else None
        self.community_notifier = CommunityNotifier(self.twilio_service) if SERVICES_AVAILABLE and CommunityNotifier and self.twilio_service else None
        
        # Track which threats have already triggered calls/notifications
        self.notified_threats: set = set()
        
        # Track lost pets across multiple cameras
        self.lost_pet_tracking: Dict[str, List[Dict[str, Any]]] = {}  # pet_id -> list of detections
    
    def _initialize_cameras(self):
        """Initialize demo camera network"""
        # Simulated neighborhood cameras with video file paths
        camera_locations = [
            {"id": "cam_001", "lat": 37.7749, "lng": -122.4194, "address": "123 Oak St", "status": "active", "video": "cam_001.mp4"},
            {"id": "cam_002", "lat": 37.7755, "lng": -122.4200, "address": "456 Pine Ave", "status": "active", "video": "cam_002.mp4"},
            {"id": "cam_003", "lat": 37.7761, "lng": -122.4206, "address": "789 Elm Dr", "status": "active", "video": "cam_003.mp4"},
            {"id": "cam_004", "lat": 37.7743, "lng": -122.4188, "address": "321 Maple Ln", "status": "active", "video": "cam_004.mp4"},
            {"id": "cam_005", "lat": 37.7757, "lng": -122.4192, "address": "654 Cedar Rd", "status": "active", "video": "cam_005.mp4"},
        ]
        
        for cam_data in camera_locations:
            self.cameras.append({
                **cam_data,
                "last_activity": None,
                "detections": [],
                "video_url": f"http://localhost:8000/videos/{cam_data['video']}" if cam_data.get('video') else None
            })
    
    def register_agent(self, agent: 'CameraAgent'):
        """Register a new agent"""
        self.agents[agent.agent_id] = agent
    
    def get_agent_count(self) -> int:
        """Get total number of registered agents"""
        return len(self.agents)
    
    def get_all_cameras(self) -> List[Dict[str, Any]]:
        """Get all camera locations"""
        return self.cameras
    
    def get_active_threats(self) -> List[Dict[str, Any]]:
        """Get all active threats"""
        return self.threats
    
    def add_threat(self, threat: Dict[str, Any]):
        """Add a new threat detection"""
        threat["id"] = str(uuid.uuid4())
        threat["timestamp"] = datetime.now().isoformat()
        threat["status"] = "active"
        self.threats.append(threat)
        
        # Track lost pets across multiple cameras
        if threat.get("type") == "lost_pet":
            self._track_lost_pet(threat)
        
        # Analyze threat and trigger appropriate responses
        # Schedule async processing (will be handled by FastAPI event loop)
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, schedule the task
            loop.create_task(self._process_threat_response(threat))
        except RuntimeError:
            # Not in async context - process synchronously but don't block
            # This is a fallback for non-async contexts
            try:
                # Try to get existing loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._process_threat_response(threat))
                else:
                    # Run in background thread to avoid blocking
                    import threading
                    def run_async():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        new_loop.run_until_complete(self._process_threat_response(threat))
                        new_loop.close()
                    thread = threading.Thread(target=run_async, daemon=True)
                    thread.start()
            except:
                # Last resort: just skip async processing
                # Threat is still added, just won't trigger calls/notifications
                pass
    
    async def _process_threat_response(self, threat: Dict[str, Any]):
        """Process threat and trigger emergency calls/notifications if needed"""
        if not self.threat_analyzer:
            return
        
        # Check if we've already processed this threat
        threat_id = threat.get("id")
        if threat_id in self.notified_threats:
            return
        
        # Analyze the threat
        analysis = self.threat_analyzer.analyze_threat(threat)
        
        # Store analysis with threat
        threat["analysis"] = analysis
        
        # Find nearby cameras that may have also detected this
        nearby_cameras = self._find_nearby_cameras(threat.get("location", {}))
        
        # Call emergency services if needed (fire dept for wildfires, wildlife authorities for dangerous wildlife, animal control for lost pets)
        if analysis.get("should_call_police", False):
            # For lost pets, call animal control instead of police
            if analysis.get("category") == "lost_pet":
                await self._call_animal_control(threat, analysis, nearby_cameras)
            else:
                await self._call_police(threat, analysis, nearby_cameras)
            self.notified_threats.add(threat_id)
        
        # Notify community if needed
        if analysis.get("should_notify_community", False):
            await self._notify_community(threat, analysis, nearby_cameras)
            if threat_id not in self.notified_threats:
                self.notified_threats.add(threat_id)
    
    def _find_nearby_cameras(self, location: Dict[str, Any], radius_miles: float = 5.0) -> List[Dict[str, Any]]:
        """Find cameras within radius of incident"""
        if not location.get("lat") or not location.get("lng"):
            return []
        
        nearby = []
        incident_lat = location["lat"]
        incident_lng = location["lng"]
        
        for camera in self.cameras:
            cam_lat = camera.get("lat")
            cam_lng = camera.get("lng")
            
            if not cam_lat or not cam_lng:
                continue
            
            # Simple distance calculation (Haversine would be better but this is fine for demo)
            distance = self._calculate_distance(incident_lat, incident_lng, cam_lat, cam_lng)
            
            if distance <= radius_miles:
                nearby.append({
                    **camera,
                    "distance_miles": distance
                })
        
        return nearby
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in miles (simplified)"""
        import math
        R = 3959.0  # Earth radius in miles
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _track_lost_pet(self, threat: Dict[str, Any]):
        """Track lost pet across multiple cameras to detect if it's moving across streets"""
        pet_type = threat.get("details", {}).get("pet_type", "pet")
        camera_id = threat.get("camera_id")
        location = threat.get("location", {})
        
        # Create a pet ID based on type and approximate location (for tracking)
        # In a real system, you'd use more sophisticated tracking
        pet_id = f"{pet_type}_{camera_id}"
        
        if pet_id not in self.lost_pet_tracking:
            self.lost_pet_tracking[pet_id] = []
        
        # Add detection
        self.lost_pet_tracking[pet_id].append({
            "camera_id": camera_id,
            "location": location,
            "timestamp": threat.get("timestamp"),
            "threat_id": threat.get("id")
        })
        
        # Keep only last 10 detections per pet
        if len(self.lost_pet_tracking[pet_id]) > 10:
            self.lost_pet_tracking[pet_id].pop(0)
        
        # Check if pet has been detected across multiple cameras (indicating movement across streets)
        unique_cameras = set([d["camera_id"] for d in self.lost_pet_tracking[pet_id]])
        if len(unique_cameras) >= 2:
            # Pet detected across multiple cameras - definitely lost
            threat["details"]["detected_across_cameras"] = True
            threat["details"]["camera_count"] = len(unique_cameras)
            threat["details"]["is_moving_across_streets"] = True
            print(f"Lost pet {pet_type} detected across {len(unique_cameras)} cameras - moving across area")
    
    async def _call_police(
        self,
        threat: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: List[Dict[str, Any]]
    ):
        """Call emergency services with threat information (fire dept for wildfires, wildlife authorities for dangerous wildlife)"""
        if not self.twilio_service:
            print("Twilio service not available - cannot call emergency services")
            return
        
        try:
            result = self.twilio_service.call_police(threat, analysis, nearby_cameras)
            if result:
                threat["police_call"] = result
                print(f"Emergency services called for threat {threat.get('id')}: {result.get('status')}")
        except Exception as e:
            print(f"Error calling emergency services: {e}")
    
    async def _call_animal_control(
        self,
        threat: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: List[Dict[str, Any]]
    ):
        """Call animal control for lost pet detection"""
        if not self.twilio_service:
            print("Twilio service not available - cannot call animal control")
            return
        
        try:
            # Use the same call_police method but with different messaging
            result = self.twilio_service.call_police(threat, analysis, nearby_cameras)
            if result:
                threat["animal_control_call"] = result
                pet_type = threat.get("details", {}).get("pet_type", "pet")
                print(f"Animal control called for lost {pet_type} {threat.get('id')}: {result.get('status')}")
        except Exception as e:
            print(f"Error calling animal control: {e}")
    
    async def _notify_community(
        self,
        threat: Dict[str, Any],
        analysis: Dict[str, Any],
        nearby_cameras: List[Dict[str, Any]]
    ):
        """Notify community members about the threat"""
        if not self.community_notifier:
            print("Community notifier not available - cannot send notifications")
            return
        
        try:
            result = self.community_notifier.notify_community(threat, analysis, nearby_cameras)
            if result:
                threat["community_notification"] = result
                print(f"Community notified for threat {threat.get('id')}: {result.get('notified_count')} members")
        except Exception as e:
            print(f"Error notifying community: {e}")
    
    def correlate_pattern(self, detection: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Correlate detection with existing patterns"""
        # Simple pattern matching: same behavior across multiple cameras
        for pattern in self.patterns:
            if (pattern.get("behavior") == detection.get("behavior") and
                abs(pattern.get("timestamp", 0) - datetime.now().timestamp()) < 3600):
                pattern["occurrences"].append(detection)
                pattern["count"] += 1
                return pattern
        
        # Create new pattern
        new_pattern = {
            "id": str(uuid.uuid4()),
            "behavior": detection.get("behavior"),
            "occurrences": [detection],
            "count": 1,
            "timestamp": datetime.now().timestamp(),
            "predicted_next": None
        }
        self.patterns.append(new_pattern)
        return new_pattern
    
    def predict_next_target(self, pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Predict next likely target based on pattern"""
        if pattern["count"] < 2:
            return None
        
        # Simple prediction: extrapolate from movement pattern
        occurrences = pattern["occurrences"]
        if len(occurrences) >= 2:
            # Calculate direction of movement
            last = occurrences[-1]
            prev = occurrences[-2]
            
            # Find nearest camera in predicted direction
            # This is simplified - real implementation would use more sophisticated algorithms
            for camera in self.cameras:
                if camera["id"] not in [o["camera_id"] for o in occurrences]:
                    return {
                        "camera_id": camera["id"],
                        "location": {"lat": camera["lat"], "lng": camera["lng"]},
                        "confidence": min(0.9, 0.5 + (pattern["count"] * 0.1)),
                        "reasoning": f"Pattern detected: {pattern['count']} similar incidents"
                    }
        
        return None

