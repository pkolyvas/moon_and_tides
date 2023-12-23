import keyboard
import motor_control
import board


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
      motor_control.simple_anticlockwise()
    elif steps == 1:
      motor_control.simple_clockwise()   

# TODO: 
   # Retrieve new data
   # If no collection, read saved data
   # Calibrate full moon
   # Display current
