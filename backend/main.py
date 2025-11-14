"""
URSA - AI Agent Network for Wildlife and Wildfire Detection
FastAPI backend with WebSocket support for real-time wildlife and wildfire detection
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv

from agents.coordinator import AgentCoordinator
from agents.camera_agent import CameraAgent
from demo.scenarios.wildlife_detection import WildlifeDetectionScenario
import uuid

# Twilio service will be accessed via coordinator

load_dotenv()

app = FastAPI(title="URSA API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve video files
video_dir = os.path.join(os.path.dirname(__file__), "..", "demo", "videos")
if os.path.exists(video_dir):
    app.mount("/videos", StaticFiles(directory=video_dir), name="videos")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.active_connections.remove(conn)

manager = ConnectionManager()

# AI mode configuration (can be toggled)
USE_REAL_AI = os.getenv("USE_REAL_AI", "false").lower() == "true"
coordinator = AgentCoordinator(use_real_ai=USE_REAL_AI)

# Initialize demo scenario
scenario = WildlifeDetectionScenario(coordinator, manager)

@app.get("/")
async def root():
    return {
        "name": "URSA",
        "version": "1.0.0",
        "status": "operational",
        "agents": coordinator.get_agent_count(),
        "description": "Wildlife and Wildfire Detection System"
    }

@app.get("/api/cameras")
async def get_cameras():
    """Get all camera locations and status"""
    return {
        "cameras": coordinator.get_all_cameras(),
        "count": len(coordinator.get_all_cameras())
    }

@app.get("/api/threats")
async def get_threats():
    """Get current active threats"""
    return {
        "threats": coordinator.get_active_threats(),
        "count": len(coordinator.get_active_threats())
    }

@app.post("/api/scenarios/start")
async def start_scenario(scenario_name: str = "wildlife_detection"):
    """Start a demo scenario"""
    if scenario_name == "wildlife_detection":
        await scenario.start()
        return {"status": "started", "scenario": scenario_name}
    return {"status": "error", "message": "Unknown scenario"}

@app.post("/api/scenarios/stop")
async def stop_scenario():
    """Stop current scenario"""
    await scenario.stop()
    return {"status": "stopped"}

@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    return {
        "use_real_ai": coordinator.use_real_ai,
        "ai_available": True,  # Will be False if OpenCV not available
        "mode": "real_ai" if coordinator.use_real_ai else "simulated"
    }

@app.post("/api/config/toggle-ai")
async def toggle_ai_mode():
    """Toggle between real AI and simulated mode"""
    coordinator.use_real_ai = not coordinator.use_real_ai
    # Reinitialize agents with new mode
    for camera in coordinator.get_all_cameras():
        camera_id = camera["id"]
        if camera_id in coordinator.agents:
            # Update existing agent
            coordinator.agents[camera_id].use_real_ai = coordinator.use_real_ai
            if coordinator.use_real_ai and coordinator.agents[camera_id].video_analyzer is None:
                try:
                    from agents.video_analyzer import VideoAnalyzer
                    coordinator.agents[camera_id].video_analyzer = VideoAnalyzer()
                except:
                    pass
    
    return {
        "status": "updated",
        "use_real_ai": coordinator.use_real_ai,
        "mode": "real_ai" if coordinator.use_real_ai else "simulated"
    }

@app.get("/api/video/analyze/{camera_id}")
async def analyze_video_stream(camera_id: str):
    """Get real-time analysis annotations for a video stream"""
    camera = next((c for c in coordinator.get_all_cameras() if c["id"] == camera_id), None)
    if not camera or not camera.get("video"):
        return {"error": "Camera or video not found"}
    
    # Get agent for this camera
    agent = coordinator.agents.get(f"agent_{camera_id}")
    if not agent or not agent.use_real_ai or not agent.video_analyzer:
        return {"error": "AI analysis not available for this camera"}
    
    video_path = os.path.join(os.path.dirname(__file__), "..", "demo", "videos", camera["video"])
    if not os.path.exists(video_path):
        return {"error": "Video file not found"}
    
    # Analyze a sample frame to get detection info
    # In production, this would stream frame-by-frame
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Get object detections
            detected_objects = agent.video_analyzer._detect_objects(frame)
            return {
                "camera_id": camera_id,
                "objects": detected_objects.get("objects", []),
                "people": detected_objects.get("people", []),
                "vehicles": detected_objects.get("vehicles", []),
                "analysis_available": True
            }
    except Exception as e:
        return {"error": str(e)}
    
    return {"error": "Could not analyze video"}

@app.websocket("/ws/video/{camera_id}")
async def video_analysis_stream(websocket: WebSocket, camera_id: str):
    """WebSocket stream for real-time video analysis with annotations"""
    await websocket.accept()
    
    camera = next((c for c in coordinator.get_all_cameras() if c["id"] == camera_id), None)
    if not camera or not camera.get("video"):
        await websocket.close(code=1008, reason="Camera or video not found")
        return
    
    # Ensure agent exists and has Real AI enabled
    agent_id = f"agent_{camera_id}"
    if agent_id not in coordinator.agents:
        # Create agent if it doesn't exist
        agent = CameraAgent(camera_id, coordinator, use_real_ai=True)
        coordinator.register_agent(agent)
    else:
        agent = coordinator.agents[agent_id]
        # Ensure Real AI is enabled
        if not agent.use_real_ai:
            agent.use_real_ai = True
            if agent.video_analyzer is None:
                try:
                    from agents.video_analyzer import VideoAnalyzer
                    agent.video_analyzer = VideoAnalyzer()
                except Exception as e:
                    print(f"Could not initialize video analyzer: {e}")
                    await websocket.close(code=1008, reason="AI analysis not available")
                    return
    
    if not agent.video_analyzer:
        await websocket.close(code=1008, reason="AI analysis not available")
        return
    
    video_path = os.path.join(os.path.dirname(__file__), "..", "demo", "videos", camera["video"])
    if not os.path.exists(video_path):
        await websocket.close(code=1008, reason="Video file not found")
        return
    
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_delay = 1.0 / fps
        
        previous_frame = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                # Loop video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                previous_frame = None
                continue
            
            # Analyze frame with full AI pipeline
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            motion_data = agent.video_analyzer._analyze_motion(gray, previous_frame) if previous_frame is not None else (0.0, 0.0)
            
            # Get object detections
            detected_objects = agent.video_analyzer._detect_objects(frame)
            
            # Store object history for temporal analysis (loitering detection)
            if detected_objects.get("count", 0) > 0:
                agent.video_analyzer.object_history.append(detected_objects)
                if len(agent.video_analyzer.object_history) > 30:  # Keep last 30 frames
                    agent.video_analyzer.object_history.pop(0)
            
            # Run full suspicious activity detection (not just object detection)
            detection = agent.video_analyzer._detect_suspicious_activity_combined(
                gray, camera_id, previous_frame, detected_objects, motion_data
            )
            
            previous_frame = gray.copy()
            
            # Format annotations for frontend
            annotations = {
                "timestamp": datetime.now().isoformat(),
                "frame_number": int(cap.get(cv2.CAP_PROP_POS_FRAMES)),
                "objects": []
            }
            
            # Add bounding boxes and labels
            for obj in detected_objects.get("objects", []):
                annotations["objects"].append({
                    "class": obj["class_name"],
                    "confidence": obj["confidence"],
                    "bbox": obj["bbox"],
                    "center": obj["center"]
                })
            
            # If threat detected, add to coordinator and broadcast to main WebSocket
            if detection:
                # Get camera location for threat
                threat_location = {
                    "lat": camera["lat"],
                    "lng": camera["lng"]
                }
                
                # Add threat to coordinator
                coordinator.add_threat({
                    "type": detection["activity_type"],
                    "camera_id": detection["camera_id"],
                    "location": threat_location,
                    "confidence": detection["confidence"],
                    "details": detection.get("details", {})
                })
                
                # Broadcast threat detection to main WebSocket (for map/threat panel)
                await manager.broadcast({
                    "type": "detection",
                    "detection": {
                        **detection,
                        "location": threat_location
                    },
                    "threat": {
                        "id": str(uuid.uuid4()),
                        "type": detection["activity_type"],
                        "camera_id": detection["camera_id"],
                        "location": threat_location,
                        "confidence": detection["confidence"],
                        "timestamp": detection["timestamp"],
                        "status": "active",
                        "details": detection.get("details", {})
                    },
                    "reasoning": agent.get_reasoning_log()[-1] if agent.get_reasoning_log() else None,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Send annotations (always send, even if no threat)
            await websocket.send_json({
                "type": "video_analysis",
                "camera_id": camera_id,
                "annotations": annotations,
                "people_count": detected_objects.get("people_count", 0),
                "vehicles_count": detected_objects.get("vehicles_count", 0),
                "motion_speed": motion_data[0],
                "motion_consistency": motion_data[1],
                "threat_detected": detection is not None,
                "threat_type": detection["activity_type"] if detection else None,
                "threat_confidence": detection["confidence"] if detection else None
            })
            
            await asyncio.sleep(frame_delay)
            
    except Exception as e:
        print(f"Video analysis error: {e}")
    finally:
        if 'cap' in locals():
            cap.release()
        await websocket.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    # Send initial state
    await websocket.send_json({
        "type": "init",
        "cameras": coordinator.get_all_cameras(),
        "threats": coordinator.get_active_threats(),
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Twilio webhook endpoints for voice calls
@app.post("/api/twilio/voice")
async def twilio_voice_webhook(request: Request):
    """Twilio webhook for voice calls - generates TwiML response"""
    # Get the most recent threat that triggered a call
    threats = coordinator.get_active_threats()
    if not threats:
        # Return a default message if no detections
        from twilio.twiml.voice_response import VoiceResponse
        response = VoiceResponse()
        response.say("No active wildlife or wildfire detections at this time.", voice='alice')
        return Response(content=str(response), media_type="application/xml")
    
    # Get the most recent threat with analysis
    recent_threat = None
    for threat in reversed(threats):
        if threat.get("analysis"):
            recent_threat = threat
            break
    
    if not recent_threat or not coordinator.twilio_service:
        from twilio.twiml.voice_response import VoiceResponse
        response = VoiceResponse()
        response.say("Unable to retrieve detection information.", voice='alice')
        return Response(content=str(response), media_type="application/xml")
    
    # Find nearby cameras
    nearby_cameras = coordinator._find_nearby_cameras(recent_threat.get("location", {}))
    
    # Generate voice response
    twiml = coordinator.twilio_service.generate_voice_response(
        recent_threat,
        recent_threat.get("analysis", {}),
        nearby_cameras
    )
    
    return Response(content=twiml, media_type="application/xml")

@app.post("/api/twilio/gather")
async def twilio_gather(request: Request):
    """Handle user input during Twilio call"""
    form = await request.form()
    digits = form.get("Digits", "")
    
    from twilio.twiml.voice_response import VoiceResponse
    response = VoiceResponse()
    
    if digits == "1":
        # Provide more information
        threats = coordinator.get_active_threats()
        if threats:
            recent_threat = threats[-1]
            analysis = recent_threat.get("analysis", {})
            summary = analysis.get("response_summary", "No additional information available.")
            response.say(summary, voice='alice')
        else:
            response.say("No additional information available.", voice='alice')
    elif digits == "2":
        response.say("Thank you. Ending call.", voice='alice')
        response.hangup()
    else:
        response.say("Invalid selection. Goodbye.", voice='alice')
        response.hangup()
    
    return Response(content=str(response), media_type="application/xml")

@app.post("/api/twilio/call-status")
async def twilio_call_status(request: Request):
    """Receive call status updates from Twilio"""
    form = await request.form()
    call_sid = form.get("CallSid")
    call_status = form.get("CallStatus")
    
    print(f"Call status update: {call_sid} - {call_status}")
    
    # You could update threat records with call status here
    return {"status": "received"}

@app.get("/api/police-call/test")
async def test_police_call():
    """Test endpoint to manually trigger an emergency call (fire department for wildfires)"""
    try:
        # Create a test threat
        test_threat = {
            "id": str(uuid.uuid4()),
            "type": "wildfire",
            "camera_id": "cam_001",
            "location": {"lat": 37.7749, "lng": -122.4194},
            "confidence": 0.85,
            "timestamp": datetime.now().isoformat(),
            "details": {
                "description": "Test wildfire detection",
                "severity": "critical",
                "action_required": True
            }
        }
        
        # Add threat (this will trigger analysis and potentially a call)
        coordinator.add_threat(test_threat)
        
        # Give it a moment to process
        await asyncio.sleep(0.1)
        
        return {
            "status": "test_threat_created",
            "threat_id": test_threat["id"],
            "note": "Check console/logs for call status",
            "threat": test_threat
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "note": "Check backend logs for details"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
