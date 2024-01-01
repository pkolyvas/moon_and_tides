import requests
import json
import logging
from urllib.parse import urlparse
import configparser

# Application Configuration
config = configparser.ConfigParser()
config.sections()
config.read('app.conf')

# Generic API GET Request
def get_api_data(api_url, api_key, xheaders, query): 
    url = api_url

    querystring = query

    headers = xheaders

    api_name = urlparse(api_url)
    
    api_response = requests.get(url, headers=headers, params=querystring)
    return_json_raw = api_response.json()
    
    if logging.debug:
        with open(str(api_name.netloc + "_response.json"), "+a") as file:
            formatted_json_data = json.dumps(return_json_raw)
            file.write(formatted_json_data)
        logging.debug('API Request for %s: writing JSON file', api_name.netloc)
    
    return return_json_raw