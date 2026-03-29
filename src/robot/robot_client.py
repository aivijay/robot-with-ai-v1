#!/usr/bin/env python3
"""
robot_client.py — Thin client for robot-with-ai-v1
Runs on the robot (Pi Zero 2 W, Pi 3A+, or Pi 4).
Captures camera frames and streams them to the laptop brain.
Receives motor commands from the laptop and executes them.

Usage:
    python3 robot_client.py --laptop <laptop-ip> [--port 8000]

Requirements:
    pip install picamera2 gpiozero requests
"""

import argparse
import time
import io
import json
import requests
from picamera2 import Picamera2
import gpiozero
from gpiozero import Motor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

# Motor pin assignments (BCM numbering)
LEFT_MOTOR_PINS  = (22, 23)   # AIN1, AIN2
RIGHT_MOTOR_PINS = (24, 25)   # BIN1, BIN2

# Speed when turning (differential steering)
BASE_SPEED = 0.6
TURN_SPEED = 0.5

# Camera resolution (small = faster streaming)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 5  # Frames per second to stream

# How often to poll for commands (seconds)
POLL_INTERVAL = 0.2

# Safety: stop if no command received for this long (seconds)
COMMAND_TIMEOUT = 5.0


class RobotClient:
    def __init__(self, laptop_host: str, port: int = 8000):
        self.laptop_url = f"http://{laptop_host}:{port}"
        self.last_command_time = time.time()
        self.running = True

        # Initialize motors
        self.left_motor = Motor(*LEFT_MOTOR_PINS)
        self.right_motor = Motor(*RIGHT_MOTOR_PINS)
        self.stop()
        log.info("Motors initialized")

        # Initialize camera
        self.picam = Picamera2()
        config = self.picam.create_still_configuration(
            main={"size": (FRAME_WIDTH, FRAME_HEIGHT)},
            lores={"size": (FRAME_WIDTH, FRAME_HEIGHT)},
            display=False,
        )
        self.picam.configure(config)
        self.picam.start()
        log.info(f"Camera started ({FRAME_WIDTH}x{FRAME_HEIGHT})")

        # Small warmup
        time.sleep(1.0)
        log.info("Robot client ready")

    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()

    def move(self, direction: str, speed: float = None):
        """Execute a movement command."""
        if speed is None:
            speed = BASE_SPEED

        self.last_command_time = time.time()
        direction = direction.lower().strip()

        if direction == "forward":
            self.left_motor.forward(speed)
            self.right_motor.forward(speed)
        elif direction == "backward":
            self.left_motor.backward(speed)
            self.right_motor.backward(speed)
        elif direction == "left":
            # Pivot turn: left motor reverse, right motor forward
            self.left_motor.backward(speed * TURN_SPEED)
            self.right_motor.forward(speed * TURN_SPEED)
        elif direction == "right":
            self.left_motor.forward(speed * TURN_SPEED)
            self.right_motor.backward(speed * TURN_SPEED)
        elif direction == "stop":
            self.stop()
        else:
            log.warning(f"Unknown direction: {direction}")
            return

        log.info(f"Moved: {direction} @ speed {speed:.2f}")

    def capture_and_send_frame(self) -> bool:
        """Capture a frame and send it to the laptop brain."""
        try:
            # Capture frame to memory buffer
            buf = io.BytesIO()
            self.picam.capture_file(buf, format='jpeg', use_video_port=True)
            buf.seek(0)
            files = {"image": ("frame.jpg", buf, "image/jpeg")}
            resp = requests.post(
                f"{self.laptop_url}/api/frame",
                files=files,
                timeout=5
            )
            return resp.status_code == 200
        except Exception as e:
            log.error(f"Frame send failed: {e}")
            return False

    def poll_command(self):
        """Ask laptop for the next command."""
        try:
            resp = requests.get(f"{self.laptop_url}/api/command", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                direction = data.get("direction", "stop")
                speed = data.get("speed")
                self.move(direction, speed)
        except requests.exceptions.Timeout:
            pass
        except Exception as e:
            log.error(f"Poll failed: {e}")

    def safety_check(self):
        """Emergency stop if no command received recently."""
        if time.time() - self.last_command_time > COMMAND_TIMEOUT:
            if self.left_motor.value or self.right_motor.value:
                log.warning("Command timeout — stopping")
                self.stop()

    def run(self):
        """Main loop: stream frames and poll for commands."""
        log.info(f"Starting main loop, laptop at {self.laptop_url}")
        stream_interval = 1.0 / FPS
        last_stream_time = 0

        while self.running:
            now = time.time()

            # Stream a frame at configured FPS
            if now - last_stream_time >= stream_interval:
                self.capture_and_send_frame()
                last_stream_time = now

            # Poll for command
            self.poll_command()

            # Safety check
            self.safety_check()

            time.sleep(POLL_INTERVAL)

    def shutdown(self):
        log.info("Shutting down...")
        self.stop()
        self.picam.close()
        self.running = False


def main():
    parser = argparse.ArgumentParser(description="Robot thin client")
    parser.add_argument("--laptop", required=True, help="Laptop IP address")
    parser.add_argument("--port", type=int, default=8000, help="Laptop server port")
    args = parser.parse_args()

    robot = RobotClient(args.laptop, args.port)
    try:
        robot.run()
    except KeyboardInterrupt:
        log.info("Interrupted")
    finally:
        robot.shutdown()


if __name__ == "__main__":
    main()
