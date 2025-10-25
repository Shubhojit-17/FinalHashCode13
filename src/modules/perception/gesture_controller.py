"""
Fresh Gesture Controller with Position + Movement Based Controls
Supports both hands equally with accurate finger detection
"""

import cv2
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import logging
import time
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
    Fresh gesture controller with dual control modes:
    - Position-based: Hand position on screen directly sets volume/brightness (0-100%)
    - Movement-based: Moving hand left/right adjusts volume/brightness incrementally
    
    Gesture mappings (same for both hands):
    - 0 Fingers (Fist): Toggle gesture control ON/OFF
    - 1 Finger (Index): Volume Control
    - 2 Fingers (Peace): Brightness Control
    - 3 Fingers: Play/Pause toggle
    - 4 Fingers: Next track
    - 5 Fingers (Open palm): Previous track
    """
    
    def __init__(self):
        """Initialize hand detector and tracking variables"""
        self.logger = logging.getLogger(__name__)
        self.detector = HandDetector(
            detectionCon=0.85,  # Increased confidence for better accuracy
            minTrackCon=0.8,    # Minimum tracking confidence
            maxHands=1
        )
        
        # Position tracking for movement-based control
        self.last_hand_x = None
        self.last_hand_y = None
        
        # Gesture state
        self.last_gesture_type = None
        self.gesture_active = True  # Controls can be toggled with fist
        
        # Cooldown to prevent gesture spam
        self.last_action_time = 0
        self.cooldown_seconds = 2.0  # 2 seconds between discrete gestures
        self.in_cooldown = False
        self.cooldown_start_time = 0
        
        # Track registered gesture to prevent repetition
        self.registered_gesture = None
        self.registered_finger_count = None
        
        # Gesture stability - require same gesture for multiple frames
        self.last_finger_count = None
        self.finger_count_stable_frames = 0
        self.stability_threshold = 2  # Require 2 consistent frames (reduced from 3)
        
        # Movement smoothing
        self.position_history = deque(maxlen=3)
        
        # Track if hand is present
        self.hand_present = False
        
        self.logger.info("Fresh gesture controller initialized")
    
    def _count_fingers(self, hand: dict) -> Tuple[int, List[int]]:
        """
        Accurate finger counting using MediaPipe landmarks
        
        Args:
            hand: Hand dictionary from CVZone with 'lmList' and 'type'
            
        Returns:
            Tuple of (finger_count, fingers_list) where fingers_list is [thumb, index, middle, ring, pinky]
            1 = finger up, 0 = finger down
        """
        lmList = hand['lmList']  # 21 landmarks
        hand_type = hand.get('type', 'Right')
        fingers = [0, 0, 0, 0, 0]
        
        # Landmark indices
        # Thumb: 4=tip, 3=IP, 2=MCP, 1=CMC
        # Index: 8=tip, 7=DIP, 6=PIP, 5=MCP
        # Middle: 12=tip, 11=DIP, 10=PIP, 9=MCP
        # Ring: 16=tip, 15=DIP, 14=PIP, 13=MCP
        # Pinky: 20=tip, 19=DIP, 18=PIP, 17=MCP
        
        # Thumb - special handling based on hand type
        # Compare tip with IP joint for better accuracy
        thumb_tip_x = lmList[4][0]
        thumb_ip_x = lmList[3][0]
        thumb_mcp_x = lmList[2][0]
        
        # Use a dynamic threshold based on hand size
        hand_size = abs(lmList[0][1] - lmList[9][1])  # Distance from wrist to middle finger MCP
        thumb_threshold = max(25, hand_size * 0.18)  # Increased for stricter thumb detection
        
        if hand_type == 'Right':
            # For right hand, thumb extends to the right
            fingers[0] = 1 if thumb_tip_x > thumb_ip_x + thumb_threshold else 0
        else:  # Left hand
            # For left hand, thumb extends to the left
            fingers[0] = 1 if thumb_tip_x < thumb_ip_x - thumb_threshold else 0
        
        # Other fingers: Compare tip with PIP joint (more accurate than MCP)
        # tip Y-coordinate < PIP Y-coordinate means finger is up
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        finger_mcps = [5, 9, 13, 17]
        
        for i, (tip_id, pip_id, mcp_id) in enumerate(zip(finger_tips, finger_pips, finger_mcps)):
            tip_y = lmList[tip_id][1]
            pip_y = lmList[pip_id][1]
            mcp_y = lmList[mcp_id][1]
            
            # Increased adaptive threshold for stricter detection
            finger_threshold = max(15, hand_size * 0.12)
            
            # Multi-point check for better accuracy:
            # 1. Tip must be CLEARLY above PIP (stricter check)
            # 2. PIP must be above or near MCP (finger not curled)
            tip_above_pip = tip_y < pip_y - finger_threshold
            pip_not_below_mcp = pip_y <= mcp_y + (finger_threshold * 0.5)
            
            # Finger is considered up only if both conditions are met
            fingers[i + 1] = 1 if (tip_above_pip and pip_not_below_mcp) else 0
        
        finger_count = sum(fingers)
        return finger_count, fingers
    
    def _get_hand_position(self, hand: dict, frame_width: int, frame_height: int) -> Tuple[float, float]:
        """
        Get hand center position as percentage (0-100) of frame dimensions
        
        Args:
            hand: Hand dictionary from CVZone
            frame_width: Width of the frame
            frame_height: Height of the frame
            
        Returns:
            Tuple of (x_percent, y_percent) where 0=left/top, 100=right/bottom
        """
        lmList = hand['lmList']
        # Use wrist (landmark 0) as reference point
        hand_x = lmList[0][0]
        hand_y = lmList[0][1]
        
        x_percent = (hand_x / frame_width) * 100
        y_percent = (hand_y / frame_height) * 100
        
        # Clamp to 0-100
        x_percent = max(0, min(100, x_percent))
        y_percent = max(0, min(100, y_percent))
        
        return x_percent, y_percent
    
    def _get_movement_delta(self, current_x: float, current_y: float) -> Tuple[float, float]:
        """
        Calculate movement delta from last position
        
        Args:
            current_x: Current X position percentage
            current_y: Current Y position percentage
            
        Returns:
            Tuple of (delta_x, delta_y) in percentage points
        """
        if self.last_hand_x is None or self.last_hand_y is None:
            self.last_hand_x = current_x
            self.last_hand_y = current_y
            return 0, 0
        
        delta_x = current_x - self.last_hand_x
        delta_y = current_y - self.last_hand_y
        
        # Update last position
        self.last_hand_x = current_x
        self.last_hand_y = current_y
        
        return delta_x, delta_y
    
    def _classify_gesture(self, finger_count: int, fingers: List[int], 
                         x_percent: float, y_percent: float,
                         delta_x: float, delta_y: float) -> Tuple[Optional[str], Optional[float]]:
        """
        Classify gesture based on finger count and return control value
        
        Args:
            finger_count: Number of fingers up (0-5)
            fingers: List of individual finger states
            x_percent: Hand X position (0-100)
            y_percent: Hand Y position (0-100)
            delta_x: Horizontal movement delta
            delta_y: Vertical movement delta
            
        Returns:
            Tuple of (gesture_type, value) where value is for continuous controls
        """
        current_time = time.time()
        
        # Special handling for fist gesture (0 fingers) - always check, bypass cooldown check
        if finger_count == 0:
            # Additional validation: ensure ALL fingers are really down
            # Check that all finger values are 0
            if sum(fingers) != 0:
                # False fist detection - at least one finger is up
                return None, None
            
            # Check if this is the same gesture still being held
            if self.registered_gesture == 'toggle_gestures' and self.registered_finger_count == 0:
                return None, None  # Already registered and held
            
            # New toggle gesture
            self.gesture_active = not self.gesture_active
            status = "ENABLED" if self.gesture_active else "DISABLED"
            self.logger.info(f"Gesture control {status}")
            
            # Start cooldown
            self.in_cooldown = True
            self.cooldown_start_time = current_time
            self.registered_gesture = 'toggle_gestures'
            self.registered_finger_count = 0
            
            return 'toggle_gestures', None
        
        # Check if we're in cooldown for other gestures
        if self.in_cooldown:
            elapsed = current_time - self.cooldown_start_time
            if elapsed < self.cooldown_seconds:
                # Still in cooldown
                return None, None
            else:
                # Cooldown expired
                self.in_cooldown = False
                self.registered_gesture = None
                self.registered_finger_count = None
        
        # Check if this is the same gesture that was already registered
        if self.registered_gesture and finger_count == self.registered_finger_count:
            # Same gesture still being held - don't re-register
            return None, None
        
        # Continuous controls (volume/brightness) - always active, no cooldown
        if finger_count == 1:
            # Index finger: Volume control
            position_value = x_percent
            movement_adjustment = delta_x * 2
            combined_value = position_value + movement_adjustment
            combined_value = max(0, min(100, combined_value))
            return 'volume_control', combined_value
        
        elif finger_count == 2:
            # Peace sign: Brightness control
            position_value = x_percent
            movement_adjustment = delta_x * 2
            combined_value = position_value + movement_adjustment
            combined_value = max(0, min(100, combined_value))
            return 'brightness_control', combined_value
        
        # Discrete actions - require cooldown
        gesture_type = None
        
        if not self.gesture_active:
            # Gestures disabled, only fist (already handled above) can re-enable
            return None, None
            
        if finger_count == 3:
            # Play/Pause
            gesture_type = 'play_pause'
        
        elif finger_count == 4:
            # Next track
            gesture_type = 'next_track'
        
        elif finger_count == 5:
            # Previous track
            gesture_type = 'prev_track'
        
        # If we detected a discrete gesture, start cooldown
        if gesture_type:
            self.in_cooldown = True
            self.cooldown_start_time = current_time
            self.registered_gesture = gesture_type
            self.registered_finger_count = finger_count
            return gesture_type, None
        
        return None, None
    
    def detect_gestures(self, frame: np.ndarray) -> List[GestureData]:
        """
        Detect hand gestures in the frame
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            List of detected gestures with control values
        """
        gestures = []
        
        # Detect hands
        hands, img = self.detector.findHands(frame, draw=True, flipType=True)
        
        if not hands:
            # No hand detected - reset movement tracking
            self.last_hand_x = None
            self.last_hand_y = None
            self.hand_present = False
            self.last_finger_count = None
            self.finger_count_stable_frames = 0
            # Don't reset cooldown or registered gesture - let them expire naturally
            return gestures
        
        # Process first detected hand (works for both left and right)
        hand = hands[0]
        self.hand_present = True
        
        # Count fingers
        finger_count, fingers = self._count_fingers(hand)
        
        # Check finger count stability for discrete gestures (3, 4, 5 fingers)
        # Fist (0) and continuous controls (1, 2 fingers) don't need stability check for faster response
        if finger_count in [3, 4, 5]:
            if finger_count == self.last_finger_count:
                self.finger_count_stable_frames += 1
            else:
                self.last_finger_count = finger_count
                self.finger_count_stable_frames = 1
            
            # Only proceed if gesture is stable
            if self.finger_count_stable_frames < self.stability_threshold:
                return gestures
        else:
            # Reset stability for fist and continuous controls
            self.last_finger_count = None
            self.finger_count_stable_frames = 0
            self.finger_count_stable_frames = 0
        
        # Get hand position
        frame_height, frame_width = frame.shape[:2]
        x_percent, y_percent = self._get_hand_position(hand, frame_width, frame_height)
        
        # Get movement delta
        delta_x, delta_y = self._get_movement_delta(x_percent, y_percent)
        
        # Classify gesture
        gesture_type, value = self._classify_gesture(
            finger_count, fingers, x_percent, y_percent, delta_x, delta_y
        )
        
        # Log detection
        hand_type = hand.get('type', 'Unknown')
        if gesture_type:
            self.logger.debug(
                f"Hand: {hand_type} | Fingers: {finger_count} {fingers} | "
                f"Position: ({x_percent:.1f}%, {y_percent:.1f}%) | "
                f"Movement: ({delta_x:.1f}, {delta_y:.1f}) | "
                f"Gesture: {gesture_type} | Value: {value}"
            )
        
        if gesture_type:
            gesture = GestureData(
                gesture_type=gesture_type,
                confidence=0.9,
                value=value,
                hand_type=hand_type
            )
            gestures.append(gesture)
        
        return gestures
    
    def update_cooldown(self, dt: float = 0) -> None:
        """
        Update cooldown timer (called every frame)
        Check if cooldown has expired even when no hand is detected
        
        Args:
            dt: Delta time in seconds (unused, cooldown is time-based)
        """
        if self.in_cooldown:
            current_time = time.time()
            elapsed = current_time - self.cooldown_start_time
            
            if elapsed >= self.cooldown_seconds:
                # Cooldown expired
                self.in_cooldown = False
                self.registered_gesture = None
                self.registered_finger_count = None
    
    def is_active(self) -> bool:
        """Check if gesture control is active"""
        return self.gesture_active
    
    def draw_gesture_info(self, frame: np.ndarray, gestures: List[GestureData], 
                         actual_volume: Optional[float] = None, 
                         actual_brightness: Optional[int] = None) -> np.ndarray:
        """
        Draw gesture information on frame
        
        Args:
            frame: Input image
            gestures: List of detected gestures
            actual_volume: Actual applied volume (0-1 range)
            actual_brightness: Actual applied brightness (0-100 range)
            
        Returns:
            Frame with drawn information
        """
        if not gestures:
            status_text = "Gestures: " + ("ENABLED" if self.gesture_active else "DISABLED")
            cv2.putText(frame, status_text, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if self.gesture_active else (0, 0, 255), 2)
            return frame
        
        gesture = gestures[0]
        
        # Draw gesture type
        gesture_names = {
            'toggle_gestures': 'Fist: Toggle Gestures',
            'volume_control': '1 Finger: Volume Control',
            'brightness_control': '2 Fingers: Brightness Control',
            'play_pause': '3 Fingers: Play/Pause',
            'next_track': '4 Fingers: Next Track',
            'prev_track': '5 Fingers: Previous Track'
        }
        
        text = gesture_names.get(gesture.gesture_type, gesture.gesture_type)
        
        # Show actual applied values instead of gesture values
        if gesture.gesture_type == 'volume_control' and actual_volume is not None:
            text += f" ({int(actual_volume * 100)}%)"
        elif gesture.gesture_type == 'brightness_control' and actual_brightness is not None:
            text += f" ({actual_brightness}%)"
        elif gesture.value is not None:
            text += f" ({gesture.value:.1f}%)"
        
        cv2.putText(frame, text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame
