import sqlite3
import requests
import json
import os
import time
import threading, queue
#from adafruit_motorkit import MotorKit

connection = sqlite3.connect("moons_and_tides.db")



latitude = 45.38988
longitude = -65.97948
motor_resolution = 45000

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

# Our moon class really only needs the name of the next phase and 
# the timestamp of that phase.
class Moon:
    def __init__(self, moon, timestamp, percent=None):
        self.moon = moon
        self.timestamp = timestamp
        self.percent = percent

    # Sorting logic
    def __eq__(self, other):
        return self.timestamp == other.timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp
    
    def set_percentage(self):
        # We might need a check here in case it's the first (current)
        # moon on boot
        if self.moon == "first_quarter":
            self.percent = 0.25
        elif self.moon == "full_moon":
            self.percent = 0.5
        elif self.moon == "last_quarter":
            self.percent = 0.75
        else:
            self.percent = 0

moons = []

# We need to get the current moon if we're loading up and put it at the front of the 
# list. 
moons.append(Moon(moon_data["moon"]["phase_name"], moon_data["timestamp"], float(moon_data["moon"]["phase"])))

# Here we iterate over the next moon phases to create an 
# object for each moon phase with a timestamp
for moon in moon_data["moon_phases"]:
    moon_phase = Moon(moon, moon_data["moon_phases"][moon]["next"]["timestamp"])
    moon_phase.set_percentage()
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
# We also want to set and store the absolute position.
def set_moon_mask_position(phase_percentage):
    position = phase_percentage * motor_resolution
    return int(position)

# We set the moon position to "Full Moon" when the application loads
# We will also use this for calibration
# TODO: calibration routine (led, hole in mask at back or something).
# Will also need to set a global calibration = true mode to prevent another function 
# from moving the motor
moon_position = set_moon_mask_position(0.5)

def moon_worker():
    while True:
        # if we don't have anything in our list, break 
        if len(moons_sorted) == 1:
            break

        if len(moons_sorted) == 2:
            # we want to trigger the API call at this point to replenish our queue
            # may want to do this at the end of each cycle, but perhaps a non-blocking thread?
            # IE spawn a new thread, or have a new separate threaded function for this. 
            pass

        # Getting some numbers to work with.
        # Could probably make this more elegant, but I think clarity works
        # for now. 
        timerange = moons_sorted[1].timestamp - moons_sorted[0].timestamp
        print("Timerange: "+str(timerange))
        # need to reset percent to where we actually are
        
        percent_to_next_phase = moons_sorted[1].percent - moons_sorted[0].percent
        print("Percent to next phase: "+str(percent_to_next_phase))

        steps_to_next_phase = round((motor_resolution/4) * percent_to_next_phase)
        print("Steps to next phase: "+str(steps_to_next_phase))

        time_per_step = int(timerange / steps_to_next_phase)
        print("Time per step: "+str(time_per_step))         
                 
        current_percent = moons_sorted[0].percent                         
        percent_per_step = percent_to_next_phase / steps_to_next_phase
        
        
        print()
        print(time_per_step)
        print(percent_per_step)
        current_time = int(time.time())
      

        while moons_sorted[1].timestamp > int(time.time()):
            next_step = int(current_time+time_per_step)
            print("Next step: "+str(next_step))
            print("Current time: "+str(time.time()))
            time.sleep(5)
            print("Sleeping.")
            if time.time() >= next_step:
                # motor increment by current percent
                moon_position = set_moon_mask_position(current_percent+percent_per_step)
                current_time = time.time()
                print("incrementing") 

        moons_sorted.pop(0)
        
moon_thread = threading.Thread(target=moon_worker)
moon_thread.start()



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

tide_list = []

# for tide in tide_data["extremes"]:
#     new_tide = Tide(tide["state"], tide["timestamp"], tide["height"])
#     tide_list.append(new_tide)
#     if len(tide_list) != 1:
#         current_index = len(tide_list)-1
#         tide_list[current_index-1].next_tide = tide_list[current_index]

# tide_queue = queue.Queue()

# def tide_worker():
#     while True
#         item = tide_queue.get()
#         # stuff
#         tide_queue.done()
        
# threading.Thread(target=tide_queue, daemon=True).start()

# tide_queue.join()