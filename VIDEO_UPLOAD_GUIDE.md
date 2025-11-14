# Video Upload Guide

## Where to Upload Videos

**Upload your videos to:**
```
/Users/grace/constellation/demo/videos/
```

## File Naming

Name your videos exactly as follows:
- `cam_001.mp4` - For Camera 1 (123 Oak St)
- `cam_002.mp4` - For Camera 2 (456 Pine Ave)
- `cam_003.mp4` - For Camera 3 (789 Elm Dr)
- `cam_004.mp4` - For Camera 4 (321 Maple Ln)
- `cam_005.mp4` - For Camera 5 (654 Cedar Rd)

## Supported Formats

- **MP4** (recommended - H.264 codec)
- **MOV**
- **WebM**

## How to Upload

### Option 1: Drag and Drop
1. Open Finder (Mac) or File Explorer (Windows)
2. Navigate to `/Users/grace/constellation/demo/videos/`
3. Drag your video files into this folder
4. Rename them to match the camera IDs (cam_001.mp4, etc.)

### Option 2: Terminal
```bash
# Copy videos to the directory
cp /path/to/your/video.mp4 /Users/grace/constellation/demo/videos/cam_001.mp4
```

### Option 3: VS Code/Cursor
1. Open the `demo/videos/` folder in your editor
2. Right-click → "Upload Files" or drag files in
3. Rename as needed

## After Uploading

1. **Restart the backend** if it's running:
   ```bash
   # Stop backend (Ctrl+C)
   # Then restart:
   cd backend
   python main.py
   ```

2. **Open the app** in browser (`http://localhost:3000`)

3. **Enable Real AI mode** - Toggle the switch in Control Panel

4. **Click a camera marker** on the map

5. **Click "View Feed"** - You'll see the video with real-time AI annotations!

## What You'll See

When viewing a video feed with Real AI enabled:
- **Bounding boxes** around detected people (blue)
- **Bounding boxes** around detected vehicles (green)
- **Labels** showing object class and confidence
- **Threat indicators** when suspicious activity is detected
- **Real-time analysis** as the video plays

## Tips

- Keep videos under 50MB for best performance
- Use MP4 format with H.264 codec
- Videos will loop automatically
- Analysis happens in real-time as video plays
- Make sure Real AI mode is enabled for annotations

## Testing

After uploading, test that videos are accessible:
```bash
# Should return video file
curl -I http://localhost:8000/videos/cam_001.mp4
```

If you get a 404, check:
- File name matches exactly (case-sensitive)
- File is in `demo/videos/` directory
- Backend is running

