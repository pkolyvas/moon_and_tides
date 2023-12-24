import requests
import apploader
import requests
import json
import time
import threading
from datetime import datetime

latitude = float(apploader.config['location']['latitude'])
longitude = float(apploader.config['location']['longitude'])

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
tide_display_trend = ""
tide_display_next = ""
tide_display_afternext = ""
tide_progress = None

def tide_worker():
    while True:
        # while moon_calibrated == False:
        #     time.sleep(1)
        
        clock = datetime.fromtimestamp(time.time())

        # TODO: pop-off the first element if it's in the past.

        if tides_sorted[0].tide == "HIGH TIDE":         
            tide_display_trend = "A Rising Tide"
            tide_display_next = "High tide will be at " + str(datetime.fromtimestamp(tides_sorted[0].timestamp).strftime('%H:%M'))
            tide_display_afternext = "Low tide will be at " +str(datetime.fromtimestamp(tides_sorted[1].timestamp).strftime('%H:%M'))
            # TODO: Calculate progress to next tide phase based on time remaining to phase and average tide phase time
            #tide_progress = 
        else:
            tide_display_trend = "Tide Receding"
            tide_display_next = "Low tide will be at " + str(datetime.fromtimestamp(tides_sorted[0].timestamp).strftime('%H:%M'))
            tide_display_afternext = "High tide will be at " + str(datetime.fromtimestamp(tides_sorted[1].timestamp).strftime('%H:%M'))
            # TODO: Calculate progress to next tide phase based on time remaining to phase and average tide phase time
            #tide_progress = 

        time.sleep(15)

def tide_display():
    pass

def menu_display():
    pass
     
        
tide_thread = threading.Thread(target=tide_worker)
tide_thread.start()