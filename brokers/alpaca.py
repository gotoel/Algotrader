import alpaca_trade_api as tradeapi
import config
from datetime import datetime, timedelta
import constants
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import math


class Alpaca(object):
    api = None
    config = config.load_config()
    discord_client = None

    def connect(self):
        keyid = self.config.get("alpaca_keyid")
        secret = self.config.get("alpaca_secret")
        if not keyid or not secret:
            print("Could not connect to Alpaca. "
                  "Ensure alpaca_keyid and alpaca_secret are set in the settings file.")
            return False

        self.api = tradeapi.REST(keyid, secret, base_url='https://paper-api.alpaca.markets')
        account = self.api.get_account()
        if account:
            if account.status == 'ACTIVE':
                return True
            else:
                print("Login failed or account is not active.")
        return False

    def check_trades(self, strategy):
        self.report("------------------------------------------------------")
        self.report("[check_trades] Checking trades...")
        moving_averages = strategy['movingAverages']

        for symbol in strategy['symbols']:
            self.report("[check_trades] Checking %s..." % symbol)

            asset = self.api.get_asset(symbol)

            barset_timeframe = "15Min"
            barset_data = self.api.get_barset(symbol, barset_timeframe, start=datetime.now())
            close = barset_data.df[(symbol, 'close')]

            last_trade = self.api.get_last_trade(symbol)
            # Calculate moving averages, SMA and EMA
            for m in moving_averages:
                ma_func = constants.moving_average_functions[m]
                val = moving_averages[m]['val']
                barset_data[m] = ma_func(close, val)

            # Get the last values of the moving averages
            sma = barset_data['SMA'].values[-1]
            ema = barset_data['EMA'].values[-1]

            try:
                self.graph_test(symbol)
            except:
                pass

            # Check positions
            open_positions = self.get_positions(symbol)

            # Check if there are no open positions for this stock
            if open_positions is None:
                self.report("[check_trades] No open positions, checking if one should be opened...")
                # Entry strategy: Is last close price higher than EMA and lower than SMA
                self.report("[check_trades] Checking entry strategy: EMA50(%s) < PRICE(%s) < SMA10(%s)" %
                            (ema, last_trade.price, sma))
                if ema < last_trade.price < sma:
                    lot_size = self.calc_position_size(symbol, strategy)
                    self.open_position(symbol, "BUY", lot_size, float(strategy['takeProfit']),
                                                                float(strategy['stopLoss']))
            else:
                self.report("[check_trades] Checking if entered positions should be exited...")
                # Exit strategy: Is last close price lower than EMA and higher than SMA?
                self.report("[check_trades] Checking exit strategy: EMA50(%s) > PRICE(%s) > SMA10(%s)" %
                            (ema, last_trade.price, sma))
                if ema > last_trade.price > sma:
                    self.close_position(symbol)
        self.report("------------------------------------------------------")

    def close_position(self, symbol):
        self.report("[close_position]: Closing position on (%s)." % symbol)
        asset = self.api.get_asset(symbol)
        orders = self.api.list_orders()

        # Close out all incomplete orders
        for order in orders:
            if order.asset_id == asset.id:
                self.api.cancel_order(order.id)

        try:
            self.close_position(symbol)
        except Exception as err:
            self.report("[close_position]: Unable to close position on (%s). Debug: %s" % (symbol, err))

    def get_positions(self, symbol=None):
        try:
            if symbol is None:
                return self.api.list_positions()
            else:
                return self.api.get_position(symbol)
        except:
            return None

    def get_historic_trades(self):
        return self.api.polygon.historic_trades_v2()

    def calc_position_size(self, symbol, strategy):
        self.report("[calc_position_size]: Calculating position size for (%s)" % symbol)
        account = self.api.get_account()
        balance = account.cash
        lot_size = float(balance) * float(strategy["risk"]/100) / strategy["stopLoss"]
        lot_size = math.floor(lot_size)  # Alpaca does not support fractional shares, round down to nearest integer.
        return lot_size


    def open_position(self, symbol, order_type, size, tp_distance=None, stop_distance=None):
        self.report("[open_position]: Opening position on (%s)." % symbol)
        try:
            symbol_info = self.api.get_asset(symbol)
        except Exception as err:
            self.report("[open_position]: Error: Unable to get symbol information for (%s). Debug: %s" % (symbol, err))
            return False

        # Check if symbol is not valid/tradable.
        if not symbol_info.status == 'active':
            self.report("[open_position]: Error: symbol (%s) is not active. Debug: %s" % (symbol, symbol_info))
            return False

        symbol_quote = self.api.get_last_quote(symbol)

        if order_type == "BUY":
            order = 'buy'
            price = symbol_quote.askprice
            if stop_distance:
                sl = price - stop_distance
            if tp_distance:
                tp = price + tp_distance
        elif order_type == "SELL":
            order = 'sell'
            price = symbol_quote.bidprice
            if stop_distance:
                sl = price + stop_distance
            if tp_distance:
                tp = price - tp_distance
        else:
            self.report("[open_position]: Error: Order type undefined: (%s)" % order_type)
            return False

        try:
            resp = self.api.submit_order(
                symbol=symbol,
                side=order,
                type='market',
                qty=size,
                time_in_force='day',
                order_class='bracket',
                take_profit=dict(
                    limit_price=tp,
                ),
                stop_loss=dict(
                    stop_price=sl,  # Should one of these be something other than stop loss calculated above?
                    limit_price=sl,
                )
            )
            self.report("[open_position]: Successfully opened (%s) position on (%s)" % (order_type, symbol))
            return True
        except Exception as err:
            self.report("[open_position]: Error: Failed to open position for (%s). Debug: %s" % (symbol, err))
            return False

    def graph_test(self, symbol):
        self.report("[graph_test] Plotting data...")

        barset_timeframe = "15Min"  # 1Min, 5Min, 15Min, 1H, 1D
        returned_data = self.api.get_barset(symbol, barset_timeframe, start=datetime.now())
        closeData = returned_data.df[(symbol, "close")]

        # Pull Time values... need to find a better/quicker way of doing it on the returned data.
        timeList = []
        for bar in returned_data[symbol]:
            timeList.append(datetime.strftime(bar.t, '%Y-%m-%dT%H:%M:%SZ'))
        timeList = np.array(timeList)

        # Below is some candlestick charting
        #import plotly.graph_objects as go
        #fig = go.Figure(data=[go.Candlestick(x=timeList,
        #                                    open=openList, high=highList,
        #                                      low=lowList, close=closeList)])
        #fig.show()
        #fig.to_image()

        sma20 = ta.sma(closeData, 10)
        ema50 = ta.ema(closeData, 50)

        # Defines the plot for each trading symbol
        f, ax = plt.subplots()
        f.suptitle(symbol)

        # Plots market data and indicators
        ax.plot(timeList, closeData,
                label=symbol, color="black")
        ax.plot(timeList, sma20, label="SMA10", color="green")
        ax.plot(timeList, ema50, label="EMA50", color="red")

        # Fills the green region if SMA20 > SMA50 and red if SMA20 < SMA50
        ax.fill_between(timeList,
                        ema50, sma20, where=sma20 >= ema50, facecolor='green', alpha=0.5, interpolate=True)
        ax.fill_between(timeList,
                        ema50, sma20, where=sma20 <= ema50, facecolor='red', alpha=0.5, interpolate=True)

        # Adds the legend to the right of the chart
        ax.legend(loc='best')

        #plot = plt.show()
        plt.savefig('graphs/%s.png' % symbol)
        if self.discord_client:
            self.report_file('graphs/%s.png' % symbol)
        else:
            #plt.show()
            pass

    def report(self, msg):
        if self.discord_client:
            self.discord_client.msg(msg)
        print(msg)

    def report_file(self, filename):
        if self.discord_client:
            self.discord_client.msg_file(filename)

