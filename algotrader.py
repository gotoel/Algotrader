import MetaTrader5 as mt5
import metatrader
import config
import time
import schedule
from datetime import datetime

conf = config.load_config()


def live_trading():
    schedule.every().hour.at(":00").do(run_trader, mt5.TIMEFRAME_M15)
    schedule.every().hour.at(":15").do(run_trader, mt5.TIMEFRAME_M15)
    schedule.every().hour.at(":30").do(run_trader, mt5.TIMEFRAME_M15)
    schedule.every().hour.at(":45").do(run_trader, mt5.TIMEFRAME_M15)

    while True:
        schedule.run_pending()
        time.sleep(1)

def run_trader(time_frame):
    print("Running trader at", datetime.now())
    metatrader.connect(conf.get('metaquotes_id'))
    pair_data = metatrader.get_data(time_frame)
    metatrader.check_trades(time_frame, pair_data)


run_trader(mt5.TIMEFRAME_M15)
#live_trading()

