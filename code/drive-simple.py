#!/usr/bin/env python3
"""
Autonomous driving with floor/cliff detection using rpicam-still + OpenCV
Robot-with-AI-v1 - Version 1.0

Hardware: Pi Zero W + TB6612FNG + 5MP Camera v2 (OV5647)
GPIO: AIN1=17, AIN2=27, PWMA=18, BIN1=22, BIN2=24, PWMB=23, STBY=5

Requirements:
- rpicam-still (libcamera-apps)
- OpenCV (cv2)
- RPi.GPIO
"""
import subprocess
import time
import RPi.GPIO as GPIO
import cv2
import numpy as np
import os

# Motor pins
STBY = 5
AIN1, AIN2, PWMA = 17, 27, 18
BIN1, BIN2, PWMB = 22, 24, 23

# Detection thresholds
BRIGHTNESS_THRESHOLD = 40      # Floor mean brightness must be above this
FLOOR_DARK_THRESHOLD = 15      # Pixel value considered "dark"
DARK_PIXEL_RATIO = 0.1         # 10% dark pixels = edge/cliff detected

# Timing
REVERSE_DURATION = 0.5          # Seconds to reverse when edge detected
LOOP_DELAY = 0.3               # Seconds between camera checks

def setup_gpio():
    """Initialize GPIO pins for motor control"""
    GPIO.setmode(GPIO.BCM)
    for pin in [STBY, AIN1, AIN2, PWMA, BIN1, BIN2, PWMB]:
        GPIO.setup(pin, GPIO.OUT)
    GPIO.output(STBY, GPIO.HIGH)
    print("GPIO initialized")

def drive_forward():
    """Drive both motors forward"""
    # Motor A (front) - steering
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    # Motor B (rear) - drive
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)
    GPIO.output(PWMA, GPIO.HIGH)
    GPIO.output(PWMB, GPIO.HIGH)

def stop():
    """Stop both motors"""
    GPIO.output(PWMA, GPIO.LOW)
    GPIO.output(PWMB, GPIO.LOW)

def reverse():
    """Reverse for a short duration to escape edges"""
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)
    GPIO.output(PWMB, GPIO.HIGH)
    time.sleep(REVERSE_DURATION)
    stop()

def capture_frame():
    """Capture a frame using rpicam-still"""
    try:
        # Remove old frame
        subprocess.run(['rm', '-f', '/tmp/floor.jpg'], check=False, capture_output=True)
        # Capture new frame
        subprocess.run([
            'rpicam-still',
            '-o', '/tmp/floor.jpg',
            '-t', '200',
            '--width', '640',
            '--height', '480',
            '-n'
        ], check=True, capture_output=True)
        # Read image
        img = cv2.imread('/tmp/floor.jpg')
        return img
    except Exception as e:
        print(f"Capture error: {e}")
        return None

def analyze_frame(frame):
    """Analyze frame for floor/edge detection
    
    Returns:
        floor_mean: Average brightness of floor region
        dark_ratio: Fraction of floor pixels darker than FLOOR_DARK_THRESHOLD
    """
    if frame is None:
        return 0, 1.0  # Treat as edge if capture failed
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    
    # Bottom 40% of image is the floor
    floor_region = gray[int(h*0.6):, :]
    floor_mean = floor_region.mean()
    
    # Count dark pixels (potential edges/cliffs)
    dark_pixels = np.sum(floor_region < FLOOR_DARK_THRESHOLD)
    dark_ratio = dark_pixels / floor_region.size
    
    return floor_mean, dark_ratio

def main():
    """Main autonomous driving loop"""
    print("=" * 50)
    print("Autonomous Driving - Robot-with-AI-v1")
    print("=" * 50)
    print(f"Thresholds: brightness>{BRIGHTNESS_THRESHOLD}, dark_ratio<{DARK_PIXEL_RATIO}")
    print("Press Ctrl+C to stop")
    print()
    
    setup_gpio()
    time.sleep(2)  # Give robot time to settle
    
    try:
        while True:
            frame = capture_frame()
            floor_mean, dark_ratio = analyze_frame(frame)
            
            # Debug output
            status = "FORWARD" if floor_mean >= BRIGHTNESS_THRESHOLD and dark_ratio <= DARK_PIXEL_RATIO else "REVERSE!"
            print(f"[{status}] Floor: mean={floor_mean:.1f}, dark_px={dark_ratio*100:.1f}%")
            
            # Decision
            if floor_mean < BRIGHTNESS_THRESHOLD or dark_ratio > DARK_PIXEL_RATIO:
                print("  -> EDGE/CLIFF DETECTED!")
                stop()
                reverse()
            else:
                drive_forward()
            
            time.sleep(LOOP_DELAY)
            
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("Stopping...")
        print("=" * 50)
        stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
