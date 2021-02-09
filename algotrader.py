import MetaTrader5 as mt5
import config
import time
import schedule
import sys
import strategy
from datetime import datetime


conf = config.load_config()


def live_trading(strategy):
    schedule.every().hour.at(":00").do(run_trader, strategy)
    schedule.every().hour.at(":15").do(run_trader, strategy)
    schedule.every().hour.at(":30").do(run_trader, strategy)
    schedule.every().hour.at(":45").do(run_trader, strategy)

    while True:
        schedule.run_pending()
        time.sleep(1)

def run_trader(strategy):
    print("Running trader at", datetime.now())

    if 'brokers' not in strategy:
        print("[run_trader]: No brokers defined in strategy (%s)", strategy["name"])
        return

    for broker in strategy["brokers"]:
        if broker == "metatrader":
            from brokers import metatrader
            metatrader.connect(conf.get('metaquotes_id'))
            pair_data = metatrader.get_data(mt5.TIMEFRAME_M15, strategy)
            metatrader.check_trades(mt5.TIMEFRAME_M15, pair_data, strategy)
        elif broker == "alpaca":
            from brokers import alpaca  # alpaca testing
            if alpaca.connect():
                alpaca.open_position("AMD", "BUY", 1, 10, 10)
                pass
        else:
            print("[run_trader]: Error: Broker not implemented: %s" % broker)


if __name__ == '__main__':
    # ALPACA TESTING BEGIN.
    from brokers import alpaca
    alpaca = alpaca.Alpaca()
    if alpaca.connect():
        alpaca.open_position("AMD", "BUY", 1, 10, 10)
        pass
    sys.exit(1)
    # ALPACA TESTING END.

    current_strategy = sys.argv[1]
    print("Trading bot started with strategy: ", current_strategy)
    current_strategy = strategy.load_strategy(current_strategy)
    live_trading(current_strategy)

