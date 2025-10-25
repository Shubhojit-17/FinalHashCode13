"""
EADA Pro - Main Entry Point
Edge AI Display Adaptation Professional System
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.core.system_manager import SystemManager


def setup_logging():
    """Configure logging for the application"""
    # Create logs directory
    settings.LOGS_DIR.mkdir(exist_ok=True)
    
    # Configure file logging (INFO level)
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Configure console logging (ERROR level only - suppress warnings)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Set root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Suppress specific warnings
    logging.getLogger('screen_brightness_control').setLevel(logging.ERROR)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("EADA Pro - Edge AI Display Adaptation System")
    logger.info("Version: 1.0.0")
    logger.info("=" * 60)
    logger.info(f"Log file: {settings.LOG_FILE}")


def main():
    """Main entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Display configuration (to log file only)
        logger.info("System Configuration:")
        logger.info(f"  Camera: {settings.CAMERA_WIDTH}x{settings.CAMERA_HEIGHT} @ {settings.CAMERA_FPS} FPS")
        logger.info(f"  Face Detection: {settings.ENABLE_FACE_DETECTION}")
        logger.info(f"  Gesture Recognition: {settings.ENABLE_GESTURE_RECOGNITION}")
        logger.info(f"  Audio Monitoring: {settings.ENABLE_AUDIO_MONITORING}")
        logger.info(f"  Brightness Control: {settings.ENABLE_BRIGHTNESS_CONTROL}")
        logger.info(f"  Volume Control: {settings.ENABLE_VOLUME_CONTROL}")
        logger.info(f"  Weighted Adaptation: {settings.ENABLE_WEIGHTED_ADAPTATION}")
        logger.info(f"  Face Counting: {settings.ENABLE_FACE_COUNTING}")
        
        # Print clean startup message to console
        print("\n" + "="*60)
        print("🎯 EADA Pro - Smart Workspace Optimizer")
        print("="*60)
        print("✓ System initialized successfully")
        print("✓ Camera active | Face detection enabled")
        if settings.ENABLE_GESTURE_RECOGNITION:
            print("✓ Hand gesture recognition active")
        print("✓ Auto brightness & volume control active")
        print("✓ Media pause/resume enabled (3s delay)")
        print("\n💡 Features:")
        print("  • Distance-based brightness (30-100%)")
        print("  • Distance-based volume (20-100%)")
        if settings.ENABLE_GESTURE_RECOGNITION:
            print("  • Gesture adjustments (pinch=volume, wrist=brightness, palm=pause)")
        print("  • Auto media pause when away")
        print("  • Crowd-friendly: Waits for stability before adjusting")
        print("\n📊 Behavior:")
        print("  • Waits for distance to stabilize (1.5 seconds)")
        print("  • Grace range: ±5cm (no updates within this range)")
        print("  • Movement threshold: 5cm (resets stability timer)")
        if settings.ENABLE_GESTURE_RECOGNITION:
            print("  • Gestures blend with distance control (30% gesture + 70% auto)")
        print("  • Perfect for crowds settling in!")
        print("\n⌨️  Press 'q' in the camera window to quit")
        print("="*60 + "\n")
        
        # Create and run system manager
        system = SystemManager()
        system.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
