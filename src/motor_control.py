import board
import keyboard
import time
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())

# We will need a calibration screen
def motor_calibration():
  print("Calibration moon.")
  while True:
    if keyboard.read_key() == 'left':
      set_position(1)
    if keyboard.read_key() == 'right':
      set_position(-1)
    if keyboard.read_key() == 'down':
      for i in range(100):
        kit.stepper1.onestep()
        time.sleep(0.05)
      return True

def set_position(steps):
    # TODO: improve function move motor one step in either direction. Forward for my stepper is anti-clockwise, backward is clockwise
    if steps == -1:
      simple_forward()
    elif steps == 1:
      simple_backward() 

def simple_forward():
  kit.stepper1.onestep()
  time.sleep(0.05)

def simple_backward():
  kit.stepper1.onestep(direction=stepper.BACKWARD)
  time.sleep(0.05)

# TODO: Make the movement correct for any hemisphere (Longitude)