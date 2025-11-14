# Wildlife & Wildfire Video Files

## 📍 Upload Location

**Upload your wildlife and fire videos here:**
```
/Users/grace/ursa/demo/videos/
```

## 📝 File Naming

You can name your video files anything you want, but update the camera configuration in `backend/agents/coordinator.py` to match:

Example:
- `wildlife_bear.mp4` - Bear detection video
- `wildlife_deer.mp4` - Deer detection video  
- `wildfire.mp4` - Fire/smoke detection video
- `cam_001.mp4` - Camera 1 (123 Oak St)
- `cam_002.mp4` - Camera 2 (456 Pine Ave)
- `cam_003.mp4` - Camera 3 (789 Elm Dr)
- `cam_004.mp4` - Camera 4 (321 Maple Ln)
- `cam_005.mp4` - Camera 5 (654 Cedar Rd)

## 🎬 Supported Formats

- **MP4** (recommended - H.264 codec)
- **MOV**
- **WebM**

## 📤 How to Upload

### Method 1: Drag and Drop
1. Open Finder (Mac) or File Explorer (Windows)
2. Navigate to: `/Users/grace/constellation/demo/videos/`
3. Drag your video files into this folder
4. Rename them to match camera IDs (cam_001.mp4, etc.)

### Method 2: Terminal
```bash
# Copy your video files
cp /path/to/your/video.mp4 /Users/grace/constellation/demo/videos/cam_001.mp4
```

### Method 3: VS Code/Cursor
1. Open the `demo/videos/` folder in your editor
2. Right-click → "Upload Files" or drag files in
3. Rename as needed

## ✅ After Uploading

1. **Restart backend** (if running):
   ```bash
   # Stop with Ctrl+C, then:
   cd backend
   python main.py
   ```

2. **Open app** at `http://localhost:3000`

3. **Enable Real AI mode** - Toggle switch in Control Panel

4. **Click camera marker** on map

5. **Click "View Feed"** - See video with real-time AI annotations!

## 🎯 What You'll See

With Real AI enabled, you'll see:
- **Bounding boxes** around detected animals (bears, deer, birds, etc.)
- **Fire/smoke detection** with color analysis
- **Labels** showing animal type and confidence (e.g., "bear 85%")
- **Real-time analysis** as video plays
- **Detection count** showing number of animals detected
- **Wildfire alerts** with critical severity when fire is detected

## 💡 Tips

- Keep videos under 50MB for best performance
- Use MP4 format with H.264 codec
- Videos loop automatically
- Analysis happens frame-by-frame in real-time
- Make sure Real AI mode is ON for annotations

## 🧪 Testing

Test that videos are accessible:
```bash
curl -I http://localhost:8000/videos/cam_001.mp4
```

Should return HTTP 200 if file exists.

## 📋 Example Structure

```
demo/videos/
├── cam_001.mp4  ← Your video here
├── cam_002.mp4  ← Your video here
├── cam_003.mp4  ← Your video here
├── cam_004.mp4  ← Your video here
└── cam_005.mp4  ← Your video here
```

## ⚠️ Troubleshooting

**Video not showing?**
- Check file name matches exactly (case-sensitive)
- Verify file is in `demo/videos/` directory
- Restart backend after adding files
- Check browser console for errors

**No annotations?**
- Make sure Real AI mode is enabled (toggle in Control Panel)
- Check that YOLO is installed: `pip install ultralytics`
- Verify backend console shows "YOLO model loaded successfully"
- For fire detection: Make sure video has visible red/orange/yellow flames or smoke
- For wildlife: Make sure animals are clearly visible in the video
