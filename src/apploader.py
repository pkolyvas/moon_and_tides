import configparser
import os
import sys

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Check for command-line argument, otherwise default to script directory
if len(sys.argv) > 1:
    CONFIG_PATH = sys.argv[1]
else:
    CONFIG_PATH = os.path.join(SCRIPT_DIR, 'app.conf')

config = configparser.ConfigParser()
config.sections()

# TODO: We could add an if statement here and write the config file using a web UI
config.read(CONFIG_PATH)