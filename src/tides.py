# def get_tide_data(latitude, longitude):

#     url = "https://api.marea.ooo/v2/tides"

#     querystring = {
#         "duration":"10080",
#         "latitude":latitude,
#         "longitude":longitude
#         }

#     headers = {
#         "x-marea-api-token": apploader.config['apis']['marea_api'],
#     }

#     tides_json_raw = requests.get(url, headers=headers, params=querystring)
    
#     return  json.loads(tides_json_raw.json())

# This replaces the request from the API for testing
# using a local file which matches the Moons API response.

# This replaces the request from the API for testing
# using a local file which matches the tides API response.
with open('current_tides.json') as user_file:
    tides_json_raw = user_file.read()
    
tide_data = json.loads(tides_json_raw)

class Tide:
    def __init__(self, tide, timestamp, height, next_tide=None) -> None:
        self.tide = tide
        self.timestamp = timestamp
        self.height = height
        self.next_tide = next_tide

tide_list = []

for tide in tide_data["extremes"]:
    new_tide = Tide(tide["state"], tide["timestamp"], tide["height"])
    tide_list.append(new_tide)
    if len(tide_list) != 1:
        current_index = len(tide_list)-1
        tide_list[current_index-1].next_tide = tide_list[current_index]

def tide_worker():
    while True
        item = tide_queue.get()
        # stuff
        tide_queue.done()
        
tide_thread = threading.Thread(target=tide_worker)
tide_thread.start()

# tide_queue.join()