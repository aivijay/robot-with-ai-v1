"""
Reflex controller - handles millisecond safety reactions.
This is the 'cerebellum' layer - fast, automatic, never waits for LLM.

The reflex controller continuously monitors camera and motor state,
and can interrupt/stop/override the skill layer when danger is detected.
"""
import threading
import time
import queue
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .camera import CameraStream, FrameAnalyzer
from .motors import MotorController
from ..common.hardware import RobotConfig


class ReflexState(Enum):
    NORMAL = "normal"
    CAUTION = "caution"    # Something interesting ahead, slow down
    DANGER = "danger"      # Obstacle/cliff detected, stop or reverse
    STOPPED = "stopped"    # Full stop, waiting for skill layer


@dataclass
class ReflexResult:
    state: ReflexState
    action_taken: str  # "none", "stopped", "reversed", "turned"
    analysis: dict     # Frame analysis results


class ReflexController:
    """
    Safety reflex system - runs in real-time alongside skills.
    
    Monitors:
    - Floor brightness (cliff detection)
    - Obstacle presence (object detection)
    - Motion (approaching obstacles)
    
    Can override skill commands when danger detected.
    """
    
    def __init__(self, config: RobotConfig, 
                 camera: CameraStream,
                 motors: MotorController):
        self.config = config
        self.camera = camera
        self.motors = motors
        self.analyzer = FrameAnalyzer(config)
        
        self.state = ReflexState.NORMAL
        self.last_action = "none"
        self.override_active = False
        self._stop_event = threading.Event()
        self._reflex_thread: Optional[threading.Thread] = None
        self._skill_speeds = (0.0, 0.0)  # What the skill layer wants
        self._last_reflex_time = 0
        
        # Callbacks for reflex events
        self.on_cliff = None      # Called when cliff detected
        self.on_obstacle = None   # Called when obstacle detected
        self.on_danger = None     # Called in any danger state
        
    def start(self):
        """Start the reflex monitoring loop."""
        self._stop_event.clear()
        self._reflex_thread = threading.Thread(target=self._reflex_loop, daemon=True)
        self._reflex_thread.start()
        
    def stop(self):
        """Stop reflex monitoring."""
        self._stop_event.set()
        if self._reflex_thread:
            self._reflex_thread.join(timeout=2)
        self.motors.stop()
        
    def set_skill_speeds(self, left: float, right: float):
        """
        Call from skill layer to set intended motor speeds.
        Reflex may override these if danger detected.
        """
        self._skill_speeds = (left, right)
        
    def _reflex_loop(self):
        """
        Real-time reflex loop - runs at camera fps (~2-3 Hz).
        Makes instant decisions about motor control.
        """
        frame_count = 0
        caution_cooldown = 0  # Frames to stay in caution before resuming normal
        
        while not self._stop_event.is_set():
            frame = self.camera.get_frame(timeout=0.5)
            if frame is None:
                time.sleep(0.1)
                continue
                
            analysis = self.analyzer.analyze(frame)
            frame_count += 1
            
            # Check for danger conditions
            danger = False
            action = "none"
            
            if analysis['status'] == 'cliff':
                # CLIFF DETECTED - emergency reverse!
                self.state = ReflexState.DANGER
                self.motors.reverse(self.config.speed_slow)
                action = "reversed"
                danger = True
                self.override_active = True
                
                if self.on_cliff:
                    self.on_cliff(analysis)
                if self.on_danger:
                    self.on_danger("cliff", analysis)
                    
            elif analysis['status'] == 'obstacle':
                # OBSTACLE DETECTED - stop immediately
                self.state = ReflexState.DANGER
                self.motors.stop()
                action = "stopped"
                danger = True
                self.override_active = True
                
                if self.on_obstacle:
                    self.on_obstacle(analysis)
                if self.on_danger:
                    self.on_danger("obstacle", analysis)
                    
            elif analysis['status'] == 'caution':
                # SLOW DOWN - something ahead
                self.override_active = False  # Clear override on caution
                if not self.override_active:
                    self.state = ReflexState.CAUTION
                    # Slow to half speed
                    slow_left = self._skill_speeds[0] * 0.5
                    slow_right = self._skill_speeds[1] * 0.5
                    self.motors.set_speed(slow_left, slow_right)
                    action = "slowed"
                caution_cooldown = 5  # Stay cautious for 5 more frames
                
            elif caution_cooldown > 0:
                caution_cooldown -= 1
                if caution_cooldown == 0 and not self.override_active:
                    self.state = ReflexState.NORMAL
                    
            elif analysis['status'] == 'clear':
                # Clear - pass through skill speeds
                self.override_active = False
                if not self.override_active:
                    self.state = ReflexState.NORMAL
                    self.motors.set_speed(*self._skill_speeds)
                    
            else:
                # Clear - pass through skill speeds
                self.override_active = False
                if not self.override_active:
                    self.state = ReflexState.NORMAL
                    self.motors.set_speed(*self._skill_speeds)
                    
            self.last_action = action
            self._last_reflex_time = time.time()
            
            # Debug output every 30 frames (~10 sec)
            if frame_count % 30 == 0:
                print(f"[REFLEX] {self.state.value} | action={action} | "
                      f"floor={analysis.get('floor_brightness', 0):.0f} "
                      f"obs={analysis.get('obstacle_score', 0):.2f} "
                      f"override={self.override_active} "
                      f"skill={self._skill_speeds}")
    
    @property
    def fps(self) -> float:
        """Reflex loop fps."""
        return self.camera.fps


class SkillLayer:
    """
    Skill layer - executes navigation skills using reflex safety.
    
    Skills are atomic movement commands that run to completion
    while the reflex system provides safety coverage.
    """
    
    def __init__(self, motors: MotorController, reflex: ReflexController, config: RobotConfig):
        self.motors = motors
        self.reflex = reflex
        self.config = config
        self._current_skill = None
        
    def forward(self, duration: float = 1.0, speed: float = 0.3):
        """Move forward for duration seconds."""
        self._current_skill = "forward"
        steps = int(duration / 0.05)
        for _ in range(steps):
            if self.reflex.override_active:
                break  # Reflex took over
            self.reflex.set_skill_speeds(speed, speed)
            self.motors.forward(speed)
            time.sleep(0.05)
        self.motors.stop()
        
    def reverse(self, duration: float = 1.0, speed: float = 0.3):
        """Move backward for duration seconds."""
        self._current_skill = "reverse"
        steps = int(duration / 0.05)
        for _ in range(steps):
            if self.reflex.override_active:
                break
            self.reflex.set_skill_speeds(-speed, -speed)
            self.motors.reverse(speed)
            time.sleep(0.05)
        self.motors.stop()
        
    def turn(self, direction: str, duration: float = 0.5, speed: float = 0.3):
        """
        Turn in place.
        direction: 'left' or 'right'
        """
        self._current_skill = f"turn_{direction}"
        self.reflex.set_skill_speeds(0, 0)
        
        if direction == "left":
            self.motors.turn_left(speed)
        else:
            self.motors.turn_right(speed)
        time.sleep(duration)
        self.motors.stop()
        
    def arc(self, direction: str, duration: float = 1.0, speed: float = 0.3):
        """
        Arc turn.
        direction: 'left' or 'right'
        """
        self._current_skill = f"arc_{direction}"
        self.reflex.set_skill_speeds(speed, speed)
        
        if direction == "left":
            self.motors.arc_left(speed)
        else:
            self.motors.arc_right(speed)
        time.sleep(duration)
        self.motors.stop()
        
    def wait(self, duration: float = 1.0):
        """Wait/delay."""
        self._current_skill = "wait"
        self.reflex.set_skill_speeds(0, 0)
        self.motors.stop()
        time.sleep(duration)
        
    def stop(self):
        """Immediate stop."""
        self._current_skill = "stop"
        self.reflex.set_skill_speeds(0, 0)
        self.motors.stop()
