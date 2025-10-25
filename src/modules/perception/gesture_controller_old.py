"""
Gesture Controller Module
Handles hand detection and gesture recognition using MediaPipe Hands
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, Dict, List
import logging
from dataclasses import dataclass
from collections import deque
from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class GestureData:
    """Data structure for detected gesture information"""
    gesture_type: str  # 'volume_up', 'volume_down', 'brightness_up', 'brightness_down', 'play_pause', etc.
    confidence: float
    hand_landmarks: np.ndarray
    hand_type: str  # 'Left' or 'Right'
    value: Optional[float] = None  # For continuous gestures (e.g., volume level)


class GestureController:
    """Detects hand gestures and maps them to actions"""
    
    def __init__(self):
        """Initialize gesture controller"""
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=settings.GESTURE_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.GESTURE_DETECTION_CONFIDENCE
        )
        
        # Gesture state tracking
        self.last_gesture: Optional[GestureData] = None
        self.gesture_history = deque(maxlen=settings.GESTURE_SMOOTHING_WINDOW)
        self.last_gestures_cache: List[GestureData] = []
        self.frame_count = 0
        
        # Gesture value smoothing
        self.thumb_index_distances = deque(maxlen=settings.GESTURE_SMOOTHING_WINDOW)
        self.wrist_y_positions = deque(maxlen=settings.GESTURE_SMOOTHING_WINDOW)
        
        # Palm state for play/pause
        self.palm_open_count = 0
        self.palm_closed_count = 0
        self.last_palm_state = None
        
        logger.info("Gesture controller initialized")
    
    def detect_gestures(self, frame: np.ndarray) -> List[GestureData]:
        """
        Detect hand gestures in frame (optimized to run every 2nd frame)
        
        Args:
            frame: BGR image from camera
            
        Returns:
            List of GestureData objects
        """
        if frame is None:
            return []
        
        self.frame_count += 1
        
        # Run gesture detection every 2nd frame to improve FPS
        # Return cached gestures on alternate frames
        if self.frame_count % 2 == 0:
            return self.last_gestures_cache
        
        # Convert to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect hands
        results = self.hands.process(frame_rgb)
        
        gestures = []
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_type = handedness.classification[0].label
                gesture_data = self._process_hand_landmarks(hand_landmarks, hand_type, frame.shape)
                if gesture_data:
                    gestures.append(gesture_data)
        
        # Update gesture history
        if gestures:
            self.gesture_history.extend(gestures)
            self.last_gesture = gestures[0]  # Use most recent
        
        # Cache for next frame
        self.last_gestures_cache = gestures
        
        return gestures
    
    def _process_hand_landmarks(self, hand_landmarks, hand_type: str, frame_shape) -> Optional[GestureData]:
        """Process hand landmarks to detect gestures"""
        try:
            landmarks = hand_landmarks.landmark
            h, w = frame_shape[:2]
            
            # Extract key landmarks
            wrist = landmarks[self.mp_hands.HandLandmark.WRIST]
            thumb_tip = landmarks[self.mp_hands.HandLandmark.THUMB_TIP]
            index_tip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            ring_tip = landmarks[self.mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_tip = landmarks[self.mp_hands.HandLandmark.PINKY_TIP]
            
            # Calculate thumb-index distance (for volume control)
            thumb_index_dist = self._calculate_distance(thumb_tip, index_tip)
            self.thumb_index_distances.append(thumb_index_dist)
            
            # Calculate wrist Y position (for brightness control)
            wrist_y = wrist.y
            self.wrist_y_positions.append(wrist_y)
            
            # Smooth values
            smooth_thumb_index = np.mean(self.thumb_index_distances) if self.thumb_index_distances else thumb_index_dist
            smooth_wrist_y = np.mean(self.wrist_y_positions) if self.wrist_y_positions else wrist_y
            
            # Detect gesture type
            gesture_type, value = self._classify_gesture(
                smooth_thumb_index, smooth_wrist_y, 
                landmarks
            )
            
            # Extract landmarks as array
            landmarks_array = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
            
            return GestureData(
                gesture_type=gesture_type,
                confidence=0.9,  # MediaPipe Hands doesn't provide confidence per gesture
                hand_landmarks=landmarks_array,
                hand_type=hand_type,
                value=value
            )
            
        except Exception as e:
            logger.error(f"Error processing hand landmarks: {e}")
            return None
    
    def _calculate_distance(self, point1, point2) -> float:
        """Calculate Euclidean distance between two landmarks"""
        return np.sqrt(
            (point1.x - point2.x)**2 + 
            (point1.y - point2.y)**2 + 
            (point1.z - point2.z)**2
        )
    
    def _classify_gesture(self, thumb_index_dist: float, wrist_y: float, landmarks) -> Tuple[str, Optional[float]]:
        """
        Classify gesture based on hand landmarks
        
        Gesture Mappings:
        - Open palm: Play/Pause toggle (highest priority)
        - Thumb-Index distance (pinch): Volume control
        - Wrist Y position: Brightness control (always evaluated)
        
        Returns:
            Tuple of (gesture_type, value)
        """
        # Check play/pause FIRST (highest priority)
        if self._is_palm_open(landmarks):
            self.palm_open_count += 1
            self.palm_closed_count = 0
            if self.palm_open_count >= 15 and self.last_palm_state != 'open':
                self.last_palm_state = 'open'
                return ('play_pause', None)
        else:
            self.palm_closed_count += 1
            self.palm_open_count = 0
            if self.palm_closed_count >= 10:
                self.last_palm_state = 'closed'
        
        # Volume control: Thumb-Index pinch distance (only if pinching)
        if settings.THUMB_INDEX_MIN_DISTANCE <= thumb_index_dist <= settings.THUMB_INDEX_MAX_DISTANCE:
            # Map distance to volume (0-100)
            volume_range = settings.THUMB_INDEX_MAX_DISTANCE - settings.THUMB_INDEX_MIN_DISTANCE
            volume_normalized = (thumb_index_dist - settings.THUMB_INDEX_MIN_DISTANCE) / volume_range
            volume_percent = np.clip(volume_normalized * 100, 0, 100)
            return ('volume_control', volume_percent)
        
        # Brightness control: Wrist Y position (always check, no threshold needed)
        # Lower Y = top of screen = brighter
        # Higher Y = bottom of screen = dimmer
        brightness_normalized = 1.0 - np.clip(wrist_y, 0.2, 0.8)  # Invert and limit range
        brightness_percent = ((brightness_normalized - 0.2) / 0.6) * 100  # Map to 0-100
        
        # Always return brightness control (removed the threshold check)
        return ('brightness_control', brightness_percent)
    
    def _is_palm_open(self, landmarks) -> bool:
        """
        Detect if palm is open (all fingers extended)
        
        Returns:
            True if palm is open
        """
        # Check if all fingertips are higher than their respective MCP joints
        finger_tips = [
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.PINKY_TIP
        ]
        
        finger_mcps = [
            self.mp_hands.HandLandmark.INDEX_FINGER_MCP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
            self.mp_hands.HandLandmark.RING_FINGER_MCP,
            self.mp_hands.HandLandmark.PINKY_MCP
        ]
        
        fingers_extended = 0
        for tip, mcp in zip(finger_tips, finger_mcps):
            # Finger is extended if tip Y is less than MCP Y (tip is higher)
            if landmarks[tip].y < landmarks[mcp].y - 0.05:  # 5% margin
                fingers_extended += 1
        
        # Palm is open if at least 3 fingers are extended
        return fingers_extended >= 3
    
    def get_smoothed_gesture(self) -> Optional[GestureData]:
        """
        Get smoothed gesture from history
        
        Returns:
            Most common gesture from recent history
        """
        if not self.gesture_history:
            return None
        
        # Count gesture types
        gesture_counts = {}
        for gesture in self.gesture_history:
            gesture_type = gesture.gesture_type
            if gesture_type not in gesture_counts:
                gesture_counts[gesture_type] = []
            gesture_counts[gesture_type].append(gesture)
        
        # Find most common gesture
        if gesture_counts:
            most_common = max(gesture_counts.items(), key=lambda x: len(x[1]))
            gestures_list = most_common[1]
            
            # Average values if available
            values = [g.value for g in gestures_list if g.value is not None]
            avg_value = np.mean(values) if values else None
            
            # Return smoothed gesture
            return GestureData(
                gesture_type=gestures_list[0].gesture_type,
                confidence=gestures_list[0].confidence,
                hand_landmarks=gestures_list[0].hand_landmarks,
                hand_type=gestures_list[0].hand_type,
                value=avg_value
            )
        
        return None
    
    def draw_hands(self, frame: np.ndarray, gestures: List[GestureData]) -> np.ndarray:
        """
        Draw hand landmarks and gesture info on frame
        
        Args:
            frame: BGR image
            gestures: List of GestureData objects
            
        Returns:
            Annotated frame
        """
        annotated_frame = frame.copy()
        h, w = frame.shape[:2]
        
        for gesture in gestures:
            # Convert landmarks back to MediaPipe format for drawing
            landmark_list = []
            for lm in gesture.hand_landmarks:
                landmark = self.mp_hands.HandLandmark
                # Create a simple object with x, y, z attributes
                class LandmarkPoint:
                    def __init__(self, x, y, z):
                        self.x = x
                        self.y = y
                        self.z = z
                landmark_list.append(LandmarkPoint(lm[0], lm[1], lm[2]))
            
            # Draw gesture info
            text = f"{gesture.hand_type}: {gesture.gesture_type}"
            if gesture.value is not None:
                text += f" ({gesture.value:.0f}%)"
            
            cv2.putText(
                annotated_frame, text,
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2
            )
        
        return annotated_frame
    
    def release(self):
        """Release MediaPipe resources"""
        try:
            if hasattr(self, 'hands') and self.hands is not None:
                self.hands.close()
                self.hands = None
        except Exception:
            pass  # Ignore errors during cleanup
        logger.info("Gesture controller released")
    
    def __del__(self):
        """Destructor to ensure resources are released"""
        try:
            self.release()
        except Exception:
            pass  # Ignore errors during cleanup
