import board
import keyboard
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())

# calibration in this case will 
def motor_calibration():
  while True:
    if keyboard.read_key() == 'left':
      set_position(1)
    if keyboard.read_key() == 'right':
      set_position(-1)
    if keyboard.read_key() == 'down':
      return True

def set_position(steps):
    # TODO: move motor one step in either direction. Clockwise (positive), anti-clockwise (negative) 
    # print(f"Moving moon mask {direction} the following number of steps: {steps}")
    if steps == -1:
      simple_anticlockwise()
    elif steps == 1:
      simple_clockwise() 

def simple_clockwise():
  kit.stepper1.onestep()

def simple_anticlockwise():
  kit.stepper1.onestep(direction=stepper.BACKWARD)
