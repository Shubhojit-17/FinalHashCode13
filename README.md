# EADA Pro - Edge AI Display Adaptation System

An intelligent, privacy-preserving adaptive workspace assistant that optimizes accessibility, ergonomics, and productivity through real-time AI.

## Features

- 🎯 **Automatic Brightness & Volume Control**: Adapts based on user distance and environment
- 👤 **Face Detection & Counting**: Tracks multiple users with weighted adaptation
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
- [x] Camera capture
- [x] Face detection
- [x] Distance estimation
- [x] Brightness control
- [x] Volume control
- [x] Presence detection

### Phase 2: Advanced Features ✅
- [x] Face counting
- [x] Weighted adaptation
- [x] Ambient light detection
- [x] Background music analysis
- [x] Multi-face tracking

### Phase 3: Intelligence ✅
- [x] Environmental monitoring
- [x] Audio analysis
- [x] Adaptive algorithms
- [x] Smooth transitions

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Face Detection Accuracy | ≥95% | ✅ |
| System Latency | ≤50ms | ✅ |
| Face Counting Accuracy | ≥95% | ✅ |
| Weighted Adaptation | ≥90% | ✅ |
| FPS | ≥30 | ✅ |

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
- Reduce camera resolution in `settings.py`
- Enable frame skipping
- Disable unnecessary features

## Development

### Adding New Features

1. Create module in appropriate package
2. Register in `__init__.py`
3. Integrate in `system_manager.py`
4. Update configuration in `settings.py`

### Testing

```powershell
python test.py
```

## Documentation

See the following files for detailed information:
- `EADA_Pro_Plan.md` - Project plan and phases
- `EADA_Pro_Technical_Specification.md` - Technical details
- `EADA_Pro_TV_Billboard_Applications.md` - Use cases
- `tasks.md` - Implementation tasks
- `tasks_testing.md` - Testing requirements

## License

Copyright © 2025 EADA Pro Team

## Support

For issues and questions, please refer to the documentation files or create an issue in the repository.

---

**EADA Pro** - Intelligent Display Adaptation at the Edge 🚀
