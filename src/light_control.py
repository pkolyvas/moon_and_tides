import board
import neopixel
import apploader
import time


# moon_white = apploader.config["visuals"]["moon_white"]
num_pixels = int(apploader.config["visuals"]["neopixels_num"])
moon_white = (250, 140, 80)
tide_blue = (0, 60, 220)
off = (0, 0, 0)
pixel_brightness = 1

pixels = neopixel.NeoPixel(board.D18, num_pixels)


def moonlight():
    # Reset lights they're being used for something else
    pixels.fill(moon_white)
    pixels.show()


def tide(level, brightness):
    # Low Tide
    if level <= 0.5:
        for i in range(1, 32):
            pixels[i] = off
    elif level > 0.5 and level <= 0.25:
        for i in range(25, 32):
            pixels[i] = tide_blue
        for i in range(1, 24):
            pixels[i] = off
    elif level > 0.25 and level < 0.75:
        for i in range(17, 32):
            pixels[i] = tide_blue
        for i in range(1, 16):
            pixels[i] = off
    elif level >= 0.75 and level <= 0.9:
        for i in range(9, 32):
            pixels[i] = tide_blue
        for i in range(1, 8):
            pixels[i] = off
    else:
        for i in range(1, 32):
            pixels[i] = tide_blue
    pixels.show
