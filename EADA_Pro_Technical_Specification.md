# EADA Pro - Technical Specification

## 1. System Overview
EADA Pro uses real-time computer vision and audio processing to adjust environmental parameters (brightness, volume, media) according to user presence, distance, and gestures.

## 2. Architecture Diagram

Webcam/Mic → Perception Layer → Intelligence Layer → Adaptation Layer → User

## 3. Core Modules
| Module | Description |
|---------|-------------|
| AudioMonitor | Captures RMS sound levels and analyzes background music |
| ErgonomicsMonitor | Tracks posture and gestures |
| GestureController | Maps hand gestures to actions |
| CrowdAnalyzer | Detects audience size and engagement for public displays |
| WeatherAdapter | Adjusts display settings based on environmental conditions |
| EnergyManager | Optimizes power consumption for outdoor displays |
| SecurityMonitor | Detects unusual behavior and emergency situations |
| ContentOptimizer | Adapts media content based on audience demographics |
| AmbientLightController | Adjusts brightness based on environmental lighting conditions |
| BackgroundMusicAnalyzer | Analyzes ambient audio and adjusts volume accordingly |
| **FaceCounter** | **Detects and counts faces in real-time with position tracking** |
| **WeightedAdapter** | **Applies weighted algorithms for volume/brightness based on face count and positions** |
| WorkspaceOptimizer | Orchestrates adaptation logic |
| APIService (planned) | Provides REST endpoints |

## 4. Algorithms

- **Distance Estimation:** Face width triangulation.
- **Gesture Recognition:** MediaPipe Hands → Thumb–Index distance → Volume; Wrist Y-position → Brightness.
- **Presence Detection:** No face for 3 s → pause; reappearance → resume.
- **Crowd Analysis:** YOLO-based person detection → count estimation → content adaptation.
- **Weather Adaptation:** Ambient light sensors + weather API → brightness/contrast optimization.
- **Energy Optimization:** Time-of-day + crowd presence → power management scheduling.
- **Behavior Monitoring:** Pose estimation + movement patterns → anomaly detection.
- **Content Personalization:** Age/gender estimation → demographic-based content selection.
- **Background Music Analysis:** Audio frequency analysis → volume adjustment to maintain optimal S/N ratio.
- **Ambient Light Detection:** Camera-based illuminance estimation → brightness compensation for optimal visibility.
- **Face Counting & Weighted Adaptation:** Multi-face detection → count display → weighted average volume/brightness based on face positions and distances.

## 5. Data Flow
1. Capture frame/audio/environmental data (camera, microphone, light sensors)
2. Extract landmarks/RMS/crowd metrics/ambient conditions
3. Analyze background music levels and ambient lighting
4. **Detect and count faces with position/distance weighting**
5. Process intelligence logic (presence + crowd + weather + audio environment + face metrics)
6. **Apply weighted adaptation for volume/brightness based on face count and positions**
7. Adapt display settings, volume, and content dynamically
8. Monitor security and energy parameters
9. Store metrics and analytics (SQLite planned)

## 6. Dependencies
mediapipe==0.10.14
opencv-python==4.5.5.64
numpy==1.21.6
pycaw
sounddevice
screen-brightness-control
fastapi
uvicorn
cryptography
yolov5
torch
torchvision
requests
weather-api
scikit-learn
pandas
librosa
pydub
scipy
light-sensor
