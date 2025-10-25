"""
EADA Pro - Simple Test Script
Tests basic functionality of all modules
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all modules can be imported"""
    logger.info("Testing imports...")
    
    try:
        from src.config import settings
        logger.info("✓ Config module")
        
        from src.modules.perception import CameraCapture, AudioCapture, FaceDetector, FaceCounter
        logger.info("✓ Perception modules")
        
        from src.modules.adaptation import BrightnessController, VolumeController, WeightedAdapter
        logger.info("✓ Adaptation modules")
        
        from src.modules.intelligence import EnvironmentMonitor, AudioAnalyzer
        logger.info("✓ Intelligence modules")
        
        from src.core.system_manager import SystemManager
        logger.info("✓ System manager")
        
        return True
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_camera():
    """Test camera capture"""
    logger.info("\nTesting camera...")
    
    try:
        from src.modules.perception import CameraCapture
        
        camera = CameraCapture()
        if camera.start():
            logger.info("✓ Camera started")
            
            ret, frame = camera.read_frame()
            if ret:
                logger.info(f"✓ Frame captured: {frame.shape}")
            else:
                logger.warning("✗ Failed to read frame")
            
            camera.release()
            logger.info("✓ Camera released")
            return True
        else:
            logger.warning("✗ Camera failed to start")
            return False
    except Exception as e:
        logger.error(f"✗ Camera test failed: {e}")
        return False


def test_face_detection():
    """Test face detection"""
    logger.info("\nTesting face detection...")
    
    try:
        from src.modules.perception import FaceDetector
        import numpy as np
        
        detector = FaceDetector()
        logger.info("✓ Face detector initialized")
        
        # Create dummy frame
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        faces = detector.detect_faces(dummy_frame)
        logger.info(f"✓ Face detection works (found {len(faces)} faces in blank frame)")
        
        detector.release()
        return True
    except Exception as e:
        logger.error(f"✗ Face detection test failed: {e}")
        return False


def test_controllers():
    """Test brightness and volume controllers"""
    logger.info("\nTesting controllers...")
    
    try:
        from src.modules.adaptation import BrightnessController, VolumeController
        
        brightness = BrightnessController()
        logger.info(f"✓ Brightness controller (available: {brightness.available})")
        logger.info(f"  Current brightness: {brightness.get_brightness()}%")
        
        volume = VolumeController()
        logger.info(f"✓ Volume controller (available: {volume.available})")
        logger.info(f"  Current volume: {volume.get_volume_percent()}%")
        
        return True
    except Exception as e:
        logger.error(f"✗ Controllers test failed: {e}")
        return False


def test_weighted_adapter():
    """Test weighted adaptation"""
    logger.info("\nTesting weighted adapter...")
    
    try:
        from src.modules.adaptation import WeightedAdapter
        from src.modules.perception.face_detector import FaceData
        import numpy as np
        
        adapter = WeightedAdapter()
        
        # Create dummy faces
        face1 = FaceData(
            bbox=(100, 100, 80, 80),
            landmarks=np.array([]),
            distance=60.0,  # Close
            position=(0.5, 0.5),  # Center
            confidence=0.9
        )
        
        face2 = FaceData(
            bbox=(400, 200, 60, 60),
            landmarks=np.array([]),
            distance=120.0,  # Far
            position=(0.8, 0.4),  # Edge
            confidence=0.85
        )
        
        faces = [face1, face2]
        
        weighted_dist = adapter.calculate_weighted_distance(faces)
        logger.info(f"✓ Weighted distance: {weighted_dist:.1f}cm")
        
        brightness = adapter.calculate_brightness_target(faces, ambient_light=128)
        volume = adapter.calculate_volume_target(faces, background_noise=0.1)
        logger.info(f"✓ Target brightness: {brightness}%")
        logger.info(f"✓ Target volume: {volume*100:.0f}%")
        
        return True
    except Exception as e:
        logger.error(f"✗ Weighted adapter test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("EADA Pro - System Test")
    logger.info("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Camera", test_camera),
        ("Face Detection", test_face_detection),
        ("Controllers", test_controllers),
        ("Weighted Adapter", test_weighted_adapter),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            logger.error(f"Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{name:.<40} {status}")
    
    logger.info("-" * 60)
    logger.info(f"Total: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
