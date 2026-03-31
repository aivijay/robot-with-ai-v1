import RPi.GPIO as GPIO
import time

# Pins
STBY = 5
AIN1 = 17
AIN2 = 27
PWMA = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(STBY, GPIO.OUT)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(PWMA, GPIO.OUT)

# Enable motors
GPIO.output(STBY, GPIO.HIGH)

# Test forward
print("Forward...")
GPIO.output(AIN1, GPIO.HIGH)
GPIO.output(AIN2, GPIO.LOW)
GPIO.output(PWMA, GPIO.HIGH)
time.sleep(2)

# Stop
print("Stop...")
GPIO.output(PWMA, GPIO.LOW)
time.sleep(1)

# Test backward
print("Backward...")
GPIO.output(AIN1, GPIO.LOW)
GPIO.output(AIN2, GPIO.HIGH)
GPIO.output(PWMA, GPIO.HIGH)
time.sleep(2)

# Cleanup
GPIO.output(PWMA, GPIO.LOW)
GPIO.cleanup()
print("Done!")
