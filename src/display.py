#!/usr/bin/env python3
from ST7789 import ST7789, BG_SPI_CS_FRONT
from displayhatmini import DisplayHATMini
from PIL import Image, ImageDraw, ImageFont

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

buffer = Image.new("RGB", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(buffer)

# draw.rectangle((0, 0, 50, 50), (255, 0, 0))
# draw.rectangle((320-50, 0, 320, 50), (0, 255, 0))
# draw.rectangle((0, 240-50, 50, 240), (0, 0, 255))
# draw.rectangle((320-50, 240-50, 320, 240), (255, 255, 0))


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

display_hat = DisplayHATMini(None)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
top_row_height = 63
left_column_left_justification = 10
bottom_row_height = 153
right_column_right_justification = 250

# The Calibrating Moon screen's button control is in the motor calibration function.
def calibrate_moon_screen():
    button_a = "Backward"
    button_b = "Forward"
    button_x = "Done"
    #button_y = "Back"   

    while True:
        draw.text((left_column_left_justification,top_row_height), button_a, font=font, fill=(255, 255, 255))
        draw.text((left_column_left_justification,bottom_row_height), button_b, font=font, fill=(255, 255, 255))
        draw.text((right_column_right_justification,top_row_height), button_x, font=font, fill=(0, 255, 0))
        draw.text((75,10), "Calibrating Moon", font=font, fill=(150, 150, 255))
        #draw.text((right_column_right_justification,bottom_row_height), button_y, font=font, fill=(255, 255, 255))
        display.display(buffer)

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

# Screens:
# Moon display
# Tide display
# Menu Screen (toggled by any button)
# Info