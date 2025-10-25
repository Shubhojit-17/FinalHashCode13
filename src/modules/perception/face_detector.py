"""
Face Detector Module
Handles face detection, tracking, and distance estimation using MediaPipe
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Optional, Dict
import logging
from dataclasses import dataclass
from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class FaceData:
    """Data structure for detected face information"""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    landmarks: np.ndarray
    distance: float  # in cm
    position: Tuple[float, float]  # normalized (0-1)
    confidence: float


class FaceDetector:
    """Detects faces and estimates distance using MediaPipe Face Mesh"""
    
    def __init__(self):
        """Initialize face detector"""
        # Initialize MediaPipe Face Mesh (more accurate than Face Detection)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=3,
            refine_landmarks=True,
            min_detection_confidence=settings.FACE_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.FACE_DETECTION_CONFIDENCE
        )
        
        # Distance estimation parameters
        self.known_face_width = settings.KNOWN_FACE_WIDTH_CM
        self.focal_length = settings.FOCAL_LENGTH
        
        # Tracking
        self.last_faces: List[FaceData] = []
        self.frame_width = 0
        self.frame_height = 0
        
        logger.info("Face detector initialized")
    
    def detect_faces(self, frame: np.ndarray) -> List[FaceData]:
        """
        Detect faces in frame using Face Mesh
        
        Args:
            frame: BGR image from camera
            
        Returns:
            List of FaceData objects
        """
        if frame is None:
            return []
        
        # Store frame dimensions
        self.frame_height, self.frame_width = frame.shape[:2]
        
        # Convert to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        results = self.face_mesh.process(frame_rgb)
        
        faces = []
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                face_data = self._process_face_mesh(face_landmarks)
                if face_data:
                    faces.append(face_data)
        
        self.last_faces = faces
        return faces
    
    def _process_face_mesh(self, face_landmarks) -> Optional[FaceData]:
        """Process Face Mesh landmarks"""
        try:
            landmarks = face_landmarks.landmark
            
            # Get face width using landmarks 234 (left) and 454 (right)
            left_x = landmarks[234].x
            right_x = landmarks[454].x
            face_width_normalized = abs(right_x - left_x)
            face_width_px = face_width_normalized * self.frame_width
            
            # Calculate distance using face width
            if face_width_px > 10:  # Reasonable minimum
                distance_cm = (settings.KNOWN_FACE_WIDTH_CM * settings.FOCAL_LENGTH) / face_width_px
                distance = float(np.clip(distance_cm, settings.MIN_DISTANCE_CM, settings.MAX_DETECTION_DISTANCE))
            else:
                return None
            
            # Calculate bounding box from landmarks
            xs = [lm.x for lm in landmarks]
            ys = [lm.y for lm in landmarks]
            
            x_min = int(min(xs) * self.frame_width)
            x_max = int(max(xs) * self.frame_width)
            y_min = int(min(ys) * self.frame_height)
            y_max = int(max(ys) * self.frame_height)
            
            w = x_max - x_min
            h = y_max - y_min
            
            # Filter out too small faces
            if w < settings.MIN_FACE_SIZE or h < settings.MIN_FACE_SIZE:
                return None
            
            # Calculate normalized position (center of face)
            pos_x = (x_min + w/2) / self.frame_width
            pos_y = (y_min + h/2) / self.frame_height
            
            # Extract key landmarks for storage
            key_landmarks = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
            
            return FaceData(
                bbox=(x_min, y_min, w, h),
                landmarks=key_landmarks,
                distance=distance,
                position=(pos_x, pos_y),
                confidence=0.9  # Face Mesh doesn't provide confidence, use high value
            )
            
        except Exception as e:
            logger.error(f"Error processing face mesh: {e}")
            return None
    
    def estimate_distance(self, face_width_pixels: int) -> float:
        """
        Estimate distance to face using triangulation
        
        Args:
            face_width_pixels: Width of detected face in pixels
            
        Returns:
            Distance in centimeters
        """
        if face_width_pixels == 0:
            return settings.MAX_DETECTION_DISTANCE
        
        # Distance = (Known Width * Focal Length) / Perceived Width
        distance = (self.known_face_width * self.focal_length) / face_width_pixels
        
        # Clamp to reasonable range
        distance = max(10, min(distance, settings.MAX_DETECTION_DISTANCE))
        
        return distance
    
    def get_average_distance(self, faces: List[FaceData]) -> float:
        """
        Calculate average distance of all detected faces
        
        Args:
            faces: List of FaceData objects
            
        Returns:
            Average distance in cm
        """
        if not faces:
            return settings.MAX_DETECTION_DISTANCE
        
        return np.mean([face.distance for face in faces])
    
    def get_closest_face(self, faces: List[FaceData]) -> Optional[FaceData]:
        """Get the closest face to camera"""
        if not faces:
            return None
        
        return min(faces, key=lambda f: f.distance)
    
    def draw_faces(self, frame: np.ndarray, faces: List[FaceData]) -> np.ndarray:
        """
        Draw face bounding boxes and information on frame
        
        Args:
            frame: BGR image
            faces: List of FaceData objects
            
        Returns:
            Annotated frame
        """
        annotated_frame = frame.copy()
        
        for i, face in enumerate(faces):
            x, y, w, h = face.bbox
            
            # Draw bounding box
            color = (0, 255, 0)  # Green
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw distance info
            distance_text = f"Dist: {face.distance:.1f}cm"
            cv2.putText(
                annotated_frame, distance_text,
                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, color, 2
            )
            
            # Draw face number
            face_num = f"Face {i+1}"
            cv2.putText(
                annotated_frame, face_num,
                (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 1
            )
            
            # Draw landmarks if available
            if settings.SHOW_LANDMARKS and len(face.landmarks) > 0:
                for landmark in face.landmarks:
                    lm_x = int(landmark[0] * self.frame_width)
                    lm_y = int(landmark[1] * self.frame_height)
                    cv2.circle(annotated_frame, (lm_x, lm_y), 3, (255, 0, 0), -1)
        
        return annotated_frame
    
    def release(self):
        """Release resources"""
        try:
            if hasattr(self, 'face_mesh') and self.face_mesh is not None:
                self.face_mesh.close()
                self.face_mesh = None
        except Exception:
            pass  # Ignore errors during cleanup
        logger.info("Face detector released")
    
    def __del__(self):
        """Destructor to ensure resources are released"""
        try:
            self.release()
        except Exception:
            pass  # Ignore errors during cleanup
        logger.info("Face detector released")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.release()
