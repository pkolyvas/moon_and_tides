import keyboard

# calibration in this case will 
def motor_calibration():
  # We will need a calibration that allows for rotating left/right and confirming
  # display "is calibrated" message.
  # TODO: Calibration light on: shine single light through hole (pinhole)
  calibration_light(True):
  while True:
    if keyboard.read_key() == 'left':
      set_position(1)
    if keyboard.read_key() == 'right':
      set_position(-1)
    if keyboard.read_key() == 'down':
      calibration_light(False)
      return True

def set_position(steps):
    # TODO: move motor one step in either direction. Clockwise (positive), anti-clockwise (negative) 
    print(f"Moving moon mask {direction} the following number of steps: {steps}")

while True:
    motor_calibration()
    print("break")
    break
    
def calibration_light(state):
   if state == True:
      # set light on
      pass
   

# TODO: 
   # Retrieve new data
   # If no collection, read saved data
   # Calibrate full moon
   # Display current
