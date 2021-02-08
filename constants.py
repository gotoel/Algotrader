import talib as ta

moving_average_functions = {
    'SMA' : lambda close, timeP: ta.SMA(close, timeP),
    'EMA' : lambda close, timeP: ta.EMA(close, timeP),
    'WMA' : lambda close, timeP: ta.WMA(close, timeP),
    'linearReg' : lambda close, timeP: ta.LINEARREG(close, timeP),
    'TRIMA' : lambda close, timeP: ta.TRIMA(close, timeP),
    'DEMA' : lambda close, timeP: ta.DEMA(close, timeP),
    'HT_TRENDLINE' : lambda close, timeP: ta.HT_TRENDLINE(close, timeP),
    'TSF' : lambda close, timeP: ta.TSF(close, timeP)
}