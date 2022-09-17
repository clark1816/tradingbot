
from unicodedata import name
from urllib import request
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import config
import alpaca_trade_api as api
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import psycopg2
import psycopg2.extras
from matplotlib import *
import yfinance as yf
import numpy as np
import backtrader as bt

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/add")
async def index(request: Request, add_symbol: str = Form(...), add_exchange: str = Form(...)):
    connection = psycopg2.connect(port = config.DB_PORT,host=config.DB_HOST, database=config.DB_NAME, user=config.DB_USER, password=config.DB_PASS)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""
            INSERT INTO watchlist(symbol, exchange) VALUES (%s, %s)
        """, (add_symbol,add_exchange,))
    connection.commit()
    cursor.execute("""
        SELECT symbol from watchlist 
    """)
    rows = cursor.fetchall()
    
    #get current positions 
    tradeing_client = api.REST(config.API_Key, config.API_Secret, config.URL_ENDPT)
    BASE_URL = config.URL_ENDPT
    print(BASE_URL)
    x = 1
    orders = tradeing_client.list_positions()  
    #for order in orders:
        # print(order.symbol)
        # print(f"Already a trade open for: {order.symbol} skipping")
    #list comprhension is not easy
    order_symbols = [order.symbol for order in orders if x == 1]

    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "orders": order_symbols})
    # return {"Title": "Dashboard", "stocks": rows}

@app.post("/delete")
async def index(request: Request, delete_stock: str = Form(...)):
    print(delete_stock)
    connection = psycopg2.connect(port = config.DB_PORT,host=config.DB_HOST, database=config.DB_NAME, user=config.DB_USER, password=config.DB_PASS)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("""
            DELETE from watchlist where symbol =  %s
        """, (delete_stock,))
    connection.commit()
    cursor.execute("""
        SELECT symbol from watchlist 
    """)
    rows = cursor.fetchall()
    
    #get current positions 
    tradeing_client = api.REST(config.API_Key, config.API_Secret, config.URL_ENDPT)
    BASE_URL = config.URL_ENDPT
    print(BASE_URL)
    x = 1
    orders = tradeing_client.list_positions()  
    #for order in orders:
        # print(order.symbol)
        # print(f"Already a trade open for: {order.symbol} skipping")
    #list comprhension is not easy
    order_symbols = [order.symbol for order in orders if x == 1]

    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "orders": order_symbols})

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
db_username = 'letstrade'
db_password = '123'

@app.post('/', response_class=HTMLResponse)
async def index(request: Request, username: str = Form(...), password: str = Form(...)):
    print(type(username))
    print(f'password: {password}')
    if username == db_username:
        if password == db_password:
            print("success")
            connection = psycopg2.connect(port = config.DB_PORT,host=config.DB_HOST, database=config.DB_NAME, user=config.DB_USER, password=config.DB_PASS)
            cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT symbol from watchlist 
            """)
            rows = cursor.fetchall()

            #get current positions 
            tradeing_client = api.REST(config.API_Key, config.API_Secret, config.URL_ENDPT)
            BASE_URL = config.URL_ENDPT
            print(BASE_URL)
            x = 1
            orders = tradeing_client.list_positions()  
            #for order in orders:
                # print(order.symbol)
                # print(f"Already a trade open for: {order.symbol} skipping")
            #list comprhension is not easy
            order_symbols = [order.symbol for order in orders if x == 1]

            return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "orders": order_symbols})
    # return {"Title": "Dashboard", "stocks": rows}

@app.get("/stock/{symbol}")
async def stock_detail(request: Request, symbol):
    stock_filter = request.query_params.get('filter', False)
    
    connection = psycopg2.connect(port = config.DB_PORT,host=config.DB_HOST, database=config.DB_NAME, user=config.DB_USER, password=config.DB_PASS)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if stock_filter == 'confirm':
        cursor.execute("""
            DELETE from watchlist where symbol =  %s
        """, (symbol,))
        connection.commit()
    else:
        cursor.execute("""
            SELECT symbol from watchlist WHERE symbol = %s
        """, (symbol,))
        rows = cursor.fetchone()

    return templates.TemplateResponse("stock_detail.html", {"request": request, "stock": rows})


@app.post("/backtest")
async def index(request: Request, symbol: str = Form(...)):
    ticker = symbol
    class MyStrategy(bt.Strategy):

        def __init__(self):
                df =yf.download(tickers=ticker, start='2021-01-01', interval="1d",rounding = True)
                df.head()
                price = [bar for bar in df['Close'] if bar != "NaN"]
                prices = np.array(price)
                length_price = (len(prices))-1
                current_price = prices[length_price]
                for x in range(len(price)):
                    if x >= 4:
                        if price[x] > price[x-1]+4 and price[x-1] > price[x-2]+4 and price[x-2] > price[x-3]:
                            self.entry = True

        def next(self):
            if self.entry == True:
                self.buy_bracket(limitprice=current_price*.05+current_price, price=current_price, stopprice=current_price-current_price*.025)
                pass
        
    cerebro = bt.Cerebro()

    df =yf.download(ticker, start='2021-01-01', interval="1d",rounding = True)
    df.head()
    price = [bar for bar in df['Close'] if bar != "NaN"]
    prices = np.array(price)
    length_price = (len(prices))-1
    current_price = prices[length_price]
    print(current_price)
    print(prices[length_price-1])
    feed = bt.feeds.PandasData(dataname=df)

    cerebro.adddata(feed)
    cerebro.addstrategy(MyStrategy)
    cerebro.run()
    cerebro.plot()

    return templates.TemplateResponse("backtest.html", {"request": request, "symbol":symbol})



