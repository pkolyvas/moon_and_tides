import board
import time
import logging
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from displayhatmini import DisplayHATMini

kit = MotorKit(i2c=board.I2C())
display_hat = DisplayHATMini(None)

# We will need a calibration screen
def motor_calibration():
  logging.info(" Moon motor calibration: Motor calibrating")
  while True:
    if display_hat.read_button(display_hat.BUTTON_A):
      set_position(1)
    if display_hat.read_button(display_hat.BUTTON_X):
      set_position(-1)
    if display_hat.read_button(display_hat.BUTTON_B):
      logging.info("Done calibration. Resetting moon.")
      for i in range(100):
        kit.stepper1.onestep()
        time.sleep(0.10)
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
  time.sleep(0.10)

# TODO: Make the movement correct for any hemisphere (Longitude)
  
  