import board
import neopixel
import apploader

moon_white = apploader.config["visuals"]["moon_white"]
tide_blue = (0,60,220)
pixel_brightness = 0.5

pixels = neopixel.NeoPixel(board.D18, 20, brightness=pixel_brightness)

def moonlight(brightness):
    setpixelbrightness(brightness)
    pixels.fill((253,244,220))


def tide(level, brightness):
    setpixelbrightness(brightness)
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
    pixels.neopixel.NeoPixel(board.D18, 20, brightness=pixel_brightness)
    pixel_brightness = new_brightness
    
def soft_on(brightness):
    for 
    