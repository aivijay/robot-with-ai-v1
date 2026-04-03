"""Camera module - handles MJPEG streaming from rpicam-vid."""
import os
import subprocess
import threading
import time
import queue
import cv2
import numpy as np
from typing import Optional, Tuple


class CameraStream:
    """
    Continuous camera stream using rpicam-vid MJPEG output.
    Provides frames at ~2-3 fps without reinitialization overhead.
    """
    
    def __init__(self, width: int = 640, height: int = 480, fifo_path: str = '/tmp/mjpeg_fifo'):
        self.width = width
        self.height = height
        self.fifo_path = fifo_path
        self.frame_queue: queue.Queue = queue.Queue(maxsize=3)
        self.stop_event = threading.Event()
        self.proc: Optional[subprocess.Popen] = None
        self.capture_thread: Optional[threading.Thread] = None
        self._frame_count = 0
        self._fps = 0.0
        self._fps_start = time.time()
        self._fps_counter = 0
        
    def start(self):
        """Start the camera stream in background thread."""
        if self.capture_thread and self.capture_thread.is_alive():
            return  # Already running
            
        if os.path.exists(self.fifo_path):
            os.unlink(self.fifo_path)
        os.mkfifo(self.fifo_path)
        
        self.stop_event.clear()
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        time.sleep(2)  # Warm up
        
    def _capture_loop(self):
        """Background loop: runs rpicam-vid and parses MJPEG frames."""
        while not self.stop_event.is_set():
            try:
                cmd = [
                    'rpicam-vid',
                    '--width', str(self.width),
                    '--height', str(self.height),
                    '-t', '0',  # infinite
                    '--codec', 'mjpeg',
                    '-o', self.fifo_path,
                ]
                
                self.proc = subprocess.Popen(cmd, stderr=subprocess.DEVNULL)
                buffer = b''
                fd = os.open(self.fifo_path, os.O_RDONLY | os.O_NONBLOCK)
                
                while not self.stop_event.is_set() and self.proc.poll() is None:
                    try:
                        data = os.read(fd, 8192)
                        if data:
                            buffer += data
                            
                            # Extract JPEG frames
                            while True:
                                start = buffer.find(b'\xff\xd8\xff')
                                if start == -1:
                                    break
                                end = buffer.find(b'\xff\xd9', start + 2)
                                if end == -1:
                                    buffer = buffer[start:]
                                    break
                                    
                                jpeg = buffer[start:end+3]
                                buffer = buffer[end+3:]
                                
                                out_path = f'/tmp/cam_{self._frame_count:04d}.jpg'
                                with open(out_path, 'wb') as f:
                                    f.write(jpeg)
                                    
                                try:
                                    self.frame_queue.put_nowait(out_path)
                                except queue.Full:
                                    pass
                                    
                                self._frame_count += 1
                                self._fps_counter += 1
                                
                                # Calculate fps every second
                                now = time.time()
                                if now - self._fps_start >= 1.0:
                                    self._fps = self._fps_counter / (now - self._fps_start)
                                    self._fps_counter = 0
                                    self._fps_start = now
                                    
                    except OSError:
                        time.sleep(0.01)
                
                os.close(fd)
                self.proc.terminate()
                self.proc.wait()
                
            except Exception as e:
                print(f"Camera error: {e}")
                time.sleep(1)
    
    def get_frame(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        Get next available frame as numpy array.
        Returns None if no frame available within timeout.
        """
        try:
            frame_path = self.frame_queue.get(timeout=timeout)
            frame = cv2.imread(frame_path)
            try:
                os.remove(frame_path)
            except:
                pass
            return frame
        except queue.Empty:
            return None
    
    @property
    def fps(self) -> float:
        """Current estimated fps."""
        return self._fps
    
    def stop(self):
        """Stop the camera stream."""
        self.stop_event.set()
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
        if os.path.exists(self.fifo_path):
            os.unlink(self.fifo_path)


class FrameAnalyzer:
    """Analyzes camera frames for floor, obstacles, and features."""
    
    def __init__(self, config):
        self.config = config
        self.prev_frame: Optional[np.ndarray] = None
        
    def analyze(self, frame: np.ndarray) -> dict:
        """
        Full analysis of a frame.
        Returns dict with:
        - floor_brightness: mean brightness of floor region
        - floor_dark_pct: % of dark pixels in floor
        - obstacle_score: 0-1 likelihood of obstacle ahead
        - motion: estimated motion score
        - status: 'clear', 'cliff', 'obstacle'
        """
        if frame is None:
            return {'status': 'unknown'}
            
        result = {}
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # Floor region (bottom 60% of image)
        floor_top = int(h * 0.4)
        floor_region = gray[floor_top:, :]
        
        # Obstacle region (top 40%)
        obstacle_region = gray[:floor_top, :]
        
        # Basic stats
        result['floor_brightness'] = floor_region.mean()
        floor_bright = (floor_region > self.config.brightness_threshold).sum()
        result['floor_dark_pct'] = 100 * (1 - floor_bright / floor_region.size)
        
        # Obstacle detection
        obs_score = self._detect_obstacle(frame, floor_top, h, w)
        result['obstacle_score'] = obs_score
        
        # Motion detection
        result['motion'] = self._detect_motion(gray)
        
        # Determine status
        if result['floor_dark_pct'] > 50:
            result['status'] = 'cliff'
        elif obs_score > self.config.obstacle_threshold * 1.5:
            result['status'] = 'obstacle'
        elif obs_score > self.config.obstacle_threshold:
            result['status'] = 'caution'
        else:
            result['status'] = 'clear'
            
        # Store for next motion detection
        self.prev_frame = frame.copy()
        
        return result
    
    def _detect_obstacle(self, frame: np.ndarray, floor_top: int, h: int, w: int) -> float:
        """Calculate obstacle likelihood 0-1."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        floor_region = gray[floor_top:, :]
        obstacle_region = gray[:floor_top, :]
        floor_mean = floor_region.mean()
        
        score = 0.0
        
        # 1. Brightness contrast between obstacle zone and floor
        brightness_diff = abs(obstacle_region.mean() - floor_mean)
        if brightness_diff > 30:
            score += 0.4
            
        # 2. Edge strength at floor line (object edges)
        floor_line = gray[floor_top:floor_top+10, :]
        above_floor = gray[floor_top-5:floor_top, :]
        edge_strength = abs(floor_line.mean() - above_floor.mean())
        if edge_strength > 25:
            score += 0.3
            
        # 3. Center region variance
        center_region = gray[h//3:floor_top, w//3:2*w//3]
        center_var = center_region.var()
        if center_var > 500:
            score += 0.2
            
        # 4. Center column brightness anomaly (wall directly ahead)
        center_col = gray[:, w//4:3*w//4]
        col_std = center_col.std()
        if col_std > 40:
            score += 0.3
            
        return min(score, 1.0)
    
    def _detect_motion(self, gray: np.ndarray) -> float:
        """Detect motion between consecutive frames."""
        if self.prev_frame is None:
            return 0.0
        try:
            prev_gray = cv2.cvtColor(self.prev_frame, cv2.COLOR_BGR2GRAY)
            if prev_gray.shape != gray.shape:
                return 0.0
            diff = np.abs(gray.astype(float) - prev_gray.astype(float))
            return diff.mean()
        except:
            return 0.0
