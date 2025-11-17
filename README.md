# Ursa 🐻✨

**AI-Powered Neighborhood Safety System for Wildlife and Wildfire Detection**

Ursa transforms neighborhood security cameras into an intelligent safety network that detects wildfires and wildlife threats, automatically alerts emergency services, and keeps your community informed in real-time.

Built with cutting-edge AI agents that analyze video feeds, assess threats, and autonomously coordinate emergency responses to protect your neighborhood from wildfires and dangerous wildlife encounters.

## 🎯 Features

### 🔥 Wildfire Detection & Emergency Response
- **Real-Time Fire Detection**: AI agents continuously monitor camera feeds for signs of wildfire, smoke, and fire
- **Automatic Emergency Calls**: System autonomously calls fire department when wildfire is detected with high confidence
- **Multi-Camera Correlation**: Tracks fire spread across multiple cameras to provide accurate location data to first responders
- **Community-Wide Alerts**: Automatically notifies all residents within 50-mile radius via SMS when wildfire is detected

### 🦌 Wildlife Detection & Safety
- **Dangerous Wildlife Alerts**: Detects bears, coyotes, and other potentially dangerous wildlife in residential areas
- **Lost Pet Detection**: Identifies and tracks lost pets across camera network, coordinating with animal control
- **Wildlife Authorities Coordination**: Automatically contacts appropriate wildlife authorities for dangerous animal encounters
- **Pattern Tracking**: Monitors wildlife movement patterns across cameras to predict behavior and protect residents

### 🤖 AI Agent Network
- **Multi-Agent Coordination**: AI agents work together across multiple camera feeds to correlate threats
- **Intelligent Threat Analysis**: Advanced AI analyzes threat severity, confidence levels, and appropriate responses
- **Autonomous Emergency Response**: AI agents automatically call fire department, wildlife authorities, or animal control based on threat type
- **Live Reasoning Visualization**: See AI "thinking" in real-time as it analyzes threats and makes decisions
- **Contextual Communication**: AI generates dynamic, context-aware messages for emergency calls and community notifications

### 📍 Community Features
- **Interactive Map**: Visualize all cameras, active threats, and detections on an interactive neighborhood map
- **50-Mile Radius Notifications**: Automatic SMS alerts to all community members within 50 miles of incidents
- **Real-Time Updates**: WebSocket-powered live updates for instant threat awareness
- **Threat Panel**: Comprehensive view of all active threats with severity levels and recommended actions

## 🏗️ Architecture

- **Backend**: Python, FastAPI, WebSockets
- **Frontend**: React (TypeScript), Vite, Leaflet.js
- **AI Detection**: YOLOv8 for real-time object detection, OpenCV for video processing
- **AI Agents**: Multi-agent coordination system with autonomous decision-making
- **Emergency Services**: Twilio integration for automated calls and SMS notifications
- **Communication**: Real-time WebSocket updates for instant threat coordination

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- Twilio account (for emergency calls and SMS notifications)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file in the backend directory with:
```bash
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
POLICE_NUMBER=+1234567890  # Number to call for emergencies (demo)
BASE_URL=http://localhost:8000
USE_REAL_AI=false  # Set to 'true' to enable real AI video analysis
```

5. Start the server:
```bash
python main.py
```

Or use the convenience script:
```bash
./start_backend.sh
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

Or use the convenience script:
```bash
./start_frontend.sh
```

The frontend will run on `http://localhost:5173`

## 🎮 Using the Demo

1. **Start both servers** (backend and frontend)

2. **Open the app** in your browser at `http://localhost:5173`

3. **Start the Wildlife Detection Scenario**:
   - Click "Start Scenario" in the Control Panel
   - Watch as AI agents detect wildfires and wildlife across multiple cameras
   - See real-time reasoning in the AI Reasoning panel
   - Observe automatic emergency calls being placed
   - Watch community notifications being sent

4. **Monitor the Dashboard**:
   - **Map View**: See camera locations, active threats, and detection zones
   - **Threat Panel**: View all detected threats with severity levels (Critical, High, Medium, Low)
   - **AI Reasoning Panel**: Watch the AI's decision-making process in real-time
   - **Control Panel**: Start/stop scenarios and view system statistics

5. **Emergency Response Features**:
   - When a wildfire is detected, the system automatically calls fire department
   - For dangerous wildlife (bears, coyotes), wildlife authorities are contacted
   - Lost pets trigger animal control notifications
   - All nearby community members (50-mile radius) receive SMS alerts

## 📁 Project Structure

```
ursa/
├── backend/
│   ├── agents/
│   │   ├── coordinator.py          # Multi-agent coordination & emergency response
│   │   ├── camera_agent.py         # Individual camera AI agents
│   │   ├── video_analyzer.py       # YOLOv8-based video analysis
│   │   └── __init__.py
│   ├── services/
│   │   ├── twilio_service.py       # Emergency calls & SMS via Twilio
│   │   ├── community_notifier.py   # Community-wide alert system
│   │   ├── threat_analyzer.py      # Threat severity & response analyzer
│   │   ├── ai_message_generator.py # AI-generated contextual messages
│   │   └── __init__.py
│   ├── demo/
│   │   ├── scenarios/
│   │   │   ├── wildlife_detection.py # Wildlife & wildfire scenario
│   │   │   └── __init__.py
│   │   └── videos/                 # Demo video files for AI analysis
│   ├── main.py                     # FastAPI server with WebSocket
│   ├── requirements.txt            # Python dependencies
│   ├── yolov8n.pt                 # YOLOv8 model weights
│   └── verify_setup.py            # Setup verification script
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapView.tsx        # Interactive Leaflet map
│   │   │   ├── ThreatPanel.tsx    # Active threats display
│   │   │   ├── ReasoningPanel.tsx # AI reasoning visualization
│   │   │   ├── ControlPanel.tsx   # Scenario controls
│   │   │   └── CameraFeed.tsx     # Camera video feeds
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts    # WebSocket connection hook
│   │   ├── types.ts               # TypeScript type definitions
│   │   └── App.tsx                # Main application
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── start_backend.sh               # Backend startup script
├── start_frontend.sh              # Frontend startup script
├── test_backend.sh                # Backend testing script
└── README.md
```

## 🎬 Demo Scenarios

### Wildlife & Wildfire Detection

Simulates real-world wildlife and wildfire threats across the neighborhood:

**Wildfire Detection**:
- AI detects smoke and fire indicators in camera feeds
- System automatically calls fire department with location details
- All residents within 50 miles receive immediate SMS alerts
- Multi-camera correlation tracks fire spread and direction

**Wildlife Encounters**:
- Detects bears, coyotes, deer, and other wildlife near residential areas
- Assesses threat level based on animal type and behavior
- Automatically contacts wildlife authorities for dangerous animals
- Sends community alerts to keep residents informed and safe

**Lost Pet Recovery**:
- Identifies lost pets across multiple camera feeds
- Tracks pet movement patterns throughout neighborhood
- Coordinates with animal control for safe recovery
- Notifies community to assist in reunion efforts

## 🔧 API Endpoints

### REST API

- `GET /` - API status and agent count
- `GET /api/cameras` - Get all camera locations and status
- `GET /api/threats` - Get active threats with severity levels
- `POST /api/scenarios/start?scenario_name=wildlife_detection` - Start wildlife/wildfire demo
- `POST /api/scenarios/stop` - Stop current scenario
- `POST /api/twilio/voice` - Twilio webhook for emergency call voice content
- `POST /api/twilio/call-status` - Twilio webhook for call status updates
- `POST /api/twilio/sms-status` - Twilio webhook for SMS delivery status

### WebSocket

- `ws://localhost:8000/ws` - Real-time bidirectional communication
  - **Receives**: 
    - `detection` - New wildlife/wildfire detection events
    - `threat` - Threat alerts with severity analysis
    - `reasoning` - AI decision-making logs
    - `scenario_started` - Scenario initialization
    - `scenario_stopped` - Scenario completion
    - `emergency_call_placed` - Emergency service notification
    - `community_notified` - Community alert confirmation

## 🛠️ Development

### Backend Architecture

The backend uses FastAPI with WebSocket support and a sophisticated multi-agent system:

**Core Components**:
- **AgentCoordinator**: Orchestrates multiple camera agents, correlates threats across cameras, manages emergency response
- **CameraAgent**: Individual AI agents that process video feeds, detect wildlife/wildfire, maintain detection logs
- **VideoAnalyzer**: YOLOv8-based computer vision for real-time object detection in video streams
- **ThreatAnalyzer**: Evaluates threat severity (Critical/High/Medium/Low) and determines appropriate responses
- **TwilioService**: Handles automated emergency calls and SMS notifications to authorities and community
- **CommunityNotifier**: Manages 50-mile radius community alerts with distance-based targeting
- **AIMessageGenerator**: Creates contextual, dynamic messages for emergency calls and notifications

**Emergency Response Flow**:
1. Camera agent detects wildlife/wildfire in video feed
2. Detection sent to coordinator for multi-camera correlation
3. Threat analyzer evaluates severity and confidence level
4. If critical: AI agent automatically calls appropriate emergency service
5. Community notifier sends SMS alerts to all residents within 50 miles
6. Real-time updates broadcast to all connected clients via WebSocket

### Frontend Architecture

The frontend is built with React + TypeScript + Vite:

**Key Components**:
- **MapView**: Interactive Leaflet.js map showing camera network, threat zones, and detection events
- **ThreatPanel**: Real-time threat dashboard with severity indicators and recommended actions
- **ReasoningPanel**: Live AI reasoning visualization showing decision-making process
- **ControlPanel**: Scenario management, system statistics, and AI mode toggle
- **CameraFeed**: Video stream visualization for connected cameras

**WebSocket Integration**:
- Custom `useWebSocket` hook manages persistent connection
- Real-time updates for detections, threats, and AI reasoning
- Automatic reconnection handling
- Type-safe message parsing with TypeScript

### AI Modes

**Simulated Mode** (`USE_REAL_AI=false`):
- Pre-programmed detection scenarios for demonstration
- No actual video analysis required
- Fast and reliable for testing

**Real AI Mode** (`USE_REAL_AI=true`):
- YOLOv8-based computer vision analysis
- Processes actual video files frame-by-frame
- Detects real objects, animals, and fire indicators
- Requires GPU for optimal performance

## 🎨 Tech Stack

**Backend**:
- **Framework**: FastAPI, Uvicorn
- **AI/ML**: YOLOv8 (Ultralytics), OpenCV, NumPy
- **Communication**: WebSockets, Twilio API
- **Utilities**: Python-dotenv, asyncio

**Frontend**:
- **Framework**: React 18, TypeScript, Vite
- **Mapping**: Leaflet.js, React-Leaflet
- **Styling**: CSS3, Flexbox/Grid
- **State Management**: React Hooks

**Architecture**:
- **Multi-Agent System**: Autonomous AI agents with coordinated decision-making
- **Real-Time Communication**: WebSocket bidirectional updates
- **Emergency Integration**: Twilio for voice calls and SMS
- **Computer Vision**: YOLOv8 for object and threat detection

## 📝 Notes

**Demo Configuration**:
- Camera locations are simulated for demonstration purposes
- In demo mode, emergency calls go to configured POLICE_NUMBER (not actual 911)
- Community member database is simulated (would connect to real DB in production)
- Video files in `demo/videos/` are used for AI analysis in real mode

**Production Considerations**:
- Integrate with real IP camera feeds (RTSP/ONVIF protocols)
- Connect to actual emergency dispatch systems with proper authorization
- Implement user authentication and authorization
- Add database for threat history, community members, and camera registry
- Deploy with proper security (HTTPS, API authentication)
- Scale with load balancing and distributed agent processing
- Add false positive reduction with multi-frame verification

## 🧪 Testing

Run backend tests:
```bash
./test_backend.sh
```

Test Twilio integration:
```bash
python backend/test_twilio_call.py
python backend/check_twilio_call_status.py
```

Verify setup:
```bash
python backend/verify_setup.py
```

## 🚨 Safety & Compliance

**Important**: This system is designed for demonstration and testing purposes. For production deployment:

- Ensure compliance with local emergency service protocols
- Obtain proper authorization before connecting to 911 or emergency dispatch
- Implement false positive reduction to prevent unnecessary emergency calls
- Follow privacy regulations for video surveillance in your jurisdiction
- Test thoroughly with non-emergency numbers before production use
- Maintain proper logging and audit trails for all emergency calls

**Emergency Call Disclaimer**: In demo mode, calls are placed to the configured test number, NOT actual emergency services. Configure appropriately for your use case.

## 🔮 Future Enhancements

- **Advanced AI Models**: Integration with larger models for improved detection accuracy
- **Smoke Detection**: Specialized algorithms for early smoke and fire detection
- **Wildlife Species Identification**: Detailed species classification for appropriate response
- **Predictive Analytics**: Machine learning to predict wildlife movement patterns
- **Mobile App**: iOS/Android apps for community members
- **Historical Analysis**: Long-term trend analysis for wildlife and fire risk
- **Integration with Weather Data**: Enhanced fire risk assessment with weather conditions
- **Drone Integration**: Automatic drone deployment for aerial assessment

## 🤝 Contributing

This project is built to protect neighborhoods from wildfires and wildlife threats. Contributions are welcome! Feel free to open issues or submit pull requests.

## 📄 License

MIT License - Built for neighborhood safety and community protection

---

**Built with ❤️ to protect neighborhoods from wildfires and wildlife threats**

**Ursa** - Named after Ursa Major (Great Bear constellation), symbolizing our mission to keep communities safe from wildlife and natural threats while maintaining harmony with nature.
