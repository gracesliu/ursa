"""
Video Analyzer - Real AI video analysis using computer vision + YOLO object detection
Wildlife and Wildfire Detection System
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
    """Analyzes video frames using computer vision + YOLO object detection for wildlife and wildfire detection"""
    
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
        Analyze a single video frame for wildlife and wildfire using YOLO + motion detection
        
        Args:
            frame: OpenCV frame (numpy array, BGR format)
            camera_id: ID of the camera
            
        Returns:
            Detection dict if wildlife or wildfire found, None otherwise
        """
        # Convert to grayscale for processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Get previous frame for motion analysis
        previous = self.frame_buffer[-2] if len(self.frame_buffer) >= 2 else None
        
        # Step 1: Fire/smoke detection (color-based, before object detection)
        fire_detection = self._detect_fire(frame, gray, previous, camera_id)
        
        # Step 2: Object detection with YOLO (if available) - for wildlife
        detected_objects = self._detect_objects(frame) if self.yolo_model else None
        
        # Step 3: Motion analysis
        motion_data = self._analyze_motion(gray, previous) if previous is not None else (0.0, 0.0)
        
        # Step 4: Fire takes priority - return immediately if detected
        if fire_detection:
            return fire_detection
        
        # Step 5: Check for lost pet (pet without person nearby)
        lost_pet_detection = self._detect_lost_pet(
            frame, gray, camera_id, previous, detected_objects, motion_data
        )
        if lost_pet_detection:
            return lost_pet_detection
        
        # Step 6: Combined wildlife activity detection
        detection = self._detect_wildlife_activity_combined(
            frame, gray, camera_id, previous, detected_objects, motion_data
        )
        
        return detection
    
    def _detect_fire(self, frame: np.ndarray, gray_frame: np.ndarray, previous_frame: Optional[np.ndarray], camera_id: str) -> Optional[Dict[str, Any]]:
        """
        Detect fire and smoke using color analysis and motion patterns
        
        Returns:
            Detection dict if fire detected, None otherwise
        """
        # Convert BGR to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for fire (red, orange, yellow)
        # Fire colors in HSV
        lower_fire1 = np.array([0, 50, 50])    # Red lower bound
        upper_fire1 = np.array([10, 255, 255]) # Red upper bound
        lower_fire2 = np.array([10, 50, 50])   # Orange lower bound
        upper_fire2 = np.array([30, 255, 255]) # Orange/Yellow upper bound
        
        # Create masks for fire colors
        mask1 = cv2.inRange(hsv, lower_fire1, upper_fire1)
        mask2 = cv2.inRange(hsv, lower_fire2, upper_fire2)
        fire_mask = cv2.bitwise_or(mask1, mask2)
        
        # Calculate fire pixel density
        fire_pixel_count = np.sum(fire_mask > 0)
        total_pixels = fire_mask.shape[0] * fire_mask.shape[1]
        fire_density = fire_pixel_count / total_pixels
        
        # Check for smoke (grayish colors, high motion, expanding)
        gray_mask = cv2.inRange(hsv, np.array([0, 0, 50]), np.array([180, 50, 200]))
        smoke_pixel_count = np.sum(gray_mask > 0)
        smoke_density = smoke_pixel_count / total_pixels
        
        # Motion analysis for fire (fire flickers and moves)
        motion_intensity = 0.0
        if previous_frame is not None:
            diff = cv2.absdiff(gray_frame, previous_frame)
            motion_intensity = np.sum(diff > 30) / total_pixels
        
        # Fire detection criteria
        fire_score = 0.0
        if fire_density > 0.05:  # At least 5% of frame has fire colors
            fire_score += 0.4
        if fire_density > 0.10:  # Strong fire presence
            fire_score += 0.3
        if motion_intensity > 0.05 and fire_density > 0.03:  # Flickering fire
            fire_score += 0.2
        if smoke_density > 0.08:  # Smoke present
            fire_score += 0.1
        
        # Threshold for fire detection
        if fire_score > 0.5:
            confidence = min(0.95, fire_score)
            
            return {
                "camera_id": camera_id,
                "activity_type": "wildfire",
                "confidence": float(confidence),
                "timestamp": datetime.now().isoformat(),
                "behavior": "wildfire",
                "details": {
                    "description": f"Wildfire detected - fire density: {fire_density:.1%}, smoke density: {smoke_density:.1%}",
                    "severity": "critical" if confidence > 0.8 else "high",
                    "action_required": True,
                    "ai_metrics": {
                        "fire_density": float(fire_density),
                        "smoke_density": float(smoke_density),
                        "motion_intensity": float(motion_intensity),
                        "fire_score": float(fire_score),
                        "detection_method": "color_analysis"
                    }
                }
            }
        
        return None
    
    def _detect_objects(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Detect wildlife (animals) in frame using YOLO
        
        Returns:
            Dict with detected animals, their classes, and positions
        """
        if not self.yolo_model:
            return {"objects": [], "animals": [], "count": 0}
        
        try:
            # Run YOLO inference
            results = self.yolo_model(frame, verbose=False)
            
            # Parse results
            detected_objects = []
            animals = []
            pets = []
            people = []
            
            # COCO animal class IDs for wildlife detection
            # 14: bird, 15: cat, 16: dog, 17: horse, 18: sheep, 19: cow, 
            # 20: elephant, 21: bear, 22: zebra, 23: giraffe
            animal_class_ids = [14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
            
            # Pet class IDs (domestic animals that could be lost pets)
            pet_class_ids = [15, 16]  # cat, dog
            person_class_id = 0  # COCO class 0 = person
            
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
                    elif cls in pet_class_ids and conf > 0.5:
                        pets.append(obj_data)
                    elif cls in animal_class_ids and conf > 0.5:
                        animals.append(obj_data)
                    
            # Store in history for temporal analysis
            self.object_history.append({
                "timestamp": datetime.now().isoformat(),
                "animals": animals,
                "pets": pets,
                "people": people,
                "all_objects": detected_objects
            })
            if len(self.object_history) > 30:  # Keep last 30 frames
                self.object_history.pop(0)
            
            return {
                "objects": detected_objects,
                "animals": animals,
                "pets": pets,
                "people": people,
                "count": len(detected_objects),
                "animals_count": len(animals),
                "pets_count": len(pets),
                "people_count": len(people)
            }
        except Exception as e:
            print(f"YOLO detection error: {e}")
            return {"objects": [], "animals": [], "pets": [], "people": [], "count": 0}
    
    def _detect_lost_pet(
        self, frame: np.ndarray, gray_frame: np.ndarray, camera_id: str,
        previous_frame: Optional[np.ndarray],
        detected_objects: Optional[Dict[str, Any]],
        motion_data: Tuple[float, float]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect lost pet: pet (dog/cat) detected without a person nearby
        and moving across multiple locations (not just in yard)
        
        Returns:
            Detection dict if lost pet found, None otherwise
        """
        if not detected_objects:
            return None
        
        pets = detected_objects.get("pets", [])
        people = detected_objects.get("people", [])
        
        if not pets or len(pets) == 0:
            return None
        
        # Check if any pet is without a person nearby
        lost_pets = []
        for pet in pets:
            pet_center = pet["center"]
            pet_bbox = pet["bbox"]
            
            # Check if there's a person nearby (within 100 pixels)
            has_person_nearby = False
            for person in people:
                person_center = person["center"]
                # Calculate distance between pet and person centers
                distance = np.sqrt(
                    (pet_center[0] - person_center[0])**2 + 
                    (pet_center[1] - person_center[1])**2
                )
                # Also check if person bbox overlaps with pet area
                person_bbox = person["bbox"]
                if (distance < 100 or 
                    (person_bbox[0] < pet_bbox[2] + 50 and person_bbox[2] > pet_bbox[0] - 50 and
                     person_bbox[1] < pet_bbox[3] + 50 and person_bbox[3] > pet_bbox[1] - 50)):
                    has_person_nearby = True
                    break
            
            if not has_person_nearby:
                lost_pets.append(pet)
        
        if len(lost_pets) == 0:
            return None
        
        # Check if pet is moving (not stationary in yard)
        motion_speed, motion_consistency = motion_data
        
        # Check if pet has been moving across frames (indicating it's not just in a yard)
        pet_moving = False
        if len(self.object_history) >= 5:
            recent_pet_positions = []
            for hist in self.object_history[-5:]:
                if hist.get("pets"):
                    for p in hist["pets"]:
                        # Check if it's the same pet (similar position)
                        if abs(p["center"][0] - lost_pets[0]["center"][0]) < 200:
                            recent_pet_positions.append(p["center"])
            
            if len(recent_pet_positions) >= 3:
                # Calculate position variance
                positions = np.array(recent_pet_positions)
                position_variance = np.var(positions, axis=0).sum()
                # High variance = pet moving around (not just in yard)
                if position_variance > 5000:  # Pet has moved significantly
                    pet_moving = True
        
        # Also check motion speed
        if motion_speed > 0.02:  # Pet is moving
            pet_moving = True
        
        # Lost pet criteria: pet without person nearby AND moving
        if pet_moving:
            pet_type = lost_pets[0]["class_name"]
            confidence = min(0.90, lost_pets[0]["confidence"] + 0.1 if pet_moving else lost_pets[0]["confidence"])
            
            return {
                "camera_id": camera_id,
                "activity_type": "lost_pet",
                "confidence": float(confidence),
                "timestamp": datetime.now().isoformat(),
                "behavior": "lost_pet",
                "details": {
                    "description": f"Lost {pet_type} detected - no owner nearby, moving across area",
                    "severity": "medium",
                    "action_required": True,
                    "pet_type": pet_type,
                    "pet_count": len(lost_pets),
                    "ai_metrics": {
                        "motion_speed": float(motion_speed),
                        "motion_consistency": float(motion_consistency),
                        "pet_moving": pet_moving,
                        "has_owner_nearby": False,
                        "detection_method": "yolo_pet_analysis"
                    }
                }
            }
        
        return None
    
    def _detect_wildlife_activity_combined(
        self, frame: np.ndarray, gray_frame: np.ndarray, camera_id: str, 
        previous_frame: Optional[np.ndarray], 
        detected_objects: Optional[Dict[str, Any]],
        motion_data: Tuple[float, float]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect wildlife activity using combined YOLO object detection + motion analysis
        
        Uses holistic approach:
        - YOLO object detection (animals)
        - Motion analysis (speed, consistency)
        - Temporal analysis (persistent patterns)
        - Behavioral analysis (animal presence and movement)
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
        object_analysis = self._analyze_wildlife_objects(detected_objects) if detected_objects else {}
        
        # Combined wildlife detection score
        wildlife_score = self._calculate_wildlife_score(
            edge_density, std_intensity, motion_speed, 
            motion_consistency, persistent_activity, movement_pattern,
            object_analysis
        )
        
        # Only trigger if score exceeds threshold
        if wildlife_score > 0.50:  # Threshold for wildlife detection
            activity_type = self._classify_wildlife_activity(
                gray_frame, edge_density, std_intensity, 
                motion_speed, persistent_activity, movement_pattern,
                object_analysis
            )
            
            if activity_type:
                # Confidence based on multiple factors including object detection
                confidence = min(0.95, wildlife_score)
                
                # Build description with object info
                description = f"AI detected {activity_type}"
                animal_count = object_analysis.get("animals_count", 0)
                if animal_count > 0:
                    animal_types = object_analysis.get("animal_types", [])
                    if animal_types:
                        description += f" - {animal_count} {animal_types[0]}(s) detected"
                    else:
                        description += f" - {animal_count} animal(s) detected"
                
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
                            "wildlife_score": float(wildlife_score),
                            "detection_method": "yolo_motion_combined" if self.yolo_model else "motion_analysis",
                            "animals_detected": object_analysis.get("animals_count", 0),
                            "animal_types": object_analysis.get("animal_types", [])
                        }
                    }
                }
        
        return None
    
    def _analyze_wildlife_objects(self, detected_objects: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze detected wildlife objects for patterns
        
        Returns analysis of animal positions, types, and behaviors
        """
        if not detected_objects or detected_objects.get("count", 0) == 0:
            return {
                "animals_count": 0,
                "animal_types": [],
                "has_animals": False
            }
        
        animals = detected_objects.get("animals", [])
        animal_types = list(set([a["class_name"] for a in animals]))
        
        # Check for persistent wildlife presence (animals staying in area)
        persistent_wildlife = False
        if len(self.object_history) >= 10 and animals:
            # Check if animals have been in similar location for multiple frames
            recent_animal_positions = []
            for hist in self.object_history[-10:]:
                if hist.get("animals"):
                    for a in hist["animals"]:
                        recent_animal_positions.append(a["center"])
            
            if len(recent_animal_positions) >= 5:
                # Calculate position variance
                positions = np.array(recent_animal_positions)
                position_variance = np.var(positions, axis=0).sum()
                if position_variance < 15000:  # Low variance = animals staying in same area
                    persistent_wildlife = True
        
        return {
            "animals_count": len(animals),
            "animal_types": animal_types,
            "has_animals": len(animals) > 0,
            "persistent_wildlife": persistent_wildlife,
            "animals": animals
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
    
    def _calculate_wildlife_score(
        self, edge_density: float, std_intensity: float, 
        motion_speed: float, motion_consistency: float,
        persistent_activity: float, movement_pattern: str,
        object_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate wildlife detection score using multiple factors + object detection
        
        Higher score = more likely wildlife present. Threshold: 0.50
        """
        score = 0.0
        
        # Factor 1: Edge density (indicates movement/activity)
        if 0.08 < edge_density < 0.25:  # Good range for animal movement
            score += 0.15
        elif edge_density > 0.25:  # Too high = likely noise
            score += 0.05
        
        # Factor 2: Motion consistency (concentrated motion = animal, scattered = noise)
        if motion_consistency > 0.3:  # Motion is concentrated (likely an animal)
            score += 0.20
        elif motion_consistency < 0.1:  # Scattered motion (likely noise)
            score -= 0.10  # Penalty
        
        # Factor 3: Motion speed (animals move at various speeds)
        if 0.01 < motion_speed < 0.15:  # Animal movement range
            score += 0.15
        elif motion_speed > 0.20:  # Too fast = likely noise
            score -= 0.05
        
        # Factor 4: Persistent activity (animals often stay in area)
        if persistent_activity > 0.5:  # Activity for 50%+ of recent frames
            score += 0.25
        elif persistent_activity < 0.2:  # Brief activity
            score -= 0.10  # Penalty
        
        # Factor 5: Movement pattern
        if movement_pattern in ["slow_deliberate", "moderate", "erratic"]:
            score += 0.10  # Animal-like movement
        elif movement_pattern == "fast_movement":
            score += 0.05  # Could be animal running
        
        # Factor 6: Intensity variation
        if 20 < std_intensity < 90:  # Moderate variation
            score += 0.05
        
        # Factor 7: Animal Detection (MOST IMPORTANT!)
        animals_count = object_analysis.get("animals_count", 0)
        if animals_count > 0:
            score += 0.30  # Strong indicator of wildlife
            if animals_count > 1:
                score += 0.10  # Multiple animals
        elif object_analysis.get("has_animals", False):
            score += 0.15  # Animal detected but low confidence
        
        # Factor 8: Persistent wildlife presence
        if object_analysis.get("persistent_wildlife", False):
            score += 0.15  # Animals staying in area
        
        # If no animals detected but high motion, reduce score (likely false positive)
        if not object_analysis.get("has_animals", False) and motion_speed > 0.15:
            score -= 0.15  # High motion but no animal = likely noise
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
    
    def _classify_wildlife_activity(
        self, gray_frame: np.ndarray, edge_density: float, 
        std_intensity: float, motion_speed: float,
        persistent_activity: float, movement_pattern: str,
        object_analysis: Dict[str, Any]
    ) -> Optional[str]:
        """
        Classify wildlife activity using object detection + motion analysis
        
        Uses YOLO detections to identify specific wildlife types
        """
        has_animals = object_analysis.get("has_animals", False)
        animals_count = object_analysis.get("animals_count", 0)
        persistent_wildlife = object_analysis.get("persistent_wildlife", False)
        animal_types = object_analysis.get("animal_types", [])
        
        # If animals detected, classify as wildlife
        if has_animals and animals_count > 0:
            # Determine specific type if possible
            if animal_types:
                # Use the most common animal type
                primary_type = animal_types[0]
                return f"wildlife_{primary_type}"
            else:
                return "wildlife_detected"
        
        # Fallback to motion-only classification if no objects detected
        # (for cases where YOLO misses detection but motion is clear)
        if not has_animals:
            if (movement_pattern in ["slow_deliberate", "moderate", "erratic"] and 
                0.08 < edge_density < 0.25 and 
                0.01 < motion_speed < 0.15 and
                persistent_activity > 0.5):
                return "wildlife_detected"
            elif (persistent_activity > 0.6 and
                  0.08 < edge_density < 0.20 and
                  0.01 < motion_speed < 0.10):
                return "wildlife_detected"
        
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

