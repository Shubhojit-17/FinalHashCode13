"""
Gesture Controller using CVZone
Provides accurate hand gesture recognition with finger counting
"""

import cv2
import numpy as np
from typing import List, Optional
from dataclasses import dataclass
from collections import deque
import logging
import time
import math
from cvzone.HandTrackingModule import HandDetector

logger = logging.getLogger(__name__)


@dataclass
class GestureData:
    """Data structure for detected gesture information"""
    gesture_type: str
    confidence: float
    value: Optional[float] = None
    hand_type: str = 'Right'


class GestureController:
    """
    Enhanced gesture controller using CVZone for accurate hand tracking
    
    Gestures based on finger count:
    - 0 Fingers (Fist): Toggle gesture control ON/OFF
    - 1 Finger (Index): Volume Control - move hand left/right (0-100)
    - 2 Fingers (Peace): Brightness Control - move hand left/right (0-100)
    - 3 Fingers: Play/Pause toggle
    - 4 Fingers: Next track
    - 5 Fingers (Open palm): Previous track
    """
    
    def __init__(self):
        """Initialize CVZone hand detector"""
        self.detector = HandDetector(
            detectionCon=0.8,  # High confidence for accuracy
            maxHands=1
        )
        
        # Gesture state tracking
        self.gesture_history = deque(maxlen=10)
        self.last_gesture_type = None
        self.gesture_hold_frames = 0
        self.cooldown_frames = 0
        
        # Thresholds
        self.hold_threshold = 15  # Frames to hold before triggering (~0.5 seconds at 30fps)
        self.cooldown_duration = 45  # 1.5 seconds at 30fps (45 frames)
        
        # Y-position tracking for continuous controls (volume/brightness)
        self.last_y_positions = deque(maxlen=5)
        
        # Frame skip for performance
        self.frame_skip = 2
        self.frame_count = 0
        
        # Track last triggered gesture to prevent spam
        self.last_triggered_gesture = None
        self.last_triggered_time = 0
        
        # Track if hand is present
        self.hand_present = False
        
        logger.info("CVZone Gesture Controller initialized - 6 distinct gestures")
    
    def detect_gestures(self, frame: np.ndarray) -> List[GestureData]:
        """
        Detect hand gestures in frame
        
        Args:
            frame: Input BGR image
            
        Returns:
            List of detected gestures
        """
        self.frame_count += 1
        
        # Skip frames for performance
        if self.frame_count % self.frame_skip != 0:
            return self.last_gestures_cache if hasattr(self, 'last_gestures_cache') else []
        
        gestures = []
        
        # Detect hands
        hands, img = self.detector.findHands(frame, draw=True, flipType=True)
        
        if hands:
            self.hand_present = True
            hand = hands[0]  # Get first hand
            
            fingers = self.detector.fingersUp(hand)  # Get which fingers are up [thumb, index, middle, ring, pinky]
            finger_count = fingers.count(1)
            
            # Get hand center position (both X and Y)
            lmList = hand['lmList']  # List of 21 landmarks
            hand_center_x = lmList[9][0]  # Middle finger MCP joint X coordinate
            hand_center_y = lmList[9][1]  # Middle finger MCP joint Y coordinate
            
            frame_width = frame.shape[1]
            frame_height = frame.shape[0]
            
            # Calculate horizontal position (0=left, 100=right)
            x_percent = int((hand_center_x / frame_width) * 100)
            x_percent = max(0, min(100, x_percent))
            
            # Calculate vertical position (0=top, 100=bottom, but inverted for intuitive control)
            # Top of screen = low value, Bottom of screen = high value
            y_percent = int(((frame_height - hand_center_y) / frame_height) * 100)
            y_percent = max(0, min(100, y_percent))
            
            # Classify gesture based on finger count and position
            gesture_type, value = self._classify_by_fingers(finger_count, fingers, x_percent, y_percent)
            
            if gesture_type:
                gesture = GestureData(
                    gesture_type=gesture_type,
                    confidence=0.9,
                    value=value,
                    hand_type=hand['type']
                )
                gestures.append(gesture)
                
                # Add to history for smoothing
                self.gesture_history.append(gesture)
        else:
            # No hand detected - clear state
            if self.hand_present:
                # Hand was just removed
                self.hand_present = False
                self.gesture_history.clear()
                self.last_gesture_type = None
                self.gesture_hold_frames = 0
                # Keep cooldown active to prevent immediate re-trigger
        
        self.last_gestures_cache = gestures
        return gestures
    
    def _classify_by_fingers(self, finger_count: int, fingers: List[int], x_percent: int, y_percent: int) -> tuple:
        """
        Classify gesture based on number of fingers up and hand position
        
        Args:
            finger_count: Number of fingers extended
            fingers: List of finger states [thumb, index, middle, ring, pinky]
            x_percent: Horizontal position of hand (0=left, 100=right)
            y_percent: Vertical position of hand (0=top, 100=bottom)
            
        Returns:
            (gesture_type, value) tuple
        """
        # 0 Fingers (Fist): Toggle gesture control
        if finger_count == 0:
            return ('toggle_gestures', None)
        
        # 1 Finger: Volume Control based on vertical position
        # Top (y=0) = 0% volume, Bottom (y=100) = 100% volume
        elif finger_count == 1 and fingers[1] == 1:  # Only index finger
            return ('volume_control', y_percent)
        
        # 2 Fingers: Brightness Control based on vertical position
        # Top (y=0) = 10% brightness, Bottom (y=100) = 100% brightness
        elif finger_count == 2 and fingers[1] == 1 and fingers[2] == 1:  # Index + Middle
            return ('brightness_control', y_percent)
        
        # 3 Fingers: Play/Pause
        elif finger_count == 3 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:
            return ('play_pause', None)
        
        # 4 Fingers: Next Track
        elif finger_count == 4:
            return ('next_track', None)
        
        # 5 Fingers: Previous Track
        elif finger_count == 5:
            return ('prev_track', None)
        
        return (None, None)
    
    def update_cooldown(self):
        """
        Update cooldown timer every frame, regardless of hand detection
        """
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
            if self.cooldown_frames == 0:
                self.last_triggered_gesture = None
                print(f"[COOLDOWN] Gesture cooldown expired - ready for next gesture")
    
    def get_smoothed_gesture(self) -> Optional[GestureData]:
        """
        Get smoothed gesture with hold detection
        
        Returns:
            Smoothed gesture or None
        """
        if not self.gesture_history:
            return None
        
        # Get most recent gesture
        current_gesture = self.gesture_history[-1]
        
        # For continuous controls (volume/brightness), return immediately (no cooldown)
        if current_gesture.gesture_type in ['volume_control', 'brightness_control']:
            return current_gesture
        
        # For toggle actions (play/pause, next, prev), use hold + cooldown per gesture
        # Only block the SAME gesture from repeating, not different gestures
        if self.cooldown_frames > 0 and current_gesture.gesture_type == self.last_triggered_gesture:
            return None  # Still in cooldown for this specific gesture
        
        # Different gesture - allow it immediately
        if self.cooldown_frames > 0 and current_gesture.gesture_type != self.last_triggered_gesture:
            self.cooldown_frames = 0  # Reset cooldown for new gesture
            self.last_triggered_gesture = None
        
        # Check if same gesture is being held
        if current_gesture.gesture_type == self.last_gesture_type:
            self.gesture_hold_frames += 1
        else:
            self.gesture_hold_frames = 1
            self.last_gesture_type = current_gesture.gesture_type
        
        # Trigger only if held long enough
        if self.gesture_hold_frames >= self.hold_threshold:
            # Only trigger if hand is present (prevent ghost triggers)
            if self.hand_present:
                self.gesture_hold_frames = 0
                self.cooldown_frames = self.cooldown_duration
                self.last_triggered_gesture = current_gesture.gesture_type
                print(f"[COOLDOWN] 1.5-second cooldown started for {current_gesture.gesture_type}")
                return current_gesture
            else:
                # Hand removed, reset
                self.gesture_hold_frames = 0
        
        return None
    
    def draw_gesture_info(self, frame: np.ndarray, gestures: List[GestureData]) -> np.ndarray:
        """
        Draw gesture information on frame
        
        Args:
            frame: Input image
            gestures: List of detected gestures
            
        Returns:
            Frame with drawn information
        """
        if not gestures:
            # Show cooldown status if active
            if self.cooldown_frames > 0:
                cooldown_seconds = self.cooldown_frames / 30.0  # Assuming 30fps
                text = f"Cooldown: {cooldown_seconds:.1f}s"
                cv2.putText(frame, text, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)  # Orange color
            return frame
        
        gesture = gestures[0]
        
        # Draw gesture type
        gesture_names = {
            'toggle_gestures': 'Fist: Toggle Gestures',
            'volume_control': '1 Finger: Volume (←→)',
            'brightness_control': '2 Fingers: Brightness (←→)',
            'play_pause': '3 Fingers: Play/Pause',
            'next_track': '4 Fingers: Next Track',
            'prev_track': '5 Fingers: Previous Track'
        }
        
        text = gesture_names.get(gesture.gesture_type, gesture.gesture_type)
        if gesture.value is not None:
            text += f" ({gesture.value}%)"
        
        # Show cooldown if active
        if self.cooldown_frames > 0:
            cooldown_seconds = self.cooldown_frames / 30.0
            text += f" [Cooldown: {cooldown_seconds:.1f}s]"
        
        cv2.putText(frame, text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame
    
    def __del__(self):
        """Cleanup"""
        pass
