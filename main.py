import metatrader
from datetime import datetime
import config

conf = config.load_config()

metatrader.connect(conf.get('metaquotes_id'))
metatrader.open_position("EURUSD", "BUY", 1, 300, 100)