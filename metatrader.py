import MetaTrader5 as mt5
import pandas as pd

def connect(account):
    account = int(account)
    mt5.initialize()
    authorized=mt5.login(account)

    if authorized:
        print("Connected: Connecting to MT5 Client")
    else:
        print("Failed to connect at account #{}, error code: {}"
              .format(account, mt5.last_error()))


def open_position(pair, order_type, size, tp_distance=None, stop_distance=None):
    symbol_info = mt5.symbol_info(pair)
    if symbol_info is None:
        print(pair, "not found")
        return

    if not symbol_info.visible:
        print(pair, "is not visible, trying to switch on")
        if not mt5.symbol_select(pair, True):
            print("symbol_select({}}) failed, exit",pair)
            return
    print(pair, "found!")

    point = symbol_info.point

    if(order_type == "BUY"):
        order = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(pair).ask
        if(stop_distance):
            sl = price - (stop_distance * point)
        if(tp_distance):
            tp = price + (tp_distance * point)

    if(order_type == "SELL"):
        order = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(pair).bid
        if(stop_distance):
            sl = price + (stop_distance * point)
        if(tp_distance):
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
        print ("Order successfully placed!")

def positions_get(symbol=None):
    if(symbol is None):
        res = mt5.positions_get()
    else:
        res = mt5.positions_get(symbol=symbol)

    if(res is not None and res != ()):
        df = pd.DataFrame(list(res),columns=res[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    return pd.DataFrame()

def close_position(deal_id):
    open_positions = positions_get()
    open_positions = open_positions[open_positions['ticket'] == deal_id]
    order_type  = open_positions["type"][0]
    symbol = open_positions['symbol'][0]
    volume = open_positions['volume'][0]

    if(order_type == mt5.ORDER_TYPE_BUY):
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask

    close_request={
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
        print ("Order successfully closed!")

def close_positons_by_symbol(symbol):
    open_positions = positions_get(symbol)
    open_positions['ticket'].apply(lambda x: close_position(x))