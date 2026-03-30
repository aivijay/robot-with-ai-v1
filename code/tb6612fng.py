"""
TB6612FNG Dual Motor Driver — Python Control Module
====================================================
Controls 4 motors (2 per TB6612FNG board) on a Raspberry Pi Zero W.

Each TB6612FNG board drives 2 motors:
  - Motor A: PWMA (speed), AIN1/AIN2 (direction)
  - Motor B: PWMB (speed), BIN1/BIN2 (direction)

Board 1 = Front motors (FL, FR)
Board 2 = Rear  motors (RL, RR)

Hardware:
  - 2× TB6612FNG motor driver boards
  - 7.4V LiPo battery (VMOTOR)
  - Raspberry Pi Zero W (3.3V logic)
  - LM2596 step-down: 7.4V → 5V for the Pi

Reference: See docs/wiring-diagram.md and docs/gpio-reference.md
"""

import time
from enum import Enum
from typing import Optional

# ── RPi.GPIO must be installed on the Pi Zero W ─────────────────────────────────
try:
    import RPi.GPIO as GPIO
except ImportError:
    raise ImportError("RPi.GPIO not found. Install with: sudo apt install python3-rpi.gpio")

# ─────────────────────────────────────────────────────────────────────────────
# GPIO Pin Assignments
# ─────────────────────────────────────────────────────────────────────────────
# BCM numbering (GPIO numbers, not physical pin numbers)

class MotorID(Enum):
    """Identifies each of the 4 motors."""
    FRONT_LEFT  = "front_left"
    FRONT_RIGHT = "front_right"
    REAR_LEFT   = "rear_left"
    REAR_RIGHT  = "rear_right"


# Board 1 — Front motors (TB6612FNG #1)
_BOARD1_AIN1  = 17   # Motor A direction 1
_BOARD1_AIN2  = 27   # Motor A direction 2
_BOARD1_PWMA  = 18   # Motor A speed (PWM)
_BOARD1_BIN1  = 22   # Motor B direction 1
_BOARD1_BIN2  = 24   # Motor B direction 2
_BOARD1_PWMB  = 23   # Motor B speed (PWM)
_BOARD1_STBY  = 5    # Standby pin (HIGH = enabled)

# Board 2 — Rear motors (TB6612FNG #2)
_BOARD2_AIN1  = 10   # Motor C direction 1
_BOARD2_AIN2  = 11   # Motor C direction 2
_BOARD2_PWMA  = 9    # Motor C speed (PWM)
_BOARD2_BIN1  = 8    # Motor D direction 1
_BOARD2_BIN2  = 25   # Motor D direction 2
_BOARD2_PWMB  = 7    # Motor D speed (PWM)
_BOARD2_STBY  = 6    # Standby pin (HIGH = enabled)

# Maps MotorID → (direction pin 1, direction pin 2, PWM pin, standby pin)
_MOTOR_GPIO_MAP = {
    MotorID.FRONT_LEFT:  (_BOARD1_AIN1, _BOARD1_AIN2, _BOARD1_PWMA, _BOARD1_STBY),
    MotorID.FRONT_RIGHT: (_BOARD1_BIN1, _BOARD1_BIN2, _BOARD1_PWMB, _BOARD1_STBY),
    MotorID.REAR_LEFT:   (_BOARD2_AIN1, _BOARD2_AIN2, _BOARD2_PWMA, _BOARD2_STBY),
    MotorID.REAR_RIGHT:  (_BOARD2_BIN1, _BOARD2_BIN2, _BOARD2_PWMB, _BOARD2_STBY),
}

# ─────────────────────────────────────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────────────────────────────────────

class MotorError(Exception):
    """Base exception for motor driver errors."""
    pass


class SpeedOutOfRangeError(MotorError):
    """Raised when speed value is not between 0 and 100."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Single Motor Controller
# ─────────────────────────────────────────────────────────────────────────────

class TB6612FNGMotor:
    """
    Controls one motor channel on a TB6612FNG board.

    A single TB6612FNG has two motor channels (A and B). This class represents
    one channel — either Motor A or Motor B — on a specific board.

    Direction control uses two logic pins (IN1, IN2):
        IN1=HIGH, IN2=LOW  → forward
        IN1=LOW,  IN2=HIGH → backward
        IN1=LOW,  IN2=LOW  → brake (fast stop)
        IN1=HIGH, IN2=HIGH → brake (fast stop)

    Args:
        in1:  BCM GPIO pin for direction input 1
        in2:  BCM GPIO pin for direction input 2
        pwm:  BCM GPIO pin for speed (PWM output)
        stby: BCM GPIO pin for the board's STBY line
        name: Human-readable name for this motor (used in logs)
    """

    PWM_FREQ_HZ = 1000  # Safe default for small DC motors

    def __init__(
        self,
        in1: int,
        in2: int,
        pwm: int,
        stby: int,
        name: str = "motor"
    ):
        self._in1  = in1
        self._in2  = in2
        self._pwm  = pwm
        self._stby = stby
        self._name = name
        self._pwm_handle: Optional[GPIO.PWM] = None
        self._current_speed: float = 0.0

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _validate_speed(self, speed: float) -> None:
        """Raise if speed is outside 0–100 range."""
        if not (0.0 <= speed <= 100.0):
            raise SpeedOutOfRangeError(
                f"[{self._name}] Speed must be 0–100, got {speed}"
            )

    def _set_direction(self, forward: bool) -> None:
        """Set direction pins. Does not affect PWM."""
        if forward:
            GPIO.output(self._in1, GPIO.HIGH)
            GPIO.output(self._in2, GPIO.LOW)
        else:
            GPIO.output(self._in1, GPIO.LOW)
            GPIO.output(self._in2, GPIO.HIGH)

    def _apply_speed(self, speed: float) -> None:
        """Set PWM duty cycle from 0–100."""
        duty = max(0.0, min(100.0, speed))
        if self._pwm_handle:
            self._pwm_handle.ChangeDutyCycle(duty)
        self._current_speed = duty

    # ── Public API ────────────────────────────────────────────────────────────

    def init(self) -> None:
        """
        Initialize GPIO pins. Call once at program startup.
        Sets all pins to output mode and starts PWM on the speed pin.
        """
        for pin in (self._in1, self._in2, self._stby):
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        # Standby HIGH = board enabled
        GPIO.output(self._stby, GPIO.HIGH)

        # Start PWM at 0% (motors off)
        self._pwm_handle = GPIO.PWM(self._pwm, self.PWM_FREQ_HZ)
        self._pwm_handle.start(0.0)

    def cleanup(self) -> None:
        """Stop PWM and release pins. Call at program exit."""
        if self._pwm_handle:
            self._pwm_handle.stop()
            self._pwm_handle = None
        # Leave direction pins low, keep standby HIGH
        GPIO.output(self._in1, GPIO.LOW)
        GPIO.output(self._in2, GPIO.LOW)

    def forward(self, speed: float = 100.0) -> None:
        """
        Run the motor forward at the given speed.

        Args:
            speed: Duty cycle 0–100 (default 100).
        """
        self._validate_speed(speed)
        self._set_direction(forward=True)
        self._apply_speed(speed)

    def backward(self, speed: float = 100.0) -> None:
        """
        Run the motor backward at the given speed.

        Args:
            speed: Duty cycle 0–100 (default 100).
        """
        self._validate_speed(speed)
        self._set_direction(forward=False)
        self._apply_speed(speed)

    def stop(self) -> None:
        """
        Brake the motor (fast decay — motors resist motion).
        Unlike coast(), stop() actively resists wheel movement.
        """
        # Both direction pins HIGH = brake
        GPIO.output(self._in1, GPIO.HIGH)
        GPIO.output(self._in2, GPIO.HIGH)
        self._apply_speed(0.0)

    def coast(self) -> None:
        """
        Coast to stop (motor is not driven, just freewheels).
        Slightly ambiguous on TB6612FNG — sets both direction pins LOW.
        """
        GPIO.output(self._in1, GPIO.LOW)
        GPIO.output(self._in2, GPIO.LOW)
        self._apply_speed(0.0)

    def set_speed(self, speed: float) -> None:
        """
        Set motor speed without changing direction.
        Direction must already be set (via forward() or backward()),
        or call set_speed() AFTER one of those to keep that direction.

        Args:
            speed: Duty cycle 0–100. Use 0 to coast.

        Note:
            If no direction has been set yet, the motor state is undefined.
            Always call forward() or backward() at least once before using
            set_speed() alone.
        """
        self._validate_speed(speed)
        self._apply_speed(speed)

    @property
    def speed(self) -> float:
        """Return the last set speed (0–100)."""
        return self._current_speed

    def is_moving(self) -> bool:
        """Return True if the motor is currently being driven."""
        return self._current_speed > 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Full 4WD Controller
# ─────────────────────────────────────────────────────────────────────────────

class TB6612FNGController:
    """
    High-level controller for a 4-motor TB6612FNG setup.

    Manages two TB6612FNG boards (4 motors total) with a unified interface.

    Example usage::

        controller = TB6612FNGController()
        controller.init()

        # Drive forward
        controller.forward(speed=60)
        time.sleep(2)

        # Spin in place (tank turn left)
        controller.tank_turn(TB6612FNGController.Turn.LEFT, speed=50)
        time.sleep(1)

        controller.stop_all()
        controller.cleanup()

    Motor layout::

         [FL]           [FR]
           \\             /
            \\___________/
            |     X     |
            |___________|
           /             \\
         [RL]           [RR]
    """

    class Turn(Enum):
        """Tank steering direction."""
        LEFT  = "left"
        RIGHT = "right"

    def __init__(self):
        self._motors: dict[MotorID, TB6612FNGMotor] = {
            MotorID.FRONT_LEFT:  TB6612FNGMotor(
                _BOARD1_AIN1, _BOARD1_AIN2, _BOARD1_PWMA, _BOARD1_STBY,
                name="front_left"
            ),
            MotorID.FRONT_RIGHT: TB6612FNGMotor(
                _BOARD1_BIN1, _BOARD1_BIN2, _BOARD1_PWMB, _BOARD1_STBY,
                name="front_right"
            ),
            MotorID.REAR_LEFT:   TB6612FNGMotor(
                _BOARD2_AIN1, _BOARD2_AIN2, _BOARD2_PWMA, _BOARD2_STBY,
                name="rear_left"
            ),
            MotorID.REAR_RIGHT:  TB6612FNGMotor(
                _BOARD2_BIN1, _BOARD2_BIN2, _BOARD2_PWMB, _BOARD2_STBY,
                name="rear_right"
            ),
        }

        # GPIO setup mode — call GPIO.setmode(GPIO.BCM) before init
        self._initialized = False

    def init(self, gpio_mode: int = GPIO.BCM) -> None:
        """
        Initialize all GPIO pins and start PWM on all motor channels.

        Args:
            gpio_mode: GPIO numbering mode (default BCM).
        """
        GPIO.setmode(gpio_mode)
        for motor in self._motors.values():
            motor.init()
        self._initialized = True

    def cleanup(self) -> None:
        """Stop all motors and release GPIO pins."""
        for motor in self._motors.values():
            motor.cleanup()
        GPIO.cleanup()
        self._initialized = False

    # ── Individual motor access ───────────────────────────────────────────────

    def motor(self, motor_id: MotorID) -> TB6612FNGMotor:
        """Return the TB6612FNGMotor instance for the given motor."""
        return self._motors[motor_id]

    @property
    def front_left(self)   -> TB6612FNGMotor: return self._motors[MotorID.FRONT_LEFT]
    @property
    def front_right(self)  -> TB6612FNGMotor: return self._motors[MotorID.FRONT_RIGHT]
    @property
    def rear_left(self)    -> TB6612FNGMotor: return self._motors[MotorID.REAR_LEFT]
    @property
    def rear_right(self)   -> TB6612FNGMotor: return self._motors[MotorID.REAR_RIGHT]

    # ── 4WD movement commands ────────────────────────────────────────────────

    def forward(self, speed: float = 100.0) -> None:
        """Run all 4 motors forward at the same speed."""
        for motor in self._motors.values():
            motor.forward(speed)

    def backward(self, speed: float = 100.0) -> None:
        """Run all 4 motors backward at the same speed."""
        for motor in self._motors.values():
            motor.backward(speed)

    def stop_all(self) -> None:
        """Brake all 4 motors simultaneously."""
        for motor in self._motors.values():
            motor.stop()

    def coast_all(self) -> None:
        """Coast all 4 motors to stop (freewheel)."""
        for motor in self._motors.values():
            motor.coast()

    def set_all_speeds(self, speed: float) -> None:
        """Set the same speed on all 4 motors (direction unchanged)."""
        for motor in self._motors.values():
            motor.set_speed(speed)

    # ── Differential steering (tank turn) ────────────────────────────────────

    def tank_turn(self, direction: "TB6612FNGController.Turn", speed: float = 100.0) -> None:
        """
        Spin in place using tank (differential) steering.

        Args:
            direction: Turn.LEFT or Turn.RIGHT
            speed: Drive motor speed 0–100
        """
        if direction == self.Turn.LEFT:
            # Left-side motors reverse, right-side motors forward
            self.front_left.backward(speed)
            self.rear_left.backward(speed)
            self.front_right.forward(speed)
            self.rear_right.forward(speed)
        else:  # RIGHT
            # Right-side motors reverse, left-side motors forward
            self.front_left.forward(speed)
            self.rear_left.forward(speed)
            self.front_right.backward(speed)
            self.rear_right.backward(speed)

    def turn(self, direction: "TB6612FNGController.Turn", speed: float = 60.0,
             pivot_speed: float = 30.0) -> None:
        """
        Execute a smooth turn by slowing the inner track.

        Args:
            direction: Turn.LEFT or Turn.RIGHT
            speed: outer track speed (drive side)
            pivot_speed: inner track speed (pivot side, lower = tighter turn)
        """
        if direction == self.Turn.LEFT:
            self.front_left.forward(pivot_speed)
            self.rear_left.forward(pivot_speed)
            self.front_right.forward(speed)
            self.rear_right.forward(speed)
        else:  # RIGHT
            self.front_left.forward(speed)
            self.rear_left.forward(speed)
            self.front_right.forward(pivot_speed)
            self.rear_right.forward(pivot_speed)

    # ── Board-level standby control ──────────────────────────────────────────

    def enable_board(self, board: int) -> None:
        """
        Drive a board's STBY pin HIGH to enable it.

        Args:
            board: 1 for front board, 2 for rear board
        """
        if board == 1:
            GPIO.output(_BOARD1_STBY, GPIO.HIGH)
        elif board == 2:
            GPIO.output(_BOARD2_STBY, GPIO.HIGH)
        else:
            raise MotorError(f"Invalid board number: {board} (use 1 or 2)")

    def disable_board(self, board: int) -> None:
        """
        Drive a board's STBY pin LOW to disable it (coast stop).

        Args:
            board: 1 for front board, 2 for rear board
        """
        if board == 1:
            GPIO.output(_BOARD1_STBY, GPIO.LOW)
        elif board == 2:
            GPIO.output(_BOARD2_STBY, GPIO.LOW)
        else:
            raise MotorError(f"Invalid board number: {board} (use 1 or 2)")

    # ── Diagnostic ──────────────────────────────────────────────────────────

    def status(self) -> dict:
        """Return a dict with current speed for each motor."""
        return {mid.value: m.speed for mid, m in self._motors.items()}

    def __repr__(self) -> str:
        status = " | ".join(f"{mid.value}: {m.speed:.0f}%"
                            for mid, m in self._motors.items())
        return f"<TB6612FNGController [{status}]>"


# ─────────────────────────────────────────────────────────────────────────────
# Test / Demo Script
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("TB6612FNG 4WD Motor Controller — Test")
    print("=" * 45)
    print("This script will run each motor in sequence.")
    print("Make sure all wiring is complete before running.")
    print()
    print("Press Ctrl+C to stop all motors and exit.")
    print()

    controller = TB6612FNGController()

    try:
        controller.init()
        print(controller)
        print()

        # 1. Drive forward slowly
        print("[1] Forward at 40% — 2 seconds")
        controller.forward(speed=40)
        time.sleep(2)

        # 2. Stop (brake)
        print("[2] Brake — 0.5 seconds")
        controller.stop_all()
        time.sleep(0.5)

        # 3. Drive backward slowly
        print("[3] Backward at 40% — 2 seconds")
        controller.backward(speed=40)
        time.sleep(2)

        # 4. Stop
        print("[4] Brake — 0.5 seconds")
        controller.stop_all()
        time.sleep(0.5)

        # 5. Test each motor individually (forward at 50%)
        for mid in MotorID:
            print(f"[5] {mid.value} forward at 50% — 0.8 seconds")
            controller.motor(mid).forward(speed=50)
            time.sleep(0.8)
            controller.motor(mid).stop()
            time.sleep(0.2)

        # 6. Tank turn left
        print("[6] Tank turn LEFT at 60% — 1.5 seconds")
        controller.tank_turn(controller.Turn.LEFT, speed=60)
        time.sleep(1.5)
        controller.stop_all()

        # 7. Tank turn right
        print("[7] Tank turn RIGHT at 60% — 1.5 seconds")
        controller.tank_turn(controller.Turn.RIGHT, speed=60)
        time.sleep(1.5)
        controller.stop_all()

        print()
        print("All tests complete. Cleaning up.")

    except KeyboardInterrupt:
        print("\nInterrupted! Stopping all motors...")

    finally:
        controller.stop_all()
        time.sleep(0.3)
        controller.cleanup()
        print("Done. GPIO pins released.")
