#!/usr/bin/env python3
from ST7789 import ST7789, BG_SPI_CS_FRONT
from PIL import Image, ImageDraw, ImageFont
import apploader
import random
import time
import sys
import os

# Buttons
BUTTON_A = 5
BUTTON_B = 6
BUTTON_X = 16
BUTTON_Y = 24

# Onboard RGB LED
LED_R = 17
LED_G = 27
LED_B = 22

# General
SPI_PORT = 0
SPI_CS = 1
SPI_DC = 9
BACKLIGHT = 13

# Screen dimensions
WIDTH = 320
HEIGHT = 240

display = ST7789(
    port=SPI_PORT,
    cs=SPI_CS,
    dc=SPI_DC,
    backlight=BACKLIGHT,
    width=WIDTH,
    height=HEIGHT,
    rotation=180,
    spi_speed_hz=60 * 1000 * 1000
)

default_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
top_row_height = 63
left_column_left_justification = 10
bottom_row_height = 153
right_column_right_justification = 220

# Stubbing a screen class
class Screen:
    def __init__(self, name) -> None:
        self.name = name

# The Calibrating Moon screen's button control is in the motor calibration function.
def calibrate_moon_screen(display_controller):

    buffer = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(buffer)

    button_a = "Backward"
    button_b = "Done"
    button_x = "Forward" 
    
    draw.text((left_column_left_justification,top_row_height), button_a, font=default_font, fill=(255, 255, 255))
    draw.text((left_column_left_justification,bottom_row_height), button_b, font=default_font, fill=(0, 255, 0))
    draw.text((right_column_right_justification,top_row_height), button_x, font=default_font, fill=(255, 255, 255))
    draw.text((75,10), "Calibrating Moon", font=default_font, fill=(150, 150, 255))
    if display_controller == "calibration":
        display.display(buffer)
        print("Active display: Moon calibration")

def tide_display(display_controller, trend, next, afternext, progress, clock):     

    heading_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    clock_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58)
       
    screen = Image.open('images/tide_bg.png')
    tide = Image.open('images/water.png')
    
    # When the tide is receding we need the image to lower
    # When the tide is rising we need the image to raise
    # Tide receding: 1 = high tide, 0=low tide
    # Tide rising: 1=low tide, 0=high tide
    # Progress always goes down to 0
    if trend == "Tide Receding":
        screen.paste(tide, (0, int(260-(130*progress))))
    else:
        ## not right
        screen.paste(tide, (0, int(130+(130*progress))))
    
    draw = ImageDraw.Draw(screen)

    
    if (trend == "Tide Receding" and progress < 0.05) or (trend == "Rising Tide" and progress > 0.95):
        trend = "Low Tide"
        print("Low Tide Conditions.")
    elif (trend == "Tide Receding" and progress > 0.95) or (trend == "Rising Tide" and progress < 0.05):
        trend = "High Tide"
        print("High Tide Conditions.")

    draw.text((15, 15), trend, font=heading_font, fill=(255, 255, 255))
    draw.text((65, 130), clock, font=clock_font, fill=(255,255,255))
    draw.text((15, 210), next, font=default_font, fill=(255, 255, 255))
    draw.text((195, 210), afternext, font=default_font, fill=(255, 255, 255))
    
    if display_controller == "tide":
        display.display(screen)
        print("Active display: Tide")

def menu_display():
    pass


# reference this as well : https://github.com/pimoroni/displayhatmini-python/blob/main/examples/pygame-button-interrupt.py 

# TODO: Need at a minimum a tide display, a tide/moon swap, and a calibrate moon display. 

# TODO: Boot display for 30 seconds. 

# TODO: Main display is tide display

# TODO: Any button press brings up the menu, no other button press menu goes away

# TODO: Menu: Swap Displays (Tide to moon, moon to screen), Calibrate Moon Phase, Settings & Info, Back.

# def tide_display(high, low):
#     # TODO: Clock
#     # TODO: Tide display

# def settings():
#ipaddress = os.popen("ifconfig wlan0 \
#                      | grep 'inet' \
#                      | awk '{print $2}' \
#                      | awk 'NR==1{print $1}'").read()

# ssid = os.popen("iwconfig wlan0 \
#                 | grep 'ESSID' \
#                 | awk '{print $4}' \
#                 | awk -F\\\" '{print $2}'").read()
#