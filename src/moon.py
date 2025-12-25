import apploader
import json
import requests
import time
import logging

try:
    import motor_control
    import light_control
    import display
except ImportError:
    import dev as motor_control
    import dev as light_control
    import dev as display

latitude = float(apploader.config['location']['latitude'])
longitude = float(apploader.config['location']['longitude'])
motor_resolution = int(apploader.config['motor']['resolution'])
tide_correction = int(apploader.config['location']['correction'])
moon_position = 


# Retreive moon data from the API
# API key configured in your app.conf
def get_moon_data(latitude, longitude):
    url = "https://moon-phase.p.rapidapi.com/advanced"

    querystring = {
       "lat": str(latitude),
       "lon": str(longitude)
       }

    headers = {
        "X-RapidAPI-Key": apploader.config['apis']['moon_api_key'],
        "X-RapidAPI-Host": "moon-phase.p.rapidapi.com"
    }

    api_response = requests.get(url, headers=headers, params=querystring)
    moons_json_raw = api_response.json()

    # Logging is set to debug we write the response
    # to a file for poking.
    with open("moon_api_response.json", "+w") as file:
        moon_json_data = json.dumps(moons_json_raw)
        file.write(moon_json_data)
    logging.debug('Moon worker: writing JSON file')

    return moons_json_raw


# Our moon class really only needs the name of the next phase and
# the timestamp of that phase.
class Moon:
    def __init__(self, moon, timestamp, percent=None):
        self.moon = moon
        self.timestamp = timestamp
        self.percent = 0

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

    def update_current_percent(self, percent):
        self.percent = percent


# Here we iterate over the next moon phases to create an
# object for each moon phase with a timestamp and store
# the objects in a list.
def create_sorted_moon_list(data):
    moon_list = []
    for moon in data["moon_phases"]:
        moon_phase = Moon(
            moon,
            data["moon_phases"][moon]["next"]["timestamp"]
        )
        moon_phase.set_percentage()
        moon_list.append(moon_phase)
    sorted(moon_list)


# This simple function takes the phase percentage and
# will calculate the number of motor steps to move the
# mask. The motor is a 200 step motor or 1.8 degrees per
# step. That gives us clear correlation with the four
# moon phases: new (0), first quarter (50 steps), etc. etc.
# We also want to set and store the absolute position.
def set_moon_mask_position(phase_percentage):
    position = phase_percentage * motor_resolution
    return int(position)


# This function moves the moon mask a number of steps
# based on a delta, which is the difference between
# two percentages.
def move_moon_mask(delta):
    steps = round(delta * motor_resolution, 1)
    if steps > 0:
        for step in range(steps):
            motor_control.simple_backward()
    elif steps < 0:
        for step in range(abs(steps)):
            motor_control.simple_forward()


def moon_order_check(list):
    if logging.debug:
        for moon in list:
            logging.debug(
                "Moon order check: %s - %s - %s",
                moon.moon, moon.percent,
                moon.timestamp
            )
        logging.debug("Current timestamp: %s", time.time())


# Returns an estimate of the absolute position
# of the moon, based on a 29.5 average moon
# moon cycle length
def estimate_current_position(moon_data):
    # 1/4 of 29.5 days in seconds
    seconds_in_quarter = 637200
    next_moon_time = moon_data[1].timestamp
    seconds_left_in_quarter = next_moon_time - time.time()
    percent_remaining_in_quarter = seconds_left_in_quarter / seconds_in_quarter
    if moon_data[1].percent == 0:
        1 - percent_remaining_in_quarter
    else:
        moon_data[1].percent - percent_remaining_in_quarter


def moon_worker(screen_owner):
    # Start moonlight and calibrate moon on start
    light_control.moonlight()
    display.calibrate_moon_screen(screen_owner)
    motor_control.motor_calibration(screen_owner)

    # Moon position is 0 after calibration
    # We set motor position to compare
    moon_position = 0
    motor_position = 0

    # Get our moon data, create objects, put it in a list, and sort the list
    # We sort them such that we create a list which will
    # allow us to use the next moon, and, following that,
    # retain a list of subsequent moons in case internet connectivity
    # is limited. We remove items from the front of the
    # list when they're in the past via the moon worker thread.
    raw_moon_data = get_moon_data(latitude, longitude)
    logging.info('Moon worker: getting moon data.')
    moons_sorted = create_sorted_moon_list(raw_moon_data)
    logging.info(
        'Moon worker: there are %s moons in the queue', len(moons_sorted)
    )

    # We need to remove the first element from the
    # "future" moon phases if it's in the past
    # Currently the API returns some "next"/future
    # elements in the past (a bug)
    if moons_sorted[0].timestamp < time.time():
        logging.info(
            'Moon worker: API returned a future moon in the past. Removing.'
        )
        moons_sorted.pop(0)

    # We need to insert the current moon if we're
    # loading up and put it at the front of the
    # list. We use the computer's time instead of \
    # the timestamp returned via the API.
    moons_sorted.insert(
        0,
        Moon(
            raw_moon_data["moon"]["phase_name"],
            time.time(),
            float(raw_moon_data["moon"]["phase"])
        )
    )
    logging.info(
        'Adding the in-progress moon to the tip of the list'
    )

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

        # This needs work
        # We want to trigger the API call at this point to replenish our queue
        if len(moons_sorted) == 2:
            logging.info('Our list is almost empty. Updating data from API.')
            updated_raw_moon_data = get_moon_data(latitude, longitude)
            moons_sorted = create_sorted_moon_list(updated_raw_moon_data)

        # If it's first load we need to set the position based on
        # the calibrated full moon. Then we set first load to false.
        if first_load is True:
            logging.info(
                "Moon worker: First Load. Moving mask to %s", moon_position
            )
            move_moon_mask(moon_position)
            motor_position = moon_position
            first_load = False
        # Otherwise we poll the API for updated data, or pull
        # the data from our stored records
        else:
            updated_current_moon = get_moon_data(latitude, longitude)
            if len(updated_current_moon.get['moon']) != 0:
                moons_sorted.pop(0)
                moons_sorted.insert(
                    0,
                    Moon(
                        updated_current_moon["moon"]["phase_name"],
                        time.time(),
                        float(updated_current_moon["moon"]["phase"])
                    )
                )
                moon_position = float(updated_current_moon['moon']['phase'])
            else:
                moon_position = estimate_current_position(moons_sorted)
            delta = moon_position - motor_position
            move_moon_mask(delta)
            motor_position = moon_position
        time.sleep(3600)
