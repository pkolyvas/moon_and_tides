def motor_calibration():
  print("Dev: Motor calibrating")
  pass

def simple_forward():
  print("Motor moving forward. This is counter clockwise.")
  pass

def simple_backward():
  print("Motor moving backwards. This is clockwise / correct for northern hemisphere.")
  pass

def calibrate_moon_screen(display_controller):
  if display_controller == "calibration":
        print("Active display: Moon calibration")

def tide_display(display_controller, trend, next, afternext, progress, clock):     
  if (trend == "Tide Receding" and progress < 0.05) or (trend == "Rising Tide" and progress > 0.95):
        trend = "Low Tide"
        print("Low Tide Conditions.")
  elif (trend == "Tide Receding" and progress > 0.95) or (trend == "Rising Tide" and progress < 0.05):
      trend = "High Tide"
      print("High Tide Conditions.")
  if display_controller == "tide":
      print("Active display: Tide")

def moonlight():
   print("Moon light on.")
   pass