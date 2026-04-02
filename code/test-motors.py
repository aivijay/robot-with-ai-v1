#!/usr/bin/env python3
"""Test script for motor control - Robot-with-AI-v1"""
import RPi.GPIO as GPIO
import time

STBY = 5
AIN1, AIN2, PWMA = 17, 27, 18
BIN1, BIN2, PWMB = 22, 24, 23

def setup():
    GPIO.setmode(GPIO.BCM)
    for pin in [STBY, AIN1, AIN2, PWMA, BIN1, BIN2, PWMB]:
        GPIO.setup(pin, GPIO.OUT)
    GPIO.output(STBY, GPIO.HIGH)

def test_forward():
    print("Testing FORWARD...")
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)
    GPIO.output(PWMA, GPIO.HIGH)
    GPIO.output(PWMB, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(PWMA, GPIO.LOW)
    GPIO.output(PWMB, GPIO.LOW)
    print("Stop")

def test_reverse():
    print("Testing REVERSE...")
    time.sleep(1)
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)
    GPIO.output(PWMA, GPIO.HIGH)
    GPIO.output(PWMB, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(PWMA, GPIO.LOW)
    GPIO.output(PWMB, GPIO.LOW)
    print("Stop")

def test_turn_left():
    print("Testing LEFT TURN (Motor A forward, Motor B off)...")
    time.sleep(1)
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)
    GPIO.output(PWMA, GPIO.HIGH)
    GPIO.output(PWMB, GPIO.LOW)  # Motor B off
    time.sleep(1.5)
    GPIO.output(PWMA, GPIO.LOW)
    GPIO.output(PWMB, GPIO.LOW)
    print("Stop")

def test_turn_right():
    print("Testing RIGHT TURN (Motor A off, Motor B forward)...")
    time.sleep(1)
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)
    GPIO.output(PWMA, GPIO.LOW)  # Motor A off
    GPIO.output(PWMB, GPIO.HIGH)
    time.sleep(1.5)
    GPIO.output(PWMA, GPIO.LOW)
    GPIO.output(PWMB, GPIO.LOW)
    print("Stop")

def main():
    setup()
    try:
        test_forward()
        test_reverse()
        test_turn_left()
        test_turn_right()
        print("\nAll tests complete!")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
