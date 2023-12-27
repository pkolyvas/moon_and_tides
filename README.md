# Moon and Tides 

A RPi Zero & 3D printed project. 

![IMG_1253](https://github.com/pkolyvas/moon_and_tides/assets/43178667/b17be359-96a7-4a00-8a7c-f6911aabca4a)


Eventually, you'll find the code, 3D models, and instructions for building. For now, it's just the code.


## Requirements
- RPi with the appropriate hats listed in the hardware section.
- A python environment run as root (on the RPi some of the libraries require root for hardware access.)
- API Keys to the APIs I've used here. They are not free. They will at least require registration, at most cost a few bucks.
  - [Marea Tides API](https://api.marea.ooo/doc/v2#overview). This one is about $4 USD for 10,000 requests. I expect my credits to last longer than the API is available. There are likely free sources to explore over time.
  - [Moon Phase](https://rapidapi.com/user/MoonAPIcom). This one is free at 500/requests a month. Each single request contains about a month's worth of data. 

## Hardware
This is a list of hardware used in this project. Feel free to experiment and expand. 
- [Raspberry Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
- [Adafruit DC & Stepper Motor HAT](https://www.adafruit.com/product/2348)
- [Pimoroni miniDisplay HAT](https://shop.pimoroni.com/products/display-hat-mini?variant=39496084717651)
- Adafruit Neopixels. See the section on lights below.
- [TI 74AHCT125 Level Converter IC](https://www.pishop.ca/product/74ahct125-quad-level-shifter-3v-to-5v-74ahct125/)
- A minimum 5V, 4A power supply. We use one supply for the whole project.

## Installation Instructions

### Hardware
[TODO]

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
Note: if you want to modify this project on hardware other than a Raspberry Pi, you can install the `dev` requirmments. `pip3 install -r dev_requirments.txt`

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

## Todo
- Build a function to switch between moon and tide in the globe
- Build a menu to recalibrate the moon
- Implement better logging
- Multiple networks: https://raspberrypi.stackexchange.com/questions/11631/how-to-setup-multiple-wifi-networks
