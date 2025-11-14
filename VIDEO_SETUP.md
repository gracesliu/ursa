# Video Setup Guide

## How to Add Camera Videos

### Step 1: Prepare Your Video Files

1. **Get your video files** ready (MP4 format recommended)
2. **Name them** according to camera IDs:
   - `cam_001.mp4` for Camera 1
   - `cam_002.mp4` for Camera 2
   - `cam_003.mp4` for Camera 3
   - `cam_004.mp4` for Camera 4
   - `cam_005.mp4` for Camera 5

### Step 2: Upload Videos

**Option A: Using File Explorer/Finder**
- Navigate to `/Users/grace/constellation/demo/videos/`
- Copy your video files into this folder
- Make sure they're named correctly (e.g., `cam_001.mp4`)

**Option B: Using Terminal**
```bash
# Navigate to project root
cd /Users/grace/constellation

# Copy your videos (replace with your actual file paths)
cp /path/to/your/video1.mp4 demo/videos/cam_001.mp4
cp /path/to/your/video2.mp4 demo/videos/cam_002.mp4
# ... etc
```

**Option C: Drag and Drop in Cursor/VS Code**
- Open the `demo/videos/` folder in your file explorer
- Drag and drop your video files
- Rename them if needed

### Step 3: Verify Files

Check that your files are in the right place:
```bash
ls -la demo/videos/
```

You should see:
```
cam_001.mp4
cam_002.mp4
cam_003.mp4
cam_004.mp4
cam_005.mp4
```

### Step 4: Restart Backend (if running)

If your backend server is running, restart it:
```bash
# Stop the server (Ctrl+C)
# Then restart:
cd backend
python main.py
```

### Step 5: Test in Browser

1. Open the frontend app (`http://localhost:3000`)
2. Click on any camera marker on the map
3. Click the **"View Feed"** button in the popup
4. The video should play in a modal overlay

## Video Requirements

- **Format**: MP4 (H.264 codec recommended)
- **Size**: Keep under 50MB for best performance
- **Resolution**: Any (will scale to fit)
- **Duration**: Any length (will loop automatically)

## Troubleshooting

### Video doesn't play
- Check that the file name matches exactly (e.g., `cam_001.mp4`)
- Verify the file is in `demo/videos/` directory
- Check browser console for errors
- Make sure backend is running and serving files

### "Video not found" error
- Double-check file naming (case-sensitive)
- Verify file is in the correct directory
- Restart backend server after adding files

### Video won't load
- Check file format (MP4 recommended)
- Verify file isn't corrupted
- Check browser supports the video codec

## File Structure

```
constellation/
├── demo/
│   └── videos/
│       ├── cam_001.mp4  ← Your video here
│       ├── cam_002.mp4  ← Your video here
│       ├── cam_003.mp4  ← Your video here
│       ├── cam_004.mp4  ← Your video here
│       └── cam_005.mp4  ← Your video here
```

## Accessing Videos

Once uploaded, videos are accessible at:
- `http://localhost:8000/videos/cam_001.mp4`
- `http://localhost:8000/videos/cam_002.mp4`
- etc.

You can test this directly in your browser while the backend is running!

