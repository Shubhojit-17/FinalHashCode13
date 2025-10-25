# EADA Pro - Installation & Setup Guide

## Important: Python Version Requirements

**EADA Pro requires Python 3.10 or 3.11**

MediaPipe (our core face detection library) does not support Python 3.12+ yet.

### Check Your Python Version

```powershell
python --version
```

If you see Python 3.12 or 3.13, you need to install Python 3.10 or 3.11.

## Step 1: Install Python 3.10 or 3.11

### Option A: Using Python.org

1. Download Python 3.10 or 3.11 from [python.org](https://www.python.org/downloads/)
2. Install with "Add to PATH" checked
3. Verify installation:
   ```powershell
   py -3.10 --version
   # or
   py -3.11 --version
   ```

### Option B: Using Windows Store

1. Open Microsoft Store
2. Search for "Python 3.10" or "Python 3.11"
3. Install
4. Verify: `python3.10 --version`

### Option C: Using Chocolatey (if installed)

```powershell
choco install python310
```

## Step 2: Create Virtual Environment

**Important:** Use the correct Python version

```powershell
# Navigate to project directory
cd D:\Hashcode

# Create virtual environment with Python 3.10
py -3.10 -m venv venv

# Or with Python 3.11
py -3.11 -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Step 3: Install Dependencies

With virtual environment activated:

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

### If Installation Fails

Install in stages:

```powershell
# Stage 1: Core libraries
pip install numpy==1.24.3
pip install opencv-python==4.8.1.78
pip install mediapipe==0.10.9

# Stage 2: Audio
pip install sounddevice==0.4.6
pip install scipy==1.11.4

# Stage 3: System control
pip install screen-brightness-control==0.21.0
pip install comtypes==1.2.0
pip install pycaw==20230407

# Stage 4: Web framework
pip install fastapi==0.104.1
pip install uvicorn==0.24.0

# Stage 5: Utilities
pip install requests==2.31.0
pip install Pillow==10.1.0
```

## Step 4: Verify Installation

```powershell
python test.py
```

Expected output:
```
✓ Config module
✓ Perception modules
✓ Adaptation modules
✓ Intelligence modules
✓ System manager
✓ Camera started
✓ Frame captured
...
🎉 All tests passed!
```

## Step 5: Run EADA Pro

```powershell
python run.py
```

## Troubleshooting

### Issue: "No module named 'cv2'"
**Solution:** MediaPipe needs Python 3.10 or 3.11. Recreate venv with correct version.

### Issue: "Failed to open camera"
**Solution:** 
- Close other apps using camera (Zoom, Teams, etc.)
- Try different camera index in `src/config/settings.py`
- Grant camera permissions in Windows Settings

### Issue: "screen-brightness-control not available"
**Solution:** This is normal. System runs in simulation mode. On Windows with proper permissions, brightness control will work automatically.

### Issue: "pycaw not available"
**Solution:** 
```powershell
pip install comtypes==1.2.0
pip install pycaw==20230407
```

### Issue: PowerShell script execution disabled
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Quick Commands Reference

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Deactivate environment
deactivate

# Run tests
python test.py

# Run EADA Pro
python run.py

# Check installed packages
pip list

# Update requirements
pip freeze > requirements.txt
```

## System Requirements

### Minimum
- Python 3.10 or 3.11
- 4 GB RAM
- Webcam
- Windows 10+

### Recommended
- Python 3.10 or 3.11
- 8 GB RAM
- HD Webcam
- Microphone
- Windows 11

## Feature Availability

| Feature | Windows | Linux | macOS |
|---------|---------|-------|-------|
| Camera | ✅ | ✅ | ✅ |
| Face Detection | ✅ | ✅ | ✅ |
| Audio | ✅ | ✅ | ✅ |
| Brightness Control | ✅ | ⚠️ | ⚠️ |
| Volume Control | ✅ | ⚠️ | ⚠️ |

✅ = Fully supported  
⚠️ = Limited/simulation mode

## Development Setup

For development with hot-reload:

```powershell
# Install development dependencies
pip install pytest black pylint

# Run with debug logging
$env:LOG_LEVEL="DEBUG"
python run.py
```

## Getting Help

1. Check documentation in `.md` files
2. Review `src/config/settings.py` for configuration options
3. Enable debug logging for detailed output
4. Check `logs/eada_pro.log` for error details

---

**Important:** Always use Python 3.10 or 3.11 for this project!
