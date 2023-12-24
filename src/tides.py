import requests
import apploader
import requests
import json
import time
import threading
from datetime import datetime

latitude = float(apploader.config['location']['latitude'])
longitude = float(apploader.config['location']['longitude'])
tide_correction = int(apploader.config['location']['correction'])

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

def tide_worker():
    while True:

        clock = datetime.fromtimestamp(time.time())

        print(clock.strftime("%H:%M"))

        if tides_sorted[0].tide == "HIGH TIDE":
            print("Rising Tide.")
            print(f"High tide is at {datetime.fromtimestamp(tides_sorted[0].timestamp-tide_correction).strftime('%H:%M')}. High tide will be {tides_sorted[0].height}m above sea level.")
            print(f"Next low tide is at {datetime.fromtimestamp(tides_sorted[1].timestamp-tide_correction).strftime('%H:%M')}")

        else:
            print("Tide Receding")
            print(f"Low tide is at {datetime.fromtimestamp(tides_sorted[0].timestamp-tide_correction).strftime('%H:%M')}. Low tide will be {tides_sorted[0].height}m below sea level.")
            print(f"Next high tide is at {datetime.fromtimestamp(tides_sorted[1].timestamp-tide_correction).strftime('%H:%M')}")

        time.sleep(15)