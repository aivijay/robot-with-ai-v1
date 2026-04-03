#!/usr/bin/env python3
"""Test motors directly."""
import sys
sys.path.insert(0, '/home/vijay/working/car-ai/src')

from robot import MotorController
from common.hardware import RobotConfig
import time

config = RobotConfig()
m = MotorController(config)
m.setup()
print('Testing forward (0.3 speed, 2s)...')
m.forward(0.3)
time.sleep(2)
print('Stop')
m.stop()
time.sleep(1)
print('Testing reverse (0.3 speed, 2s)...')
m.reverse(0.3)
time.sleep(2)
print('Stop')
m.stop()
print('Done')
m.cleanup()
