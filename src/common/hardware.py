"""Robot hardware configuration and constants."""
from dataclasses import dataclass
from typing import Tuple

# Motor driver pins (BCM numbering)
STBY = 5
AIN1, AIN2, PWMA = 17, 27, 18   # Motor A (steering/front)
BIN1, BIN2, PWMB = 22, 24, 23   # Motor B (drive/rear)

PWM_FREQ = 1000  # Hz

# Speed settings
SPEED_SLOW = 0.30      # 30% - obstacle avoidance mode
SPEED_MEDIUM = 0.50    # 50% - normal driving
SPEED_FAST = 0.70      # 70% - fast traversal

# Camera settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS_TARGET = 3  # Realistic fps from MJPEG stream

# Image analysis thresholds
BRIGHTNESS_THRESHOLD = 60   # floor brightness
DARK_PIXEL_THRESHOLD = 8    # % dark pixels to trigger reverse (cliff)
OBSTACLE_THRESHOLD = 0.15   # obstacle score to stop

# Timing
SKILL_TIMEOUT = 5.0  # seconds before skill considered stuck
AGENT_THINK_INTERVAL = 0.5  # seconds between LLM thoughts - more responsive

@dataclass
class RobotConfig:
    """Complete robot configuration."""
    # Motors
    stby: int = STBY
    ain1: int = AIN1
    ain2: int = AIN2
    pwma: int = PWMA
    bin1: int = BIN1
    bin2: int = BIN2
    pwmb: int = PWMB
    pwm_freq: int = PWM_FREQ
    
    # Speeds
    speed_slow: float = SPEED_SLOW
    speed_medium: float = SPEED_MEDIUM
    speed_fast: float = SPEED_FAST
    
    # Camera
    camera_width: int = CAMERA_WIDTH
    camera_height: int = CAMERA_HEIGHT
    
    # Thresholds
    brightness_threshold: int = BRIGHTNESS_THRESHOLD
    dark_pixel_threshold: int = DARK_PIXEL_THRESHOLD
    obstacle_threshold: float = OBSTACLE_THRESHOLD
    
    # Timing
    skill_timeout: float = SKILL_TIMEOUT
    agent_think_interval: float = AGENT_THINK_INTERVAL
