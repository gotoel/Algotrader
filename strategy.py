import json
import os
import talib as ta

strategy_dir = "./strategies/"


def load_strategy(strategy_name):
    with open(strategy_dir + strategy_name + '.json') as json_file:
        data = json.load(json_file)
        return data