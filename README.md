<<<<<<< HEAD
# Constellation
=======
# Constellation 🌟
>>>>>>> 7b15a4a (basic skeleton)

**AI-Powered Neighborhood Security Network**

Constellation transforms neighborhood security cameras into a coordinated defense system that detects threats, predicts criminal patterns, and autonomously prevents crime before it happens.

Built for hackathon demonstration - an intelligent multi-agent system using AI to coordinate security across an entire neighborhood.

## 🎯 Features

- **Multi-Agent Coordination**: AI agents work together across multiple camera feeds
- **Real-Time Threat Detection**: Instant detection and alerting of suspicious activity
- **Pattern Recognition**: Correlates incidents across cameras to identify patterns
- **Predictive Analytics**: Predicts likely next targets based on movement patterns
- **Live Reasoning Visualization**: See AI "thinking" in real-time as it makes decisions
- **Interactive Map**: Visualize cameras, threats, and detections on an interactive map

## 🏗️ Architecture

- **Backend**: Python, FastAPI, WebSockets
- **Frontend**: React (TypeScript), Leaflet.js
- **AI**: Multi-agent coordination via MCP (Model Context Protocol)
- **Communication**: Real-time WebSocket updates

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

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

4. Start the server:
```bash
python main.py
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

The frontend will run on `http://localhost:3000`

## 🎮 Using the Demo

1. **Start both servers** (backend and frontend)

2. **Open the app** in your browser at `http://localhost:3000`

3. **Start the Car Prowler Scenario**:
   - Click "Start Scenario" in the Control Panel
   - Watch as AI agents detect suspicious activity across multiple cameras
   - See real-time reasoning in the AI Reasoning panel
   - Observe pattern correlation and threat predictions on the map

4. **Monitor the Dashboard**:
   - **Map View**: See camera locations, detections, and threats
   - **Threat Panel**: View all detected threats and their details
   - **AI Reasoning Panel**: Watch the AI's decision-making process in real-time

## 📁 Project Structure

```
constellation/
├── backend/
│   ├── agents/
│   │   ├── coordinator.py      # Multi-agent coordination
│   │   └── camera_agent.py     # Individual camera agents
│   ├── api/
│   ├── demo/
│   │   └── scenarios/
│   │       └── car_prowler.py  # Car prowler demo scenario
│   ├── main.py                 # FastAPI server
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── types.ts           # TypeScript types
│   │   └── App.tsx            # Main app component
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🎬 Demo Scenarios

### Car Prowler Detection

Simulates a car prowler moving through the neighborhood:
- AI detects suspicious activity at multiple camera locations
- Correlates patterns across cameras
- Predicts next likely target
- Shows real-time reasoning and evidence

## 🔧 API Endpoints

### REST API

- `GET /` - API status
- `GET /api/cameras` - Get all camera locations
- `GET /api/threats` - Get active threats
- `POST /api/scenarios/start?scenario_name=car_prowler` - Start demo scenario
- `POST /api/scenarios/stop` - Stop current scenario

### WebSocket

- `ws://localhost:8000/ws` - Real-time updates
  - Receives: detections, threats, reasoning logs, scenario events

## 🛠️ Development

### Backend Development

The backend uses FastAPI with WebSocket support. Key components:

- **AgentCoordinator**: Manages multiple camera agents and threat correlation
- **CameraAgent**: Individual agents that process camera feeds
- **Scenarios**: Demo scenarios that simulate real-world threats

### Frontend Development

The frontend is built with React + TypeScript + Vite:

- **MapView**: Interactive Leaflet map showing cameras and threats
- **ThreatPanel**: Real-time threat and detection display
- **ReasoningPanel**: AI reasoning visualization
- **ControlPanel**: Scenario controls and statistics

## 🎨 Tech Stack

- **Backend**: Python, FastAPI, WebSockets, Python-dotenv
- **Frontend**: React 18, TypeScript, Vite, Leaflet.js, React-Leaflet
- **Architecture**: Multi-agent system with MCP coordination
- **Real-time**: WebSocket bidirectional communication

## 📝 Notes

- This is a hackathon demo - no database, everything in-memory
- Camera locations are simulated for demonstration
- AI detection logic is simplified for demo purposes
- Production implementation would integrate with real camera feeds and ML models

## 🤝 Contributing

This is a hackathon project. For questions or improvements, feel free to open an issue or PR!

## 📄 License

MIT License - Built for hackathon demonstration

---

**Built with ❤️ for neighborhood security**
