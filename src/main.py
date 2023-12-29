import sqlite3
import json
import requests
import time
import threading
from datetime import datetime
from urllib.parse import urlparse
import logging  
import apploader

# Install this script with `pip install -r dev_requirements.txt` to avoid
# RPi libraries and run on machines without GPIO/I2C/etc.
try:
    import motor_control
    import light_control
    import display
except ImportError:
    import dev as motor_control
    import dev as light_control
    import dev as display

# Not yet using the DB
# connection = sqlite3.connect(apploader.config['db']['sqlite3_db'])
latitude = float(apploader.config['location']['latitude'])
longitude = float(apploader.config['location']['longitude'])
motor_resolution = int(apploader.config['motor']['resolution'])
tide_correction = int(apploader.config['location']['correction'])

# Tidal half period in seconds (low to high or high to low)
TIDAL_HALF_PERIOD = 22350

# Tide data request
def get_tide_data(latitude, longitude): 
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
    
    if logging.debug:
        with open("tide_response.json", "+a") as file:
            tide_json_data = json.dumps(tides_json_raw)
            file.write(tide_json_data)
        logging.debug('Tide worker: writing JSON file')
    
    return tides_json_raw

# Retreive moon data from the API
# API key configured in your app.conf
def get_moon_data(latitude, longitude):
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
    
    if logging.debug:
        with open("moon_api_response.json", "+a") as file:
            moon_json_data = json.dumps(moons_json_raw)
            file.write(moon_json_data)
        logging.debug('Moon worker: writing JSON file')
    
    return  moons_json_raw

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
 
# This simple function takes the phase percentage and
# will calculate the number of motor steps to move the
# mask. The moto is a 200 step motor or 1.8 degrees per
# step. That gives us clear correlation with the four
# moon phases: new (0), first quarter (50 steps), etc. etc.
# We also want to set and store the absolute position.
def set_moon_mask_position(phase_percentage):  
    position = phase_percentage * motor_resolution
    return int(position)

# Moon order check if we're in debug mode
def moon_order_check(list):
    if logging.debug:
        for moon in list:
            logging.debug("Moon order check: %s - %s - %s", moon.moon, moon.percent, moon.timestamp)
        logging.debug("Current timestamp: %s", time.time())
        
def tide_order_check(list):
    if logging.debug:
        for tide in list:
            logging.debug("Tide order check: %s - %s - %s", tide.tide, tide.timestamp)
        logging.debug("Current timestamp: %s", time.time())

def moon_worker():
    # Start moonlight and calibrate moon on start
    light_control.moonlight()
    display.calibrate_moon_screen("calibration")
    motor_control.motor_calibration()

    # Moon position is 0 after calibration
    # We set motor position to compare
    moon_position = 0
    motor_position = 0
    
    # Here we iterate over the next moon phases to create an 
    # object for each moon phase with a timestamp and store
    # the objects in a list.
    def moon_creator_iterator(data):
        list = []
        for moon in data["moon_phases"]:
            moon_phase = Moon(moon, data["moon_phases"][moon]["next"]["timestamp"])
            moon_phase.set_percentage()
            list.append(moon_phase)
        return list
    
    # Get our moon data, create objects, put it in a list, and sort the list 
    # We sort them such that we create a list which will
    # allow us to use the next moon, and, following that,
    # retain a list of subsequent moons in case internet connectivity
    # is limited. We remove items from the front of the 
    # list when they're in the past via the moon worker thread.          
    moon_data = get_moon_data(latitude, longitude)
    logging.info('Moon worker: getting moon data.')
    moons_sorted = sorted(moon_creator_iterator(moon_data))
    logging.info('Moon worker: there are %s moons in the queue', len(moons_sorted))       
    
    # We need to remove the first element from the "future" moon phases if it's in the past
    # Currently the API returns some "next"/future elements in the past (a bug)
    if moons_sorted[0].timestamp < time.time():
        logging.info('Moon worker: API returned a future moon that\'s actually in the past. Removing.')
        moons_sorted.pop(0)
    
    # We need to insert the current moon if we're loading up and put it at the front of the 
    # list. We use the computer's time instead of the timestamp returned via the API.
    moons_sorted.insert(0, Moon(moon_data["moon"]["phase_name"], time.time(), float(moon_data["moon"]["phase"])))
    logging.info('Adding the current, already-in-progress, quarter moon to the tip of the list') 
    moon_order_check(moons_sorted)

    # Toggle for first run
    first_load = True

    # Enter thread's main loop
    while True:
        # if we don't have anything left in our list we error 
        if len(moons_sorted) == 1:
           break
        
        # Update list if second element is now in the past
        # by removing the first element.
        if moons_sorted[1].timestamp <= time.time():
            moons_sorted.pop(0)
            logging.info("Moon worker: Outdated entry removed")

        # We want to trigger the API call at this point to replenish our queue
        if len(moons_sorted) == 2:
            logging.info('Our list is almost empty. Updating data from API.')
            update_moons = get_moon_data(latitude, longitude)
            new_moons = moon_creator_iterator(update_moons)
            moons_sorted = sorted(list(set(moons_sorted + new_moons)))
            logging.info('Moon worker: combining lists and checking order.')
            moon_order_check(moons_sorted)
        
        # This should give us the number of seconds between "known" quarter phases.
        # Quarter phases are returned from the API.
        timerange = moons_sorted[1].timestamp - moons_sorted[0].timestamp
        logging.debug("Timerange: %s", str(timerange)) 
        
         # We need to update the percent of the phase on load.
        time_delta_to_now = time.time()-moons_sorted[0].timestamp # gives us the seconds since stored phase start time
        remaining_percent_of_current_phase = (timerange - time_delta_to_now) / timerange # gives us the percent remaining of the current phase
        percent_to_next_phase = (moons_sorted[1].percent - moons_sorted[0].percent)*(remaining_percent_of_current_phase)
        logging.debug("Moon worker: Time delta is %s", (time_delta_to_now))
        logging.debug("Moon worker: Remaining percent of current phase is %s", remaining_percent_of_current_phase)
        logging.info("Moon worker: Percent to next phase is %s", str(percent_to_next_phase))

        steps_to_next_phase = round(motor_resolution * percent_to_next_phase)
        logging.debug("Moon worker: Steps to next phase are %s", str(steps_to_next_phase))

        time_per_step = int(timerange / steps_to_next_phase)
        logging.debug("Moon worker: Time per step is %s", str(time_per_step))                 
                
        percent_per_step = percent_to_next_phase / steps_to_next_phase
        logging.info("Moon worker: Percent per step is %s", str(percent_per_step))        
        
        # Update percent
        moons_sorted[0].percent = moons_sorted[0].percent + (time_delta_to_now/timerange)
        current_percent = moons_sorted[0].percent
        logging.info("Moon worker: Current percent is %s", str(current_percent))
        moon_position = set_moon_mask_position(current_percent)
        
        # If it's first load we need to set the position based on the calibrated full moon. Then we set first load to false.
        if first_load == True:
            logging.info("Moon worker: First Load. Moving mask to %s", moon_position)
            for i in range(moon_position):
                motor_control.simple_backward()
            motor_position = moon_position
            first_load = False
        # If we're moving through the loop and the system is calibrated, we want to correct any error
        else:
            if moon_position > motor_position:
                logging.warning("Moon worker: Motor behind. Fixing.")
                delta = moon_position - motor_position
                for i in range(delta):
                    motor_control.simple_backward()
                motor_position = moon_position
            elif moon_position < motor_position:
                logging.warning("Moon worker: Motor ahead. Fixing.")
                delta = motor_position - moon_position
                for i in range(delta):
                    motor_control.simple_forward()

        current_time = int(time.time())
        logging.debug("Moon worker: Current time %s", str(current_time))
      
        while moons_sorted[1].timestamp > int(time.time()):
            next_step = int(current_time+time_per_step)
            #print("Next step: "+str(next_step))
            #print("Current time: "+str(time.time()))
            time.sleep(15)
            logging.debug('Moon worker: Active')
            if time.time() >= next_step:
                current_percent = current_percent+percent_per_step
                motor_position = set_moon_mask_position(current_percent)
                logging.info('Moon Worker: Moving mask')
                motor_control.simple_backward()
                current_time = time.time()
                
        # I think this is a wasted pop since we do it at the top of the while loop just as effectively.
        # It might be worse: I might be popping out two entries by accident. 
        # moons_sorted.pop(0)


# Our tide class stores the name of the next tide (high/low) and the timestamp of the tide. 
# It also accepts height but the height value isn't used currently.
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

def tide_worker():
    
    # Worker initialization
    # We do a bunch of data prep here. Eventually we'll check stored data before making a request.
    # That way we can resume while offline.

    # Here we iterate over the next tides to create an 
    # object for each high or low tide with a timestamp    
    def tide_creator_iterator(data):
        list = []
        for tide in data["extremes"]:
            tide_list = []
            new_tide = Tide(tide["state"], tide["timestamp"], tide["height"])
            tide_list.append(new_tide) 
        return list

    # Here we sort them such that we create a list which will
    # allow us to use the next tides, and, following that,
    # retain a list of subsequent tides in case internet connectivity
    # is limited. We remove items from the front of the 
    # list when they're in the past via the tide worker thread
    tide_data = get_tide_data(latitude, longitude)
    logging.info('Tide worker: getting tide data from API.')
    tides_sorted = sorted(tide_creator_iterator(tide_data))
    logging.info('Tide worker: there are %s tides in the queue', len(tides_sorted))  
    tide_order_check(tides_sorted)
    
    # Worker loop
    while True:
        time.sleep(15)

        tide_tod_clock = str(datetime.fromtimestamp(time.time()).strftime('%H:%M'))

        tide_progress_remaining = (tides_sorted[0].timestamp - time.time()) / TIDAL_HALF_PERIOD

        if tides_sorted[0].tide == "HIGH TIDE":         
            tide_display_trend = "Rising Tide"
            tide_display_next = "High: " + str(datetime.fromtimestamp(tides_sorted[0].timestamp).strftime('%H:%M'))
            tide_display_afternext = "Low: " +str(datetime.fromtimestamp(tides_sorted[1].timestamp).strftime('%H:%M'))
                    
        else:
            tide_display_trend = "Tide Receding"
            tide_display_next = "Low: " + str(datetime.fromtimestamp(tides_sorted[0].timestamp).strftime('%H:%M'))
            tide_display_afternext = "High: " + str(datetime.fromtimestamp(tides_sorted[1].timestamp).strftime('%H:%M'))
        
        # TODO: We need a better way to switch between active displays.
        display.tide_display("tide", tide_display_trend, tide_display_next, tide_display_afternext, tide_progress_remaining, tide_tod_clock)
        logging.debug('Tide worker: Active')
        
        if time.time() > tides_sorted[0].timestamp:
            tides_sorted.pop(0)
            tides_in_queue = len(tides_sorted)
            if tides_in_queue <= 2:
                logging.info(f"Updating tides list. %s tides remaining in queue.", (tides_in_queue))
                updated_tide_data = get_tide_data(latitude, longitude)
                new_tides = tide_creator_iterator(updated_tide_data)
                tides_sorted = sorted(list(set(tides_sorted + new_tides)))
                logging.info('Tide worker: combining lists and checking order.')
                tide_order_check(tides_sorted)
                
            
        
def main():
    logging.basicConfig(filename=apploader.config['logging']['location'], encoding=apploader.config['logging']['encoding'], level=apploader.config['logging']['level'])
    logging.info('Moon and tides app started.')
    
    tide_thread = threading.Thread(target=tide_worker)
    moon_thread = threading.Thread(target=moon_worker)
    moon_thread.start()
    tide_thread.start()
    
    #TODO: Deinit lights function on exit
    #TODO: Clean exit

if __name__ == "__main__":
    main()