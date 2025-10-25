"""
Environment Monitor Module
Monitors environmental conditions (ambient light, crowd, weather)
"""

import logging
import numpy as np
import cv2
from typing import Optional
from collections import deque
from src.config import settings

logger = logging.getLogger(__name__)


class EnvironmentMonitor:
    """Monitors environmental conditions for adaptive control"""
    
    def __init__(self):
        """Initialize environment monitor"""
        self.ambient_light_history = deque(maxlen=settings.AMBIENT_LIGHT_SAMPLES)
        self.current_ambient_light = 128.0
        
        logger.info("Environment monitor initialized")
    
    def estimate_ambient_light(self, frame: np.ndarray) -> float:
        """
        Estimate ambient light level from camera frame
        
        Args:
            frame: BGR image from camera
            
        Returns:
            Ambient light level (0-255)
        """
        if frame is None:
            return self.current_ambient_light
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate mean brightness
        mean_brightness = np.mean(gray)
        
        # Update history
        self.ambient_light_history.append(mean_brightness)
        
        # Calculate smoothed value
        if len(self.ambient_light_history) > 0:
            self.current_ambient_light = np.mean(list(self.ambient_light_history))
        
        return self.current_ambient_light
    
    def get_lighting_condition(self) -> str:
        """
        Get qualitative lighting condition
        
        Returns:
            'dark', 'normal', or 'bright'
        """
        if self.current_ambient_light < settings.DARK_THRESHOLD:
            return 'dark'
        elif self.current_ambient_light > settings.BRIGHT_THRESHOLD:
            return 'bright'
        else:
            return 'normal'
    
    def get_statistics(self) -> dict:
        """Get environment statistics"""
        return {
            'ambient_light': self.current_ambient_light,
            'lighting_condition': self.get_lighting_condition(),
            'history_size': len(self.ambient_light_history)
        }
