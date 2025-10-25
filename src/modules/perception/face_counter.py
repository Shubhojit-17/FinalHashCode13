"""
Face Counter Module
Tracks and counts faces with smoothing and history
"""

import numpy as np
from typing import List
from collections import deque
import logging
from src.modules.perception.face_detector import FaceData
from src.config import settings

logger = logging.getLogger(__name__)


class FaceCounter:
    """Counts and tracks faces over time with smoothing"""
    
    def __init__(self):
        """Initialize face counter"""
        self.face_count_history = deque(maxlen=settings.FACE_COUNT_SMOOTHING)
        self.current_count = 0
        self.smoothed_count = 0
        self.total_faces_detected = 0
        
        logger.info("Face counter initialized")
    
    def update(self, faces: List[FaceData]) -> int:
        """
        Update face count with smoothing
        
        Args:
            faces: List of detected faces
            
        Returns:
            Smoothed face count
        """
        self.current_count = len(faces)
        self.face_count_history.append(self.current_count)
        
        # Calculate smoothed count using moving average
        if len(self.face_count_history) > 0:
            self.smoothed_count = int(np.round(np.mean(list(self.face_count_history))))
        
        # Update total
        if self.current_count > self.total_faces_detected:
            self.total_faces_detected = self.current_count
        
        return self.smoothed_count
    
    def get_count(self) -> int:
        """Get current smoothed face count"""
        return self.smoothed_count
    
    def get_raw_count(self) -> int:
        """Get current raw face count (no smoothing)"""
        return self.current_count
    
    def get_max_count(self) -> int:
        """Get maximum face count detected"""
        return self.total_faces_detected
    
    def get_statistics(self) -> dict:
        """Get face counting statistics"""
        return {
            'current': self.current_count,
            'smoothed': self.smoothed_count,
            'max': self.total_faces_detected,
            'history_size': len(self.face_count_history)
        }
    
    def reset(self):
        """Reset counter statistics"""
        self.face_count_history.clear()
        self.current_count = 0
        self.smoothed_count = 0
        self.total_faces_detected = 0
        logger.info("Face counter reset")
