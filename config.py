import json
import sys
from os import path

conf_template = {
    "metaquotes_id" : "",
    "timezone": "America/New_York",
    "alpaca_keyid": "",
    "alpaca_secret": ""
}

settings_filename = "settings.json"


def load_config():
    if not path.exists(settings_filename):
        with open(settings_filename, "w+") as jsonfile:
            template_json = json.dumps(conf_template, indent=4)
            jsonfile.write(template_json)
            sys.exit("Wrote config file: %s. Please configure and re-launch." % settings_filename)
    else:
        with open(settings_filename, "r") as jsonfile:
            conf = json.load(jsonfile)
            return conf
