import threading
import logging
import datasources

class Sun:
    def __init__(self, type, time) -> None:
        self.type = type
        self.timestamp = time
    
    # Sorting logic
    def __eq__(self, other):
        return self.timestamp == other.timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp

# Create and sort the sunrise & sunset list in one function
def sun_creator_iterator(data):
        list = []
        for sun in data["sun"]:
            list.append = Sun("sunrise",sun["sunrise"])
            list.append = Sun("sunset", sun["sunset"])
        list = sorted(list)
        return list 

def sun_worker():
    sun_data = datasources.get_api_data(
        datasources.config["apis"]["sun_api"],
        datasources.config["apis"]["sun_api_key"],
        {"latitude":datasources.config["location"]["latitude"], "logitude":datasources.config["location"]["longitude"]}
        )
    
