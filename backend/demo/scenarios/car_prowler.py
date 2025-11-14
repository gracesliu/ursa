"""
Car Prowler Detection Scenario
Simulates a car prowler moving through the neighborhood
"""

import asyncio
import uuid
from typing import Dict, Any
from datetime import datetime
from agents.camera_agent import CameraAgent

class CarProwlerScenario:
    """Car prowler detection demo scenario"""
    
    def __init__(self, coordinator, connection_manager):
        self.coordinator = coordinator
        self.connection_manager = connection_manager
        self.running = False
        self.task = None
        self.agents: Dict[str, CameraAgent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize camera agents for scenario"""
        cameras = self.coordinator.get_all_cameras()
        for camera in cameras:
            agent = CameraAgent(camera["id"], self.coordinator, use_real_ai=self.coordinator.use_real_ai)
            self.coordinator.register_agent(agent)
            self.agents[camera["id"]] = agent
    
    async def start(self):
        """Start the car prowler scenario"""
        if self.running:
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run_scenario())
        
        # Broadcast scenario start
        await self.connection_manager.broadcast({
            "type": "scenario_started",
            "scenario": "car_prowler",
            "message": "Car prowler scenario started - monitoring neighborhood",
            "timestamp": datetime.now().isoformat()
        })
    
    async def stop(self):
        """Stop the scenario"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        await self.connection_manager.broadcast({
            "type": "scenario_stopped",
            "scenario": "car_prowler",
            "timestamp": datetime.now().isoformat()
        })
    
    async def _run_scenario(self):
        """Run the car prowler scenario sequence"""
        try:
            # Wait a moment before starting
            await asyncio.sleep(2)
            
            # Sequence of detections across different cameras
            sequence = [
                {"camera": "cam_001", "delay": 3, "confidence": 0.75},
                {"camera": "cam_002", "delay": 8, "confidence": 0.82},
                {"camera": "cam_003", "delay": 6, "confidence": 0.88},
            ]
            
            for step in sequence:
                if not self.running:
                    break
                
                await asyncio.sleep(step["delay"])
                
                # Trigger detection
                agent = self.agents.get(step["camera"])
                if agent:
                    if agent.use_real_ai:
                        # Real AI mode: try to analyze video file if it exists
                        camera = next((c for c in self.coordinator.get_all_cameras() if c["id"] == step["camera"]), None)
                        if camera and camera.get("video"):
                            import os
                            video_path = os.path.join(os.path.dirname(__file__), "..", "..", "demo", "videos", camera["video"])
                            if os.path.exists(video_path):
                                # Analyze video with real AI
                                detections = agent.analyze_video_file(video_path)
                                detection = detections[0] if detections else None
                                if not detection:
                                    # Fallback to simulated if no AI detection
                                    detection = agent.detect_suspicious_activity(
                                        "car_prowling",
                                        confidence=step["confidence"]
                                    )
                            else:
                                # Video not found, use simulated
                                detection = agent.detect_suspicious_activity(
                                    "car_prowling",
                                    confidence=step["confidence"]
                                )
                        else:
                            # No video file, use simulated
                            detection = agent.detect_suspicious_activity(
                                "car_prowling",
                                confidence=step["confidence"]
                            )
                    else:
                        # Simulated mode
                        detection = agent.detect_suspicious_activity(
                            "car_prowling",
                            confidence=step["confidence"]
                        )
                    
                    if detection:
                        # Add threat to coordinator
                        self.coordinator.add_threat({
                            "type": "car_prowling",
                            "camera_id": detection["camera_id"],
                            "location": detection["location"],
                            "confidence": detection["confidence"],
                            "details": detection["details"]
                        })
                        
                        # Correlate pattern
                        pattern = self.coordinator.correlate_pattern(detection)
                        
                        # Predict next target if pattern is strong
                        prediction = None
                        if pattern and pattern["count"] >= 2:
                            prediction = self.coordinator.predict_next_target(pattern)
                            pattern["predicted_next"] = prediction
                        
                        # Broadcast detection
                        reasoning_log = agent.get_reasoning_log()
                        await self.connection_manager.broadcast({
                            "type": "detection",
                            "detection": detection,
                            "pattern": pattern,
                            "prediction": prediction,
                            "reasoning": reasoning_log[-1] if reasoning_log else None,
                            "threat": {
                                "id": str(uuid.uuid4()),
                                "type": detection["activity_type"],
                                "camera_id": detection["camera_id"],
                                "location": detection["location"],
                                "confidence": detection["confidence"],
                                "timestamp": detection["timestamp"],
                                "status": "active",
                                "details": detection["details"]
                            },
                            "timestamp": datetime.now().isoformat()
                        })
            
            # Final summary after sequence
            if self.running:
                await asyncio.sleep(2)
                await self.connection_manager.broadcast({
                    "type": "scenario_summary",
                    "message": "Pattern detected: Car prowler moving through neighborhood",
                    "threats_detected": len(self.coordinator.get_active_threats()),
                    "patterns_found": len(self.coordinator.patterns),
                    "timestamp": datetime.now().isoformat()
                })
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Scenario error: {e}")

