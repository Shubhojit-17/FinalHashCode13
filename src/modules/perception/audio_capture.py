"""
Audio Capture Module
Handles audio recording and RMS level monitoring
"""

import sounddevice as sd
import numpy as np
from typing import Optional
import logging
from collections import deque
from src.config import settings

logger = logging.getLogger(__name__)


class AudioCapture:
    """Manages audio capture and real-time analysis"""
    
    def __init__(self):
        """Initialize audio capture"""
        self.sample_rate = settings.AUDIO_SAMPLE_RATE
        self.channels = settings.AUDIO_CHANNELS
        self.chunk_size = settings.AUDIO_CHUNK_SIZE
        self.device_index = settings.AUDIO_DEVICE_INDEX
        
        self.is_running = False
        self.stream: Optional[sd.InputStream] = None
        
        # RMS history for smoothing
        self.rms_history = deque(maxlen=10)
        self.current_rms = 0.0
        self.background_noise_level = 0.0
        
    def start(self) -> bool:
        """
        Start audio capture
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Test audio device
            devices = sd.query_devices()
            logger.info(f"Available audio devices: {len(devices)}")
            
            if self.device_index is not None:
                logger.info(f"Using audio device: {devices[self.device_index]['name']}")
            else:
                default_device = sd.query_devices(kind='input')
                logger.info(f"Using default audio device: {default_device['name']}")
            
            self.is_running = True
            logger.info("Audio capture started successfully")
            logger.info(f"Sample rate: {self.sample_rate} Hz")
            logger.info(f"Channels: {self.channels}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting audio capture: {e}")
            return False
    
    def capture_chunk(self) -> Optional[np.ndarray]:
        """
        Capture a single chunk of audio
        
        Returns:
            Audio data as numpy array, or None if error
        """
        if not self.is_running:
            return None
        
        try:
            audio_data = sd.rec(
                frames=self.chunk_size,
                samplerate=self.sample_rate,
                channels=self.channels,
                device=self.device_index,
                blocking=True
            )
            return audio_data
            
        except Exception as e:
            logger.error(f"Error capturing audio chunk: {e}")
            return None
    
    def calculate_rms(self, audio_data: np.ndarray) -> float:
        """
        Calculate RMS (Root Mean Square) of audio data
        
        Args:
            audio_data: Audio samples
            
        Returns:
            RMS value (0.0 to 1.0)
        """
        if audio_data is None or len(audio_data) == 0:
            return 0.0
        
        # Calculate RMS
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Update history
        self.rms_history.append(rms)
        
        # Smooth RMS using exponential moving average
        if len(self.rms_history) > 0:
            self.current_rms = np.mean(list(self.rms_history))
        
        return float(self.current_rms)
    
    def get_audio_level(self) -> float:
        """
        Get current audio level with background noise compensation
        
        Returns:
            Audio level (0.0 to 1.0)
        """
        audio_data = self.capture_chunk()
        if audio_data is None:
            return 0.0
        
        rms = self.calculate_rms(audio_data)
        
        # Normalize and compensate for background noise
        level = max(0.0, rms - self.background_noise_level)
        level = min(1.0, level * 10)  # Scale for better visibility
        
        return level
    
    def calibrate_background_noise(self, duration: float = 2.0):
        """
        Calibrate background noise level
        
        Args:
            duration: Calibration duration in seconds
        """
        logger.info(f"Calibrating background noise for {duration} seconds...")
        
        samples = []
        num_samples = int(duration * self.sample_rate / self.chunk_size)
        
        for _ in range(num_samples):
            audio_data = self.capture_chunk()
            if audio_data is not None:
                rms = np.sqrt(np.mean(audio_data ** 2))
                samples.append(rms)
        
        if samples:
            self.background_noise_level = np.mean(samples)
            logger.info(f"Background noise level: {self.background_noise_level:.4f}")
        else:
            logger.warning("Failed to calibrate background noise")
    
    def get_frequency_analysis(self, audio_data: np.ndarray) -> dict:
        """
        Perform basic frequency analysis
        
        Args:
            audio_data: Audio samples
            
        Returns:
            Dictionary with frequency information
        """
        if audio_data is None or len(audio_data) == 0:
            return {'bass': 0.0, 'mid': 0.0, 'treble': 0.0}
        
        # Perform FFT
        fft = np.fft.rfft(audio_data.flatten())
        freqs = np.fft.rfftfreq(len(audio_data.flatten()), 1/self.sample_rate)
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
    
    def stop(self):
        """Stop audio capture"""
        self.is_running = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        logger.info("Audio capture stopped")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.stop()
