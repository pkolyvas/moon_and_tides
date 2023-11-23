import sqlite3
import requests
import json
import os

connection = sqlite3.connect("moons_and_tides.db")

#from adafruit_motorkit import MotorKit

latitude = 45.38988
longitude = -65.97948

# def get_moon_data(latitude, longitude):

#     url = "https://moon-phase.p.rapidapi.com/advanced"

#     querystring = {
#        "lat":str(latitude),
#        "lon":str(longitude)
#        }

#     headers = {
#         "X-RapidAPI-Key": os.environ.get('RAPIDAPI_KEY'),
#         "X-RapidAPI-Host": "moon-phase.p.rapidapi.com"
#     }

#     response = requests.get(url, headers=headers, params=querystring)
    
#     return  json.loads(response.json())

# def get_tide_data(latitude, longitude):

#     url = "https://api.marea.ooo/v2/tides"

#     querystring = {
#         "duration":"1440",
#         "latitude":latitude,
#         "longitude":longitude
#         }

#     headers = {
#         "x-marea-api-token": os.environ.get('MAREA_API_TOKEN'),
#     }

#     response = requests.get(url, headers=headers, params=querystring)
    
#     with open('current_tides.json', 'w') as json_file:
#         json.dump(response.json(), json_file )
    
#     return  json.loads(response.json())

with open('moon_sample.json') as user_file:
    moons = user_file.read()

moon_data = json.loads(moons)

cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS current_moon (phase REAL, timestamp TEXT)")


def set_mask_position(phase):
    steps = 200
    position = phase * steps
    return int(position)

print("Current phase: "+str(moon_data["moon"]["phase"])) 
print("Days until next new moon: "+str(moon_data["moon_phases"]["new_moon"]["next"]["days_ahead"]))
print("Steps to set moon mask: "+str(set_mask_position(float(moon_data["moon"]["phase"]))))

with open('current_tides.json') as user_file:
    tides = user_file.read()
    
tide_data = json.loads(tides)

cursor.execute("CREATE TABLE IF NOT EXISTS tides (tide TEXT, date TEXT, height REAL, timestamp INT)")

class Tide:
    def __init__(self, tide, timestamp, height, next_tide=None) -> None:
        self.tide = tide
        self.timestamp = timestamp
        self.height = height
        self.next_tide = next_tide
        
    def status(self):
        if self.tide == "HIGH TIDE":
            return "Decreasing"
        else:
            return "Increasing"



print("Currently the tide is "+tidestatus())

print(tide_data["extremes"][0]["state"])
# current_tide_level = 
# high_tide_time =
# low_tide_time = 

