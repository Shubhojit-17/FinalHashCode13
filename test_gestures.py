"""
Gesture Recognition Test Script
Tests the gesture controller functionality
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import cv2
import time
from src.modules.perception import CameraCapture, GestureController
from src.config import settings

def test_gesture_recognition():
    """Test gesture recognition system"""
    print("="*60)
    print("Gesture Recognition Test")
    print("="*60)
    print("\nTesting gestures:")
    print("1. Thumb-Index Pinch: Volume control")
    print("2. Wrist Y Position: Brightness control")
    print("3. Open Palm: Play/Pause")
    print("\nPress 'q' to quit\n")
    print("="*60)
    
    # Initialize camera and gesture controller
    camera = CameraCapture()
    gesture_controller = GestureController()
    
    if not camera.start():
        print("❌ Failed to start camera")
        return False
    
    print("✓ Camera started")
    print("✓ Gesture controller initialized")
    print("\nShow hand gestures to the camera...\n")
    
    try:
        frame_count = 0
        start_time = time.time()
        
        while True:
            # Capture frame
            ret, frame = camera.read_frame()
            if not ret:
                continue
            
            frame_count += 1
            
            # Detect gestures
            gestures = gesture_controller.detect_gestures(frame)
            
            # Get smoothed gesture
            smoothed_gesture = gesture_controller.get_smoothed_gesture()
            
            # Draw gestures
            display_frame = gesture_controller.draw_hands(frame, gestures)
            
            # Display metrics
            y_offset = 80
            if smoothed_gesture:
                gesture_text = f"Gesture: {smoothed_gesture.gesture_type}"
                if smoothed_gesture.value is not None:
                    gesture_text += f" ({smoothed_gesture.value:.0f}%)"
                
                cv2.putText(
                    display_frame, gesture_text,
                    (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 255, 0), 2
                )
                
                # Log gesture
                if frame_count % 30 == 0:  # Log every second
                    print(f"[{time.time() - start_time:.1f}s] {gesture_text}")
            
            # Display FPS
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            cv2.putText(
                display_frame, f"FPS: {fps:.1f}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2
            )
            
            # Show frame
            cv2.imshow('Gesture Test', display_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Calculate statistics
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed
        
        print("\n" + "="*60)
        print("Test Results:")
        print(f"  Total Frames: {frame_count}")
        print(f"  Duration: {elapsed:.1f}s")
        print(f"  Average FPS: {avg_fps:.1f}")
        print(f"  Target FPS: ≥30")
        print(f"  Status: {'✅ PASS' if avg_fps >= 30 else '❌ FAIL'}")
        print("="*60)
        
        return avg_fps >= 30
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        camera.release()
        gesture_controller.release()
        cv2.destroyAllWindows()
        print("\nTest completed")
    
    return True


if __name__ == "__main__":
    success = test_gesture_recognition()
    sys.exit(0 if success else 1)
