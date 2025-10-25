"""
Test brightness and volume control directly
"""
import sys
import time
sys.path.insert(0, 'd:\\Hashcode')

from src.modules.adaptation.brightness_controller import BrightnessController
from src.modules.adaptation.volume_controller import VolumeController
from src.config import settings

def test_brightness():
    print("\n=== Testing Brightness Control ===")
    controller = BrightnessController()
    
    print(f"Current brightness: {controller.get_brightness()}%")
    
    # Test at different distances
    distances = [50, 100, 150, 200]  # in cm
    
    for distance in distances:
        print(f"\nTesting distance: {distance}cm")
        controller.adapt_to_distance(distance)
        time.sleep(0.5)
        print(f"Brightness after: {controller.get_brightness()}%")

def test_volume():
    print("\n=== Testing Volume Control ===")
    controller = VolumeController()
    
    print(f"Current volume: {controller.get_volume()*100:.0f}%")
    
    # Test at different distances
    distances = [50, 100, 150, 200]  # in cm
    
    for distance in distances:
        print(f"\nTesting distance: {distance}cm")
        controller.adapt_to_distance(distance)
        time.sleep(0.5)
        print(f"Volume after: {controller.get_volume()*100:.0f}%")

if __name__ == "__main__":
    print(f"Stability thresholds:")
    print(f"  Distance change: {settings.DISTANCE_CHANGE_THRESHOLD}m")
    print(f"  Stable time: {settings.STABLE_TIME_THRESHOLD}s")
    
    test_brightness()
    test_volume()
