# Real-Time Video Analysis

## Overview

Constellation now analyzes uploaded videos in **real-time** using computer vision (YOLO + motion detection) as the video plays, completely independent of scenarios.

## How It Works

### 1. Video Upload
- Upload videos to `/Users/grace/constellation/demo/videos/`
- Name them: `cam_001.mp4`, `cam_002.mp4`, etc.

### 2. View Video Feed
- Click any camera marker on the map
- Click "View Feed" button
- Video opens in full-screen modal

### 3. Real-Time Analysis
When Real AI mode is enabled:
- **WebSocket connection** automatically starts
- **YOLO analyzes each frame** as video plays
- **Motion detection** tracks movement patterns
- **Threat detection** identifies suspicious activity
- **Annotations appear** in real-time on video

## What You'll See

### Visual Annotations
- **Blue bounding boxes** around detected people
- **Green bounding boxes** around detected vehicles
- **Labels** showing class and confidence (e.g., "person 87%")
- **Updates frame-by-frame** as video plays

### Threat Alerts
- **Red alert badge** appears when threat detected
- Shows threat type and confidence
- Threat also appears on map and in Threat Panel
- AI reasoning logged in Reasoning Panel

### Detection Stats
- **Footer shows**: "2 person(s), 1 vehicle(s)"
- Updates in real-time
- Shows current frame analysis

## Technical Details

### Analysis Pipeline
```
Video Frame
    ↓
[YOLO Object Detection]
    ├─→ People detected?
    ├─→ Vehicles detected?
    └─→ Bounding boxes
    ↓
[Motion Analysis]
    ├─→ Motion speed
    └─→ Motion consistency
    ↓
[Behavioral Analysis]
    ├─→ Person near vehicle?
    ├─→ Loitering detected?
    └─→ Suspicious movement?
    ↓
[Threat Detection]
    └─→ Suspicious score > 0.60?
    ↓
[Broadcast Results]
    ├─→ Annotations to video viewer
    └─→ Threats to main WebSocket
```

### WebSocket Stream
- **Endpoint**: `ws://localhost:8000/ws/video/{camera_id}`
- **Frequency**: Matches video FPS (typically 30fps)
- **Data**: Object annotations, threat status, detection counts
- **Auto-reconnect**: Handles disconnections gracefully

## Requirements

1. **Real AI mode enabled** (toggle in Control Panel)
2. **Video file uploaded** to `demo/videos/`
3. **YOLO installed** (`pip install ultralytics`)
4. **Backend running** on port 8000

## Features

✅ **Real-time analysis** - Frame-by-frame as video plays
✅ **Visual annotations** - Bounding boxes and labels
✅ **Threat detection** - Identifies suspicious activity
✅ **Independent of scenarios** - Works standalone
✅ **Automatic** - Starts when video opens (if Real AI enabled)
✅ **Continuous** - Analyzes entire video, loops automatically

## Usage

1. **Enable Real AI**:
   - Toggle switch in Control Panel
   - Should show "🤖 Real AI"

2. **Open video feed**:
   - Click camera marker on map
   - Click "View Feed"

3. **Watch analysis**:
   - Video plays with annotations
   - Bounding boxes appear around objects
   - Threat alerts show when detected

4. **View results**:
   - Check Threat Panel for detected threats
   - Check Reasoning Panel for AI thinking
   - Check map for threat markers

## Performance

- **Speed**: ~30-60 FPS analysis (depends on hardware)
- **Accuracy**: Uses YOLO + motion detection
- **Latency**: Near real-time (minimal delay)
- **Resource**: Moderate CPU/GPU usage

## Troubleshooting

**No annotations appearing?**
- Check Real AI mode is enabled
- Verify YOLO is installed
- Check browser console for WebSocket errors
- Ensure video file exists

**Analysis too slow?**
- Use smaller video files
- Reduce video resolution
- Use GPU if available

**WebSocket connection fails?**
- Check backend is running
- Verify camera ID is correct
- Check video file path

## Summary

The system now provides **true real-time video analysis**:
- Analyzes uploaded videos frame-by-frame
- Shows annotations as video plays
- Detects threats using computer vision
- Works completely independent of scenarios
- Provides visual feedback with bounding boxes

This is the **real AI** in action - analyzing actual video content in real-time!

