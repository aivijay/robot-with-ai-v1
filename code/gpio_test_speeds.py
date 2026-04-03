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

# Test at different speeds
for speed in [20, 30, 50, 70]:
    print(f'Forward {speed}% for 1.5s...')
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)
    pwma.ChangeDutyCycle(speed)
    pwmb.ChangeDutyCycle(speed)
    time.sleep(1.5)
    
    print('Stop for 0.5s...')
    pwma.ChangeDutyCycle(0)
    pwmb.ChangeDutyCycle(0)
    time.sleep(0.5)

print('Cleanup')
pwma.stop()
pwmb.stop()
GPIO.cleanup()
print('Done')
