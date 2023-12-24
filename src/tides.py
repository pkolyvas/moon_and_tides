import requests
import apploader
import requests
import json
import time
import threading
from datetime import datetime
from ST7789 import ST7789, BG_SPI_CS_FRONT
from displayhatmini import DisplayHATMini
from PIL import Image, ImageDraw, ImageFont

# Tidal half period in seconds (low to high or high to low)
TIDAL_HALF_PERIOD = 22350

# Display initialization
display = ST7789(
    port=0,
    cs=1,
    dc=9,
    backlight=13,
    width=320,
    height=240,
    rotation=180,
    spi_speed_hz=60 * 1000 * 1000
)

display_hat = DisplayHATMini(None)
default_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)

# Configuration load
latitude = float(apploader.config['location']['latitude'])
longitude = float(apploader.config['location']['longitude'])

# Tide data request
def get_tide_data(latitude, longitude): 
    # if bool(apploader.config['DEFAULT']['offline']):
    #     print("-- OFFLINE MODE --")
    #     with open('current_tides.json') as user_file:
    #         raw_json_file = user_file.read()
    #         return json.loads(raw_json_file)

    url = apploader.config['apis']['marea_api_url']

    querystring = {
        "duration":"10080",
        "latitude":latitude,
        "longitude":longitude
        }

    headers = {
        "x-marea-api-token": apploader.config['apis']['marea_api_key'],
    }
    
    api_response = requests.get(url, headers=headers, params=querystring)
    tides_json_raw = api_response.json()
    
    return tides_json_raw
    
tide_data = get_tide_data(latitude, longitude)
##Debugging request
# print(tide_data)
# print(type(tide_data))

class Tide:
    def __init__(self, tide, timestamp, height, next_tide=None) -> None:
        self.tide = tide
        self.timestamp = timestamp
        self.height = height
        
    # Sorting logic
    def __eq__(self, other):
        return self.timestamp == other.timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp

tide_list = []

for tide in tide_data["extremes"]:
    new_tide = Tide(tide["state"], tide["timestamp"], tide["height"])
    tide_list.append(new_tide) 
    
tides_sorted = sorted(tide_list)
    
active_display = "tide"

def tide_worker():
    while True:
        # while moon_calibrated == False:
        #     time.sleep(1)
        
        tide_tod_clock = str(datetime.fromtimestamp(time.time()).strftime('%H:%M'))

        # TODO: pop-off the first element if it's in the past.

        tide_progress_remaining = (tides_sorted[0].timestamp - time.time()) / TIDAL_HALF_PERIOD

        if tides_sorted[0].tide == "HIGH TIDE":         
            tide_display_trend = "A Rising Tide"
            tide_display_next = "High: " + str(datetime.fromtimestamp(tides_sorted[0].timestamp).strftime('%H:%M'))
            tide_display_afternext = "Low: " +str(datetime.fromtimestamp(tides_sorted[1].timestamp).strftime('%H:%M'))
                    
        else:
            tide_display_trend = "Tide Receding"
            tide_display_next = "Low: " + str(datetime.fromtimestamp(tides_sorted[0].timestamp).strftime('%H:%M'))
            tide_display_afternext = "High: " + str(datetime.fromtimestamp(tides_sorted[1].timestamp).strftime('%H:%M'))
        
        tide_display(tide_display_trend, tide_display_next, tide_display_afternext, tide_progress_remaining, tide_tod_clock)
        print("Tide worker: Active")
        time.sleep(15)
        if time.time() > tides_sorted[0].timestamp:
            tides_sorted.pop(0)
            tides_in_queue = len(tides_sorted)
            if tides_in_queue <= 2:
                #TODO: Need to refresh tide list
                pass
            print(f"Updating tides list. {tides_in_queue} tides remaining in queue.")

def tide_display(trend, next, afternext, progress, clock):     

        heading_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        clock_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58)
        
        if trend == "Tide Receding":
            if progress <= 0.20: 
                tide_image = "images/low_tide.png"
            elif progress > 0.20 and progress <= 0.80:
                tide_image = "images/mid_tide.png"
            elif progress > 0.80:
                tide_image = "images/high_tide.png"
        else:
            if progress <= 0.20: 
                tide_image = "images/high_tide.png"
            elif progress > 0.20 and progress <= 0.80:
                tide_image = "images/mid_tide.png"
            elif progress > 0.80:
                tide_image = "images/low_tide.png"
            
        
        screen = Image.open(tide_image)
        draw = ImageDraw.Draw(screen)
        
        if (trend == "Tide Receding" and progress < 0.05) or (trend == "A Rising Tide" and progress > 0.95):
            trend = "Low Tide"
            print("Low Tide Conditions.")
        elif (trend == "Tide Receding" and progress > 0.95) or (trend == "A Rising Tide" and progress < 0.05):
            trend = "High Tide"
            print("High Tide Conditions.")

        draw.text((15, 15), trend, font=heading_font, fill=(255, 255, 255))
        draw.text((65, 130), clock, font=clock_font, fill=(255,255,255))
        draw.text((15, 210), next, font=default_font, fill=(255, 255, 255))
        draw.text((195, 210), afternext, font=default_font, fill=(255, 255, 255))
        
        if active_display == "tide":
            display.display(screen)
            print("Active display: Tide")

def menu_display():
    pass
        
tide_thread = threading.Thread(target=tide_worker)
tide_thread.start()