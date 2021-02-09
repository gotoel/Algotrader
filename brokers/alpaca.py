import alpaca_trade_api as tradeapi
import config


class Alpaca(object):
    api = None
    config = config.load_config()

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

    def open_position(self, symbol, order_type, size, tp_distance=None, stop_distance=None):
        print("[open_position]: Opening position on (%s)." % symbol)
        try:
            symbol_info = self.api.get_asset(symbol)
        except Exception as err:
            print("[open_position]: Error: Unable to get symbol information for (%s). Debug: %s" % (symbol, err))
            return False

        # Check if symbol is not valid/tradable.
        if not symbol_info.status == 'active':
            print("[open_position]: Error: symbol (%s) is not active. Debug: %s" % (symbol, symbol_info))
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
            print("[open_position]: Error: Order type undefined: (%s)" % order_type)
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
            print("[open_position]: Successfully opened (%s) position on (%s)" % (order_type, symbol))
            return True
        except Exception as err:
            print("[open_position]: Error: Failed to open position for (%s). Debug: %s" % (symbol, err))
            return False