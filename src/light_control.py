import board
import neopixel
import apploader
import time
import math


# moon_white = apploader.config["visuals"]["moon_white"]
num_pixels = int(apploader.config["visuals"]["neopixels_num"])
moon_white = (250, 140, 80)
tide_blue = (0, 80, 220)
off = (0, 0, 0)
pixel_brightness = float(apploader.config["visuals"]["neopixels_brightness"])

pixels = neopixel.NeoPixel(board.D18, num_pixels)


def moonlight():
    light = tuple(math.ceil(x * pixel_brightness) for x in moon_white)
    pixels.fill(light)
    pixels.show()


def high_tide(level):
    # Low Tide
    color = tuple(math.ceil(x * pixel_brightness) for x in tide_blue)
    while level > 0.95:
        for i in range(0, 101):
            fade_color = tuple(math.ceil(x * (i/100)) for x in color)
            for i in range(0, 8):
                pixels[i] = fade_color
            pixels.show
        for i in range(101, 0, -1):
            fade_color = tuple(math.ceil(x * (i/100)) for x in color)
            for i in range(0, 8):
                pixels[i] = fade_color
            pixels.show
        time.sleep(0.05)
    moonlight()


def low_tide(level):
    # Low Tide
    color = tuple(math.ceil(x * pixel_brightness) for x in tide_blue)
    while level < 0.05:
        for i in range(0, 101):
            fade_color = tuple(math.ceil(x * (i/100)) for x in color)
            for i in range(24, 32):
                pixels[i] = fade_color
            pixels.show
        for i in range(101, 0, -1):
            fade_color = tuple(math.ceil(x * (i/100)) for x in color)
            for i in range(24, 32):
                pixels[i] = fade_color
            pixels.show
        time.sleep(0.05)
    moonlight()


def tide_rising(screen_owner):
    # Rising tide: bottom to top (27→19→11→3)
    color = tuple(math.ceil(x * pixel_brightness) for x in tide_blue)
    pixels[3] = off
    pixels[4] = off
    pixels[11] = off
    pixels[12] = off
    pixels[19] = off
    pixels[20] = off
    pixels[27] = off
    pixels[28] = off

    while screen_owner.owner == "moon":
        for i in range(0, 101):
            if i < 25:
                fade_in = tuple(math.ceil(x * (i/25)) for x in color)
                pixels[27] = fade_in
                pixels[28] = fade_in
            elif i < 50:
                fade_out = tuple(math.ceil(x * ((25-(i-25))/25)) for x in color)
                pixels[27] = fade_out
                pixels[28] = fade_out
                fade_in = tuple(math.ceil(x * ((i-25)/25)) for x in color)
                pixels[19] = fade_in
                pixels[20] = fade_in
            elif i < 75:
                fade_out = tuple(math.ceil(x * ((25-(i-50))/25)) for x in color)
                pixels[19] = fade_out
                pixels[20] = fade_out
                fade_in = tuple(math.ceil(x * ((i-50)/25)) for x in color)
                pixels[11] = fade_in
                pixels[12] = fade_in
            else:  # i >= 75
                fade_out = tuple(math.ceil(x * ((25-(i-75))/25)) for x in color)
                pixels[11] = fade_out
                pixels[12] = fade_out
                fade_in = tuple(math.ceil(x * ((i-75)/25)) for x in color)
                pixels[3] = fade_in
                pixels[4] = fade_in
            pixels.show()
            time.sleep(0.05)
    moonlight()


def tide_receding(screen_owner):
    # Receding tide: top to bottom (3→11→19→27)
    color = tuple(math.ceil(x * pixel_brightness) for x in tide_blue)
    pixels[3] = off
    pixels[4] = off
    pixels[11] = off
    pixels[12] = off
    pixels[19] = off
    pixels[20] = off
    pixels[27] = off
    pixels[28] = off

    while screen_owner.owner == "moon":
        for i in range(0, 101):
            if i < 25:
                fade_in = tuple(math.ceil(x * (i/25)) for x in color)
                pixels[3] = fade_in
                pixels[4] = fade_in
            elif i < 50:
                fade_out = tuple(math.ceil(x * ((25-(i-25))/25)) for x in color)
                pixels[3] = fade_out
                pixels[4] = fade_out
                fade_in = tuple(math.ceil(x * ((i-25)/25)) for x in color)
                pixels[11] = fade_in
                pixels[12] = fade_in
            elif i < 75:
                fade_out = tuple(math.ceil(x * ((25-(i-50))/25)) for x in color)
                pixels[11] = fade_out
                pixels[12] = fade_out
                fade_in = tuple(math.ceil(x * ((i-50)/25)) for x in color)
                pixels[19] = fade_in
                pixels[20] = fade_in
            else:  # i >= 75
                fade_out = tuple(math.ceil(x * ((25-(i-75))/25)) for x in color)
                pixels[19] = fade_out
                pixels[20] = fade_out
                fade_in = tuple(math.ceil(x * ((i-75)/25)) for x in color)
                pixels[27] = fade_in
                pixels[28] = fade_in
            pixels.show()
            time.sleep(0.05)
    moonlight()
