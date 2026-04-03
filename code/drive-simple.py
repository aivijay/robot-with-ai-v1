#!/usr/bin/env python3
"""Basic autonomous driving using rpicam-still for capture - with speed control"""
import subprocess
import time
import RPi.GPIO as GPIO
import cv2

# Speed control: 0.0 to 1.0 (0.3-0.5 recommended for careful navigation)
SPEED = 0.40

STBY = 5
AIN1, AIN2, PWMA = 17, 27, 18
BIN1, BIN2, PWMB = 22, 24, 23
BRIGHTNESS_THRESHOLD = 60

# PWM frequency (Hz)
PWM_FREQ = 1000

# Global PWM handles
pwm_a = None
pwm_b = None

def setup():
    global pwm_a, pwm_b
    GPIO.setmode(GPIO.BCM)
    for pin in [STBY, AIN1, AIN2, BIN1, BIN2]:
        GPIO.setup(pin, GPIO.OUT)
    GPIO.setup(PWMA, GPIO.OUT)
    GPIO.setup(PWMB, GPIO.OUT)
    GPIO.output(STBY, GPIO.HIGH)
    
    # Initialize PWM for speed control
    pwm_a = GPIO.PWM(PWMA, PWM_FREQ)
    pwm_b = GPIO.PWM(PWMB, PWM_FREQ)
    pwm_a.start(0)  # start with motors off
    pwm_b.start(0)

def drive_forward():
    # Set direction (both wheels forward)
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)
    # Set speed via PWM
    pwm_a.ChangeDutyCycle(SPEED * 100)
    pwm_b.ChangeDutyCycle(SPEED * 100)

def stop():
    pwm_a.ChangeDutyCycle(0)
    pwm_b.ChangeDutyCycle(0)

def reverse():
    # Direction already set in main loop via drive_forward/stop
    # Just need to set reverse direction
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)
    pwm_b.ChangeDutyCycle(SPEED * 100)
    time.sleep(0.8)
    stop()

def capture_frame():
    subprocess.run(['rm', '-f', '/tmp/floor.jpg'], check=False)
    subprocess.run(['rpicam-still', '-o', '/tmp/floor.jpg', '-t', '200', '--width', '640', '--height', '480', '-n'], check=True)
    img = cv2.imread('/tmp/floor.jpg')
    return img

def analyze_frame(frame):
    if frame is None:
        return 255, 255
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    floor_region = gray[int(h*0.6):, :]
    return floor_region.mean(), floor_region.min()

def main():
    setup()
    print(f"Autonomous driving started. Speed: {SPEED*100:.0f}%. Press Ctrl+C to stop.")
    time.sleep(2)
    
    try:
        while True:
            frame = capture_frame()
            brightness, min_pixel = analyze_frame(frame)
            print(f"Floor brightness: {brightness:.1f}, min: {min_pixel}")
            
            if brightness < BRIGHTNESS_THRESHOLD or min_pixel < 20:
                print("EDGE/CLIFF DETECTED - reversing!")
                stop()
                reverse()
            else:
                drive_forward()
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nStopping...")
        stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
