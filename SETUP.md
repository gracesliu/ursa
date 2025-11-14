# Quick Setup Guide

## Step 1: Backend Setup

Open a terminal and run:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 2: Frontend Setup

Open a **new terminal** and run:

```bash
cd frontend
npm install
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:3000/
```

## Step 3: Run the Demo

1. Open your browser to `http://localhost:3000`
2. Wait for the connection indicator to show "Connected" (green dot)
3. Click "Start Scenario" in the Control Panel
4. Watch the AI detect threats across the neighborhood!

## Troubleshooting

### Backend won't start
- Make sure Python 3.8+ is installed: `python3 --version`
- Check if port 8000 is available
- Try: `pip install --upgrade pip` then reinstall requirements

### Frontend won't start
- Make sure Node.js 18+ is installed: `node --version`
- Delete `node_modules` and `package-lock.json`, then run `npm install` again
- Check if port 3000 is available

### WebSocket connection fails
- Make sure backend is running on port 8000
- Check browser console for errors
- Verify CORS settings in `backend/main.py`

### Map doesn't load
- Check browser console for Leaflet errors
- Make sure you have internet connection (map tiles load from OpenStreetMap)

## Next Steps

- Customize camera locations in `backend/agents/coordinator.py`
- Add new scenarios in `backend/demo/scenarios/`
- Modify AI reasoning in `backend/agents/camera_agent.py`
- Customize UI in `frontend/src/components/`

