#!/usr/bin/env python3
import moon
from PIL.ImageChops import screen
import logging
from ST7789 import ST7789, BG_SPI_CS_FRONT
from PIL import Image, ImageDraw, ImageFont
from displayhatmini import DisplayHATMini
import time
import motor_control
from typing import Optional

#display = DisplayHATMini(None)

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

display: Optional[DisplayHATMini] = None
buffer = Image.new("RGB", (WIDTH, HEIGHT))


def init_display():
    global display, buffer
    width = DisplayHATMini.WIDTH
    height = DisplayHATMini.HEIGHT
    buffer = Image.new("RGB", (width, height))
    display = DisplayHATMini(buffer)

default_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
top_row_height = 63
left_column_left_justification = 10
bottom_row_height = 153
right_column_right_justification = 220


class Screen:
    def __init__(self) -> None:
        self.owner = "calibration"

    def update_owner(self, new_owner):
        self.owner = new_owner


# The Calibrating Moon screen's button control is in the motor calibration
# function.
def calibrate_moon_screen(screen_owner):
    if screen_owner.owner == "calibration":
        draw = ImageDraw.Draw(buffer)

        button_a = "Backward"
        button_b = "Moon Mode"
        button_x = "Forward"
        button_y = "Tide Mode"

        draw.text((left_column_left_justification, top_row_height),
                  button_a, font=default_font, fill=(255, 255, 255))
        draw.text((left_column_left_justification, bottom_row_height),
                  button_b, font=default_font, fill=(0, 255, 0))
        draw.text((right_column_right_justification, top_row_height),
                  button_x, font=default_font, fill=(255, 255, 255))
        draw.text((right_column_right_justification, bottom_row_height),
                  button_y, font=default_font, fill=(255, 255, 255))
        draw.text((75, 10), "Calibrating Moon",
                  font=default_font, fill=(150, 150, 255))
        display.display()


def tide_display(screen_owner, trend, next, afternext, progress, clock):
    if screen_owner.owner == "tides":
        heading_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        clock_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58)

        buffer = Image.open('images/tide_bg.png')
        tide = Image.open('images/water.png')

        # When the tide is receding we need the image to lower
        # When the tide is rising we need the image to raise
        # Tide receding: 1 = high tide, 0=low tide
        # Tide rising: 1=low tide, 0=high tide
        # Progress always goes down to 0
        if trend == "Tide Receding":
            buffer.paste(tide, (0, int(245 - (111 * progress))))
        else:
            buffer.paste(tide, (0, int(134 + (111 * progress))))

        draw = ImageDraw.Draw(buffer)

        if (trend == "Tide Receding" and progress < 0.05) or (
                trend == "Rising Tide" and progress > 0.95):
            trend = "Low Tide"
            logging.info("Low Tide Conditions.")
        elif (trend == "Tide Receding" and progress > 0.95) or (trend == "Rising Tide" and progress < 0.05):
            trend = "High Tide"
            logging.info("High Tide Conditions.")

        draw.text((15, 15), trend, font=heading_font, fill=(255, 255, 255))
        draw.text((65, 130), clock, font=clock_font, fill=(255, 255, 255))
        draw.text((15, 210), next, font=default_font, fill=(255, 255, 255))
        draw.text((195, 210), afternext, font=default_font, fill=(255, 255, 255))

        display.display()


def moon_display(screen_owner, moons_sorted, full_moon):
    heading_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
    detail_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    if screen_owner.owner == "moon":
        if moons_sorted[0].percent < 0.02 or moons_sorted[0].percent > 0.98:
            pass
        elif moons_sorted.percent <= 0.175:
            screen = Image.open('images/waxing_crescent.png')
            phase_name = "Waxing Crescent"
        elif moons_sorted.percent <= 0.30:
            screen = Image.open('images/first_quarter.png')
            phase_name = "First Quarter"
        elif moons_sorted.percent <= 0.49:
            screen = Image.open('images/waxing_gibbous.png')
            phase_name = "Waxing Gibbous"
        elif moons_sorted.percent < 0.52:
            screen = Image.open('images/full_moon.png')
            phase_name = "Full Moon"
        elif moons_sorted.percent >= 0.52:
            screen = Image.open('images/waning_gibbous.png')
            phase_name = "Waning Gibbous"
        elif moons_sorted.percent >= 0.67:
            screen = Image.open('images/third_quarter.png')
            phase_name = "Third Quarter"
        elif moons_sorted.percent >= 0.825:
            screen = Image.open('images/waxing_crescent.png')
            phase_name = "Waning Cresent"
        draw = ImageDraw.Draw(screen)

        next_full_moon = f"{full_moon.name} on {full_moon.date}"
        if moons_sorted[0].percent > 0.49 or moons_sorted[0].percent < 0.52:
            draw.text((190, 140), full_moon.name, font=heading_font, fill=(255, 255, 255))
        else: 
            draw.text((190, 140), phase_name, font=heading_font, fill=(255,255, 255))
            draw.text((220, 100), next_full_moon, font=detail_font, fill=(255, 255, 255))
        display.display()


def menu_display(screen_owner):
    if screen_owner.owner == "menu":
        button_a = "Tides on screen"
        button_b = "Tides in the moon"
        button_x = "Re-calibrate moon"
        button_y = "View system details"
        draw = ImageDraw.Draw(buffer)
        draw.text(
            (left_column_left_justification, top_row_height),
            button_a,
            font=default_font,
            fill=(255, 255, 255)
        )
        draw.text(
            (left_column_left_justification, bottom_row_height),
            button_b,
            font=default_font,
            fill=(0, 255, 0)
        )
        draw.text(
            (right_column_right_justification, top_row_height),
            button_x,
            font=default_font,
            fill=(255, 255, 255)
        )
        draw.text(
            (right_column_right_justification, bottom_row_height),
            button_y,
            font=default_font,
            fill=(255, 255, 255)
        )
        display.display()


def button_worker(screen_owner, current_moon):
    old_screen_owner = "calibration"
    while True:
        if screen_owner.owner != old_screen_owner:
            logging.info(f"Screen owner change: {screen_owner.owner}")
            old_screen_owner = screen_owner.owner
        if (screen_owner.owner == "tides") and (
                display.read_button(display.BUTTON_A) or
                display.read_button(display.BUTTON_A) or
                display.read_button(display.BUTTON_X) or
                display.read_button(display.BUTTON_Y)
        ):
            screen_owner.update_owner("menu")
        elif screen_owner.owner == "calibration":
            if display.read_button(display.BUTTON_A):
                motor_control.simple_clockwise()
            if display.read_button(display.BUTTON_X):
                motor_control.simple_anti_clockwise()
            if display.read_button(display.BUTTON_B):
                screen_owner.update_owner("tides")
        elif screen_owner.owner == "menu":
            if display.read_button(display.BUTTON_A):
                screen_owner.update_owner("tides")
            if display.read_button(display.BUTTON_B):
                screen_owner.update_owner("moon")
            if display.read_button(display.BUTTON_X):
                screen_owner.update_owner("calibration")
            if display.read_button(display.BUTTON_Y):
                screen_owner.update_owner("system")
        elif screen_owner.owner == "moon" and (
                display.read_button(display.BUTTON_A) or
                display.read_button(display.BUTTON_A) or
                display.read_button(display.BUTTON_X) or
                display.read_button(display.BUTTON_Y)
        ):
            screen_owner.update_owner("menu")
        time.sleep(0.05)


def display_worker(screen_owner):
    logging.debug(f"Screen owner {screen_owner.owner}")
    while True:
        if screen_owner.owner == "tides":
            pass
        elif screen_owner.owner == "moon":
            pass
        elif screen_owner.owner == "calibration":
            calibrate_moon_screen(screen_owner)
        elif screen_owner.owner == "menu":
            menu_display(screen_owner)
        time.sleep(0.5)




# reference this as well :
# https://github.com/pimoroni/displayhatmini-python/blob/main/examples/pygame-button-interrupt.py

# TODO: Need at a minimum a tide display, a tide/moon swap, and a
# calibrate moon display.

# TODO: Boot display for 30 seconds.

# TODO: Main display is tide display

# TODO: Any button press brings up the menu, no other button press menu
# goes away

# TODO: Menu: Swap Displays (Tide to moon, moon to screen), Calibrate Moon
# Phase, Settings & Info, Back.

# def tide_display(high, low):
#     # TODO: Clock
#     # TODO: Tide display

# def settings():
# ipaddress = os.popen("ifconfig wlan0 \
#                      | grep 'inet' \
#                      | awk '{print $2}' \
#                      | awk 'NR==1{print $1}'").read()

# ssid = os.popen("iwconfig wlan0 \
#                 | grep 'ESSID' \
#                 | awk '{print $4}' \
#                 | awk -F\\\" '{print $2}'").read()
#
