"""Motor controller - low-level motor control via GPIO."""
import RPi.GPIO as GPIO
import time
from typing import Optional

from ..common.hardware import (
    STBY, AIN1, AIN2, PWMA, BIN1, BIN2, PWMB, PWM_FREQ
)


class MotorController:
    """
    Low-level motor control using GPIO + PWM.
    Handles TB6612FNG motor driver.
    """
    
    def __init__(self, config=None):
        self.config = config
        self.pwma: Optional[GPIO.PWM] = None
        self.pwmb: Optional[GPIO.PWM] = None
        self._initialized = False
        
    def setup(self):
        """Initialize GPIO pins."""
        if self._initialized:
            return
        
        GPIO.setmode(GPIO.BCM)
        
        # All motor control pins as outputs
        for pin in [STBY, AIN1, AIN2, PWMA, BIN1, BIN2, PWMB]:
            GPIO.setup(pin, GPIO.OUT)
        
        # PWM on speed pins (only create if not already created)
        if self.pwma is None:
            self.pwma = GPIO.PWM(PWMA, PWM_FREQ)
            self.pwma.start(0)
        if self.pwmb is None:
            self.pwmb = GPIO.PWM(PWMB, PWM_FREQ)
            self.pwmb.start(0)
        
        # Enable motor driver
        GPIO.output(STBY, GPIO.HIGH)
        
        self._initialized = True
        
    def set_speed(self, left: float, right: float):
        """
        Set motor speeds directly (-1 to 1).
        Positive = forward, Negative = reverse.
        """
        if not self._initialized:
            self.setup()
            
        # Left motor (Motor A)
        if left > 0:
            GPIO.output(AIN1, GPIO.HIGH)
            GPIO.output(AIN2, GPIO.LOW)
        elif left < 0:
            GPIO.output(AIN1, GPIO.LOW)
            GPIO.output(AIN2, GPIO.HIGH)
        else:
            GPIO.output(AIN1, GPIO.LOW)
            GPIO.output(AIN2, GPIO.LOW)
            
        # Right motor (Motor B)
        if right > 0:
            GPIO.output(BIN1, GPIO.HIGH)
            GPIO.output(BIN2, GPIO.LOW)
        elif right < 0:
            GPIO.output(BIN1, GPIO.LOW)
            GPIO.output(BIN2, GPIO.HIGH)
        else:
            GPIO.output(BIN1, GPIO.LOW)
            GPIO.output(BIN2, GPIO.LOW)
            
        self.pwma.ChangeDutyCycle(abs(left) * 100)
        self.pwmb.ChangeDutyCycle(abs(right) * 100)
    
    def stop(self):
        """Stop both motors immediately."""
        if self.pwma and self.pwmb:
            self.pwma.ChangeDutyCycle(0)
            self.pwmb.ChangeDutyCycle(0)
        elif self._initialized:
            # Fallback: try GPIO directly
            GPIO.output(AIN1, GPIO.LOW)
            GPIO.output(AIN2, GPIO.LOW)
            GPIO.output(BIN1, GPIO.LOW)
            GPIO.output(BIN2, GPIO.LOW)
        
    def forward(self, speed: float = 0.3):
        """Drive both motors forward."""
        self.set_speed(speed, speed)
        
    def reverse(self, speed: float = 0.3):
        """Drive both motors in reverse."""
        self.set_speed(-speed, -speed)
        
    def turn_left(self, speed: float = 0.3):
        """Turn in place left (or arc left)."""
        # Left motor reverse, right motor forward = spin left
        self.set_speed(-speed * 0.5, speed)
        
    def turn_right(self, speed: float = 0.3):
        """Turn in place right (or arc right)."""
        # Left motor forward, right motor reverse = spin right
        self.set_speed(speed, -speed * 0.5)
        
    def arc_left(self, speed: float = 0.3, turn_ratio: float = 0.5):
        """Arc turn left - forward with differential speed."""
        self.set_speed(speed * turn_ratio, speed)
        
    def arc_right(self, speed: float = 0.3, turn_ratio: float = 0.5):
        """Arc turn right - forward with differential speed."""
        self.set_speed(speed, speed * turn_ratio)
        
    def reverse_arc_left(self, speed: float = 0.3, turn_ratio: float = 0.5):
        """Reverse arc left."""
        self.set_speed(-speed * turn_ratio, -speed)
        
    def reverse_arc_right(self, speed: float = 0.3, turn_ratio: float = 0.5):
        """Reverse arc right."""
        self.set_speed(-speed, -speed * turn_ratio)
        
    def cleanup(self):
        """Release GPIO resources."""
        self.stop()
        if self._initialized:
            GPIO.cleanup()
            self._initialized = False
