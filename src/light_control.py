import board
import neopixel
import apploader
import time

# moon_white = apploader.config["visuals"]["moon_white"]
moon_white = (3 , 200, 100)
tide_blue = (0,60,220)
pixel_brightness = 1

pixels = neopixel.NeoPixel(board.D18, 20, brightness=pixel_brightness)

def moonlight():
    # Reset lights they're being used for something else
    pixels.deinit()	
    pixels.fill(moon_white)


def tide(level, brightness):
    if level <= 0.25:
        for pixel in pixels[range(15,18)]:
            pixel = tide_blue
    elif level > 0.25 and level < 0.75:
        for pixel in pixels[range(9,18)]:
            pixel = tide_blue
    elif level >= 0.75 and level <= 0.9:
        for pixel in pixels[range(5,18)]:
            pixel = tide_blue
    else:
        for pixel in pixels[range(1,18)]:
            pixel = tide_blue
        

