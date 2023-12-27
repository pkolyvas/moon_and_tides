import logging

def motor_calibration():
  logging.info("Dev Mode: Moon motor calibration: Motor calibrating")
  pass

def simple_forward():
  logging.debug("Motor moving forward. This is counter clockwise.")
  pass

def simple_backward():
  logging.debug("Motor moving backwards. This is clockwise / correct for northern hemisphere.")
  pass

def calibrate_moon_screen(display_controller):
  if display_controller == "calibration":
        print("Active display: Moon calibration")

def tide_display(display_controller, trend, next, afternext, progress, clock):     
  if (trend == "Tide Receding" and progress < 0.05) or (trend == "Rising Tide" and progress > 0.95):
        trend = "Low Tide"
        logging.info("Low Tide Conditions.")
  elif (trend == "Tide Receding" and progress > 0.95) or (trend == "Rising Tide" and progress < 0.05):
      trend = "High Tide"
      logging.info("High Tide Conditions.")
  if display_controller == "tide":
      logging.info("Active display: Tide")

def moonlight():
   logging.info("Moon light on.")
   pass
 
def devmode():
   pass