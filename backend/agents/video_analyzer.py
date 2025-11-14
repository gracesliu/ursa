"""
Video Analyzer - Real AI video analysis using computer vision + YOLO object detection
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import os

# Try to import YOLO - optional dependency
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    YOLO = None

class VideoAnalyzer:
    """Analyzes video frames using computer vision + YOLO object detection for threat detection"""
    
    def __init__(self):
        self.detection_history: List[Dict[str, Any]] = []
        self.frame_buffer: List[np.ndarray] = []  # Store recent frames for temporal analysis
        self.motion_history: List[float] = []  # Track motion over time
        self.activity_duration = 0  # How long activity has been detected
        self.object_history: List[Dict[str, Any]] = []  # Track detected objects over time
        
        # Initialize YOLO model if available
        self.yolo_model = None
        if YOLO_AVAILABLE:
            try:
                # Load pretrained YOLOv8 model (automatically downloads if needed)
                self.yolo_model = YOLO('yolov8n.pt')  # nano version for speed, can use 'yolov8s.pt' or 'yolov8m.pt' for better accuracy
                print("YOLO model loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load YOLO model: {e}")
                self.yolo_model = None
        else:
            print("YOLO not available - install with: pip install ultralytics")
    
    def analyze_frame(self, frame: np.ndarray, camera_id: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a single video frame for suspicious activity using YOLO + motion detection
        
        Args:
            frame: OpenCV frame (numpy array, BGR format)
            camera_id: ID of the camera
            
        Returns:
            Detection dict if threat found, None otherwise
        """
        # Convert to grayscale for processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Get previous frame for motion analysis
        previous = self.frame_buffer[-2] if len(self.frame_buffer) >= 2 else None
        
        # Step 1: Object detection with YOLO (if available)
        detected_objects = self._detect_objects(frame) if self.yolo_model else None
        
        # Step 2: Motion analysis
        motion_data = self._analyze_motion(gray, previous) if previous is not None else (0.0, 0.0)
        
        # Step 3: Combined suspicious activity detection
        detection = self._detect_suspicious_activity_combined(
            gray, camera_id, previous, detected_objects, motion_data
        )
        
        return detection
    
    def _detect_objects(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Detect objects in frame using YOLO
        
        Returns:
            Dict with detected objects, their classes, and positions
        """
        if not self.yolo_model:
            return {"objects": [], "people": [], "vehicles": [], "count": 0}
        
        try:
            # Run YOLO inference
            results = self.yolo_model(frame, verbose=False)
            
            # Parse results
            detected_objects = []
            people = []
            vehicles = []
            
            # Classes we care about for security
            person_class_id = 0  # COCO class 0 = person
            vehicle_class_ids = [2, 3, 5, 7]  # car, motorcycle, bus, truck
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get class and confidence
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    class_name = result.names[cls]
                    
                    obj_data = {
                        "class_id": cls,
                        "class_name": class_name,
                        "confidence": conf,
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "center": [float((x1 + x2) / 2), float((y1 + y2) / 2)],
                        "area": float((x2 - x1) * (y2 - y1))
                    }
                    
                    detected_objects.append(obj_data)
                    
                    # Categorize
                    if cls == person_class_id and conf > 0.5:
                        people.append(obj_data)
                    elif cls in vehicle_class_ids and conf > 0.5:
                        vehicles.append(obj_data)
            
            # Store in history for temporal analysis
            self.object_history.append({
                "timestamp": datetime.now().isoformat(),
                "people": people,
                "vehicles": vehicles,
                "all_objects": detected_objects
            })
            if len(self.object_history) > 30:  # Keep last 30 frames
                self.object_history.pop(0)
            
            return {
                "objects": detected_objects,
                "people": people,
                "vehicles": vehicles,
                "count": len(detected_objects),
                "people_count": len(people),
                "vehicles_count": len(vehicles)
            }
        except Exception as e:
            print(f"YOLO detection error: {e}")
            return {"objects": [], "people": [], "vehicles": [], "count": 0}
    
    def _detect_suspicious_activity_combined(
        self, gray_frame: np.ndarray, camera_id: str, 
        previous_frame: Optional[np.ndarray], 
        detected_objects: Optional[Dict[str, Any]],
        motion_data: Tuple[float, float]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect suspicious activity using combined YOLO object detection + motion analysis
        
        Uses holistic approach:
        - YOLO object detection (people, vehicles)
        - Motion analysis (speed, consistency)
        - Temporal analysis (persistent patterns)
        - Behavioral analysis (object interactions)
        """
        # Store frame for temporal analysis
        self.frame_buffer.append(gray_frame.copy())
        if len(self.frame_buffer) > 10:  # Keep last 10 frames
            self.frame_buffer.pop(0)
        
        # Calculate frame statistics
        mean_intensity = np.mean(gray_frame)
        std_intensity = np.std(gray_frame)
        
        # Edge detection for movement
        edges = cv2.Canny(gray_frame, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Motion analysis
        motion_speed, motion_consistency = motion_data
        
        # Temporal analysis - check if activity is persistent
        self.motion_history.append(edge_density)
        if len(self.motion_history) > 30:  # Last 30 frames
            self.motion_history.pop(0)
        
        # Calculate activity metrics
        persistent_activity = self._check_persistent_activity()
        movement_pattern = self._analyze_movement_pattern()
        
        # Object-based analysis (if YOLO available)
        object_analysis = self._analyze_objects(detected_objects) if detected_objects else {}
        
        # Combined suspicious score with object detection
        suspicious_score = self._calculate_suspicious_score_combined(
            edge_density, std_intensity, motion_speed, 
            motion_consistency, persistent_activity, movement_pattern,
            object_analysis
        )
        
        # Only trigger if score exceeds threshold
        if suspicious_score > 0.60:  # Slightly lower threshold since we have better data
            activity_type = self._classify_activity_with_objects(
                gray_frame, edge_density, std_intensity, 
                motion_speed, persistent_activity, movement_pattern,
                object_analysis
            )
            
            if activity_type:
                # Confidence based on multiple factors including object detection
                confidence = min(0.95, suspicious_score)
                
                # Build description with object info
                description = f"AI detected {activity_type}"
                if object_analysis.get("people_near_vehicles"):
                    description += f" - Person detected near vehicle"
                elif object_analysis.get("people_count", 0) > 0:
                    description += f" - {object_analysis['people_count']} person(s) detected"
                
                return {
                    "camera_id": camera_id,
                    "activity_type": activity_type,
                    "confidence": float(confidence),
                    "timestamp": datetime.now().isoformat(),
                    "behavior": activity_type,
                    "details": {
                        "description": description + " via computer vision + object detection",
                        "severity": "medium" if confidence > 0.7 else "low",
                        "action_required": confidence > 0.7,
                        "ai_metrics": {
                            "edge_density": float(edge_density),
                            "motion_intensity": float(std_intensity),
                            "motion_speed": float(motion_speed),
                            "motion_consistency": float(motion_consistency),
                            "persistent_activity": persistent_activity,
                            "suspicious_score": float(suspicious_score),
                            "detection_method": "yolo_motion_combined" if self.yolo_model else "motion_analysis",
                            "objects_detected": object_analysis.get("people_count", 0) + object_analysis.get("vehicles_count", 0),
                            "people_count": object_analysis.get("people_count", 0),
                            "vehicles_count": object_analysis.get("vehicles_count", 0),
                            "people_near_vehicles": object_analysis.get("people_near_vehicles", False)
                        }
                    }
                }
        
        return None
    
    def _analyze_objects(self, detected_objects: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze detected objects for suspicious patterns
        
        Returns analysis of object positions, interactions, and behaviors
        """
        if not detected_objects or detected_objects.get("count", 0) == 0:
            return {
                "people_count": 0,
                "vehicles_count": 0,
                "people_near_vehicles": False,
                "loitering_detected": False
            }
        
        people = detected_objects.get("people", [])
        vehicles = detected_objects.get("vehicles", [])
        
        # Check if people are near vehicles (car prowling indicator)
        people_near_vehicles = False
        if people and vehicles:
            for person in people:
                person_center = person["center"]
                for vehicle in vehicles:
                    vehicle_bbox = vehicle["bbox"]
                    # Check if person center is near vehicle bbox
                    if (vehicle_bbox[0] - 50 < person_center[0] < vehicle_bbox[2] + 50 and
                        vehicle_bbox[1] - 50 < person_center[1] < vehicle_bbox[3] + 50):
                        people_near_vehicles = True
                        break
                if people_near_vehicles:
                    break
        
        # Check for loitering (person detected in same area over time)
        loitering_detected = False
        if len(self.object_history) >= 10 and people:
            # Check if person has been in similar location for multiple frames
            recent_people_positions = []
            for hist in self.object_history[-10:]:
                if hist.get("people"):
                    for p in hist["people"]:
                        recent_people_positions.append(p["center"])
            
            if len(recent_people_positions) >= 5:
                # Calculate position variance
                positions = np.array(recent_people_positions)
                position_variance = np.var(positions, axis=0).sum()
                if position_variance < 10000:  # Low variance = person staying in same area
                    loitering_detected = True
        
        return {
            "people_count": len(people),
            "vehicles_count": len(vehicles),
            "people_near_vehicles": people_near_vehicles,
            "loitering_detected": loitering_detected,
            "has_people": len(people) > 0,
            "has_vehicles": len(vehicles) > 0
        }
    
    def _analyze_motion(self, current_frame: np.ndarray, previous_frame: Optional[np.ndarray]) -> Tuple[float, float]:
        """
        Analyze motion between frames
        
        Returns:
            (motion_speed, motion_consistency)
            - motion_speed: How fast objects are moving (0-1)
            - motion_consistency: How consistent the motion is (0-1)
        """
        if previous_frame is None:
            return (0.0, 0.0)
        
        return self._analyze_motion_impl(current_frame, previous_frame)
    
    def _analyze_motion_impl(self, current_frame: np.ndarray, previous_frame: np.ndarray) -> Tuple[float, float]:
        """
        Analyze motion between frames
        
        Returns:
            (motion_speed, motion_consistency)
            - motion_speed: How fast objects are moving (0-1)
            - motion_consistency: How consistent the motion is (0-1)
        """
        # Frame differencing
        diff = cv2.absdiff(current_frame, previous_frame)
        motion_mask = diff > 30  # Threshold for motion
        
        # Motion speed: percentage of frame with motion
        motion_speed = np.sum(motion_mask) / (motion_mask.shape[0] * motion_mask.shape[1])
        
        # Motion consistency: check if motion is in a concentrated area (object) vs scattered (noise)
        if motion_speed > 0.01:  # If there's any motion
            # Find contours of motion
            contours, _ = cv2.findContours(motion_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                # Largest motion area
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                total_motion_area = np.sum(motion_mask)
                # Consistency: how much motion is in the largest object vs total
                motion_consistency = area / total_motion_area if total_motion_area > 0 else 0
            else:
                motion_consistency = 0
        else:
            motion_consistency = 0
        
        return float(motion_speed), float(motion_consistency)
    
    def _check_persistent_activity(self) -> float:
        """
        Check if activity has been persistent over time (reduces false positives from brief events)
        
        Returns:
            Persistence score (0-1): Higher = more persistent activity
        """
        if len(self.motion_history) < 5:
            return 0.0
        
        # Check if activity has been consistent over recent frames
        recent_activity = self.motion_history[-10:] if len(self.motion_history) >= 10 else self.motion_history
        avg_activity = np.mean(recent_activity)
        
        # Activity is persistent if consistently above threshold
        threshold = 0.08
        persistent_frames = sum(1 for a in recent_activity if a > threshold)
        persistence_ratio = persistent_frames / len(recent_activity)
        
        return float(persistence_ratio)
    
    def _analyze_movement_pattern(self) -> str:
        """
        Analyze the pattern of movement over time
        
        Returns:
            Pattern type: "slow_deliberate", "fast_movement", "erratic", "static"
        """
        if len(self.motion_history) < 5:
            return "static"
        
        recent = self.motion_history[-10:] if len(self.motion_history) >= 10 else self.motion_history
        avg = np.mean(recent)
        std = np.std(recent)
        
        if avg < 0.05:
            return "static"
        elif std < 0.02 and 0.08 < avg < 0.15:
            return "slow_deliberate"  # Consistent, moderate activity
        elif avg > 0.15:
            return "fast_movement"
        elif std > 0.03:
            return "erratic"
        else:
            return "moderate"
    
    def _calculate_suspicious_score_combined(
        self, edge_density: float, std_intensity: float, 
        motion_speed: float, motion_consistency: float,
        persistent_activity: float, movement_pattern: str,
        object_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate suspicious activity score using multiple factors + object detection
        
        Higher score = more suspicious. Threshold: 0.60
        """
        score = 0.0
        
        # Factor 1: Edge density (but not too high - very high = noise)
        if 0.10 < edge_density < 0.25:  # Sweet spot
            score += 0.12
        elif edge_density > 0.25:  # Too high = likely noise
            score += 0.03  # Penalty for excessive activity
        
        # Factor 2: Motion consistency (concentrated motion = object, scattered = noise)
        if motion_consistency > 0.3:  # Motion is concentrated (likely an object)
            score += 0.15
        elif motion_consistency < 0.1:  # Scattered motion (likely noise)
            score -= 0.10  # Penalty
        
        # Factor 3: Motion speed (slow, deliberate movement is more suspicious)
        if 0.02 < motion_speed < 0.10:  # Moderate speed
            score += 0.12
        elif motion_speed > 0.15:  # Too fast = likely normal traffic
            score -= 0.10  # Penalty
        
        # Factor 4: Persistent activity (reduces false positives from brief events)
        if persistent_activity > 0.6:  # Activity for 60%+ of recent frames
            score += 0.20
        elif persistent_activity < 0.3:  # Brief activity
            score -= 0.15  # Penalty
        
        # Factor 5: Movement pattern
        if movement_pattern == "slow_deliberate":
            score += 0.15  # Most suspicious
        elif movement_pattern == "fast_movement":
            score -= 0.10  # Less suspicious (normal traffic)
        elif movement_pattern == "erratic":
            score += 0.08  # Somewhat suspicious
        
        # Factor 6: Intensity variation (but not too high)
        if 30 < std_intensity < 80:  # Moderate variation
            score += 0.08
        elif std_intensity > 100:  # Too high = likely lighting changes
            score -= 0.10
        
        # Factor 7: Object Detection (NEW - most important!)
        if object_analysis.get("people_near_vehicles"):
            score += 0.30  # Strong indicator of car prowling
        elif object_analysis.get("loitering_detected"):
            score += 0.25  # Person staying in same area
        elif object_analysis.get("people_count", 0) > 0:
            # Person detected but not near vehicle
            if motion_speed > 0.02:  # Person is moving
                score += 0.15
            else:  # Person stationary
                score += 0.10
        elif object_analysis.get("has_people", False):
            score += 0.08  # Person detected but low confidence
        
        # If no objects detected but high motion, reduce score (likely false positive)
        if not object_analysis.get("has_people", False) and motion_speed > 0.1:
            score -= 0.15  # High motion but no person = likely noise
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
    
    def _classify_activity_with_objects(
        self, gray_frame: np.ndarray, edge_density: float, 
        std_intensity: float, motion_speed: float,
        persistent_activity: float, movement_pattern: str,
        object_analysis: Dict[str, Any]
    ) -> Optional[str]:
        """
        Improved activity classification using object detection + motion analysis
        
        Uses YOLO detections to make more accurate classifications
        """
        people_near_vehicles = object_analysis.get("people_near_vehicles", False)
        loitering_detected = object_analysis.get("loitering_detected", False)
        has_people = object_analysis.get("has_people", False)
        
        # Car prowling: Person detected near vehicle with suspicious movement
        if people_near_vehicles:
            if (movement_pattern == "slow_deliberate" or 
                (0.02 < motion_speed < 0.10 and persistent_activity > 0.4)):
                return "car_prowling"
            elif persistent_activity > 0.5:
                return "car_prowling"  # Person near vehicle for extended time
        
        # Loitering: Person detected staying in same area
        if loitering_detected and has_people:
            return "loitering"
        
        # Suspicious movement: Person detected with suspicious motion patterns
        if has_people:
            if (movement_pattern in ["slow_deliberate", "erratic"] and
                persistent_activity > 0.5):
                return "suspicious_movement"
            elif (0.10 < edge_density < 0.20 and 
                  persistent_activity > 0.6):
                return "suspicious_movement"
        
        # Fallback to motion-only classification if no objects detected
        # (for cases where YOLO misses detection but motion is clear)
        if not has_people:
            if (movement_pattern == "slow_deliberate" and 
                0.10 < edge_density < 0.20 and 
                0.02 < motion_speed < 0.08 and
                persistent_activity > 0.6):
                return "suspicious_movement"
            elif (persistent_activity > 0.7 and
                  0.08 < edge_density < 0.15 and
                  motion_speed < 0.05):
                return "loitering"
        
        return None
    
    def analyze_video_file(self, video_path: str, camera_id: str, sample_rate: int = 30) -> List[Dict[str, Any]]:
        """
        Analyze a video file frame by frame
        
        Args:
            video_path: Path to video file
            camera_id: ID of the camera
            sample_rate: Analyze every Nth frame (default: every 30th frame = ~1 per second at 30fps)
            
        Returns:
            List of detections found in the video
        """
        if not os.path.exists(video_path):
            return []
        
        detections = []
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        
        if not cap.isOpened():
            return []
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames (don't analyze every single frame)
                if frame_count % sample_rate == 0:
                    detection = self.analyze_frame(frame, camera_id)
                    if detection:
                        detections.append(detection)
                
                frame_count += 1
        finally:
            cap.release()
        
        return detections
    
    def process_live_frame(self, frame: np.ndarray, camera_id: str, previous_frame: Optional[np.ndarray] = None) -> Optional[Dict[str, Any]]:
        """
        Process a frame for live video analysis with frame differencing
        
        Args:
            frame: Current frame
            camera_id: Camera ID
            previous_frame: Previous frame for motion detection
            
        Returns:
            Detection if found
        """
        if previous_frame is not None:
            # Frame differencing for motion detection
            diff = cv2.absdiff(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 
                              cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY))
            motion = np.sum(diff > 30) / (diff.shape[0] * diff.shape[1])
            
            if motion > 0.05:  # Significant motion detected
                return self.analyze_frame(frame, camera_id)
        
        return self.analyze_frame(frame, camera_id)

