import metatrader
from datetime import datetime
import config

conf = config.load_config()

metatrader.connect(conf.get('metaquotes_id'))
print(metatrader.positions_get())