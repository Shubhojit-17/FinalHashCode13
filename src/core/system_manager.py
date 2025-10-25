"""
System Manager
Orchestrates all EADA Pro modules and manages the main control loop
"""

import cv2
import logging
import time
import numpy as np
from typing import Optional
from src.config import settings
from src.modules.perception import (
    CameraCapture, AudioCapture, FaceDetector, FaceCounter
)
from src.modules.adaptation import (
    BrightnessController, VolumeController, WeightedAdapter
)
from src.modules.intelligence import (
    EnvironmentMonitor, AudioAnalyzer
)

logger = logging.getLogger(__name__)


class SystemManager:
    """Main system manager for EADA Pro"""
    
    def __init__(self):
        """Initialize system manager and all modules"""
        logger.info("=" * 60)
        logger.info("Initializing EADA Pro System")
        logger.info("=" * 60)
        
        # Perception modules
        self.camera = CameraCapture()
        self.audio = AudioCapture()
        self.face_detector = FaceDetector()
        self.face_counter = FaceCounter()
        
        # Adaptation modules
        self.brightness_controller = BrightnessController()
        self.volume_controller = VolumeController()
        self.weighted_adapter = WeightedAdapter()
        
        # Intelligence modules
        self.environment_monitor = EnvironmentMonitor()
        self.audio_analyzer = AudioAnalyzer()
        
        # State tracking
        self.is_running = False
        self.frame_count = 0
        self.last_face_time = time.time()
        self.media_paused = False
        
        # Performance tracking
        self.fps = 0.0
        self.processing_time = 0.0
        
        logger.info("System manager initialized successfully")
    
    def start(self) -> bool:
        """
        Start all system modules
        
        Returns:
            True if successful
        """
        logger.info("Starting EADA Pro system...")
        
        # Start camera
        if settings.ENABLE_FACE_DETECTION:
            if not self.camera.start():
                logger.error("Failed to start camera")
                return False
        
        # Start audio
        if settings.ENABLE_AUDIO_MONITORING:
            if not self.audio.start():
                logger.warning("Failed to start audio (continuing without it)")
        
        self.is_running = True
        logger.info("✓ All systems started successfully")
        return True
    
    def process_frame(self):
        """Process a single frame and update all systems"""
        start_time = time.time()
        
        # Read frame
        ret, frame = self.camera.read_frame()
        if not ret or frame is None:
            return
        
        # Detect faces
        faces = []
        if settings.ENABLE_FACE_DETECTION:
            faces = self.face_detector.detect_faces(frame)
        
        # Update face count
        if settings.ENABLE_FACE_COUNTING:
            face_count = self.face_counter.update(faces)
        else:
            face_count = len(faces)
        
        # Monitor environment
        ambient_light = None
        if settings.ENABLE_AMBIENT_LIGHT_DETECTION:
            ambient_light = self.environment_monitor.estimate_ambient_light(frame)
        
        # Analyze audio
        audio_level = 0.0
        background_noise = 0.0
        if settings.ENABLE_AUDIO_MONITORING:
            audio_data = self.audio.capture_chunk()
            if audio_data is not None:
                audio_analysis = self.audio_analyzer.analyze_audio(audio_data)
                audio_level = audio_analysis['rms']
                background_noise = audio_analysis['noise_level']
        
        # Presence detection
        if len(faces) > 0:
            self.last_face_time = time.time()
            if self.media_paused:
                logger.info("User returned - resuming media")
                self.media_paused = False
                self._resume_media()
        else:
            # Check if user has been absent
            absence_duration = time.time() - self.last_face_time
            if absence_duration > settings.ABSENCE_TIMEOUT and not self.media_paused:
                logger.info(f"No user detected for {absence_duration:.1f}s - pausing media")
                self.media_paused = True
                self._pause_media()
        
        # Calculate weighted adaptation values
        if settings.ENABLE_WEIGHTED_ADAPTATION and len(faces) > 0:
            adaptation_info = self.weighted_adapter.get_adaptation_info(
                faces, ambient_light, background_noise
            )
            weighted_distance = adaptation_info['weighted_distance']
        else:
            # Simple average if no weighted adaptation
            if len(faces) > 0:
                weighted_distance = np.mean([f.distance for f in faces])
            else:
                weighted_distance = settings.MAX_DETECTION_DISTANCE
        
        # Apply brightness control based on distance
        if settings.ENABLE_BRIGHTNESS_CONTROL and len(faces) > 0:
            self.brightness_controller.adapt_to_distance(weighted_distance)
        
        # Apply volume control based on distance
        if settings.ENABLE_VOLUME_CONTROL and not self.media_paused and len(faces) > 0:
            self.volume_controller.adapt_to_distance(weighted_distance)
        elif self.media_paused:
            self.volume_controller.set_volume(0.0, smooth=False)
        
        # Get current brightness and volume for display
        current_brightness = self.brightness_controller.get_brightness()
        current_volume = self.volume_controller.get_volume()
        
        # Display preview
        if settings.SHOW_PREVIEW:
            display_frame = self._create_display_frame(
                frame, faces, face_count, weighted_distance, ambient_light, 
                audio_level, current_brightness, current_volume
            )
            cv2.imshow('EADA Pro', display_frame)
        
        # Update performance metrics
        self.processing_time = time.time() - start_time
        self.fps = 1.0 / self.processing_time if self.processing_time > 0 else 0
        self.frame_count += 1
    
    def _create_display_frame(self, frame, faces, face_count, distance, ambient_light, 
                             audio_level, brightness, volume):
        """Create annotated display frame"""
        display_frame = frame.copy()
        
        # Draw faces
        if faces and settings.SHOW_LANDMARKS:
            display_frame = self.face_detector.draw_faces(display_frame, faces)
        
        # Draw metrics overlay
        if settings.SHOW_METRICS:
            y_offset = 30
            line_height = 30
            
            # Draw semi-transparent background
            overlay = display_frame.copy()
            cv2.rectangle(overlay, (10, 10), (450, 330), (0, 0, 0), -1)
            display_frame = cv2.addWeighted(display_frame, 0.7, overlay, 0.3, 0)
            
            # System info
            metrics = [
                f"EADA Pro - Face Tracking System",
                f"Faces Detected: {face_count}",
                f"Distance: {distance:.1f} cm",
                f"FPS: {self.fps:.1f}",
                f"",
                f"Brightness: {brightness}% ({'Active' if self.brightness_controller.available else 'Simulation'})",
                f"Volume: {int(volume * 100)}% ({'Active' if self.volume_controller.available else 'Simulation'})",
                f"",
                f"Media: {'Paused' if self.media_paused else 'Playing'}",
            ]
            
            for i, text in enumerate(metrics):
                if text == "":
                    continue
                color = (0, 255, 0) if i == 0 else (255, 255, 255)
                font_scale = 0.6 if i == 0 else 0.5
                thickness = 2 if i == 0 else 1
                cv2.putText(
                    display_frame, text,
                    (20, y_offset + i * line_height),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale, color, thickness
                )
        
        return display_frame
    
    def run(self):
        """Main system loop"""
        if not self.start():
            logger.error("Failed to start system")
            return
        
        logger.info("=" * 60)
        logger.info("EADA Pro is running!")
        logger.info("Press 'q' to quit")
        logger.info("=" * 60)
        
        try:
            while self.is_running:
                self.process_frame()
                
                # Check for quit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Quit command received")
                    break
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Stop all system modules"""
        logger.info("Stopping EADA Pro system...")
        
        self.is_running = False
        
        # Release resources
        self.camera.release()
        self.audio.stop()
        self.face_detector.release()
        
        # Close windows
        cv2.destroyAllWindows()
        
        logger.info("System stopped successfully")
    
    def _pause_media(self):
        """Pause media playback using Windows media keys"""
        try:
            import win32api
            import win32con
            # Simulate media play/pause key (VK_MEDIA_PLAY_PAUSE = 0xB3)
            win32api.keybd_event(0xB3, 0, 0, 0)
            win32api.keybd_event(0xB3, 0, win32con.KEYEVENTF_KEYUP, 0)
            logger.info("Media paused")
        except ImportError:
            logger.warning("win32api not available - cannot control media")
        except Exception as e:
            logger.error(f"Failed to pause media: {e}")
    
    def _resume_media(self):
        """Resume media playback using Windows media keys"""
        try:
            import win32api
            import win32con
            # Simulate media play/pause key
            win32api.keybd_event(0xB3, 0, 0, 0)
            win32api.keybd_event(0xB3, 0, win32con.KEYEVENTF_KEYUP, 0)
            logger.info("Media resumed")
        except ImportError:
            logger.warning("win32api not available - cannot control media")
        except Exception as e:
            logger.error(f"Failed to resume media: {e}")
    
    def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        return {
            'running': self.is_running,
            'frame_count': self.frame_count,
            'fps': self.fps,
            'processing_time_ms': self.processing_time * 1000,
            'media_paused': self.media_paused,
            'face_count': self.face_counter.get_count(),
            'brightness': self.brightness_controller.get_brightness(),
            'volume': self.volume_controller.get_volume_percent(),
            'modules': {
                'camera': self.camera.is_running,
                'audio': self.audio.is_running,
                'brightness_available': self.brightness_controller.available,
                'volume_available': self.volume_controller.available,
            }
        }
