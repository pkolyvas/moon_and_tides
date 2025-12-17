import apploader
import json
import requests
import time
import logging
from datetime import datetime as dt

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


def tide_order_check(list):
    if logging.debug:
        for tide in list:
            logging.debug(
                "Tide order check: %s - %s", tide.tide, tide.timestamp
            )
        logging.debug("Current timestamp: %s", time.time())


# Tide data request
# We could probably turn the two request functions into a
# single function (DRY) and parameterize everything but meh,
# that seems like a lot of effort with other things to do.
def get_tide_data(latitude, longitude):
    url = apploader.config['apis']['marea_api_url']

    querystring = {
        "duration": "10080",
        "latitude": latitude,
        "longitude": longitude
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


# Our tide class stores the name of the next tide (high/low)
# and the timestamp of the tide.
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


def tide_worker(screen_owner):
    # Worker initialization
    # We do a bunch of data prep here. Eventually we'll
    # check stored data before making a request.
    # That way we can resume while offline.

    # Here we iterate over the next tides to create an
    # object for each high or low tide with a timestamp
    def tide_creator_iterator(data):
        tide_list = []
        for tide in data["extremes"]:
            new_tide = Tide(tide["state"], tide["timestamp"], tide["height"])
            tide_list.append(new_tide) 
        return tide_list

    # Here we sort them such that we create a list which will
    # allow us to use the next tides, and, following that,
    # retain a list of subsequent tides in case internet connectivity
    # is limited. We remove items from the front of the 
    # list when they're in the past via the tide worker thread
    tide_data = get_tide_data(latitude, longitude)
    logging.info('Tide worker: getting tide data from API.')
    tides_sorted = sorted(tide_creator_iterator(tide_data))
    logging.info(
        'Tide worker: there are %s tides in the queue', len(tides_sorted)
    )
    tide_order_check(tides_sorted)

    # Worker loop
    while True:
        tide_tod_clock = str(dt
                             .fromtimestamp(time.time())
                             .strftime('%H:%M')
                             )

        tide_progress_remaining = (tides_sorted[0].timestamp - time.time()) / TIDAL_HALF_PERIOD

        if tides_sorted[0].tide == "HIGH TIDE":
            tide_display_trend = "Rising Tide"
            tide_display_next = "High: " + str(dt.fromtimestamp(
                tides_sorted[0].timestamp).strftime('%H:%M'))
            tide_display_afternext = "Low: " + str(dt.fromtimestamp(
                tides_sorted[1].timestamp).strftime('%H:%M'))
        else:
            tide_display_trend = "Tide Receding"
            tide_display_next = "Low: " + str(dt.fromtimestamp(
                tides_sorted[0].timestamp).strftime('%H:%M'))
            tide_display_afternext = "High: " + str(dt.fromtimestamp(
                tides_sorted[1].timestamp).strftime('%H:%M'))

        # TODO: We need a better way to switch between active displays.
        display.tide_display(
            screen_owner,
            tide_display_trend,
            tide_display_next,
            tide_display_afternext,
            tide_progress_remaining,
            tide_tod_clock
        )
        logging.debug('Tide worker: Active')

        if time.time() > tides_sorted[0].timestamp:
            tides_sorted.pop(0)
            tides_in_queue = len(tides_sorted)
            if tides_in_queue <= 2:
                logging.info(
                    f"Updating tides list. %s tides remaining in queue.", (tides_in_queue)
                )
                updated_tide_data = get_tide_data(latitude, longitude)
                new_tides = tide_creator_iterator(updated_tide_data)
                tides_sorted = sorted(list(set(tides_sorted + new_tides)))
                logging.info('Tide worker: combining lists and checking order.')
                tide_order_check(tides_sorted)
