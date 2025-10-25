"""
System Manager
Orchestrates all EADA Pro modules and manages the main control loop
"""

import cv2
import logging
import time
import numpy as np
import platform
import subprocess
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
        # Control mode: 'gesture', 'head', or 'hybrid'
        self.control_mode = getattr(settings, 'CONTROL_MODE_DEFAULT', 'hybrid')
        # Button rectangle (will be updated per-frame)
        self._mode_button_rect = None  # (x1,y1,x2,y2)
        self._window_name = 'EADA Pro'
    
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
        
        # Detect gestures
        gestures = []
        gesture_adjustment_volume = None
        gesture_adjustment_brightness = None
        gesture_play_pause_toggle = False
        gesture_next_track = False
        gesture_prev_track = False
        
        if settings.ENABLE_GESTURE_RECOGNITION and self.gesture_controller:
            gestures = self.gesture_controller.detect_gestures(frame)
            
            # Get smoothed gesture for control
            smoothed_gesture = self.gesture_controller.get_smoothed_gesture()
            if smoothed_gesture:
                # Gestures now provide adjustments, not overrides
                if smoothed_gesture.gesture_type == 'volume_control' and smoothed_gesture.value is not None:
                    gesture_adjustment_volume = smoothed_gesture.value
                    # Only log if value changed significantly (>5%)
                    if self.last_logged_volume is None or abs(gesture_adjustment_volume - self.last_logged_volume) > 5:
                        print(f"[GESTURE] Volume: {gesture_adjustment_volume}%")
                        self.last_logged_volume = gesture_adjustment_volume
                    
                elif smoothed_gesture.gesture_type == 'brightness_control' and smoothed_gesture.value is not None:
                    gesture_adjustment_brightness = smoothed_gesture.value
                    # Only log if value changed significantly (>5%)
                    if self.last_logged_brightness is None or abs(gesture_adjustment_brightness - self.last_logged_brightness) > 5:
                        print(f"[GESTURE] Brightness: {gesture_adjustment_brightness}%")
                        self.last_logged_brightness = gesture_adjustment_brightness
                    
                elif smoothed_gesture.gesture_type == 'play_pause':
                    gesture_play_pause_toggle = True
                    print("✓ [GESTURE] Play/Pause triggered!")
                    
                elif smoothed_gesture.gesture_type == 'next_track':
                    gesture_next_track = True
                    print("✓ [GESTURE] Next Track triggered!")
                    
                elif smoothed_gesture.gesture_type == 'prev_track':
                    gesture_prev_track = True
                    print("✓ [GESTURE] Previous Track triggered!")
        
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
            # Behavior depends on control_mode
            if self.control_mode == 'gesture':
                if gesture_adjustment_brightness is not None:
                    self.brightness_controller.set_brightness(int(gesture_adjustment_brightness), smooth=True)
            elif self.control_mode == 'head':
                self.brightness_controller.adapt_to_distance(weighted_distance)
            else:  # hybrid
                if gesture_adjustment_brightness is not None:
                    self.brightness_controller.set_brightness(int(gesture_adjustment_brightness), smooth=True)
                else:
                    self.brightness_controller.adapt_to_distance(weighted_distance)
        
        # Apply volume control - blend distance-based with gesture adjustment
        if settings.ENABLE_VOLUME_CONTROL and not self.media_paused and len(faces) > 0:
            if self.control_mode == 'gesture':
                if gesture_adjustment_volume is not None:
                    gesture_volume = gesture_adjustment_volume / 100.0
                    self.volume_controller.set_volume(gesture_volume, smooth=True)
            elif self.control_mode == 'head':
                self.volume_controller.adapt_to_distance(weighted_distance)
            else:  # hybrid
                if gesture_adjustment_volume is not None:
                    gesture_volume = gesture_adjustment_volume / 100.0
                    self.volume_controller.set_volume(gesture_volume, smooth=True)
                else:
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
            # Draw mode button and show window
            display_frame = self._draw_mode_button(display_frame)
            cv2.imshow(self._window_name, display_frame)
        
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
        
        # Draw gestures (only if enabled)
        if gestures and settings.ENABLE_GESTURE_RECOGNITION and settings.SHOW_LANDMARKS:
            display_frame = self.gesture_controller.draw_gesture_info(display_frame, gestures)
        
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
        
        return display_frame

    def _draw_mode_button(self, frame):
        """Draw a small toggle button on the top-right corner to switch control modes"""
        h, w = frame.shape[:2]
        bw, bh = 180, 40
        x1 = w - bw - 20
        y1 = 20
        x2 = x1 + bw
        y2 = y1 + bh
        # Save rect for mouse callback
        self._mode_button_rect = (x1, y1, x2, y2)
        # Background
        cv2.rectangle(frame, (x1, y1), (x2, y2), (50, 50, 50), -1)
        # Border
        cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 200, 200), 1)
        # Text
        mode_text = f"Mode: {self.control_mode.capitalize()}"
        cv2.putText(frame, mode_text, (x1 + 10, y1 + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        return frame

    def _on_mouse(self, event, x, y, flags, param):
        """Mouse callback to detect clicks on the mode button"""
        if event == cv2.EVENT_LBUTTONDOWN and self._mode_button_rect is not None:
            x1, y1, x2, y2 = self._mode_button_rect
            if x1 <= x <= x2 and y1 <= y <= y2:
                # Cycle control mode
                if self.control_mode == 'hybrid':
                    self.control_mode = 'gesture'
                elif self.control_mode == 'gesture':
                    self.control_mode = 'head'
                else:
                    self.control_mode = 'hybrid'
                logger.info(f"Control mode switched to: {self.control_mode}")
    
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
            # Prepare preview window and mouse callback
            if settings.SHOW_PREVIEW:
                try:
                    cv2.namedWindow(self._window_name, cv2.WINDOW_NORMAL)
                    cv2.setMouseCallback(self._window_name, self._on_mouse)
                except Exception:
                    # Some OpenCV builds on macOS may not support namedWindow flags fully
                    pass

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
            if platform.system() == 'Windows':
                import win32api
                import win32con
                # Simulate media play/pause key (VK_MEDIA_PLAY_PAUSE = 0xB3)
                win32api.keybd_event(0xB3, 0, 0, 0)
                win32api.keybd_event(0xB3, 0, win32con.KEYEVENTF_KEYUP, 0)
                logger.info("Media paused (Windows)")
            elif platform.system() == 'Darwin':
                # Choose order based on configuration
                pref = getattr(settings, 'MEDIA_PLAYER_PREFERENCE', 'auto')
                order = []
                if pref == 'spotify':
                    order = ['Spotify', 'Music']
                elif pref == 'music':
                    order = ['Music', 'Spotify']
                else:
                    order = ['Spotify', 'Music']

                controlled = False
                for app in order:
                    try:
                        subprocess.run(["osascript", "-e", f'tell application "{app}" to playpause'], check=True)
                        logger.info(f"Media paused/resumed via {app} (macOS)")
                        controlled = True
                        break
                    except subprocess.CalledProcessError:
                        continue

                if not controlled:
                    logger.warning("No supported macOS media player controlled (Spotify/Music)")
            else:
                logger.warning("Media control not implemented for this platform")
        except ImportError:
            logger.warning("win32api not available - cannot control media on Windows")
        except Exception as e:
            logger.error(f"Failed to pause media: {e}")
    
    def _resume_media(self):
        """Resume media playback using Windows media keys"""
        try:
            if platform.system() == 'Windows':
                import win32api
                import win32con
                # Simulate media play/pause key
                win32api.keybd_event(0xB3, 0, 0, 0)
                win32api.keybd_event(0xB3, 0, win32con.KEYEVENTF_KEYUP, 0)
                logger.info("Media resumed (Windows)")
            elif platform.system() == 'Darwin':
                pref = getattr(settings, 'MEDIA_PLAYER_PREFERENCE', 'auto')
                order = []
                if pref == 'spotify':
                    order = ['Spotify', 'Music']
                elif pref == 'music':
                    order = ['Music', 'Spotify']
                else:
                    order = ['Spotify', 'Music']

                controlled = False
                for app in order:
                    try:
                        subprocess.run(["osascript", "-e", f'tell application "{app}" to playpause'], check=True)
                        logger.info(f"Media paused/resumed via {app} (macOS)")
                        controlled = True
                        break
                    except subprocess.CalledProcessError:
                        continue

                if not controlled:
                    logger.warning("No supported macOS media player controlled (Spotify/Music)")
            else:
                logger.warning("Media control not implemented for this platform")
        except ImportError:
            logger.warning("win32api not available - cannot control media on Windows")
        except Exception as e:
            logger.error(f"Failed to resume media: {e}")
    
    def _next_track(self):
        """Skip to next track using Windows media keys"""
        try:
            if platform.system() == 'Windows':
                import win32api
                import win32con
                # Simulate media next track key (VK_MEDIA_NEXT_TRACK = 0xB0)
                win32api.keybd_event(0xB0, 0, 0, 0)
                win32api.keybd_event(0xB0, 0, win32con.KEYEVENTF_KEYUP, 0)
                logger.info("Next track (Windows)")
            elif platform.system() == 'Darwin':
                pref = getattr(settings, 'MEDIA_PLAYER_PREFERENCE', 'auto')
                order = ['Spotify', 'Music'] if pref != 'music' else ['Music', 'Spotify']
                controlled = False
                for app in order:
                    try:
                        subprocess.run(["osascript", "-e", f'tell application "{app}" to next track'], check=True)
                        logger.info(f"Next track via {app} (macOS)")
                        controlled = True
                        break
                    except subprocess.CalledProcessError:
                        continue
                if not controlled:
                    logger.warning("No supported macOS media player controlled (Spotify/Music)")
            else:
                logger.warning("Media control not implemented for this platform")
        except ImportError:
            logger.warning("win32api not available - cannot control media on Windows")
        except Exception as e:
            logger.error(f"Failed to skip track: {e}")
    
    def _prev_track(self):
        """Skip to previous track using Windows media keys"""
        try:
            if platform.system() == 'Windows':
                import win32api
                import win32con
                # Simulate media previous track key (VK_MEDIA_PREV_TRACK = 0xB1)
                win32api.keybd_event(0xB1, 0, 0, 0)
                win32api.keybd_event(0xB1, 0, win32con.KEYEVENTF_KEYUP, 0)
                logger.info("Previous track (Windows)")
            elif platform.system() == 'Darwin':
                pref = getattr(settings, 'MEDIA_PLAYER_PREFERENCE', 'auto')
                order = ['Spotify', 'Music'] if pref != 'music' else ['Music', 'Spotify']
                controlled = False
                for app in order:
                    try:
                        subprocess.run(["osascript", "-e", f'tell application "{app}" to previous track'], check=True)
                        logger.info(f"Previous track via {app} (macOS)")
                        controlled = True
                        break
                    except subprocess.CalledProcessError:
                        continue
                if not controlled:
                    logger.warning("No supported macOS media player controlled (Spotify/Music)")
            else:
                logger.warning("Media control not implemented for this platform")
        except ImportError:
            logger.warning("win32api not available - cannot control media on Windows")
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
