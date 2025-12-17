#!/usr/bin/env python3
from numpy.polynomial.tests.test_hermite_e import He0
from PIL.ImageChops import screen
from dev import motor_calibration
import logging
from ST7789 import ST7789, BG_SPI_CS_FRONT
from PIL import Image, ImageDraw, ImageFont
from displayhatmini import DisplayHATMini
import time
import motor_control

display_hat = DisplayHATMini(None)

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
def calibrate_moon_screen(display_controller):
    draw = ImageDraw.Draw(buffer)

    button_a = "Backward"
    button_b = "Done"
    button_x = "Forward"

    draw.text((left_column_left_justification, top_row_height),
              button_a, font=default_font, fill=(255, 255, 255))
    draw.text((left_column_left_justification, bottom_row_height),
              button_b, font=default_font, fill=(0, 255, 0))
    draw.text((right_column_right_justification, top_row_height),
              button_x, font=default_font, fill=(255, 255, 255))
    draw.text((75, 10), "Calibrating Moon",
              font=default_font, fill=(150, 150, 255))
    if display_controller == "calibration":
        display.display()
        logging.info("Active display: Moon calibration")


def tide_display(screen_owner, trend, next, afternext, progress, clock):
    if screen_owner.owner == "tides":
        heading_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        clock_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58)

        screen = Image.open('images/tide_bg.png')
        tide = Image.open('images/water.png')

        # When the tide is receding we need the image to lower
        # When the tide is rising we need the image to raise
        # Tide receding: 1 = high tide, 0=low tide
        # Tide rising: 1=low tide, 0=high tide
        # Progress always goes down to 0
        if trend == "Tide Receding":
            screen.paste(tide, (0, int(245 - (111 * progress))))
        else:
            screen.paste(tide, (0, int(134 + (111 * progress))))

        draw = ImageDraw.Draw(screen)

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
        logging.info("Active display: Tide")


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


def check_display_owner():
    pass


def button_worker(screen_owner):
    while True:
        if (screen_owner.owner == "tides") and (
                display_hat.read_button(display_hat.BUTTON_A) or
                display_hat.read_button(display_hat.BUTTON_A) or
                display_hat.read_button(display_hat.BUTTON_X) or
                display_hat.read_button(display_hat.BUTTON_Y)
        ):
            screen_owner.update_owner("menu")
        elif screen_owner.owner == "calibration":
            motor_control.motor_calibration(screen_owner)
        elif screen_owner.owner == "menu":
            if display_hat.read_button(display_hat.BUTTON_A):
                screen_owner.update_owner("tides")
            if display_hat.read_button(display_hat.BUTTON_B):
                screen_owner.update_owner("moon")
            if display_hat.read_button(display_hat.BUTTON_X):
                screen_owner.update_owner("calibration")
            if display_hat.read_button(display_hat.BUTTON_Y):
                screen_owner.update_owner("system")
        elif screen_owner.owner == "moon" and (
                display_hat.read_button(display_hat.BUTTON_A) or
                display_hat.read_button(display_hat.BUTTON_A) or
                display_hat.read_button(display_hat.BUTTON_X) or
                display_hat.read_button(display_hat.BUTTON_Y)
        ):
            screen_owner.update_owner("menu")
        time.sleep(0.05)


def display_worker(screen_owner):
    while True:
        if screen_owner.owner == "tides":
            pass
        elif screen_owner.owner == "moon":
            pass
        elif screen_owner.owner == "calibration":
            calibrate_moon_screen(display)
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
