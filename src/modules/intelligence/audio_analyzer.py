"""
Audio Analyzer Module
Analyzes audio for background music detection and noise levels
"""

import logging
import numpy as np
from typing import Optional
from collections import deque
from src.config import settings

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Analyzes audio characteristics for adaptive volume control"""
    
    def __init__(self):
        """Initialize audio analyzer"""
        self.noise_history = deque(maxlen=20)
        self.current_noise_level = 0.0
        self.background_music_detected = False
        
        logger.info("Audio analyzer initialized")
    
    def analyze_audio(self, audio_data: np.ndarray) -> dict:
        """
        Analyze audio data
        
        Args:
            audio_data: Audio samples
            
        Returns:
            Dictionary with analysis results
        """
        if audio_data is None or len(audio_data) == 0:
            return self.get_default_analysis()
        
        # Calculate RMS (volume level)
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Update noise level history
        self.noise_history.append(rms)
        self.current_noise_level = np.mean(list(self.noise_history))
        
        # Detect background music (simple heuristic)
        # Music typically has consistent energy across time
        if len(self.noise_history) >= 10:
            noise_std = np.std(list(self.noise_history))
            # Low variance = consistent sound = likely music
            self.background_music_detected = (
                noise_std < 0.05 and 
                self.current_noise_level > settings.BACKGROUND_NOISE_THRESHOLD
            )
        
        # Perform frequency analysis
        freq_analysis = self._analyze_frequencies(audio_data)
        
        return {
            'rms': float(rms),
            'noise_level': float(self.current_noise_level),
            'music_detected': self.background_music_detected,
            'frequencies': freq_analysis
        }
    
    def _analyze_frequencies(self, audio_data: np.ndarray) -> dict:
        """
        Analyze frequency content
        
        Args:
            audio_data: Audio samples
            
        Returns:
            Dictionary with frequency band energies
        """
        try:
            # Perform FFT
            fft = np.fft.rfft(audio_data.flatten())
            freqs = np.fft.rfftfreq(len(audio_data.flatten()), 
                                   1/settings.AUDIO_SAMPLE_RATE)
            magnitudes = np.abs(fft)
            
            # Divide into frequency bands
            bass = np.mean(magnitudes[(freqs >= 20) & (freqs < 250)])
            mid = np.mean(magnitudes[(freqs >= 250) & (freqs < 4000)])
            treble = np.mean(magnitudes[(freqs >= 4000) & (freqs < 20000)])
            
            return {
                'bass': float(bass),
                'mid': float(mid),
                'treble': float(treble),
                'total_energy': float(np.sum(magnitudes))
            }
        except Exception as e:
            logger.error(f"Error analyzing frequencies: {e}")
            return {'bass': 0.0, 'mid': 0.0, 'treble': 0.0, 'total_energy': 0.0}
    
    def get_noise_level(self) -> float:
        """Get current background noise level"""
        return self.current_noise_level
    
    def is_music_playing(self) -> bool:
        """Check if background music is detected"""
        return self.background_music_detected
    
    def get_snr_adjustment(self) -> float:
        """
        Calculate volume adjustment to maintain target SNR
        
        Returns:
            Volume adjustment factor (0.0-1.0)
        """
        if self.current_noise_level < settings.BACKGROUND_NOISE_THRESHOLD:
            return 0.0  # No adjustment needed
        
        # Calculate adjustment to maintain target SNR
        # Higher noise = higher volume needed
        adjustment = self.current_noise_level * 0.5
        return min(0.4, adjustment)  # Cap at 40% increase
    
    def get_default_analysis(self) -> dict:
        """Get default analysis when no audio data"""
        return {
            'rms': 0.0,
            'noise_level': 0.0,
            'music_detected': False,
            'frequencies': {
                'bass': 0.0,
                'mid': 0.0,
                'treble': 0.0,
                'total_energy': 0.0
            }
        }
    
    def get_statistics(self) -> dict:
        """Get audio analysis statistics"""
        return {
            'current_noise': self.current_noise_level,
            'music_detected': self.background_music_detected,
            'snr_adjustment': self.get_snr_adjustment(),
            'history_size': len(self.noise_history)
        }
