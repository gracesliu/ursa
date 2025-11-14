# Local Testing Guide

## Prerequisites Check

First, verify you have the required tools:

```bash
# Check Python version (need 3.8+)
python3 --version

# Check Node.js version (need 18+)
node --version

# Check npm version
npm --version
```

## Step-by-Step Testing

### Step 1: Test Backend

**Terminal 1 - Backend Setup:**

```bash
# Navigate to backend directory
cd /Users/grace/constellation/backend

# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

**Expected Output:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Test Backend API (in a new terminal):**

```bash
# Test root endpoint
curl http://localhost:8000/

# Test cameras endpoint
curl http://localhost:8000/api/cameras

# Test threats endpoint
curl http://localhost:8000/api/threats
```

You should see JSON responses. If you see errors, check that the server is running.

### Step 2: Test Frontend

**Terminal 2 - Frontend Setup:**

```bash
# Navigate to frontend directory
cd /Users/grace/constellation/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### Step 3: Test in Browser

1. **Open Browser**: Navigate to `http://localhost:3000`

2. **Check Connection Status**: 
   - Look at the top-right corner
   - Should show "Connected" with a green dot
   - If it shows "Disconnected", check that backend is running

3. **Verify Map Loads**:
   - You should see a map with 5 camera markers (blue circles)
   - Map should be centered on San Francisco area

4. **Check Sidebar**:
   - Control Panel should show "5 Cameras" and "0 Active Threats"
   - Threat Panel should show "No threats detected"
   - Reasoning Panel should show "No reasoning logs yet"

### Step 4: Test Demo Scenario

1. **Start Scenario**:
   - Click the "Start Scenario" button in Control Panel
   - Wait 2-3 seconds

2. **Watch for Detections**:
   - First detection should appear at camera cam_001 (after ~3 seconds)
   - Second detection at cam_002 (after ~8 more seconds)
   - Third detection at cam_003 (after ~6 more seconds)

3. **Observe Real-Time Updates**:
   - **Map**: Orange detection markers and red threat markers should appear
   - **Threat Panel**: Threats should appear with details
   - **Reasoning Panel**: AI reasoning logs should appear showing decision-making
   - **Control Panel**: Threat count should increase

4. **Verify Pattern Recognition**:
   - After 2+ detections, you should see pattern correlation
   - AI should predict next target location

5. **Stop Scenario**:
   - Click "Stop Scenario" to end the demo
   - Scenario will stop immediately

## Testing WebSocket Connection

**Manual WebSocket Test (optional):**

You can test the WebSocket connection directly using a browser console:

1. Open browser DevTools (F12)
2. Go to Console tab
3. Run:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (event) => console.log('Message:', JSON.parse(event.data));
ws.onerror = (error) => console.error('Error:', error);
```

You should see connection messages and initial state data.

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process or change port in main.py
```

**Import errors:**
```bash
# Make sure you're in the backend directory
cd backend

# Verify virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Module not found errors:**
- Make sure you're running from the `backend/` directory
- Check that `agents/` and `demo/` folders exist

### Frontend Issues

**Port 3000 already in use:**
- Vite will automatically try the next port (3001, 3002, etc.)
- Or change port in `vite.config.ts`

**npm install fails:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Map doesn't load:**
- Check browser console for errors
- Verify internet connection (map tiles load from OpenStreetMap)
- Check that Leaflet CSS is loading (inspect Network tab)

**WebSocket connection fails:**
- Verify backend is running on port 8000
- Check browser console for CORS or connection errors
- Try refreshing the page

### Common Errors

**"Cannot find module 'agents.coordinator'"**
- Solution: Run `python main.py` from the `backend/` directory, not root

**"WebSocket connection failed"**
- Solution: Make sure backend is running before opening frontend

**"Map tiles not loading"**
- Solution: Check internet connection, or use a different tile provider

## Quick Test Script

You can also test the API endpoints quickly:

```bash
# Test all endpoints
echo "Testing root endpoint..."
curl http://localhost:8000/

echo "\n\nTesting cameras endpoint..."
curl http://localhost:8000/api/cameras

echo "\n\nTesting threats endpoint..."
curl http://localhost:8000/api/threats

echo "\n\nStarting scenario..."
curl -X POST http://localhost:8000/api/scenarios/start?scenario_name=car_prowler
```

## Expected Behavior

When everything is working correctly:

1. ✅ Backend starts without errors on port 8000
2. ✅ Frontend starts without errors on port 3000
3. ✅ Browser shows map with 5 camera markers
4. ✅ Connection status shows "Connected" (green)
5. ✅ Clicking "Start Scenario" triggers detections
6. ✅ Map updates with detection and threat markers
7. ✅ Threat panel shows new threats
8. ✅ Reasoning panel shows AI thinking process
9. ✅ Pattern recognition works after 2+ detections

## Performance Notes

- First load may take a few seconds (dependencies loading)
- Map tiles load from internet (requires connection)
- Scenario runs for ~20 seconds total
- All data is in-memory (resets on server restart)

## Next Steps

Once testing is successful:
- Customize camera locations in `backend/agents/coordinator.py`
- Modify scenario timing in `backend/demo/scenarios/car_prowler.py`
- Add new scenarios in `backend/demo/scenarios/`
- Customize UI styling in `frontend/src/components/`

