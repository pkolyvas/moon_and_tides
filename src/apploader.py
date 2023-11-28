import configparser

config = configparser.ConfigParser()
config.sections()

# TODO: We could add an if statement here and write the config file using a web UI
config.read('app.conf')