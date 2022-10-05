

from urllib import request
import os
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import config as config
import alpaca_trade_api as api
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import psycopg2
import psycopg2.extras
import tkinter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
import backtrader as bt
import strategies

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


@app.post("/backtest2")
async def index(request: Request, symbol: str = Form(...), strat: str = Form(...)):
    ticker = symbol
    strats = strat
    print(strats)
    cerebro = bt.Cerebro()

    data =yf.download(ticker, start="2016-01-01", interval="1d",rounding = True)

    feed = bt.feeds.PandasData(dataname=data)

    cerebro.adddata(feed)

    # print(feed)

    if strats == 'BuyNHold':
        cerebro.addstrategy(strategies.BuyNHold)
    if strats == 'GoldenCross':
        cerebro.addstrategy(strategies.GoldenCross)
    if strats == 'PointAnFigure':
        cerebro.addstrategy(strategies.PointAnFigure)
    
    
    print(cerebro.broker.getvalue())
    cerebro.run()
    print(cerebro.broker.getvalue())
    def saveplots(cerebro, numfigs=1, iplot=True, start=None, end=None,
                width=16, height=9, dpi=300, tight=True, use=None, file_path = '', **kwargs):

        from backtrader import plot
        if cerebro.p.oldsync:
            plotter = plot.Plot_OldSync(**kwargs)
        else:
            plotter = plot.Plot(**kwargs)

        figs = []
        for stratlist in cerebro.runstrats:
            for si, strat in enumerate(stratlist):
                rfig = plotter.plot(strat, figid=si * 100,
                                    numfigs=numfigs, iplot=iplot,
                                    start=start, end=end, use=use)
                figs.append(rfig)

        for fig in figs:
            for f in fig:
                f.savefig(file_path, bbox_inches='tight')
        return figs

    saveplots(cerebro, file_path = 'static/savefig.jpg')

    return templates.TemplateResponse("backtest.html", {"request": request, "symbol":symbol})
















#print("Code Completed")