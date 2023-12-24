import sqlite3
import requests
import json
import os
import time
import threading
import motor_control
import light_control
import display
import tides
from urllib.parse import urlparse
import apploader
# import tides

connection = sqlite3.connect(apploader.config['db']['sqlite3_db'])
latitude = float(apploader.config['location']['latitude'])
longitude = float(apploader.config['location']['longitude'])
motor_resolution = int(apploader.config['motor']['resolution'])
tide_correction = int(apploader.config['location']['correction'])

def get_moon_data(latitude, longitude):
    # if bool(apploader.config['DEFAULT']['offline']):
    #     print("-- OFFLINE MODE --")
    #     with open('current_tides.json') as user_file:
    #         moon_file_json_raw = user_file.read()
    #         return json.loads(moon_file_json_raw)

    url = "https://moon-phase.p.rapidapi.com/advanced"

    querystring = {
       "lat":str(latitude),
       "lon":str(longitude)
       }

    headers = {
        "X-RapidAPI-Key": apploader.config['apis']['moon_api_key'],
        "X-RapidAPI-Host": "moon-phase.p.rapidapi.com"
    }

    api_response = requests.get(url, headers=headers, params=querystring)
    moons_json_raw = api_response.json()
    
    return  moons_json_raw

# with open('moon_sample.json') as user_file:
#     moons_json_raw = user_file.read()

# moon_data = json.loads(moons_json_raw)
print("Getting moon data.")
moon_data = get_moon_data(latitude, longitude)

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

# This simple function takes the phase percentage and
# will calculate the number of motor steps to move the
# mask. The moto is a 200 step motor or 1.8 degrees per
# step. That gives us clear correlation with the four
# moon phases: new (0), first quarter (50 steps), etc. etc.
# We also want to set and store the absolute position.
def set_moon_mask_position(phase_percentage):  
    position = phase_percentage * motor_resolution
    return int(position)

def moon_worker():
    # Start moonlight and calibrate moon on start
    light_control.moonlight()
    requested_screen = "calibration"
    motor_control.motor_calibration()
    requested_screen = "tides"

    # Moon position is 0 after calibration
    # We set motor position to compare
    moon_position = 0
    motor_position = 0

    # Toggle for first run
    first_load = True

    # Enter thread's main loop
    while True:
        # if we don't have anything in our list, break 
        if len(moons_sorted) == 1:
            break
        
        # Update list if second element is now in the past
        # by removing the first element.
        if moons_sorted[1].timestamp <= time.time():
            moons_sorted.pop(0)
            print("Outdated entry removed")

        if len(moons_sorted) == 2:
            # we want to trigger the API call at this point to replenish our queue
            # may want to do this at the end of each cycle, but perhaps a non-blocking thread?
            # IE spawn a new thread, or have a new separate threaded function for this. 
            pass
        
        # This should give us the number of seconds between "known" quarter phases.
        # Quarter phases are returned from the API.
        timerange = moons_sorted[1].timestamp - moons_sorted[0].timestamp
        print("Timerange: "+str(timerange)) 
        
         # We need to update the percent of the phase on load.
        time_delta_to_now = time.time()-moons_sorted[0].timestamp # gives us the seconds since stored phase start time
        remaining_percent_of_current_phase = (timerange - time_delta_to_now) / timerange # gives us the percent remaining of the current phase
        percent_to_next_phase = (moons_sorted[1].percent - moons_sorted[0].percent)*(remaining_percent_of_current_phase)
        print(f"Time delta: {time_delta_to_now}")
        print(f"Remaining percent of current phase: {remaining_percent_of_current_phase}")
        print("Percent to next phase: "+str(percent_to_next_phase))

        steps_to_next_phase = round(motor_resolution * percent_to_next_phase)
        print("Steps to next phase: "+str(steps_to_next_phase))

        time_per_step = int(timerange / steps_to_next_phase)
        print("Time per step: "+str(time_per_step))                 
                
        percent_per_step = percent_to_next_phase / steps_to_next_phase
        print("Percent per step: "+str(percent_per_step))        
        
        # Update percent
        moons_sorted[0].percent = moons_sorted[0].percent + (time_delta_to_now/timerange)
        current_percent = moons_sorted[0].percent
        print("Current percent: "+str(current_percent))
        moon_position = set_moon_mask_position(current_percent)
        
        # If it's first load we need to set the position based on the calibrated full moon.
        if first_load == True:
            print(f"First Load. Moving mask to {moon_position}.")
            for i in range(moon_position):
                motor_control.simple_backward()
            motor_position = moon_position
        # If we're moving through the loop and the system is calibrated, we want to correct any error
        else:
            if moon_position > motor_position:
                print("Motor behind. Fixing.")
                delta = moon_position - motor_position
                for i in range(delta):
                    motor_control.simple_backward()
                motor_position = moon_position
            if moon_position < motor_position:
                print("Motor ahead. Fixing.")
                delta = motor_position - moon_position
                for i in range(delta):
                    motor_control.simple_forward()

        current_time = int(time.time())
        print("Current time: "+str(current_time))
      
        while moons_sorted[1].timestamp > int(time.time()):
            next_step = int(current_time+time_per_step)
            print("Next step: "+str(next_step))
            print("Current time: "+str(time.time()))
            time.sleep(5)
            print("Sleeping.")
            if time.time() >= next_step:
                current_percent = current_percent+percent_per_step
                motor_position = set_moon_mask_position(current_percent)
                print("incrementing") 
                motor_control.simple_backward()
                current_time = time.time()
                
        # I think this is a wasted pop since we do it at the top of the while loop just as effectively.
        moons_sorted.pop(0)


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

# Screen on startup is calibration
# current_screen = "calibration"
# requested_screen = "calibration"

# def screen_worker():
#     while True:
#         if requested_screen == current_screen:
#             pass
#         elif requested_screen == "moon":
#             display.moon_display_screen()
#             current_screen = "moon"
#         elif requested_screen == "tides":
#             display.tide_display_screen()
#             current_screen = "tides"
            
# 3 main threads: Moon, Tide and Screen 
moon_thread = threading.Thread(target=moon_worker)
tide_thread = threading.Thread(target=tide_worker)
#screen_thread = threading.Thread(target=screen_worker)

moon_thread.start()
#screen_thread.start()
tide_thread.start()

# Sanity check data structures and access
#########################################
# print("Current phase: "+str(moon_data["moon"]["phase"])) 
# print("Days until next new moon: "+str(moon_data["moon_phases"]["new_moon"]["next"]["days_ahead"]))
# print("Steps to set moon mask: "+str(set_mask_position(float(moon_data["moon"]["phase"]))))