"""
Brightness Controller Module
Controls screen brightness based on various factors
"""

import logging
from typing import Optional
import numpy as np
from collections import deque

try:
    import screen_brightness_control as sbc
    BRIGHTNESS_AVAILABLE = True
except ImportError:
    BRIGHTNESS_AVAILABLE = False
    logging.warning("screen-brightness-control not available")

from src.config import settings

logger = logging.getLogger(__name__)


class BrightnessController:
    """Controls screen brightness with smooth adaptation"""
    
    def __init__(self):
        """Initialize brightness controller"""
        self.current_brightness = 50
        self.target_brightness = 50
        self.brightness_history = deque(maxlen=10)
        self.last_distance = None
        self.distance_stable_since = None
        self.last_updated_distance = None  # Track last distance that triggered an update
        
        # Check if brightness control is available
        self.available = BRIGHTNESS_AVAILABLE
        
        if self.available:
            try:
                # Get current brightness
                self.current_brightness = sbc.get_brightness()[0]
                self.target_brightness = self.current_brightness
                logger.info(f"Brightness controller initialized at {self.current_brightness}%")
            except Exception as e:
                logger.error(f"Failed to get initial brightness: {e}")
                self.available = False
        else:
            logger.warning("Brightness control not available - running in simulation mode")
    
    def set_brightness(self, value: int, smooth: bool = True) -> bool:
        """
        Set screen brightness
        
        Args:
            value: Brightness value (0-100)
            smooth: Apply smoothing
            
        Returns:
            True if successful
        """
        # Clamp value
        value = max(settings.BRIGHTNESS_MIN, min(value, settings.BRIGHTNESS_MAX))
        
        if smooth:
            # Apply exponential smoothing
            self.target_brightness = value
            new_brightness = (
                settings.BRIGHTNESS_SMOOTHING * value +
                (1 - settings.BRIGHTNESS_SMOOTHING) * self.current_brightness
            )
        else:
            new_brightness = value
        
        # Only update if change is significant
        brightness_diff = abs(new_brightness - self.current_brightness)
        if brightness_diff < settings.BRIGHTNESS_STEP:
            return True
        
        # Update brightness
        if self.available:
            try:
                sbc.set_brightness(int(new_brightness))
                self.current_brightness = new_brightness
                self.brightness_history.append(new_brightness)
                return True
            except Exception as e:
                logger.error(f"Failed to set brightness: {e}")
                return False
        else:
            # Simulation mode
            self.current_brightness = new_brightness
            self.brightness_history.append(new_brightness)
            logger.debug(f"[SIMULATION] Brightness set to {new_brightness:.1f}%")
            return True
    
    def adapt_to_distance(self, distance: float) -> bool:
        """
        Adapt brightness based on user distance - only updates when stable
        Farther = brighter, Closer = dimmer
        
        Args:
            distance: Distance in cm
            
        Returns:
            True if successful
        """
        import time
        
        # Convert distance to meters for easier comparison
        distance_m = distance / 100.0
        
        # Check if we're within grace range of last updated position
        if self.last_updated_distance is not None:
            distance_from_last_update = abs(distance_m - self.last_updated_distance)
            if distance_from_last_update < settings.DISTANCE_GRACE_RANGE:
                # Within grace range - no update needed
                self.distance_stable_since = time.time()  # Reset timer
                return True
        
        # Track distance changes for stability detection
        if self.last_distance is not None:
            distance_change = abs(distance_m - self.last_distance)
            
            # If distance is changing (not stable), reset timer
            if distance_change >= 0.05:  # 5cm movement threshold for "unstable"
                self.distance_stable_since = time.time()
                self.last_distance = distance_m
                logger.debug(f"Distance changing ({distance_change:.2f}m) - waiting for stability")
                return True
            
            # Distance is stable, check if enough time has passed
            if self.distance_stable_since is not None:
                time_stable = time.time() - self.distance_stable_since
                if time_stable >= settings.STABLE_TIME_THRESHOLD:
                    # Stable for required duration - check if beyond grace range
                    if self.last_updated_distance is None or \
                       abs(distance_m - self.last_updated_distance) >= settings.DISTANCE_GRACE_RANGE:
                        logger.info(f"Distance stable at {distance:.1f}cm for {time_stable:.1f}s - updating brightness")
                        should_update = True
                    else:
                        return True
                else:
                    logger.debug(f"Distance stable: {time_stable:.1f}s / {settings.STABLE_TIME_THRESHOLD}s")
                    self.last_distance = distance_m
                    return True
            else:
                # Start stability timer
                self.distance_stable_since = time.time()
                self.last_distance = distance_m
                return True
        else:
            # First measurement - start timer
            logger.info("First distance measurement - starting stability timer")
            self.distance_stable_since = time.time()
            self.last_distance = distance_m
            return True
        
        # Update the last updated distance
        self.last_updated_distance = distance_m
        self.last_distance = distance_m
        
        # Calculate target brightness using linear interpolation
        # Map distance (25-400cm) to brightness (30-100%)
        distance_normalized = (distance - settings.MIN_DISTANCE_CM) / (settings.MAX_DETECTION_DISTANCE - settings.MIN_DISTANCE_CM)
        distance_normalized = np.clip(distance_normalized, 0, 1)
        
        target = settings.BRIGHTNESS_CLOSE + (settings.BRIGHTNESS_FAR - settings.BRIGHTNESS_CLOSE) * distance_normalized
        
        logger.info(f"Distance: {distance:.1f}cm -> Target brightness: {target:.0f}%")
        return self.set_brightness(int(target), smooth=False)
    
    def adapt_to_ambient_light(self, ambient_level: float) -> bool:
        """
        Adapt brightness based on ambient lighting
        
        Args:
            ambient_level: Ambient light level (0-255)
            
        Returns:
            True if successful
        """
        # Map ambient light to brightness
        if ambient_level < settings.DARK_THRESHOLD:
            # Dark environment - reduce brightness
            target = 40
        elif ambient_level > settings.BRIGHT_THRESHOLD:
            # Bright environment - increase brightness
            target = 100
        else:
            # Normal lighting - moderate brightness
            ratio = (ambient_level - settings.DARK_THRESHOLD) / (
                settings.BRIGHT_THRESHOLD - settings.DARK_THRESHOLD
            )
            target = 40 + (60 * ratio)  # Scale from 40% to 100%
        
        return self.set_brightness(int(target))
    
    def get_brightness(self) -> int:
        """Get current brightness level"""
        return int(self.current_brightness)
    
    def increase_brightness(self, amount: int = 5) -> bool:
        """Increase brightness by amount"""
        new_value = self.current_brightness + amount
        return self.set_brightness(int(new_value), smooth=False)
    
    def decrease_brightness(self, amount: int = 5) -> bool:
        """Decrease brightness by amount"""
        new_value = self.current_brightness - amount
        return self.set_brightness(int(new_value), smooth=False)
    
    def get_statistics(self) -> dict:
        """Get brightness statistics"""
        return {
            'current': self.get_brightness(),
            'target': int(self.target_brightness),
            'available': self.available,
            'history_mean': float(np.mean(list(self.brightness_history))) if self.brightness_history else 0.0
        }
