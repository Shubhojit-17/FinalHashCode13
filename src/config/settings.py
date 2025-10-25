"""
EADA Pro - Configuration Settings
Centralized configuration for all system parameters
"""

import os
from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ==================== Camera Settings ====================
CAMERA_INDEX = 0
CAMERA_WIDTH = 960  # Reduced from 1280 for better FPS
CAMERA_HEIGHT = 540  # Reduced from 720 for better FPS
CAMERA_FPS = 30

# ==================== Face Detection Settings ====================
# Distance estimation parameters
KNOWN_FACE_WIDTH_CM = 16.0  # Average human face width in cm
FOCAL_LENGTH = 700  # Camera focal length (calibrated)

# Face detection thresholds
FACE_DETECTION_CONFIDENCE = 0.3  # Lowered for distant face detection
MIN_FACE_SIZE = 50  # Minimum face size in pixels

# Distance ranges for adaptation (in cm)
MIN_DISTANCE_CM = 25  # Minimum distance
OPTIMAL_DISTANCE_MIN = 50  # cm
OPTIMAL_DISTANCE_MAX = 150  # cm
MAX_DETECTION_DISTANCE = 400  # cm (4 meters)

# ==================== Presence Detection ====================
ABSENCE_TIMEOUT = 3.0  # seconds - pause media after this
PRESENCE_SMOOTHING = 0.5  # seconds - debounce detection
PRESENCE_RESUME_DELAY = 2.0  # seconds - wait before resuming media

# ==================== Gesture Recognition ====================
GESTURE_DETECTION_CONFIDENCE = 0.7
GESTURE_SMOOTHING_WINDOW = 10  # frames - increased for less responsiveness

# Gesture thresholds
THUMB_INDEX_MIN_DISTANCE = 0.02  # normalized
THUMB_INDEX_MAX_DISTANCE = 0.15  # normalized
WRIST_MOVEMENT_THRESHOLD = 0.05  # normalized

# ==================== Audio Settings ====================
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 1
AUDIO_CHUNK_SIZE = 1024
AUDIO_DEVICE_INDEX = None  # None = default device

# Background music analysis
BACKGROUND_NOISE_THRESHOLD = 0.01  # RMS threshold
TARGET_SNR_DB = 17.5  # Target Signal-to-Noise ratio (15-20dB)

# ==================== Brightness Control ====================
BRIGHTNESS_MIN = 20
BRIGHTNESS_MAX = 100
BRIGHTNESS_STEP = 2  # Minimum change threshold
BRIGHTNESS_SMOOTHING = 0.3  # Exponential smoothing factor

# Ambient light adaptation
AMBIENT_LIGHT_SAMPLES = 10  # Number of samples to average
DARK_THRESHOLD = 50  # Brightness level
BRIGHT_THRESHOLD = 200  # Brightness level

# Distance-based brightness mapping (farther = brighter)
# Distance in cm: 25-250cm range
BRIGHTNESS_CLOSE = 30  # Brightness when very close (25-100cm)
BRIGHTNESS_FAR = 100  # Brightness when far (>250cm)

# Stability settings
DISTANCE_CHANGE_THRESHOLD = 0.10  # meters (10cm) - minimum distance change to trigger update
STABLE_TIME_THRESHOLD = 1.5  # seconds - stability duration before updating
DISTANCE_GRACE_RANGE = 0.05  # meters (5cm) - no updates within this range from stable position
DISTANCE_HISTORY_WINDOW = 15  # frames for distance smoothing (~0.5s at 30fps)
DISTANCE_STD_THRESHOLD = 0.05  # meters - max std dev for "stable"

# ==================== Volume Control ====================
VOLUME_MIN = 0.15
VOLUME_MAX = 1.0
VOLUME_STEP = 0.02  # Minimum change threshold (2%)
VOLUME_SMOOTHING = 0.3  # Exponential smoothing factor

# Distance-based volume mapping (farther = louder)
# Uses steep curve for pronounced changes
VOLUME_CLOSE = 0.20  # Volume when very close (25-100cm)
VOLUME_FAR = 1.0  # Volume when far (>250cm)
VOLUME_DISTANCE_EXPONENT = 0.4  # Curve steepness (lower = steeper)

# ==================== Weighted Adaptation ====================
# Distance-based weighting
DISTANCE_WEIGHT_NEAR = 2.0  # Closer faces weight multiplier
DISTANCE_WEIGHT_FAR = 1.0
DISTANCE_THRESHOLD_NEAR = 100  # cm

# Spatial weighting (position in frame)
CENTER_WEIGHT = 1.5  # Center faces weight multiplier
EDGE_WEIGHT = 1.0
CENTER_REGION_RATIO = 0.6  # Central 60% of frame

# Face counting
MAX_TRACKED_FACES = 10
FACE_COUNT_SMOOTHING = 3  # frames

# ==================== Crowd Detection ====================
CROWD_DETECTION_ENABLED = True
CROWD_MODEL_PATH = "yolov5s.pt"  # Will be downloaded automatically
CROWD_CONFIDENCE_THRESHOLD = 0.5

# ==================== Environmental Adaptation ====================
WEATHER_API_ENABLED = False  # Enable if you have API key
WEATHER_UPDATE_INTERVAL = 3600  # seconds (1 hour)

# Energy management
ENERGY_SAVE_MODE = True
LOW_TRAFFIC_TIMEOUT = 300  # seconds (5 minutes)
ENERGY_SAVE_BRIGHTNESS = 30  # %

# ==================== Security Monitoring ====================
SECURITY_MONITORING_ENABLED = True
ANOMALY_DETECTION_THRESHOLD = 0.7
EMERGENCY_GESTURE_ENABLED = True

# ==================== API Settings ====================
API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True  # Set to False in production

# WebSocket settings
WS_UPDATE_RATE = 1.0  # Hz (updates per second)

# ==================== Database Settings ====================
DATABASE_PATH = DATA_DIR / "eada_pro.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# ==================== Logging Settings ====================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = LOGS_DIR / "eada_pro.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# ==================== Performance Settings ====================
FRAME_SKIP = 0  # Skip frames for performance (0 = process all)
PROCESSING_THREADS = 2
MAX_FPS = 30

# ==================== Display Settings ====================
SHOW_PREVIEW = True  # Show camera preview window
SHOW_LANDMARKS = True  # Draw face landmarks
SHOW_METRICS = True  # Display metrics on preview

# ==================== Feature Flags ====================
ENABLE_FACE_DETECTION = True
ENABLE_GESTURE_RECOGNITION = True
ENABLE_AUDIO_MONITORING = True
ENABLE_BRIGHTNESS_CONTROL = True
ENABLE_VOLUME_CONTROL = True
ENABLE_PRESENCE_DETECTION = True
ENABLE_CROWD_DETECTION = True
ENABLE_AMBIENT_LIGHT_DETECTION = True
ENABLE_BACKGROUND_MUSIC_ANALYSIS = True
ENABLE_FACE_COUNTING = True
ENABLE_WEIGHTED_ADAPTATION = True
ENABLE_SECURITY_MONITORING = False  # Enable in production
ENABLE_API_SERVER = True

# Media player preference for macOS automation: 'spotify', 'music', or 'auto'
# - 'spotify' will attempt to control Spotify first
# - 'music' will attempt to control Apple Music first
# - 'auto' (default) will try Spotify then Apple Music
MEDIA_PLAYER_PREFERENCE = os.getenv('EADA_MEDIA_PLAYER', 'auto')
 
# Control mode for user input affecting brightness/volume:
# 'gesture' - gestures control brightness/volume
# 'head'    - head/distance tracking controls brightness/volume
# 'hybrid'  - gestures override when present, otherwise head tracking (default)
CONTROL_MODE_DEFAULT = os.getenv('EADA_CONTROL_MODE', 'hybrid')
