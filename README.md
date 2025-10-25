# EADA Pro - Edge AI Display Adaptation System

An intelligent, privacy-preserving adaptive workspace assistant that optimizes accessibility, ergonomics, and productivity through real-time AI.

## 🎉 Phase 2 Complete - Advanced Gesture Recognition!

**Latest Updates (v2.1):**
- ✋ Completely rebuilt gesture control system with dual-mode operation
- � **NEW**: Finger counting gestures (0-5 fingers) for precise control
- 🚀 Instant response with zero smoothing delay
- � Full 0-100% range control for volume and brightness
- � Position-based + movement-based gesture tracking
- 🔧 Adaptive finger detection for accurate recognition
- ⚡ Smart cooldown system prevents gesture spam

**Quick Start with Gestures:**
```powershell
python run.py
```
Then use finger gestures:
- **0 fingers (fist)**: Toggle gesture control ON/OFF
- **1 finger**: Volume control (move left-right, 0-100%)
- **2 fingers**: Brightness control (move left-right, 0-100%)  
- **3 fingers**: Play/Pause media
- **4 fingers**: Next track
- **5 fingers**: Previous track

See [Gesture Recognition System](#gesture-recognition-system) for full documentation.

## Features

- 🎯 **Automatic Brightness & Volume Control**: Adapts based on user distance and environment
- 👤 **Face Detection & Counting**: Tracks multiple users with weighted adaptation
- ✋ **Hand Gesture Recognition**: Control volume, brightness, and media with hand gestures
- 🌍 **Environmental Awareness**: Adjusts to ambient lighting and background noise
- 🎵 **Audio Intelligence**: Analyzes background music and maintains optimal SNR
- ⏸️ **Presence Detection**: Auto-pause media when no user is detected
- 🔒 **Privacy-First**: All processing happens on-device (edge AI)
- 📊 **Real-Time Metrics**: Live dashboard showing system status
- 📺 **TV & Billboard Ready**: Optimized for public displays

## System Requirements

- **Python 3.10 or 3.11** (MediaPipe not compatible with 3.12+)
- Webcam
- Microphone (optional)
- Windows OS (for brightness/volume control)

## Installation

### Prerequisites

**Important:** You need Python 3.10 or 3.11. MediaPipe does not support Python 3.12+.

Check your Python version:
```powershell
python --version
```

If you have Python 3.12 or newer, please install Python 3.10 or 3.11 from [python.org](https://www.python.org/downloads/).

### Quick Setup (Windows)

```powershell
# Run the automated setup script
.\setup.ps1
```

### Manual Installation

#### 1. Create Virtual Environment

```powershell
# With Python 3.10
py -3.10 -m venv venv

# Or with Python 3.11
py -3.11 -m venv venv

# Activate
.\venv\Scripts\Activate.ps1
```

#### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

See `INSTALL.md` for detailed installation instructions and troubleshooting.

## Quick Start

### Run the system:

```powershell
python run.py
```

Or directly:

```powershell
python src/main.py
```

### Controls:

- **Press 'q'**: Quit the application
- **Finger-Based Gesture Controls** (v2.1):
  - **0 Fingers (Fist)**: Toggle gesture control ON/OFF (instant response)
  - **1 Finger**: Volume control - move hand left/right (0-100% range)
  - **2 Fingers**: Brightness control - move hand left/right (0-100% range)
  - **3 Fingers**: Play/Pause media (2s cooldown)
  - **4 Fingers**: Next track (2s cooldown)
  - **5 Fingers**: Previous track (2s cooldown)
- **Gesture Features**:
  - Instant response (no smoothing delay)
  - Adaptive finger detection (works with different hand sizes)
  - Multi-point validation (accurate finger counting)
  - Position + movement based control
  - 2-second cooldown on media gestures prevents spam
  - Synchronized UI display shows actual applied values
- The system will automatically:
  - Detect faces and count them
  - Adjust brightness based on distance and ambient light
  - Adjust volume based on distance and background noise
  - Pause media when no faces detected for 3 seconds

## Configuration

Edit `src/config/settings.py` to customize:

- Camera resolution and FPS
- Detection thresholds
- Adaptation parameters
- Feature enable/disable flags
- Weighting algorithms
- Gesture recognition settings

### Gesture Recognition Configuration

```python
# Gesture Recognition Settings (v2.1)
GESTURE_DETECTION_CONFIDENCE = 0.85  # High confidence for accurate detection
GESTURE_COOLDOWN_SECONDS = 2.0  # Cooldown for discrete gestures (3,4,5 fingers)
GESTURE_STABILITY_THRESHOLD = 2  # Frames required for stable gesture (media controls only)

# Finger Detection Thresholds (Adaptive)
THUMB_THRESHOLD_MULTIPLIER = 0.18  # 18% of hand size for thumb detection
FINGER_THRESHOLD_MULTIPLIER = 0.12  # 12% of hand size for finger detection
MIN_THUMB_THRESHOLD = 25  # Minimum 25px threshold
MIN_FINGER_THRESHOLD = 15  # Minimum 15px threshold

# Control Ranges (Full Range)
VOLUME_MIN = 0.0  # 0% minimum volume
VOLUME_MAX = 1.0  # 100% maximum volume
BRIGHTNESS_MIN = 0  # 0% minimum brightness
BRIGHTNESS_MAX = 100  # 100% maximum brightness
```

## Gesture Recognition System

### Built-in Gestures (v2.1 - Finger-Based System)

EADA Pro uses an advanced finger counting system for intuitive gesture control:

#### 0. Gesture Toggle (Fist - 0 Fingers)
- **Gesture**: Close all fingers into a fist
- **Action**: Toggle gesture recognition ON/OFF
- **Features**: 
  - Instant response (no cooldown, no stability check)
  - Double validation (requires all fingers truly down)
  - Strict detection prevents false triggers
  - State synchronized with system manager
- **Use**: Enable/disable all gesture controls quickly

#### 1. Volume Control (1 Finger - Index)
- **Gesture**: Extend only index finger, move hand left-right
- **Control Mode**: Position-based + movement-based
- **Range**: 0-100% (full volume range)
- **Features**:
  - No smoothing for instant response
  - Continuous control (no cooldown)
  - X-axis position maps to volume percentage
  - Movement delta provides fine adjustments
  - Overrides distance-based volume control
- **Mapping**: Left edge = 0%, Right edge = 100%

#### 2. Brightness Control (2 Fingers - Index + Middle)
- **Gesture**: Extend index and middle fingers, move hand left-right
- **Control Mode**: Position-based + movement-based
- **Range**: 0-100% (full brightness range)
- **Features**:
  - No smoothing for instant response
  - Continuous control (no cooldown)
  - X-axis position maps to brightness percentage
  - Movement delta provides fine adjustments
  - Overrides distance-based brightness control
- **Mapping**: Left edge = 0%, Right edge = 100%

#### 3. Play/Pause (3 Fingers - Index + Middle + Ring)
- **Gesture**: Extend three fingers
- **Action**: Toggle media playback
- **Features**:
  - 2-second cooldown between activations
  - 2-frame stability check (prevents false triggers)
  - Works with any media player
- **Use**: Quick play/pause control without touching keyboard

#### 4. Next Track (4 Fingers - All except thumb)
- **Gesture**: Extend all four fingers
- **Action**: Skip to next track/video
- **Features**:
  - 2-second cooldown between activations
  - 2-frame stability check
  - Media key simulation
- **Use**: Navigate to next media item

#### 5. Previous Track (5 Fingers - All fingers)
- **Gesture**: Extend all five fingers (open hand)
- **Action**: Go to previous track/video
- **Features**:
  - 2-second cooldown between activations
  - 2-frame stability check
  - Media key simulation
- **Use**: Navigate to previous media item

### Advanced Gesture Features (v2.1)

#### Adaptive Finger Detection
- **Dynamic Thresholds**: Adjusts based on detected hand size
  - Thumb detection: 18% of hand size (min 25px)
  - Finger detection: 12% of hand size (min 15px)
- **Multi-Point Validation**: Checks multiple joints for accuracy
  - Thumb: IP joint comparison (not MCP)
  - Fingers: Tip vs PIP + PIP vs MCP validation
- **Hand Type Awareness**: Separate logic for left/right hands
- **Result**: Works consistently across different hand sizes and distances

#### Dual Control Modes
1. **Position-Based Control**:
   - Maps hand X-position to 0-100% value
   - Wrist landmark used as reference point
   - Provides absolute positioning

2. **Movement-Based Control**:
   - Tracks hand movement delta
   - Provides incremental adjustments
   - Combined with position for smooth control

#### Intelligent Cooldown System
- **Continuous Gestures (0, 1, 2 fingers)**: No cooldown
  - Toggle and volume/brightness respond instantly
  - Allows real-time continuous adjustment
  
- **Discrete Gestures (3, 4, 5 fingers)**: 2-second cooldown
  - Prevents accidental repeated triggers
  - Registered gesture tracking prevents re-triggering
  - Cooldown persists even if hand removed

#### Stability Requirements
- **Instant Response (0, 1, 2 fingers)**: No stability check
  - Fist toggle responds immediately
  - Volume/brightness update every frame
  
- **Stable Detection (3, 4, 5 fingers)**: 2-frame requirement
  - Prevents false media control triggers
  - Gesture must be held consistently
  - Reduces accidental activations

#### Visual Feedback
- **Real-Time Display**: Shows current finger count and gesture
- **Synchronized Values**: UI displays actual applied volume/brightness
- **State Indicators**: 
  - Gestures: ON/OFF status in top-right
  - Current gesture action displayed
  - Finger count visualization
- **Hand Landmarks**: Optional landmark overlay for debugging

### Implementing Custom Gestures (v2.1)

The finger-based gesture system is extensible for custom implementations:

#### Understanding the Finger Counting System

```python
# Finger counting returns (finger_count, fingers_list)
# fingers_list = [thumb, index, middle, ring, pinky]
# Example: [1, 1, 0, 0, 0] = thumb and index up (2 fingers)

finger_count, fingers = self._count_fingers(hand)
# finger_count: 0-5 (total fingers up)
# fingers: [0/1, 0/1, 0/1, 0/1, 0/1] for each finger
```

#### Step 1: Add Custom Finger Combination

Edit `src/modules/perception/gesture_controller.py` in `_classify_gesture()`:

```python
def _classify_gesture(self, finger_count: int, fingers: List[int], 
                     x_percent: float, y_percent: float,
                     delta_x: float, delta_y: float):
    
    # Custom gesture: Thumb + Pinky only (rock sign)
    if finger_count == 2 and fingers[0] == 1 and fingers[4] == 1:
        # Only thumb and pinky are up
        if not self.in_cooldown:
            self.in_cooldown = True
            self.cooldown_start_time = time.time()
            return ('rock_sign', None)
    
    # Custom gesture: Specific three-finger combo
    if finger_count == 3 and fingers == [0, 1, 1, 1, 0]:
        # Index + Middle + Ring only
        return ('three_middle_fingers', x_percent)
    
    # ... existing gesture logic continues ...
```

#### Step 2: Handle Custom Gesture in System Manager

In `src/core/system_manager.py`:

```python
# In the gesture processing loop
for gesture in gestures:
    if gesture == 'rock_sign':
        self.logger.info("Rock sign detected! 🤘")
        self._custom_rock_action()
    
    elif gesture == 'three_middle_fingers':
        # Use the position value for custom control
        custom_value = gesture_adjustment
        self._custom_three_finger_action(custom_value)
```

#### Step 3: Customize Detection Thresholds

For stricter or more lenient finger detection:

```python
# In gesture_controller.py __init__ or settings.py

# More strict (fewer false positives)
thumb_threshold = max(30, hand_size * 0.20)  # Higher = stricter
finger_threshold = max(20, hand_size * 0.15)

# More lenient (easier to trigger)
thumb_threshold = max(15, hand_size * 0.12)  # Lower = easier
finger_threshold = max(10, hand_size * 0.08)
```

#### Step 4: Add Custom Cooldown Logic

```python
# For gestures that need specific cooldown
CUSTOM_GESTURE_COOLDOWN = 3.0  # 3 seconds

if gesture_type == 'rock_sign':
    if time.time() - self.last_rock_sign_time > CUSTOM_GESTURE_COOLDOWN:
        self.last_rock_sign_time = time.time()
        return ('rock_sign', None)
```

### Advanced Gesture Features

#### Hand Landmark Access (CVZone + MediaPipe)
The system provides access to 21 hand landmarks:

```python
# Key landmarks (CVZone format)
lmList = hand['lmList']  # 21 landmarks with [x, y, z] coordinates

# Landmark indices
WRIST = 0
THUMB_CMC = 1
THUMB_MCP = 2
THUMB_IP = 3
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_PIP = 6
INDEX_DIP = 7
INDEX_TIP = 8
# ... and so on for middle, ring, pinky

# Access coordinates
thumb_tip_x = lmList[4][0]  # X coordinate
thumb_tip_y = lmList[4][1]  # Y coordinate
thumb_tip_z = lmList[4][2]  # Z depth (normalized)

# Calculate hand size for adaptive thresholds
hand_size = abs(lmList[0][1] - lmList[9][1])  # Wrist to middle MCP distance
```

#### Finger Detection Algorithm

The system uses a sophisticated multi-point detection algorithm:

```python
# Thumb detection (horizontal comparison)
thumb_tip_x = lmList[4][0]
thumb_ip_x = lmList[3][0]
thumb_threshold = max(25, hand_size * 0.18)  # Adaptive threshold

if hand_type == 'Right':
    thumb_up = thumb_tip_x > thumb_ip_x + thumb_threshold
else:  # Left hand
    thumb_up = thumb_tip_x < thumb_ip_x - thumb_threshold

# Other fingers (vertical comparison with multi-point check)
tip_y = lmList[tip_id][1]
pip_y = lmList[pip_id][1]
mcp_y = lmList[mcp_id][1]

finger_threshold = max(15, hand_size * 0.12)

# Two conditions must be met:
# 1. Tip is clearly above PIP
tip_above_pip = tip_y < pip_y - finger_threshold
# 2. PIP is not below MCP (finger not curled)
pip_not_below_mcp = pip_y <= mcp_y + (finger_threshold * 0.5)

finger_up = tip_above_pip and pip_not_below_mcp
```

#### Position and Movement Tracking

```python
# Get hand position as percentage (0-100)
def _get_hand_position(self, hand, frame_width, frame_height):
    wrist = hand['lmList'][0]  # Use wrist as reference
    x_percent = (wrist[0] / frame_width) * 100
    y_percent = (wrist[1] / frame_height) * 100
    return x_percent, y_percent

# Track movement delta for fine adjustments
def _get_movement_delta(self, current_x, current_y):
    delta_x = current_x - self.last_hand_x
    delta_y = current_y - self.last_hand_y
    self.last_hand_x = current_x
    self.last_hand_y = current_y
    return delta_x, delta_y

# Combined control value
combined_value = position_value + (movement_delta * 2)
```

### Gesture Performance Tips (v2.1)

1. **Detection Confidence**: Increased to 0.85 for accurate hand tracking
2. **No Smoothing**: Instant response with `smooth=False` on gesture controls
3. **Adaptive Thresholds**: Automatically adjusts based on hand size
4. **Multi-Point Validation**: Reduces false finger detections
5. **Smart Cooldown**: Only applies to discrete gestures (3,4,5 fingers)
6. **Stability Checks**: Only required for media controls, not volume/brightness
7. **Strict Fist Detection**: Double validation prevents false triggers
8. **State Synchronization**: UI always shows actual applied values
9. **Efficient Processing**: Direct gesture list processing (no smoothing overhead)
10. **Single Hand Mode**: maxHands=1 for optimal performance

### Gesture Recognition Best Practices

- **Lighting**: Works in various lighting conditions with adaptive thresholds
- **Distance**: Optimal detection at 40-100cm from camera
- **Hand Position**: Keep hand clearly visible, avoid occlusion
- **Finger Extension**: Extend fingers fully for accurate counting
- **Fist Gesture**: Close all fingers completely for reliable toggle
- **Movement**: Smooth left-right movements for volume/brightness control
- **Media Gestures**: Hold finger position steady for 2 frames (~66ms)
- **Cooldown Awareness**: 2-second delay between media control gestures
- **Visual Feedback**: Watch the UI to confirm gesture detection
- **Toggle State**: Check "Gestures: ON/OFF" indicator in top-right corner

## Project Structure

```
EADA_Pro/
├── src/
│   ├── config/          # Configuration settings
│   ├── core/            # System manager and orchestration
│   ├── modules/
│   │   ├── perception/  # Camera, audio, face detection
│   │   ├── adaptation/  # Brightness, volume, weighted adapter
│   │   └── intelligence/# Environment & audio analysis
│   └── main.py          # Main entry point
├── requirements.txt     # Python dependencies
├── run.py              # Quick start script
└── README.md           # This file
```

## Key Algorithms

### Distance Estimation
- **Method**: Face width triangulation
- **Formula**: Distance = (Known Width × Focal Length) / Perceived Width

### Weighted Adaptation
- **Distance Weighting**: Closer faces = 2x weight
- **Spatial Weighting**: Center faces = 1.5x weight
- **Application**: Weighted average for brightness/volume

### Environmental Adaptation
- **Ambient Light**: Camera-based illuminance estimation
- **Background Noise**: Audio frequency analysis
- **SNR Maintenance**: Target 15-20dB signal-to-noise ratio

## Features Implemented

### Phase 1: Core Functionality ✅
- [x] Camera capture and video processing
- [x] Face detection with MediaPipe Face Mesh
- [x] Two-stage face detection (long-range + accurate)
- [x] Distance estimation via triangulation
- [x] Adaptive brightness control (30-100%)
- [x] Adaptive volume control with steep curve (20-100%)
- [x] Presence detection with media pause/resume
- [x] Stability logic for crowd scenarios
- [x] Grace range (±5cm) to prevent micro-adjustments

### Phase 2: Gesture Recognition ✅
- [x] Hand detection with MediaPipe Hands (CVZone wrapper)
- [x] Finger-based gesture classification (0-5 fingers)
- [x] Volume control via 1 finger with position + movement tracking
- [x] Brightness control via 2 fingers with position + movement tracking
- [x] Media controls: 3=play/pause, 4=next, 5=previous
- [x] Gesture toggle with fist (0 fingers)
- [x] Adaptive finger detection with multi-point validation
- [x] Intelligent cooldown system (2s for discrete gestures)
- [x] Instant response (no smoothing on gesture controls)
- [x] Full 0-100% range for volume and brightness
- [x] State synchronization between gesture controller and UI
- [x] Real-time visual feedback with accurate value display
- [x] Priority override (gestures override distance-based control)

### Phase 3: Intelligence & Multi-User ✅
- [x] Face counting with position tracking
- [x] Weighted adaptation (closer faces = higher weight)
- [x] Ambient light detection via camera
- [x] Background music analysis
- [x] Environmental adaptation algorithms
- [x] Multi-face tracking and coordination

### Phase 4: API & Dashboard (Planned)
- [ ] FastAPI REST endpoints
- [ ] WebSocket live streaming
- [ ] React dashboard with metrics
- [ ] SQLite logging
- [ ] Face count display on dashboard

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Face Detection Accuracy | ≥95% | ✅ |
| System Latency | ≤50ms | ✅ |
| Face Counting Accuracy | ≥95% | ✅ |
| Weighted Adaptation | ≥90% | ✅ |
| Gesture Recognition | ≥90% | ✅ |
| Gesture Latency | <200ms | ✅ |
| FPS | ≥30 | ✅ (Optimized) |

### FPS Optimizations

The system includes several performance optimizations to maintain high FPS:

1. **Frame Skipping for Expensive Operations**
   - Face Mesh processing: Every 3rd frame (cached for 2 frames)
   - Gesture detection: Every 2nd frame
   - Ambient light monitoring: Every 5th frame
   - Audio analysis: Every 10th frame

2. **Reduced Camera Resolution**
   - Default: 960x540 (down from 1280x720)
   - Maintains detection accuracy while improving processing speed
   - Configurable in `settings.py`

3. **Optimized Display Rendering**
   - Simplified overlay rendering (no semi-transparent backgrounds)
   - Direct frame reference instead of copies when possible
   - Reduced text rendering overhead

4. **Smart Caching**
   - Cached face detection results for tracking
   - Cached gesture results between detection frames
   - Cached environmental monitoring results

**Expected FPS**: 25-35 FPS (depending on hardware and number of faces/hands detected)

**Note**: All optimizations maintain full functionality - no features are disabled, just processed less frequently where appropriate.

## Phase 2 Summary

### What's New in Phase 2 (v2.1)

**Completely Rebuilt Gesture Recognition System** - Advanced finger-based control:

1. **Core Gesture Engine (v2.1)**
   - CVZone HandDetector integration with high confidence (0.85)
   - Custom finger counting algorithm with adaptive thresholds
   - Multi-point validation for accurate detection
   - Dual-mode control: position-based + movement-based
   - No smoothing for instant response

2. **Finger-Based Gesture Controls**
   - 0 fingers (fist): Toggle gestures ON/OFF
   - 1 finger: Volume control (0-100% range)
   - 2 fingers: Brightness control (0-100% range)
   - 3 fingers: Play/pause media
   - 4 fingers: Next track
   - 5 fingers: Previous track

3. **Advanced Detection Features**
   - Adaptive thresholds based on hand size (18% thumb, 12% fingers)
   - Multi-point finger validation (tip vs PIP, PIP vs MCP)
   - Hand-type awareness (left/right hand separate logic)
   - Strict fist detection with double validation
   - Position + movement delta tracking for precise control

4. **Smart Control System**
   - Intelligent cooldown (2s for discrete gestures only)
   - Stability checks only for media controls (2 frames)
   - Instant response for continuous controls (volume/brightness)
   - Registered gesture tracking prevents repetition
   - State synchronization between controller and UI

5. **Performance Optimizations**
   - Zero smoothing delay on gesture controls
   - Direct gesture list processing
   - Efficient frame-by-frame detection
   - Single hand mode for optimal performance
   - Full 0-100% range utilization

### Gesture Control Architecture

**Detection Pipeline:**
1. CVZone HandDetector detects hand with 21 landmarks
2. Custom `_count_fingers()` with adaptive thresholds
3. `_get_hand_position()` maps wrist to screen percentage
4. `_get_movement_delta()` tracks hand motion
5. `_classify_gesture()` determines action and value
6. System manager applies controls with `smooth=False`

**Finger Detection Algorithm:**
- Thumb: Horizontal IP joint comparison (hand-type aware)
- Other fingers: Vertical tip vs PIP with curled-finger check
- Adaptive thresholds: Scales with detected hand size
- Multi-point validation: Two conditions must be met
- Minimum thresholds: 25px thumb, 15px fingers

**Control Value Calculation:**
```python
# Position-based (0-100% from hand X position)
position_value = (wrist_x / frame_width) * 100

# Movement-based (delta from last frame)
movement_adjustment = (current_x - last_x) * 2

# Combined value
combined = position_value + movement_adjustment
final_value = clamp(combined, 0, 100)
```

### Gesture vs Distance Control

**Blended Control System:**
- **Distance control**: Always active for hands-free automatic adaptation
- **Gesture control**: Overrides distance control when active (100% gesture)
- **Toggle control**: Fist gesture enables/disables all gesture controls
- **Smooth transitions**: Gestures provide precise manual control on top of automatic

**Responsiveness (v2.1):**
- Gesture detection: No smoothing, instant response
- Volume/brightness: Updates every frame (no delay)
- Media controls: 2-frame stability check (~66ms)
- Cooldown: 2 seconds for discrete gestures only
- Toggle: Instant response (no cooldown)

**Use Cases:**
- **Distance control**: Primary hands-free automatic adaptation
- **Gesture control**: Precise manual adjustments (0-100% full range)
- **Combined mode**: Automatic base control + manual override capability
- **Toggle**: Quick enable/disable without touching settings

### System Integration

**Seamless Module Integration:**
- GestureController (v2.1) added to perception layer
- System Manager orchestrates gesture + face detection
- Shared frame processing for efficiency
- Unified display with face + hand landmarks
- State synchronization between modules

**Configuration Flexibility:**
- Enable/disable gesture recognition via `ENABLE_GESTURE_RECOGNITION`
- Adjust detection confidence (default 0.85)
- Configure cooldown duration (default 2.0s)
- Adjust stability threshold (default 2 frames)
- Configure adaptive thresholds in `settings.py`
- Full range control (0-100%) for both volume and brightness
- Toggle visual feedback independently

**Recent Improvements (v2.1):**
- Removed all smoothing for instant response
- Extended ranges from 30-70% to 0-100%
- Fixed fist gesture toggle functionality
- Improved finger detection accuracy (adaptive thresholds)
- Added multi-point validation for reliable counting
- Synchronized UI displays with actual applied values
- Implemented intelligent cooldown system
- Added strict fist validation to prevent false triggers

## Troubleshooting

### Camera not working
- Check camera index in `settings.py`
- Ensure no other app is using the camera
- Try different camera indices (0, 1, 2...)

### Brightness/Volume control not working
- System runs in simulation mode if controls unavailable
- Check Windows permissions
- Verify dependencies installed correctly

### Low FPS
- Reduce camera resolution in `settings.py` (already optimized to 960x540)
- Enable frame skipping (already enabled)
- Disable unnecessary features via feature flags
- Close other applications using the camera/CPU
- **System is already optimized** with intelligent frame skipping

### High CPU usage
- Frame skipping is enabled by default for expensive operations
- Gesture detection runs every 2nd frame
- Face Mesh processing runs every 3rd frame
- Consider disabling gesture recognition if not needed: `ENABLE_GESTURE_RECOGNITION = False`

## Development

### Adding New Features

1. Create module in appropriate package
2. Register in `__init__.py`
3. Integrate in `system_manager.py`
4. Update configuration in `settings.py`

### Testing

```powershell
# Test full system
python test.py

# Test gesture recognition only
python test_gestures.py

# Test volume/brightness controls
python test_controls.py
```

## Project Status

### Current Phase: Phase 2 Complete ✅

**Phase 1: Core Functionality** (Complete)
- Face detection with distance estimation
- Adaptive brightness and volume control
- Presence detection and media pause/resume
- Stability logic for crowd scenarios
- Multi-face tracking and weighted adaptation

**Phase 2: Gesture Recognition** (Complete - v2.1)
- Face detection with distance estimation
- Adaptive brightness and volume control
- Presence detection and media pause/resume
- Stability logic for crowd scenarios
- Multi-face tracking and weighted adaptation
- **Advanced finger-based gesture system**
- **0-5 finger gesture mappings with instant response**
- **Full 0-100% range control with no smoothing**
- **Adaptive finger detection with multi-point validation**
- **Intelligent cooldown and stability checks**
- **State synchronization and visual feedback**

**Phase 3: API & Dashboard** (Planned)
- FastAPI REST endpoints
- WebSocket live streaming
- React dashboard with real-time metrics
- Face count and gesture displays
- SQLite data logging

**Phase 4+: Advanced Features** (Planned)
- Voice command integration
- Enterprise analytics
- Cloud synchronization
- Edge deployment (Synaptics Astra SDK)
- Security and anomaly detection

## Documentation

See the following files for detailed information:
- `README.md` - This file: Installation, usage, and gesture documentation
- `PHASE2_SUMMARY.md` - Complete Phase 2 implementation summary
- `EADA_Pro_Plan.md` - Project plan and phases
- `EADA_Pro_Technical_Specification.md` - Technical details
- `EADA_Pro_TV_Billboard_Applications.md` - Use cases
- `CHANGELOG.md` - Version history and updates
- `tasks.md` - Implementation tasks and status
- `tasks_testing.md` - Testing requirements and metrics

### Quick Reference

### Gesture Controls (v2.1 - Finger-Based System)

| Gesture | Action | Control Mode | Range | Cooldown | Notes |
|---------|--------|-------------|-------|----------|-------|
| 0 Fingers (Fist) | Toggle Gestures | ON/OFF | - | None | Instant, double-validated |
| 1 Finger (Index) | Volume | Position + Movement | 0-100% | None | Instant, no smoothing |
| 2 Fingers (Index+Middle) | Brightness | Position + Movement | 0-100% | None | Instant, no smoothing |
| 3 Fingers | Play/Pause | Toggle | - | 2s | 2-frame stability |
| 4 Fingers | Next Track | Discrete | - | 2s | 2-frame stability |
| 5 Fingers (Open Hand) | Previous Track | Discrete | - | 2s | 2-frame stability |

**Gesture Features:**
- Adaptive detection (works with different hand sizes)
- Multi-point validation (accurate finger counting)
- Instant response for continuous controls
- Smart cooldown prevents gesture spam
- State synchronized with UI display

### Distance-Based Controls

| Distance | Brightness | Volume | Behavior |
|----------|-----------|--------|----------|
| <50cm | 30% | 20% | Close proximity |
| 50-150cm | 50-80% | 40-70% | Optimal range |
| >150cm | 100% | 100% | Far away |

**Note**: Gesture controls override distance-based controls when active.

### Configuration Files

- **Main config**: `src/config/settings.py`
- **Feature flags**: `ENABLE_GESTURE_RECOGNITION`, `ENABLE_FACE_DETECTION`, etc.
- **Thresholds**: `GESTURE_DETECTION_CONFIDENCE`, `DISTANCE_GRACE_RANGE`, etc.
- **Camera**: `CAMERA_WIDTH`, `CAMERA_HEIGHT`, `CAMERA_FPS`

### Logs and Data

- **Log file**: `logs/eada_pro.log`
- **Database**: `data/eada_pro.db` (when API enabled)
- **Log level**: Configurable via `LOG_LEVEL` setting

## License

Copyright © 2025 EADA Pro Team

## Support

For issues and questions, please refer to the documentation files or create an issue in the repository.

---

## Version History

### v2.1 (Current) - Advanced Gesture Control System
**Release Date**: October 26, 2025

**Major Changes:**
- ✅ Complete gesture system rewrite with finger-based detection
- ✅ 0-5 finger gesture mappings (fist, 1-5 fingers)
- ✅ Removed all smoothing for instant response
- ✅ Extended control ranges to full 0-100%
- ✅ Adaptive finger detection with hand-size aware thresholds
- ✅ Multi-point validation for accurate finger counting
- ✅ Intelligent cooldown system (2s for discrete gestures only)
- ✅ Fixed fist toggle with double validation
- ✅ State synchronization between modules
- ✅ Position + movement based dual control mode

**Technical Improvements:**
- Thumb detection: IP joint comparison with 18% hand size threshold (min 25px)
- Finger detection: Multi-point check (tip vs PIP, PIP vs MCP) with 12% hand size threshold (min 15px)
- Cooldown: Only applies to media controls (3,4,5 fingers), not volume/brightness (1,2 fingers)
- Stability: 2-frame requirement only for media controls, instant for volume/brightness
- Fist validation: Requires finger_count==0 AND sum(fingers)==0 for strict detection
- Direct gesture processing: Removed smoothing overhead for immediate response

**Bug Fixes:**
- Fixed right hand thumb detection (was detecting extra finger)
- Fixed fist gesture not toggling properly
- Fixed volume/brightness display synchronization
- Fixed gesture sensitivity (prevented false fist triggers)
- Fixed range limitations (was 30-70%, now 0-100%)

### v2.0 - Initial Gesture Recognition
**Release Date**: October 2025

**Features:**
- Initial hand detection with MediaPipe Hands
- Basic gesture controls (pinch, wrist, palm)
- Gesture smoothing and stability
- Priority override system

### v1.0 - Core Functionality
**Release Date**: September 2025

**Features:**
- Face detection and distance estimation
- Adaptive brightness and volume control
- Presence detection with media pause
- Multi-face tracking and weighted adaptation

---

**EADA Pro** - Intelligent Display Adaptation at the Edge 🚀
