"""
Weighted Adapter Module
Applies weighted adaptation for volume/brightness based on multiple faces
"""

import logging
import numpy as np
from typing import List
from src.modules.perception.face_detector import FaceData
from src.config import settings

logger = logging.getLogger(__name__)


class WeightedAdapter:
    """Calculates weighted adaptation values based on face positions and distances"""
    
    def __init__(self):
        """Initialize weighted adapter"""
        logger.info("Weighted adapter initialized")
    
    def calculate_distance_weight(self, distance: float) -> float:
        """
        Calculate weight based on distance
        
        Args:
            distance: Distance in cm
            
        Returns:
            Weight multiplier
        """
        if distance < settings.DISTANCE_THRESHOLD_NEAR:
            # Closer faces get higher weight
            return settings.DISTANCE_WEIGHT_NEAR
        else:
            return settings.DISTANCE_WEIGHT_FAR
    
    def calculate_spatial_weight(self, position: tuple) -> float:
        """
        Calculate weight based on position in frame
        
        Args:
            position: Normalized (x, y) position (0-1)
            
        Returns:
            Weight multiplier
        """
        x, y = position
        
        # Calculate distance from center
        center_x, center_y = 0.5, 0.5
        dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Normalize distance (max distance is 0.707 for corners)
        normalized_dist = dist_from_center / 0.707
        
        # Center region gets higher weight
        if normalized_dist < (1 - settings.CENTER_REGION_RATIO):
            return settings.CENTER_WEIGHT
        else:
            return settings.EDGE_WEIGHT
    
    def calculate_face_weight(self, face: FaceData) -> float:
        """
        Calculate total weight for a face
        
        Args:
            face: FaceData object
            
        Returns:
            Total weight
        """
        distance_weight = self.calculate_distance_weight(face.distance)
        spatial_weight = self.calculate_spatial_weight(face.position)
        
        # Combine weights (multiplicative)
        total_weight = distance_weight * spatial_weight
        
        return total_weight
    
    def calculate_weighted_distance(self, faces: List[FaceData]) -> float:
        """
        Calculate weighted average distance
        
        Args:
            faces: List of detected faces
            
        Returns:
            Weighted average distance in cm
        """
        if not faces:
            return settings.MAX_DETECTION_DISTANCE
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for face in faces:
            weight = self.calculate_face_weight(face)
            weighted_sum += face.distance * weight
            total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return np.mean([f.distance for f in faces])
    
    def calculate_brightness_target(self, faces: List[FaceData], 
                                   ambient_light: float = None) -> int:
        """
        Calculate target brightness based on faces and ambient light
        
        Args:
            faces: List of detected faces
            ambient_light: Ambient light level (0-255), optional
            
        Returns:
            Target brightness (0-100)
        """
        if not faces:
            # No faces - use energy saving mode
            if settings.ENERGY_SAVE_MODE:
                return settings.ENERGY_SAVE_BRIGHTNESS
            return 50
        
        # Calculate weighted distance
        weighted_distance = self.calculate_weighted_distance(faces)
        
        # Base brightness on distance
        if weighted_distance < settings.OPTIMAL_DISTANCE_MIN:
            base_brightness = 60  # Closer = dimmer
        elif weighted_distance > settings.OPTIMAL_DISTANCE_MAX:
            base_brightness = 90  # Further = brighter
        else:
            # Linear interpolation in optimal range
            ratio = (weighted_distance - settings.OPTIMAL_DISTANCE_MIN) / \
                   (settings.OPTIMAL_DISTANCE_MAX - settings.OPTIMAL_DISTANCE_MIN)
            base_brightness = 60 + (30 * ratio)
        
        # Adjust for ambient light if provided
        if ambient_light is not None:
            if ambient_light < settings.DARK_THRESHOLD:
                # Dark - reduce brightness
                ambient_factor = 0.7
            elif ambient_light > settings.BRIGHT_THRESHOLD:
                # Bright - increase brightness
                ambient_factor = 1.3
            else:
                ambient_factor = 1.0
            
            base_brightness *= ambient_factor
        
        # Clamp to valid range
        return int(max(settings.BRIGHTNESS_MIN, 
                      min(base_brightness, settings.BRIGHTNESS_MAX)))
    
    def calculate_volume_target(self, faces: List[FaceData],
                               background_noise: float = 0.0) -> float:
        """
        Calculate target volume based on faces and background noise
        
        Args:
            faces: List of detected faces
            background_noise: Background noise level (0-1)
            
        Returns:
            Target volume (0.0-1.0)
        """
        if not faces:
            # No faces - reduce volume
            return 0.3
        
        # Calculate weighted distance
        weighted_distance = self.calculate_weighted_distance(faces)
        
        # Base volume on distance
        if weighted_distance < settings.OPTIMAL_DISTANCE_MIN:
            base_volume = 0.4  # Closer = quieter
        elif weighted_distance > settings.OPTIMAL_DISTANCE_MAX:
            base_volume = 0.8  # Further = louder
        else:
            # Linear interpolation in optimal range
            ratio = (weighted_distance - settings.OPTIMAL_DISTANCE_MIN) / \
                   (settings.OPTIMAL_DISTANCE_MAX - settings.OPTIMAL_DISTANCE_MIN)
            base_volume = 0.4 + (0.4 * ratio)
        
        # Adjust for background noise to maintain target SNR
        if background_noise > settings.BACKGROUND_NOISE_THRESHOLD:
            # Increase volume to compensate for noise
            noise_compensation = background_noise * 0.4
            base_volume = min(1.0, base_volume + noise_compensation)
        
        # Clamp to valid range
        return max(settings.VOLUME_MIN, min(base_volume, settings.VOLUME_MAX))
    
    def get_face_weights(self, faces: List[FaceData]) -> List[dict]:
        """
        Get detailed weight information for all faces
        
        Args:
            faces: List of detected faces
            
        Returns:
            List of weight dictionaries
        """
        weights = []
        for i, face in enumerate(faces):
            distance_weight = self.calculate_distance_weight(face.distance)
            spatial_weight = self.calculate_spatial_weight(face.position)
            total_weight = self.calculate_face_weight(face)
            
            weights.append({
                'face_id': i,
                'distance': face.distance,
                'position': face.position,
                'distance_weight': distance_weight,
                'spatial_weight': spatial_weight,
                'total_weight': total_weight
            })
        
        return weights
    
    def get_adaptation_info(self, faces: List[FaceData],
                           ambient_light: float = None,
                           background_noise: float = 0.0) -> dict:
        """
        Get comprehensive adaptation information
        
        Args:
            faces: List of detected faces
            ambient_light: Ambient light level
            background_noise: Background noise level
            
        Returns:
            Dictionary with adaptation details
        """
        return {
            'face_count': len(faces),
            'weighted_distance': self.calculate_weighted_distance(faces),
            'target_brightness': self.calculate_brightness_target(faces, ambient_light),
            'target_volume': self.calculate_volume_target(faces, background_noise),
            'face_weights': self.get_face_weights(faces),
            'ambient_light': ambient_light,
            'background_noise': background_noise
        }
