import MetaTrader5 as mt5
import config
import time
import schedule
import sys
import strategy
from datetime import datetime
from brokers import alpaca

from reporting import discord
import threading

conf = config.load_config()
discord_client = None

def live_trading(strategy):
    schedule.every().hour.at(":00").do(run_trader, strategy)
    schedule.every().hour.at(":05").do(run_trader, strategy)
    schedule.every().hour.at(":10").do(run_trader, strategy)
    schedule.every().hour.at(":15").do(run_trader, strategy)
    schedule.every().hour.at(":20").do(run_trader, strategy)
    schedule.every().hour.at(":25").do(run_trader, strategy)
    schedule.every().hour.at(":30").do(run_trader, strategy)
    schedule.every().hour.at(":35").do(run_trader, strategy)
    schedule.every().hour.at(":40").do(run_trader, strategy)
    schedule.every().hour.at(":45").do(run_trader, strategy)
    schedule.every().hour.at(":50").do(run_trader, strategy)
    schedule.every().hour.at(":55").do(run_trader, strategy)
    #schedule.every().minute.do(run_trader, strategy)

    while True:
        schedule.run_pending()
        time.sleep(1)


def run_trader(strategy):
    print("Running trader at", datetime.now())

    if 'brokers' not in strategy:
        print("[run_trader]: No brokers defined in strategy (%s)", strategy["name"])
        return

    # Only run strategy against supported brokers.
    for broker in strategy["brokers"]:
        if broker == "metatrader":
            from brokers import metatrader
            metatrader.connect(conf.get('metaquotes_id'))
            pair_data = metatrader.get_data(mt5.TIMEFRAME_M15, strategy)
            metatrader.check_trades(mt5.TIMEFRAME_M15, pair_data, strategy)
        elif broker == "alpaca":
            alpaca_broker = alpaca.Alpaca()
            if discord_client:
                alpaca_broker.discord_client = discord_client
            if alpaca_broker.connect():
                alpaca_broker.check_trades(strategy)
        else:
            print("[run_trader]: Error: Broker not implemented: %s" % broker)


# MAIN PROGRAM ENTRY
# Example run: python algotrader.py [strategy, located in ./strategies/]
if __name__ == '__main__':
    # REPORTING SYSTEMS BEGIN.
    if 'reporting' in conf and 'discord' in conf['reporting'] and conf['reporting']['discord'].get('enabled') == 'True':
        discord_client = discord.DiscordBot(command_prefix=">", self_bot=False)
        #discord_bot.run(conf['reporting']['discord']['token'])
        discord_client.login(conf['reporting']['discord']['token'])
        t = threading.Thread(target=discord_client.run, args=(conf['reporting']['discord']['token'],))
        t.start()
    # REPORTING SYSTEMS END.

    # METATRADER TESTING BEGIN.
    '''
    current_strategy = sys.argv[1]
    print("[Main] Trading bot started with strategy: ", current_strategy)
    current_strategy = strategy.load_strategy(current_strategy)
    from brokers import metatrader
    metatrader.connect(conf.get('metaquotes_id'))
    pair_data = metatrader.get_data(mt5.TIMEFRAME_M15, current_strategy)
    metatrader.check_trades(mt5.TIMEFRAME_M15, pair_data, current_strategy)
    '''
    # METATRADER TESTING END.

    # ALPACA TESTING BEGIN.
    '''
    from brokers import alpaca
    alpaca = alpaca.Alpaca()
    if alpaca.connect():
        if discord_client:
            alpaca.discord_client = discord_client
        #alpaca_strategy = strategy.load_strategy('alpacaStrategy')
        #alpaca.check_trades(alpaca_strategy)
        alpaca.graph_test("AMD")
    '''
    # ALPACA TESTING END.



    current_strategy = sys.argv[1]
    print("[Main] Trading bot started with strategy: ", current_strategy)
    current_strategy = strategy.load_strategy(current_strategy)
    live_trading(current_strategy)

