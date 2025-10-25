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
    CameraCapture, AudioCapture, FaceDetector, FaceCounter, GestureController
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
        self.gesture_controller = GestureController() if settings.ENABLE_GESTURE_RECOGNITION else None
        
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
        
        # Gesture toggle state
        self.gestures_enabled = settings.ENABLE_GESTURE_RECOGNITION
        
        # Store frame dimensions for UI elements
        self.frame_width = settings.CAMERA_WIDTH
        self.frame_height = settings.CAMERA_HEIGHT
        
        # Performance tracking
        self.fps = 0.0
        self.processing_time = 0.0
        
        # Optimization: cached values updated less frequently
        self.cached_ambient_light = None
        self.cached_audio_level = 0.0
        self.cached_background_noise = 0.0
        
        # Track last logged gesture values to prevent spam
        self.last_logged_brightness = None
        self.last_logged_volume = None
        
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
        
        # Create window for display
        cv2.namedWindow(settings.WINDOW_NAME)
        
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
        
        # Detect gestures
        gestures = []
        gesture_adjustment_volume = None
        gesture_adjustment_brightness = None
        gesture_play_pause_toggle = False
        gesture_next_track = False
        gesture_prev_track = False
        
        # Always detect gestures to allow toggle (fist) even when disabled
        if self.gesture_controller:
            # Update cooldown every frame, regardless of hand detection
            self.gesture_controller.update_cooldown()
            
            gestures = self.gesture_controller.detect_gestures(frame)
            
            # Process gestures directly for continuous controls
            for gesture in gestures:
                if gesture.gesture_type == 'toggle_gestures':
                    # Toggle gesture (fist) always works
                    # The gesture controller toggles its own state, we need to sync
                    self.gestures_enabled = self.gesture_controller.is_active()
                
                elif self.gestures_enabled:
                    if gesture.gesture_type == 'volume_control' and gesture.value is not None:
                        gesture_adjustment_volume = gesture.value
                        # Only log if value changed significantly (>5%)
                        if self.last_logged_volume is None or abs(gesture_adjustment_volume - self.last_logged_volume) > 5:
                            self.last_logged_volume = gesture_adjustment_volume
                        
                    elif gesture.gesture_type == 'brightness_control' and gesture.value is not None:
                        gesture_adjustment_brightness = gesture.value
                        # Only log if value changed significantly (>5%)
                        if self.last_logged_brightness is None or abs(gesture_adjustment_brightness - self.last_logged_brightness) > 5:
                            self.last_logged_brightness = gesture_adjustment_brightness
                        
                    elif gesture.gesture_type == 'play_pause':
                        gesture_play_pause_toggle = True
                        
                    elif gesture.gesture_type == 'next_track':
                        gesture_next_track = True
                        
                    elif gesture.gesture_type == 'prev_track':
                        gesture_prev_track = True
        
        # Handle play/pause gesture toggle
        if gesture_play_pause_toggle:
            if not self.media_paused:
                logger.info("Gesture: Play/Pause - pausing media")
                self.media_paused = True
                self._pause_media()
            else:
                logger.info("Gesture: Play/Pause - resuming media")
                self.media_paused = False
                self._resume_media()
        
        # Handle next/previous track gestures
        if gesture_next_track:
            logger.info("Gesture: Next Track")
            self._next_track()
        elif gesture_prev_track:
            logger.info("Gesture: Previous Track")
            self._prev_track()
        
        # Update face count
        if settings.ENABLE_FACE_COUNTING:
            face_count = self.face_counter.update(faces)
        else:
            face_count = len(faces)
        
        # Monitor environment (every 5th frame to reduce overhead)
        if self.frame_count % 5 == 0:
            if settings.ENABLE_AMBIENT_LIGHT_DETECTION:
                self.cached_ambient_light = self.environment_monitor.estimate_ambient_light(frame)
        ambient_light = self.cached_ambient_light
        
        # Analyze audio (every 10th frame to reduce overhead)
        if self.frame_count % 10 == 0:
            if settings.ENABLE_AUDIO_MONITORING:
                audio_data = self.audio.capture_chunk()
                if audio_data is not None:
                    audio_analysis = self.audio_analyzer.analyze_audio(audio_data)
                    self.cached_audio_level = audio_analysis['rms']
                    self.cached_background_noise = audio_analysis['noise_level']
        audio_level = self.cached_audio_level
        background_noise = self.cached_background_noise
        
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
        
        # Apply brightness control - blend distance-based with gesture adjustment
        if settings.ENABLE_BRIGHTNESS_CONTROL and len(faces) > 0:
            if gesture_adjustment_brightness is not None:
                # Use direct gesture control (value is already 0-100) - no smoothing
                self.brightness_controller.set_brightness(int(gesture_adjustment_brightness), smooth=False)
            else:
                # Use distance-based control when no gesture
                self.brightness_controller.adapt_to_distance(weighted_distance)
        
        # Apply volume control - blend distance-based with gesture adjustment
        if settings.ENABLE_VOLUME_CONTROL and not self.media_paused and len(faces) > 0:
            if gesture_adjustment_volume is not None:
                # Use direct gesture control (convert 0-100 to 0-1) - no smoothing
                gesture_volume = gesture_adjustment_volume / 100.0
                self.volume_controller.set_volume(gesture_volume, smooth=False)
            else:
                # Use distance-based control when no gesture
                self.volume_controller.adapt_to_distance(weighted_distance)
        elif self.media_paused:
            self.volume_controller.set_volume(0.0, smooth=False)
        
        # Get current brightness and volume for display
        current_brightness = self.brightness_controller.get_brightness()
        current_volume = self.volume_controller.get_volume()
        
        # Display preview
        if settings.SHOW_PREVIEW:
            display_frame = self._create_display_frame(
                frame, faces, gestures, face_count, weighted_distance, ambient_light, 
                audio_level, current_brightness, current_volume
            )
            cv2.imshow(settings.WINDOW_NAME, display_frame)
        
        # Update performance metrics
        self.processing_time = time.time() - start_time
        self.fps = 1.0 / self.processing_time if self.processing_time > 0 else 0
        self.frame_count += 1
    
    def _create_display_frame(self, frame, faces, gestures, face_count, distance, ambient_light, 
                             audio_level, brightness, volume):
        """Create annotated display frame (optimized)"""
        # Use reference instead of copy when possible
        display_frame = frame
        
        # Draw faces (only if landmarks enabled)
        if faces and settings.SHOW_LANDMARKS:
            display_frame = self.face_detector.draw_faces(display_frame, faces)
        
        # Draw gestures (only if enabled and gestures are on)
        if gestures and settings.ENABLE_GESTURE_RECOGNITION and settings.SHOW_LANDMARKS and self.gestures_enabled:
            display_frame = self.gesture_controller.draw_gesture_info(
                display_frame, gestures, volume, brightness
            )
        
        # Draw metrics overlay (simplified)
        if settings.SHOW_METRICS:
            # Simplified overlay - no semi-transparent background for better performance
            y_offset = 30
            line_height = 30
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
                f"",
                f"Gestures: 1=Vol 2=Bright 3=Play/Pause 4=Next 5=Prev",
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
        
        # Draw gesture status indicator (top-right corner)
        self._draw_gesture_status(display_frame)
        
        return display_frame
    
    def _draw_gesture_status(self, frame):
        """Draw gesture control and cursor control status"""
        # Status text position (top-right)
        y_offset = 25
        
        # Gesture status
        if self.gestures_enabled:
            gesture_text = "Gestures: ON"
            gesture_color = (0, 255, 0)  # Green
            gesture_help = None
        else:
            gesture_text = "Gestures: OFF"
            gesture_color = (0, 0, 255)  # Red
            gesture_help = "Make FIST to turn ON"
        
        # Draw gesture status
        gesture_size = cv2.getTextSize(gesture_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        gesture_x = frame.shape[1] - gesture_size[0] - 15
        
        cv2.rectangle(frame, (gesture_x - 5, y_offset - 20), 
                     (gesture_x + gesture_size[0] + 5, y_offset + 5), 
                     (0, 0, 0), -1)
        
        cv2.putText(frame, gesture_text, (gesture_x, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, gesture_color, 2)
        
        # Draw gesture help text
        if gesture_help:
            help_size = cv2.getTextSize(gesture_help, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            help_x = frame.shape[1] - help_size[0] - 15
            help_y = y_offset + 25
            
            cv2.rectangle(frame, (help_x - 5, help_y - 18), 
                         (help_x + help_size[0] + 5, help_y + 3), 
                         (0, 0, 0), -1)
            
            cv2.putText(frame, gesture_help, (help_x, help_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
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
        # Gesture controller doesn't need release (no MediaPipe session)
        
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
    
    def _next_track(self):
        """Skip to next track using Windows media keys"""
        try:
            import win32api
            import win32con
            # Simulate media next track key (VK_MEDIA_NEXT_TRACK = 0xB0)
            win32api.keybd_event(0xB0, 0, 0, 0)
            win32api.keybd_event(0xB0, 0, win32con.KEYEVENTF_KEYUP, 0)
            logger.info("Next track")
        except ImportError:
            logger.warning("win32api not available - cannot control media")
        except Exception as e:
            logger.error(f"Failed to skip track: {e}")
    
    def _prev_track(self):
        """Skip to previous track using Windows media keys"""
        try:
            import win32api
            import win32con
            # Simulate media previous track key (VK_MEDIA_PREV_TRACK = 0xB1)
            win32api.keybd_event(0xB1, 0, 0, 0)
            win32api.keybd_event(0xB1, 0, win32con.KEYEVENTF_KEYUP, 0)
            logger.info("Previous track")
        except ImportError:
            logger.warning("win32api not available - cannot control media")
        except Exception as e:
            logger.error(f"Failed to go to previous track: {e}")
    
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
