#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

STBY, AIN1, AIN2, PWMA = 5, 17, 27, 18
BIN1, BIN2, PWMB = 22, 24, 23
PWM_FREQ = 100

GPIO.setmode(GPIO.BCM)
for pin in [STBY, AIN1, AIN2, PWMA, BIN1, BIN2, PWMB]:
    GPIO.setup(pin, GPIO.OUT)
GPIO.output(STBY, GPIO.HIGH)

pwma = GPIO.PWM(PWMA, PWM_FREQ)
pwmb = GPIO.PWM(PWMB, PWM_FREQ)
pwma.start(0)
pwmb.start(0)

print('Forward 0.3 for 2s...')
GPIO.output(AIN1, GPIO.HIGH)
GPIO.output(AIN2, GPIO.LOW)
GPIO.output(BIN1, GPIO.HIGH)
GPIO.output(BIN2, GPIO.LOW)
pwma.ChangeDutyCycle(30)
pwmb.ChangeDutyCycle(30)
time.sleep(2)

print('Stop for 1s...')
pwma.ChangeDutyCycle(0)
pwmb.ChangeDutyCycle(0)
time.sleep(1)

print('Reverse 0.3 for 2s...')
GPIO.output(AIN1, GPIO.LOW)
GPIO.output(AIN2, GPIO.HIGH)
GPIO.output(BIN1, GPIO.LOW)
GPIO.output(BIN2, GPIO.HIGH)
pwma.ChangeDutyCycle(30)
pwmb.ChangeDutyCycle(30)
time.sleep(2)

print('Stop')
pwma.ChangeDutyCycle(0)
pwmb.ChangeDutyCycle(0)
time.sleep(0.5)

print('Cleanup')
pwma.stop()
pwmb.stop()
GPIO.cleanup()
print('Done')
