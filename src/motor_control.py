import board
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())

# calibration in this case will 
def motor_calibration():
  pass

def set_position_clockwise():
  pass

def set_position_anticlockwise():
  pass

def simple_clockwise():
  kit.stepper1.onestep()

def simple_anticlockwise():
  kit.stepper1.onestep(direction=stepper.BACKWARD)
