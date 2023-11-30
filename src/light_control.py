import board
import neopixel
import apploader
import time

# moon_white = apploader.config["visuals"]["moon_white"]
moon_white = (253, 220, 160)
tide_blue = (0,60,220)
pixel_brightness = 1

pixels = neopixel.NeoPixel(board.D18, 20, brightness=pixel_brightness)

def moonlight(brightness):
    color = moon_white
    #moon_color = [int(number) for number in color]
    moon_color = color
    soft_on(brightness, moon_color)


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
        
def setpixelbrightness(new_brightness):
    pixels.deinit()
    pixels= neopixel.NeoPixel(board.D18, 20, brightness=pixel_brightness)
    pixel_brightness = new_brightness
    
def soft_on(brightness, color):
    current_brightness = 0.0
    while current_brightness < brightness:
        if current_brightness != 0:
          pixels.deinit()
        current_brightness += 0.05
        pixels = neopixel.NeoPixel(board.D18, 20, brightness=current_brightness)
        pixels.fill(color)
        time.sleep(0.05)
        
moonlight(1)

sleep(5)

