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

def imagedisplay():
    
    while True:
        screen = Image.open('low_tide.png')
        #screen = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(screen)
        draw.text((75,10), "tide", font=font, fill=(150, 150, 255))
        #draw.text((right_column_right_justification,bottom_row_height), button_y, font=font, fill=(255, 255, 255))
        display.display(screen)
            
imagedisplay()