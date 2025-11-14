# Edge Density & Suspicious Activity Detection Explained

## What is Edge Density?

**Edge Density** is a computer vision metric that measures how much "detail" or "activity" is in a video frame. It's calculated by:

1. **Edge Detection**: Using the Canny edge detection algorithm to find sharp changes in brightness (edges) in the image
2. **Counting Edges**: Counting how many pixels are identified as edges
3. **Calculating Density**: Dividing the number of edge pixels by the total number of pixels in the frame

### Formula
```
Edge Density = (Number of Edge Pixels) / (Total Pixels in Frame)
```

### Example Values
- **0.0 - 0.05**: Very static scene (little to no movement/detail)
- **0.05 - 0.10**: Normal background activity
- **0.10 - 0.15**: Moderate activity (person walking, car passing)
- **0.15+**: High activity (rapid movement, multiple objects)

## How It Works in Code

```python
# Step 1: Convert frame to grayscale
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Step 2: Detect edges using Canny algorithm
edges = cv2.Canny(gray_frame, 50, 150)
# Parameters: 50 = low threshold, 150 = high threshold
# This finds edges where brightness changes significantly

# Step 3: Calculate edge density
edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
# edges > 0: Counts pixels that are edges (non-zero)
# Total pixels: height × width of the frame
```

## How Suspicious Activity is Determined

The system uses **three metrics** together to detect suspicious activity:

### 1. Edge Density
- Measures visual complexity/movement in the frame
- Higher = more activity/detail

### 2. Standard Deviation of Intensity (Motion Intensity)
- Measures how much pixel brightness varies across the frame
- Higher = more variation (movement, shadows, objects)
- Lower = uniform scene (static background)

### 3. Mean Intensity
- Average brightness of the frame
- Used for normalization

## Detection Logic

```python
# Calculate metrics
mean_intensity = np.mean(gray_frame)      # Average brightness
std_intensity = np.std(gray_frame)        # Variation in brightness
edge_density = (edge pixels) / (total pixels)

# Determine if there's activity
has_activity = edge_density > 0.1 and std_intensity > 30
```

### Thresholds Explained

**Edge Density > 0.1 (10%)**
- Means at least 10% of pixels are edges
- Indicates significant detail/movement in the scene
- Filters out static/empty scenes

**Standard Deviation > 30**
- Means pixel brightness varies significantly
- Indicates movement, shadows, or multiple objects
- Filters out uniform backgrounds

## Activity Classification

Once activity is detected, the system classifies it:

### Suspicious Movement
```python
if edge_density > 0.15 and std_intensity > 50:
    return "suspicious_movement"
```
- **High edge density** (>15%) = lots of detail/movement
- **High variation** (>50) = rapid changes
- Indicates: Fast movement, multiple objects, complex scene

### Car Prowling
```python
elif edge_density > 0.12 and std_intensity > 40:
    return "car_prowling"
```
- **Medium-high edge density** (>12%) = moderate activity
- **Medium variation** (>40) = some movement
- Indicates: Person near vehicle, checking doors, moderate activity

### Loitering
```python
elif edge_density > 0.12 and std_intensity <= 40:
    return "loitering"
```
- **Medium edge density** (>12%) = some activity
- **Lower variation** (≤40) = less movement
- Indicates: Person standing around, minimal movement

## Confidence Calculation

```python
confidence = min(0.95, 0.6 + (edge_density * 2) + (std_intensity / 100))
```

**Base confidence**: 0.6 (60%)
**Edge density contribution**: edge_density × 2
- If edge_density = 0.15 → adds 0.30 (30%)
**Intensity contribution**: std_intensity / 100
- If std_intensity = 50 → adds 0.50 (50%)
**Capped at**: 0.95 (95% max)

### Example
- Edge density: 0.15 (15%)
- Std intensity: 50
- Confidence = 0.6 + (0.15 × 2) + (50 / 100)
- Confidence = 0.6 + 0.3 + 0.5 = **1.4 → capped at 0.95 (95%)**

## Limitations & Why This is Simplified

This is a **basic computer vision approach** for demo purposes. Real production systems would use:

1. **YOLO/Object Detection**: Identify specific objects (people, cars, etc.)
2. **Action Recognition Models**: Classify specific behaviors (walking, running, loitering)
3. **Deep Learning**: Train models on labeled security footage
4. **Tracking**: Follow objects across frames
5. **Temporal Analysis**: Analyze sequences of frames, not just single frames

## Visual Example

### Low Edge Density (Static Scene)
```
Frame: [mostly uniform background]
Edges: [few edge pixels]
Density: 0.03 (3%)
Result: No activity detected
```

### High Edge Density (Active Scene)
```
Frame: [person walking, car in background, shadows]
Edges: [many edge pixels - person outline, car edges, etc.]
Density: 0.18 (18%)
Result: Suspicious movement detected
```

## Why Edge Detection?

Edges are good indicators of:
- **Objects**: People, vehicles, structures have edges
- **Movement**: Moving objects create more edges
- **Activity**: Active scenes have more visual complexity
- **Changes**: New objects introduce new edges

It's a simple but effective first-pass filter before more sophisticated analysis.

