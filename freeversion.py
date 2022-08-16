import alpaca_trade_api as api
import talib
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import config
from datetime import datetime, date, timedelta
import pytz
import numpy as np
import schedule as sc
import time
import yfinance as yf
def trade():
    #get the current date 
    my_date = date.today()
    yesterday =  my_date - timedelta(days=1)

    tradeing_client = api.REST(config.API_Key, config.API_Secret, config.URL_ENDPT)
    BASE_URL = config.URL_ENDPT
    x = 1
    orders = tradeing_client.list_positions()  
    #for order in orders:
        # print(order.symbol)
        # print(f"Already a trade open for: {order.symbol} skipping")
    #list comprhension is not easy
    order_symbols = [order.symbol for order in orders if x == 1]
    symbols = ["BBBY", "FUBO", "AMC", "AMD", "CCL"]
    for symbol in symbols:
        if symbol not in order_symbols:
            print(f"Symbol {symbol} does not have an active trade will look for trade to enter")
            
            #get price data from alpaca api
            bars = yf.download(tickers = symbol,start=yesterday, end=my_date, interval = '5m', rounding = True )
            bars.head()
            # #put bars into np array
            price = [bar for bar in bars['Close'] if bar != 0]
            prices = np.array(price)
            open_bar = [bar for bar in bars['Open'] if bar != 0]
            opens = np.array(open_bar)
            high_bar = [bar for bar in bars['High'] if bar != 0]
            highs = np.array(high_bar)
            low_bar = [bar for bar in bars['Low'] if bar != 0]
            lows = np.array(low_bar)
            volume_bar = [bar for bar in bars['Volume'] if bar >= 0]
            volumes = np.array(volume_bar)
            #define the TA-LIB tools that I want to use to base my strat around 
            RSI = talib.RSI(prices,14)
            SMA_20 = talib.SMA(prices, timeperiod=20)
            SMA_50 = talib.SMA(prices, timeperiod=50)
            engulfing = talib.CDLENGULFING(opens, highs, lows, prices)
            
            # #Get the value of the most recent element in the np array.
            length_sma_20 = (len(SMA_20))-1
            current_SMA_20 = SMA_20[length_sma_20]
            length_sma_50 = (len(SMA_50))-1
            current_SMA_50 = SMA_50[length_sma_50]
            length_RSI = (len(RSI))-1
            current_RSI = RSI[length_RSI]
            len_engulfing = (len(engulfing))-1
            current_engulfing = engulfing[len_engulfing]
            length_price = (len(prices))-1
            current_price = prices[length_price]
            #define params for taking profit and stoping
            take_profit = round((current_price*.05)+current_price,2)
            lost_profit = round(current_price-(current_price*.025),2)
            #now that we have all the elements we need we can create the parameteres for the strat.
            print(f"current stock {symbol}")
            print(f"current Price: {current_price}")
            print(f"current SMA 20: {current_SMA_20}")
            print(f"current SMA 50: {current_SMA_50}")
            print(f"current RSI 14: {current_RSI}")
            print(f"Candle patter: {current_engulfing}")


            #time to write the code that will conduct autotrading for me
            if current_price < current_SMA_20:
                if current_price> current_SMA_50 :
                    if current_RSI > 40:
                        if current_engulfing > 0:
                            print(f"Entering a Trade with stock {symbol} at price {current_price}")
                            tradeing_client.submit_order(
                                symbol=symbol,
                                side='buy',
                                type='market',
                                qty='1',
                                time_in_force='day',
                                order_class='bracket',
                                take_profit=dict(
                                    limit_price=take_profit,
                                ),
                                stop_loss=dict(
                                    stop_price=lost_profit,
                                    limit_price=lost_profit,
                                )
                            )   

                    
        
    print("Code Completed")
sc.every(300).seconds.do(trade)

while True:
    sc.run_pending()
    time.sleep(1)


