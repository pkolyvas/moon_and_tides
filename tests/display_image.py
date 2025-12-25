#!/usr/bin/env python3
from ST7789 import ST7789, BG_SPI_CS_FRONT
from displayhatmini import DisplayHATMini
from PIL import Image, ImageDraw, ImageFont
import datetime 
import threading
import sys
import signal

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


# draw.rectangle((0, 0, 50, 50), (255, 0, 0))
# draw.rectangle((320-50, 0, 320, 50), (0, 255, 0))
# draw.rectangle((0, 240-50, 50, 240), (0, 0, 255))
# draw.rectangle((320-50, 240-50, 320, 240), (255, 255, 0))

# display = ST7789(
#     port=SPI_PORT,
#     cs=SPI_CS,
#     dc=SPI_DC,
#     backlight=BACKLIGHT,
#     width=WIDTH,
#     height=HEIGHT,
#     rotation=180,
#     spi_speed_hz=60 * 1000 * 1000
# )
width = DisplayHATMini.WIDTH
height = DisplayHATMini.HEIGHT
buffer = Image.new("RGB", (width, height))
display = DisplayHATMini(buffer)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)

active_text = "time"

def display_loop(active_text):
    while True:
        image = Image.open('low_tide.png')
        buffer.paste(image, (0,0))
        if active_text == "time":
            draw = ImageDraw.Draw(buffer)
            draw.text((75,10), datetime.datetime.now().strftime("%I:%M:%S %p"), font=font, fill=(150, 150, 255))
        else:
            draw = ImageDraw.Draw(buffer)
            draw.text((75,10), "Button X!", font=font, fill=(150, 150, 255))
        display.display()
        time.sleep(0.5)

def button_loop(active_text):
    while True:
        if display.read_button(display.BUTTON_A):
            active_text = "time"
        elif display.read_button(display.BUTTON_X):
            active_text = "x"
        time.sleep(0.05)


def cleanup(signum=None, frame=None):
    display.set_backlight(0)  # turn off backlight
    # optionally clear the display here
    sys.exit(0)

# Handle Ctrl+C and termination
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

try:
    display_thread = threading.Thread(target=display_loop, args=(active_text,))
    control_thread = threading.Thread(target=button_loop, args=(active_text,))
    display_thread.start()
    control_thread.start()
finally:
    cleanup()
