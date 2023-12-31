# Moon and Tides 

A RPi Zero & 3D printed project. 

![IMG_1253](https://github.com/pkolyvas/moon_and_tides/assets/43178667/b17be359-96a7-4a00-8a7c-f6911aabca4a)

Eventually, you'll find the code, 3D models, and instructions for building. For now, it's just the code.

## Features
- Display shows the tide level (graphic)
- Display shows the next low tide, next high tide, and tide trend
- Moon has a light inside and a motorized mask to occlude the light and approximate what the moon would look like from where you are.

----

## Requirements
- RPi with the appropriate hats listed in the hardware section.
- A python environment run as root (on the RPi some of the libraries require root for hardware access.)
- API Keys to the APIs I've used here. They are not free. They will at least require registration, at most cost a few bucks.
  - [Marea Tides API](https://api.marea.ooo/doc/v2#overview). This one is about $4 USD for 10,000 requests. I expect my credits to last longer than the API is available. There are likely free sources to explore over time.
  - [Moon Phase](https://rapidapi.com/user/MoonAPIcom). This one is free at 500/requests a month. Each single request contains about a month's worth of data. 

----

## Hardware
This is a list of hardware used in this project. Feel free to experiment and expand. 
- [Raspberry Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
- [Adafruit DC & Stepper Motor HAT](https://www.adafruit.com/product/2348)
- [Pimoroni miniDisplay HAT](https://shop.pimoroni.com/products/display-hat-mini?variant=39496084717651)
- Adafruit Neopixels. [See the section on lights below](https://github.com/pkolyvas/moon_and_tides#neopixels).
- [TI 74AHCT125 Level Converter IC](https://www.pishop.ca/product/74ahct125-quad-level-shifter-3v-to-5v-74ahct125/)
- A minimum 5V, 4A power supply. We use one supply for the whole project.

----

## Installation & Build Instructions

### Hardware
So, uh, I didn't really take photos while assembling. The TLDR is that you stack the stepper motor HAT on top of the Pi Zero 2 W (with headers installed) — you'll also want a stacking header with long pins that will allow the display to be installed on top of the motor header. 

Then you can wire a 5v 4A + power supply into the 5v rail and ground along the right side of the HAT. From there you can solder the TI level converter chip onto the little breadboard and follow the wiring instructions linked in the Neopixels section below. 

You'll also need to wire the 5v rail and ground into the motor power inputs. The board documentation recommends a *separate* power supply for the motor, but we're using it so lightly I ignored that advice. 5v 4A is enough to run the Pi, the motor, the neopixels (tested with up to 20, though I'm only using 10), and the miniDisplay HAT. 

Oh, and yeah, just install the minidisplay Hat on top of the stack. That's about it.

#### Neopixels

I used Adafruit Neopixels for this project because, well, I didn't have any experience, wasn't sure what I wanted and there was limited stock. I wanted something that was flexible for this project since I was winging it with the initial design. The Neopixels offer a lot of flexibility. They also were a very easy to implement solution. 

This reference page from Adafruit is incredibly helpful: [NeoPixels on Raspberry Pi](https://learn.adafruit.com/neopixels-on-raspberry-pi/overview)

### Software

Clone the repository. If you're not sure how to do that, [see here](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository). 

Create and activate a virtual python environment:
```shell
cd moon_and_tides/src/
python3 -m venv env_myenv
source env_myenv/bin/activate
```

Install the required libraries/modules:
```shell
pip3 install -r requirements.txt
```

*Note: if you want to modify this project on hardware other than a Raspberry Pi, you can install the `dev` requirements. `pip3 install -r dev_requirments.txt`*

Configure the app by copying the `app.conf.default` to `app.conf` and editing the file with your Latitude and Logitude, and API keys. Set `dev` to `1` if you'd like to modify the code without RPi hardware present.
```shell
cp app.conf.default app.conf
nano app.conf
```

Run the program:
```
python3 main.py
```


### Enclosure
[TODO]

----

## Todo
- Build a function to switch between moon and tide in the globe
- Build a menu to recalibrate the moon
- Multiple networks: https://raspberrypi.stackexchange.com/questions/11631/how-to-setup-multiple-wifi-networks
