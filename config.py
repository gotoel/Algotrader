import json
import sys
from os import path

conf_template = {
    "metaquotes_id" : "[metaquotes_id]",
    "timezone": "America/New_York"
}

settings_filename = "settings.json"


def load_config():
    if not path.exists(settings_filename):
        with open(settings_filename, "w+") as jsonfile:
            json.dump(conf_template, jsonfile)
            sys.exit("Wrote config file: %s. Please configure and re-launch." % settings_filename)
    else:
        with open(settings_filename, "r") as jsonfile:
            conf = json.load(jsonfile)
            return conf
