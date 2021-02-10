import pandas_ta as ta
from forex_python.converter import CurrencyRates


moving_average_functions = {
    'SMA' : lambda close, timeP: ta.sma(close, timeP),
    'EMA' : lambda close, timeP: ta.ema(close, timeP),
    'WMA' : lambda close, timeP: ta.wma(close, timeP),
    'linearReg' : lambda close, timeP: ta.linreg(close, timeP),
    'TRIMA' : lambda close, timeP: ta.trima(close, timeP),
    'DEMA' : lambda close, timeP: ta.dema(close, timeP),
    # 'HT_TRENDLINE' : lambda close, timeP: ta.HT_TRENDLINE(close, timeP), # Can't find pandas-ta equivalent
    # 'TSF' : lambda close, timeP: ta.TSF(close, timeP)
}


# Doesn't really matter in stocks
def get_pip_value(symbol, account_currency):
    symbol_1 = symbol[0:3]
    symbol_2 = symbol[3:6]
    c = CurrencyRates()
    return c.convert(symbol_2, account_currency, c.convert(symbol_1, symbol_2, 1))