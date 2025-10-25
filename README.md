# EADA Pro - Edge AI Display Adaptation System

An intelligent, privacy-preserving adaptive workspace assistant that optimizes accessibility, ergonomics, and productivity through real-time AI.

## 🎉 Phase 2 Complete - Gesture Recognition Added!

**New in Phase 2:**
- ✋ Full hand gesture recognition system
- 🎮 Three built-in gestures: Volume (pinch), Brightness (wrist), Play/Pause (palm)
- 🔧 Custom gesture framework for extensibility
- 🎯 Gesture priority override system
- 📊 Real-time visual feedback

**Quick Start with Gestures:**
```powershell
python run.py
```
Then use hand gestures:
- **Pinch thumb & index**: Control volume
- **Move hand up/down**: Control brightness  
- **Open palm**: Toggle play/pause

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
- **Hand Gestures** (when gesture recognition enabled):
  - **Thumb-Index Pinch**: Control volume (closer = quieter, farther = louder)
  - **Wrist Y Position**: Control brightness (higher = brighter, lower = dimmer)
  - **Open Palm**: Toggle play/pause media
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
# Gesture Recognition Settings
GESTURE_DETECTION_CONFIDENCE = 0.7  # Detection confidence threshold
GESTURE_SMOOTHING_WINDOW = 5  # Frames for gesture smoothing

# Gesture thresholds
THUMB_INDEX_MIN_DISTANCE = 0.02  # Min distance for volume control
THUMB_INDEX_MAX_DISTANCE = 0.15  # Max distance for volume control
WRIST_MOVEMENT_THRESHOLD = 0.05  # Threshold for brightness control
```

## Gesture Recognition System

### Built-in Gestures

EADA Pro includes three default gesture mappings:

#### 1. Volume Control (1 Finger - Index)
- **Gesture**: Show 1 finger (index finger only)
- **Control**: Raise finger higher on screen = higher volume, lower on screen = lower volume
- **Range**: Bottom of screen = 100% volume, Top of screen = 0% volume
- **Mapping**: Vertical position from 0-100% of screen height
- **Priority**: Overrides distance-based volume control
- **Smoothing**: Applied for smooth transitions

#### 2. Brightness Control (2 Fingers - Index + Middle)
- **Gesture**: Show 2 fingers (index + middle finger)
- **Control**: Raise fingers higher on screen = higher brightness, lower on screen = lower brightness
- **Range**: Bottom of screen = 100% brightness, Top of screen = 10% brightness
- **Mapping**: Vertical position from 0-100% of screen height
- **Priority**: Overrides distance-based brightness control
- **Threshold**: Responds to vertical position changes

#### 3. Play/Pause Toggle (3 Fingers - Index + Middle + Ring)
- **Gesture**: Show 3 fingers (index + middle + ring)
- **Detection**: All three fingers extended
- **Activation**: Hold for 10 frames (~0.3s)
- **Action**: Toggles media playback state
- **Cooldown**: 1.5 seconds (45 frames) - continues even when hand is removed

### Implementing Custom Gestures

To add your own custom gestures, follow this guide:

#### Step 1: Define Gesture Logic

Edit `src/modules/perception/gesture_controller.py` in the `_classify_gesture()` method:

```python
def _classify_gesture(self, thumb_index_dist, wrist_y, landmarks):
    # Your custom gesture detection here
    
    # Example: Peace Sign Detection
    index_tip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = landmarks[self.mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[self.mp_hands.HandLandmark.PINKY_TIP]
    
    # Check if index and middle are up, ring and pinky are down
    if (index_tip.y < index_mcp.y and 
        middle_tip.y < middle_mcp.y and
        ring_tip.y > ring_mcp.y and
        pinky_tip.y > pinky_mcp.y):
        return ('peace_sign', None)
    
    # ... existing gesture logic ...
```

#### Step 2: Add Gesture Action

In `src/core/system_manager.py`, add handling for your custom gesture:

```python
# In process_frame() method
if smoothed_gesture.gesture_type == 'peace_sign':
    logger.info("Peace sign detected - custom action triggered")
    # Your custom action here
    self._custom_action()
```

#### Step 3: Create Custom Action Method

Add your custom action method to `SystemManager`:

```python
def _custom_action(self):
    """Execute custom action for peace sign gesture"""
    # Example: Take a screenshot
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    cv2.imwrite(filename, self.current_frame)
    logger.info(f"Screenshot saved: {filename}")
```

#### Step 4: Add Configuration (Optional)

Add custom gesture settings in `src/config/settings.py`:

```python
# Custom Gesture Settings
PEACE_SIGN_ENABLED = True
PEACE_SIGN_HOLD_TIME = 1.0  # seconds
PEACE_SIGN_COOLDOWN = 2.0  # seconds
```

### Advanced Gesture Features

#### Gesture State Machine
For complex gesture sequences:

```python
class GestureStateMachine:
    def __init__(self):
        self.state = 'idle'
        self.gesture_sequence = []
    
    def update(self, gesture):
        if self.state == 'idle' and gesture == 'thumbs_up':
            self.state = 'waiting_for_second'
            self.gesture_sequence.append(gesture)
        elif self.state == 'waiting_for_second' and gesture == 'peace_sign':
            self.state = 'complete'
            return 'secret_gesture_combo'
        return None
```

#### Hand Landmark Access
MediaPipe provides 21 hand landmarks:

```python
# Key landmarks
WRIST = 0
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20

# Access coordinates
landmark = landmarks[INDEX_TIP]
x, y, z = landmark.x, landmark.y, landmark.z  # Normalized 0-1
```

#### Multi-Hand Gestures
Detect gestures requiring both hands:

```python
if len(gestures) == 2:
    left_hand = [g for g in gestures if g.hand_type == 'Left'][0]
    right_hand = [g for g in gestures if g.hand_type == 'Right'][0]
    
    # Calculate distance between both index fingers
    left_index = left_hand.landmarks[8]
    right_index = right_hand.landmarks[8]
    hands_distance = self._calculate_distance(left_index, right_index)
    
    if hands_distance < 0.1:  # Hands close together
        return ('hands_together', None)
```

### Gesture Performance Tips

1. **Smoothing**: Use `GESTURE_SMOOTHING_WINDOW` to reduce jitter
2. **Confidence Thresholds**: Adjust `GESTURE_DETECTION_CONFIDENCE` for accuracy vs. speed
3. **Deadzone**: Add deadzones to prevent unintended activations
4. **State Tracking**: Use counters for hold-time requirements
5. **Priority System**: Define which gestures override others
6. **Cooldown Behavior**: Cooldown timers continue even when hands are removed, preventing gesture spam

### Gesture Recognition Best Practices

- **Test in various lighting**: Gestures may behave differently in bright/dim conditions
- **Calibrate distances**: Adjust min/max thresholds for user comfort
- **Add visual feedback**: Display current gesture on screen for user confirmation
- **Implement timeouts**: Prevent gesture spam with cooldown periods
- **Consider ergonomics**: Design gestures that are comfortable to perform
- **Document clearly**: Provide user guide for gesture usage

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
- [x] Hand detection with MediaPipe Hands
- [x] Gesture-based volume control (thumb-index pinch)
- [x] Gesture-based brightness control (wrist Y position)
- [x] Play/pause gesture (open palm)
- [x] Gesture smoothing and stability
- [x] Priority override (gestures override distance-based control)
- [x] Real-time visual feedback

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

### What's New in Phase 2

**Gesture Recognition System** - Complete hand tracking and gesture control implementation:

1. **Core Gesture Engine**
   - MediaPipe Hands integration with 2-hand tracking
   - 21-landmark hand detection per hand
   - Real-time gesture classification
   - Smoothing algorithms for stable recognition

2. **Built-in Gesture Controls**
   - Volume control via thumb-index pinch distance
   - Brightness control via wrist vertical position
   - Media play/pause via open palm detection
   - Gesture priority override system

3. **Advanced Features**
   - Multi-frame gesture smoothing (5-frame window)
   - State-based gesture detection (hold time, cooldown)
   - Confidence-based activation thresholds
   - Visual feedback overlay on camera feed

4. **Custom Gesture Framework**
   - Extensible gesture classification system
   - Easy-to-implement custom gesture API
   - State machine support for complex sequences
   - Multi-hand gesture coordination

5. **Performance Optimizations**
   - Gesture processing runs parallel to face detection
   - Minimal latency (<200ms) for responsive control
   - Efficient landmark caching and smoothing
   - Resource cleanup and memory management

### Gesture vs Distance Control

**Blended Control System:**
- **Distance control**: Always active, provides base adjustment
- **Gesture adjustments**: Blend with distance control (30% gesture + 70% auto)
- **Play/pause gesture**: Direct toggle action (not blended)
- **Smooth transitions**: Gestures fine-tune automatic control

**Responsiveness:**
- Gesture smoothing: 10-frame window (~0.3s at 30fps)
- Brightness gesture threshold: ±5% from neutral
- Play/pause hold time: 15 frames (~0.5s)
- Less jittery, more deliberate control

**Use Cases:**
- Distance control: Primary hands-free automatic adaptation
- Gesture control: Manual fine-tuning on top of automatic
- Combined mode: Best of both - automatic with manual override capability

### System Integration

**Seamless Module Integration:**
- GestureController added to perception layer
- System Manager orchestrates gesture + face detection
- Shared frame processing for efficiency
- Unified display with face + hand landmarks

**Configuration Flexibility:**
- Enable/disable gesture recognition via `ENABLE_GESTURE_RECOGNITION`
- Adjust detection confidence and smoothing parameters
- Configure gesture thresholds in `settings.py`
- Toggle visual feedback independently

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

**Phase 2: Gesture Recognition** (Complete)
- Hand detection and gesture classification
- Volume control via thumb-index pinch
- Brightness control via wrist position
- Play/pause via open palm gesture
- Custom gesture framework with documentation
- Priority override system
- Real-time visual feedback

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

## Quick Reference

### Gesture Controls

| Gesture | Action | Control | Notes |
|---------|--------|---------|-------|
| **0 fingers (Fist)** | Toggle Gestures | - | Enable/disable all gestures |
| **1 finger (Index)** | Volume | Raise hand up = quiet, down = loud | 0-100% based on vertical position |
| **2 fingers (Index+Middle)** | Brightness | Raise hand up = dim, down = bright | 10-100% based on vertical position |
| **3 fingers (Index+Middle+Ring)** | Play/Pause | Hold gesture | Toggle media playback, 1.5s cooldown |
| **4 fingers** | Next Track | Hold gesture | Skip to next track, 1.5s cooldown |
| **5 fingers (All)** | Previous Track | Hold gesture | Go to previous track, 1.5s cooldown |

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

**EADA Pro** - Intelligent Display Adaptation at the Edge 🚀
