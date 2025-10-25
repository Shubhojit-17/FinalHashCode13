"""
Python Version Checker for EADA Pro
Checks if the current Python version is compatible
"""

import sys

def check_python_version():
    """Check if Python version is compatible with EADA Pro"""
    version = sys.version_info
    
    print("=" * 60)
    print("EADA Pro - Python Version Check")
    print("=" * 60)
    print(f"\nCurrent Python Version: {version.major}.{version.minor}.{version.micro}")
    print(f"Full Version: {sys.version}")
    
    # Check if version is compatible
    if version.major == 3 and version.minor in [10, 11]:
        print("\n✅ SUCCESS: Python version is compatible!")
        print("\nYou can proceed with installation:")
        print("  1. Run: .\\setup.ps1 (Windows)")
        print("  2. Or manually: python -m venv venv")
        print("  3. Then: pip install -r requirements.txt")
        return True
    elif version.major == 3 and version.minor >= 12:
        print("\n❌ ERROR: Python version is TOO NEW")
        print("\nEADA Pro requires Python 3.10 or 3.11")
        print("MediaPipe (face detection library) does not support Python 3.12+")
        print("\nSolutions:")
        print("  1. Install Python 3.10 or 3.11 from python.org")
        print("  2. Use: py -3.10 -m venv venv")
        print("  3. Or: py -3.11 -m venv venv")
        print("\nSee INSTALL.md for detailed instructions")
        return False
    elif version.major == 3 and version.minor < 10:
        print("\n⚠️  WARNING: Python version is TOO OLD")
        print("\nEADA Pro requires Python 3.10 or 3.11")
        print("\nPlease upgrade to Python 3.10 or 3.11")
        print("Download from: https://www.python.org/downloads/")
        return False
    else:
        print("\n❌ ERROR: Unsupported Python version")
        print("\nEADA Pro requires Python 3.10 or 3.11")
        return False

if __name__ == "__main__":
    print()
    compatible = check_python_version()
    print("\n" + "=" * 60)
    
    sys.exit(0 if compatible else 1)
