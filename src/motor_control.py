import board
import time
import logging
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())

def simple_anti_clockwise():
  kit.stepper1.onestep()
  time.sleep(0.2)

def simple_clockwise():
  kit.stepper1.onestep(direction=stepper.BACKWARD)
  time.sleep(0.2)

# TODO: Make the movement correct for any hemisphere (Longitude)
