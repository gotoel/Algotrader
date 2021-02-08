import MetaTrader5 as mt5
import metatrader
import config
import time
import schedule
import sys
import strategy
from datetime import datetime

conf = config.load_config()


def live_trading(strategy):
    schedule.every().hour.at(":00").do(run_trader, mt5.TIMEFRAME_M15, strategy)
    schedule.every().hour.at(":15").do(run_trader, mt5.TIMEFRAME_M15, strategy)
    schedule.every().hour.at(":30").do(run_trader, mt5.TIMEFRAME_M15, strategy)
    schedule.every().hour.at(":45").do(run_trader, mt5.TIMEFRAME_M15, strategy)

    while True:
        schedule.run_pending()
        time.sleep(1)

def run_trader(time_frame, strategy):
    print("Running trader at", datetime.now())
    metatrader.connect(conf.get('metaquotes_id'))
    pair_data = metatrader.get_data(time_frame, strategy)
    metatrader.check_trades(time_frame, pair_data, strategy)


if __name__ == '__main__':
    run_trader(mt5.TIMEFRAME_M15, strategy.load_strategy("testStrategy"))  # Only for testing.

    current_strategy = sys.argv[1]
    print("Trading bot started with strategy: ", current_strategy)
    current_strategy = strategy.load_strategy(current_strategy)
    live_trading(current_strategy)
