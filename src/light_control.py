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


def moonlight(brightness):
    light = tuple(math.ceil(x * brightness) for x in moon_white)
    pixels.fill(light)
    pixels.show()


def high_tide(level):
    # Low Tide
    color = tuple(math.ceil(x * pixel_brightness) for x in tide_blue)
    while level >= 0.98:
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
    moonlight(pixel_brightness)


def low_tide(level):
    # Low Tide
    color = tuple(math.ceil(x * pixel_brightness) for x in tide_blue)
    while level >= 0.98:
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
    moonlight(pixel_brightness)
