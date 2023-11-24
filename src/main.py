import sqlite3
import requests
import json
import os
import time

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

#     moons_json_raw = requests.get(url, headers=headers, params=querystring)
    
#     return  json.loads(moons_json_raw.json())

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

#     tides_json_raw = requests.get(url, headers=headers, params=querystring)
    
#     return  json.loads(tides_json_raw.json())

# This replaces the request from the API for testing
# using a local file which matches the Moons API response.
with open('moon_sample.json') as user_file:
    moons_json_raw = user_file.read()

moon_data = json.loads(moons_json_raw)

cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS current_moon (phase REAL, timestamp TEXT)")

# Our moon class really on needs the name of the next phase and 
# the timestamp of that phase.
class Moon:
    def __init__(self, moon, timestamp):
        self.moon = moon
        self.timestamp = timestamp

    def __eq__(self, other):
        return self.timestamp == other.timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp

moons = []

# Here we iterate over the next moon phases to create an 
# object for each moon phase with a timestamp
for moon in moon_data["moon_phases"]:
    moon_phase = Moon(moon, moon_data["moon_phases"][moon]["next"]["timestamp"])
    moons.append(moon_phase)

# Here we sort them such that we create a list which will
# allow us to use the next moon, and, following that,
# retain a list of subsequent moons in case internet connectivity
# is limited. We should be able to remove items from the front of the 
# list when they're in the past
moons_sorted = sorted(moons)

## To Do Calculate time to next phase
## To Do Calculate daily number of steps for the motor

# This simple function takes the phase percentage and
# will calculate the number of motor steps to move the
# mask. The moto is a 200 step motor or 1.8 degrees per
# step. That gives us clear correlation with the four
# moon phases: new (0), first quarter (50 steps), etc. etc.
def set_moon_mask_position(phase_percentage):
    steps = 200
    position = phase * steps
    return int(position)

# Sanity check data structures and access
#########################################
# print("Current phase: "+str(moon_data["moon"]["phase"])) 
# print("Days until next new moon: "+str(moon_data["moon_phases"]["new_moon"]["next"]["days_ahead"]))
# print("Steps to set moon mask: "+str(set_mask_position(float(moon_data["moon"]["phase"]))))

# This replaces the request from the API for testing
# using a local file which matches the tides API response.
with open('current_tides.json') as user_file:
    tides_json_raw = user_file.read()
    
tide_data = json.loads(tides_json_raw)

cursor.execute("CREATE TABLE IF NOT EXISTS tides (tide TEXT, date TEXT, height REAL, timestamp INT)")

class Tide:
    def __init__(self, tide, timestamp, height, next_tide=None) -> None:
        self.tide = tide
        self.timestamp = timestamp
        self.height = height
        self.next_tide = next_tide

# tide_list = []

# for tide in tide_data["extremes"]:
#     new_tide = Tide(tide["state"], tide["timestamp"], tide["height"])
#     tide_list.append(new_tide)
#     if len(tide_list) != 1:
#         current_index = len(tide_list)-1
#         tide_list[current_index-1].next_tide = tide_list[current_index]