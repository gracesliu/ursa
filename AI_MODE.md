# AI Mode Toggle - Hybrid Approach

## Overview

Constellation now supports **two modes** of operation:

1. **🎭 Simulated Mode** (Default) - Scripted detections for reliable demo
2. **🤖 Real AI Mode** - Computer vision analysis of actual video frames

## How It Works

### Simulated Mode
- Uses scripted detections with predefined timing
- Reliable and predictable for demos
- No video processing required
- Fast and lightweight

### Real AI Mode
- Uses OpenCV for computer vision analysis
- Analyzes actual video frames from uploaded files
- Detects motion, edges, and activity patterns
- Falls back to simulated if video not found or no detection made

## Toggling Between Modes

### In the UI
1. Open the Control Panel in the sidebar
2. Find the "AI Mode Toggle" section
3. Click the toggle switch to switch between:
   - 🎭 Simulated (OFF)
   - 🤖 Real AI (ON)

### Via API
```bash
# Get current mode
curl http://localhost:8000/api/config

# Toggle mode
curl -X POST http://localhost:8000/api/config/toggle-ai
```

### Via Environment Variable
```bash
# Start backend with real AI enabled
USE_REAL_AI=true python main.py
```

## Real AI Detection

When Real AI mode is enabled:

1. **Video Analysis**: System attempts to analyze video files in `demo/videos/`
2. **Frame Processing**: Uses OpenCV to:
   - Convert frames to grayscale
   - Detect edges using Canny edge detection
   - Calculate motion intensity
   - Classify activity types based on patterns

3. **Detection Metrics**:
   - Edge density (movement detection)
   - Motion intensity (activity level)
   - Confidence scoring based on detected patterns

4. **Activity Classification**:
   - `suspicious_movement` - High activity detected
   - `car_prowling` - Medium activity with specific patterns
   - `loitering` - Lower activity levels

## Requirements

### For Real AI Mode
- OpenCV (`opencv-python`) - Already in requirements.txt
- NumPy - Already in requirements.txt
- Video files in `demo/videos/` directory

### Installation
```bash
cd backend
pip install -r requirements.txt
```

## How Scenarios Work in Each Mode

### Simulated Mode
- Scenario triggers detections at specific times
- Uses predefined confidence levels
- Predictable sequence for demos

### Real AI Mode
- Scenario attempts to analyze video files
- If video exists and AI detects activity → uses AI detection
- If video missing or no detection → falls back to simulated
- AI confidence based on actual frame analysis

## Reasoning Panel Differences

### Simulated Mode
- Shows scripted reasoning
- Generic evidence descriptions
- Standard confidence values

### Real AI Mode
- Shows actual AI analysis metrics
- Includes edge density, motion intensity
- Shows detection method (opencv_motion_detection)
- Confidence based on real frame analysis

## Best Practices

1. **For Demos**: Use Simulated mode for reliable, predictable results
2. **For Testing AI**: Use Real AI mode with actual video files
3. **For Hackathon**: Start with Simulated, then toggle to Real AI to show both approaches
4. **Video Files**: Ensure videos are in `demo/videos/` and named correctly (cam_001.mp4, etc.)

## Troubleshooting

### Real AI Not Working
- Check that OpenCV is installed: `pip install opencv-python`
- Verify video files exist in `demo/videos/`
- Check browser console for errors
- Real AI will gracefully fall back to simulated if issues occur

### Toggle Not Responding
- Refresh the page
- Check backend is running
- Verify API endpoint: `curl http://localhost:8000/api/config`

## Future Enhancements

The current Real AI uses basic computer vision. Future improvements could include:
- YOLO object detection
- Action recognition models
- Deep learning for activity classification
- Real-time streaming analysis
- Multi-object tracking

