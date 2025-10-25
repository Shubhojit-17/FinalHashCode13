"""
Test script to verify cooldown behavior continues even when hands are removed
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.modules.perception.gesture_controller import GestureController, GestureData
import time

def test_cooldown_behavior():
    """Test that cooldown continues even when no hands are detected"""
    print("Testing cooldown behavior...")

    # Create gesture controller
    controller = GestureController()

    # Simulate triggering a gesture
    print("\n1. Simulating gesture trigger...")
    gesture = GestureData('play_pause', None, time.time())
    controller.gesture_history.append(gesture)
    controller.hand_present = True
    controller.last_gesture_type = 'play_pause'
    controller.gesture_hold_frames = 15  # Above threshold

    # Trigger the gesture
    result = controller.get_smoothed_gesture()
    if result and result.gesture_type == 'play_pause':
        print("✓ Gesture triggered successfully")
        print(f"✓ Cooldown started: {controller.cooldown_frames} frames")
    else:
        print("✗ Gesture not triggered")
        return False

    # Simulate removing hand (no more gesture detection)
    print("\n2. Simulating hand removal...")
    controller.gesture_history.clear()  # No more gestures detected
    controller.hand_present = False

    # Update cooldown for several frames (simulating time passing)
    initial_cooldown = controller.cooldown_frames
    for frame in range(10):
        controller.update_cooldown()
        if frame % 5 == 0:
            print(f"Frame {frame}: Cooldown = {controller.cooldown_frames}")

    # Check that cooldown continued
    if controller.cooldown_frames < initial_cooldown:
        print("✓ Cooldown continued decrementing even without hand detection")
    else:
        print("✗ Cooldown did not decrement")
        return False

    # Wait for cooldown to expire
    print("\n3. Waiting for cooldown to expire...")
    while controller.cooldown_frames > 0:
        controller.update_cooldown()

    print("✓ Cooldown expired")
    print("✓ Different gestures can now be triggered")

    # Test that a different gesture can be triggered immediately
    print("\n4. Testing different gesture after cooldown...")
    gesture2 = GestureData('next_track', None, time.time())
    controller.gesture_history.append(gesture2)
    controller.hand_present = True
    controller.last_gesture_type = 'next_track'
    controller.gesture_hold_frames = 15

    result2 = controller.get_smoothed_gesture()
    if result2 and result2.gesture_type == 'next_track':
        print("✓ Different gesture triggered immediately after cooldown")
        return True
    else:
        print("✗ Different gesture was blocked")
        return False

if __name__ == "__main__":
    success = test_cooldown_behavior()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)