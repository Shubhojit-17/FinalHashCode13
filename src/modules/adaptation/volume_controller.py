"""
Volume Controller Module
Controls system volume based on various factors
"""

import logging
import numpy as np
from typing import Optional
from collections import deque

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    VOLUME_AVAILABLE = True
except ImportError:
    VOLUME_AVAILABLE = False
    logging.warning("pycaw not available")

from src.config import settings

logger = logging.getLogger(__name__)


class VolumeController:
    """Controls system volume with smooth adaptation"""
    
    def __init__(self):
        """Initialize volume controller"""
        self.current_volume = 0.5
        self.target_volume = 0.5
        self.volume_history = deque(maxlen=10)
        self.last_distance = None
        self.distance_stable_since = None
        self.last_updated_distance = None  # Track last distance that triggered an update
        
        # Check if volume control is available
        self.available = VOLUME_AVAILABLE
        self.volume_interface = None
        
        if self.available:
            try:
                # Get default audio device (newer pycaw API)
                devices = AudioUtilities.GetSpeakers()
                self.volume_interface = devices.EndpointVolume
                
                # Get current volume
                self.current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
                self.target_volume = self.current_volume
                logger.info(f"Volume controller initialized at {self.current_volume*100:.0f}%")
            except Exception as e:
                logger.error(f"Failed to initialize volume control: {e}")
                self.available = False
        else:
            logger.warning("Volume control not available - running in simulation mode")
    
    def set_volume(self, value: float, smooth: bool = True) -> bool:
        """
        Set system volume
        
        Args:
            value: Volume value (0.0 to 1.0)
            smooth: Apply smoothing
            
        Returns:
            True if successful
        """
        # Clamp value
        value = max(settings.VOLUME_MIN, min(value, settings.VOLUME_MAX))
        
        if smooth:
            # Apply exponential smoothing
            self.target_volume = value
            new_volume = (
                settings.VOLUME_SMOOTHING * value +
                (1 - settings.VOLUME_SMOOTHING) * self.current_volume
            )
        else:
            new_volume = value
        
        # Only update if change is significant
        volume_diff = abs(new_volume - self.current_volume)
        if volume_diff < settings.VOLUME_STEP:
            return True
        
        # Update volume
        if self.available and self.volume_interface:
            try:
                self.volume_interface.SetMasterVolumeLevelScalar(new_volume, None)
                self.current_volume = new_volume
                self.volume_history.append(new_volume)
                return True
            except Exception as e:
                logger.error(f"Failed to set volume: {e}")
                return False
        else:
            # Simulation mode
            self.current_volume = new_volume
            self.volume_history.append(new_volume)
            logger.debug(f"[SIMULATION] Volume set to {new_volume*100:.0f}%")
            return True
    
    def adapt_to_distance(self, distance: float) -> bool:
        """
        Adapt volume based on user distance - only updates when stable
        Farther = louder, Closer = quieter
        
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
                        logger.info(f"Distance stable at {distance:.1f}cm for {time_stable:.1f}s - updating volume")
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
        
        # Calculate target volume using STEEP curve for pronounced changes
        # Map distance (25-400cm) to volume (20-100%)
        distance_normalized = (distance - settings.MIN_DISTANCE_CM) / (settings.MAX_DETECTION_DISTANCE - settings.MIN_DISTANCE_CM)
        distance_normalized = np.clip(distance_normalized, 0, 1)
        
        # Apply power curve for extremely steep response: volume = 20 + 80 * (normalized^0.4)
        target_percent = 20 + 80 * (distance_normalized ** settings.VOLUME_DISTANCE_EXPONENT)
        target = target_percent / 100.0  # Convert to 0-1 range
        
        logger.info(f"Distance: {distance:.1f}cm -> Target volume: {target*100:.0f}%")
        return self.set_volume(target, smooth=False)
    
    def adapt_to_background_noise(self, noise_level: float) -> bool:
        """
        Adapt volume based on background noise
        
        Args:
            noise_level: Background noise level (0.0 to 1.0)
            
        Returns:
            True if successful
        """
        # Adjust volume to maintain target SNR
        # Higher background noise = higher volume
        base_volume = 0.5
        noise_compensation = noise_level * 0.4  # Up to 40% increase
        
        target = min(1.0, base_volume + noise_compensation)
        return self.set_volume(target)
    
    def get_volume(self) -> float:
        """Get current volume level (0.0 to 1.0)"""
        return self.current_volume
    
    def get_volume_percent(self) -> int:
        """Get current volume as percentage (0-100)"""
        return int(self.current_volume * 100)
    
    def increase_volume(self, amount: float = 0.05) -> bool:
        """Increase volume by amount"""
        new_value = self.current_volume + amount
        return self.set_volume(new_value, smooth=False)
    
    def decrease_volume(self, amount: float = 0.05) -> bool:
        """Decrease volume by amount"""
        new_value = self.current_volume - amount
        return self.set_volume(new_value, smooth=False)
    
    def mute(self) -> bool:
        """Mute system volume"""
        return self.set_volume(0.0, smooth=False)
    
    def unmute(self, restore_level: Optional[float] = None) -> bool:
        """
        Unmute system volume
        
        Args:
            restore_level: Level to restore to (None = use target)
        """
        level = restore_level if restore_level is not None else self.target_volume
        return self.set_volume(level, smooth=False)
    
    def get_statistics(self) -> dict:
        """Get volume statistics"""
        return {
            'current': self.get_volume(),
            'current_percent': self.get_volume_percent(),
            'target': self.target_volume,
            'available': self.available,
            'history_mean': float(np.mean(list(self.volume_history))) if self.volume_history else 0.0
        }
