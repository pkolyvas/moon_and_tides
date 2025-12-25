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
pixel_brightness = 1

pixels = neopixel.NeoPixel(board.D18, num_pixels)


def moonlight():
    # Reset lights they're being used for something else
    pixels.fill(moon_white)
    pixels.show()


def tide(level, brightness):
    # Low Tide
    color = tuple(x * brightness for x in tide_blue)
    if level <= 0.05:
        for i in range(0, 32):
            pixels[i] = off
    elif level > 0.05 and level <= 0.25:
        for i in range(27, 29):
            light = tuple(math.ceil(x * (level * 100 / 25)) for x in color)
            pixels[i] = light
        for i in range(0, 24):
            pixels[i] = off
    elif level > 0.25 and level <= 0.50:
        for i in range(27, 29):
            pixels[i] = color
        for i in range(19, 21):
            light = tuple(math.ceil(x * (level - 0.25) * 100 / 25) for x in color)
            pixels[i] = light
        for i in range(0, 16):
            pixels[i] = off
    elif level >= 0.50 and level <= 0.8:
        for i in range(27, 29):
            pixels[i] = color
        for i in range(19, 21):
            pixels[i] = color
        for i in range(11, 13):
            light = tuple(math.ceil(x * ((level - 0.5) * 100 / 30)) for x in color)
            pixels[i] = light
        for i in range(0, 8):
            pixels[i] = off
    else:
        for i in range(27, 29):
            pixels[i] = color
        for i in range(19, 21):
            pixels[i] = color
        for i in range(11, 13):
            pixels[i] = color
        for i in range(3, 5):
            light = tuple(math.ceil(x * ((level - 0.80) * 100 / 20)) for x in color)
            pixels[i] = light
    pixels.show

