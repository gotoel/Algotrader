import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import pytz
import talib as ta
import config

conf = config.load_config()


def connect(account):
    account = int(account)
    mt5.initialize()
    authorized = mt5.login(account)

    if authorized:
        print("Connected: Connecting to MT5 Client")
    else:
        print("Failed to connect at account #{}, error code: {}"
              .format(account, mt5.last_error()))


def check_trades(time_frame, pair_data):
    print("Checking trades...")
    for pair, data in pair_data.items():
        data['SMA'] = ta.SMA(data['close'], 10)
        data['EMA'] = ta.EMA(data['close'], 50)
        last_row = data.tail(1)
        open_positions = positions_get()
        current_dt = datetime.now().astimezone(pytz.timezone(conf.get('timezone')))
        for index, position in open_positions.iterrows():
            #print("Index: %s -- Position: %s" % (index, position))
            # Check to see if the trade has exceeded the time limit
            trade_open_dt = position['time'].replace(tzinfo=pytz.timezone(conf.get('timezone')))
            deal_id = position['ticket']
            if (current_dt - trade_open_dt >= timedelta(hours=2)):
                close_position(deal_id)

        for index, last in last_row.iterrows():
            # Exit strategy
            if (last['close'] < last['EMA'] and last['close'] > last['SMA']):
                close_positon_by_symbol(pair)

            # Entry strategy
            if (last['close'] > last['EMA'] and last['close'] < last['SMA']):
                open_position(pair, "BUY", 1, 300, 100)


def close_positon_by_symbol(symbol):
    open_positions = positions_get(symbol)
    if 'ticket' in open_positions:
        open_positions['ticket'].apply(lambda x: close_position(x))


def get_data(time_frame):
    pairs = ['EURUSD', 'USDCAD']
    pair_data = dict()
    for pair in pairs:
        utc_from = datetime(2021, 1, 1, tzinfo=pytz.timezone('Europe/Athens'))
        date_to = datetime.now().astimezone(pytz.timezone('Europe/Athens'))
        date_to = datetime(date_to.year, date_to.month, date_to.day, hour=date_to.hour, minute=date_to.minute)
        rates = mt5.copy_rates_range(pair, time_frame, utc_from, date_to)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
        rates_frame.drop(rates_frame.tail(1).index, inplace=True)
        pair_data[pair] = rates_frame
    return pair_data


def open_position(pair, order_type, size, tp_distance=None, stop_distance=None):
    symbol_info = mt5.symbol_info(pair)
    if symbol_info is None:
        print(pair, "not found")
        return

    if not symbol_info.visible:
        print(pair, "is not visible, trying to switch on")
        if not mt5.symbol_select(pair, True):
            print("symbol_select({}}) failed, exit", pair)
            return
    print(pair, "found!")

    point = symbol_info.point

    if (order_type == "BUY"):
        order = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(pair).ask
        if (stop_distance):
            sl = price - (stop_distance * point)
        if (tp_distance):
            tp = price + (tp_distance * point)

    if (order_type == "SELL"):
        order = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(pair).bid
        if (stop_distance):
            sl = price + (stop_distance * point)
        if (tp_distance):
            tp = price - (tp_distance * point)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": pair,
        "volume": float(size),
        "type": order,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": 234000,
        "comment": "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to send order :(")
    else:
        print("Order successfully placed!")


def positions_get(symbol=None):
    if (symbol is None):
        res = mt5.positions_get()
    else:
        res = mt5.positions_get(symbol=symbol)

    if (res is not None and res != ()):
        df = pd.DataFrame(list(res), columns=res[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    return pd.DataFrame()


def close_all_positions():
    open_positions = positions_get()
    for index, position in open_positions.iterrows():
        if 'ticket' in position:
            deal_id = position['ticket']
            close_position(deal_id)


def close_position(deal_id):
    open_positions = positions_get()
    open_positions = open_positions[open_positions['ticket'] == deal_id]
    order_type = open_positions["type"][0]
    symbol = open_positions['symbol'][0]
    volume = open_positions['volume'][0]

    if (order_type == mt5.ORDER_TYPE_BUY):
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask

    close_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": order_type,
        "position": deal_id,
        "price": price,
        "magic": 234000,
        "comment": "Close trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(close_request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to close order :(")
    else:
        print("Order successfully closed!")


def close_positons_by_symbol(symbol):
    open_positions = positions_get(symbol)
    open_positions['ticket'].apply(lambda x: close_position(x))
