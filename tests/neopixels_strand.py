import board
import neopixel
import time
import random

pixels = neopixel.NeoPixel(board.D18, 20)

def setpixels():
	pixels[random.randrange(0,19,1)] = (random.randrange(0,255, 5), random.randrange(0,255,5), random.randrange(0,255,5))
	pixels[1] = (25,20,20)
	pixels[2] = (110,0,100)
	pixels.show()
setpixels()
time.sleep(2)
setpixels()
time.sleep(2)
setpixels()
time.sleep(2)
pixels.deinit()	
