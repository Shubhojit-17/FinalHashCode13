"""
Camera Capture Module
Handles video capture from webcam with configurable settings
"""

import cv2
import numpy as np
from typing import Optional, Tuple
import logging
from src.config import settings

logger = logging.getLogger(__name__)


class CameraCapture:
    """Manages camera initialization and frame capture"""
    
    def __init__(self, camera_index: int = None):
        """
        Initialize camera capture
        
        Args:
            camera_index: Camera device index (None uses config default)
        """
        self.camera_index = camera_index or settings.CAMERA_INDEX
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.frame_count = 0
        
    def start(self) -> bool:
        """
        Start camera capture
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, settings.CAMERA_FPS)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_index}")
                return False
            
            self.is_running = True
            logger.info(f"Camera {self.camera_index} started successfully")
            logger.info(f"Resolution: {settings.CAMERA_WIDTH}x{settings.CAMERA_HEIGHT}")
            logger.info(f"FPS: {settings.CAMERA_FPS}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            return False
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the camera
        
        Returns:
            Tuple of (success, frame) where frame is BGR image
        """
        if not self.is_running or self.cap is None:
            return False, None
        
        try:
            ret, frame = self.cap.read()
            if ret:
                self.frame_count += 1
                return True, frame
            else:
                logger.warning("Failed to read frame from camera")
                return False, None
                
        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            return False, None
    
    def get_frame_rgb(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame and convert to RGB
        
        Returns:
            Tuple of (success, frame) where frame is RGB image
        """
        ret, frame = self.read_frame()
        if ret and frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return True, frame_rgb
        return False, None
    
    def get_camera_properties(self) -> dict:
        """Get current camera properties"""
        if self.cap is None:
            return {}
        
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
            'brightness': self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
            'contrast': self.cap.get(cv2.CAP_PROP_CONTRAST),
            'frame_count': self.frame_count
        }
    
    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_running = False
            logger.info(f"Camera {self.camera_index} released")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.release()
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()
