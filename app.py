
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import config
from alpaca_trade_api.rest import TimeFrameUnit
from matplotlib import *
import yfinance as yf
import numpy as np
import backtrader as bt
from matplotlib import warnings
import sqlite3
import talib
import strategies

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

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
            connection = sqlite3.connect(config.DB_FILE)

            connection.row_factory = sqlite3.Row
            
            cursor = connection.cursor()
            cursor.execute("""
                SELECT symbol from watchlist 
            """)
            rows = cursor.fetchall()
            #active investments
            cursor.execute("""
                SELECT stock from assets 
            """)
            assets = cursor.fetchall()


            return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "assets":assets})
    # return {"Title": "Dashboard", "stocks": rows}
    
@app.post("/add")
async def index(request: Request, add_symbol: str = Form(...), add_exchange: str = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
            INSERT INTO watchlist(symbol, exchange) VALUES (?, ?)
        """, (add_symbol,add_exchange,))
    connection.commit()

    

    cursor.execute("""
        SELECT symbol from watchlist 
    """)
    rows = cursor.fetchall()

    #active investments
    cursor.execute("""
        SELECT stock from assets 
    """)
    assets = cursor.fetchall()

    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "assets":assets})
    # return {"Title": "Dashboard", "stocks": rows}

@app.post("/add_asset")
async def index(request: Request, add_asset: str = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
            INSERT INTO assets(stock) VALUES (?)
        """, (add_asset,))
    connection.commit()

    cursor.execute("""
        SELECT symbol from watchlist 
    """)
    rows = cursor.fetchall()

    #get current positions 
    cursor.execute("""
        SELECT stock from assets 
    """)
    assets = cursor.fetchall()

    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "assets":assets})
    # return {"Title": "Dashboard", "stocks": rows}

@app.post("/delete")
async def index(request: Request, delete_stock: str = Form(...)):
    print(delete_stock)
    connection = sqlite3.connect(config.DB_FILE)

    connection.row_factory = sqlite3.Row
    
    cursor = connection.cursor()

    cursor.execute("""
            DELETE from watchlist where symbol =  ?
        """, (delete_stock,))
    connection.commit()
    cursor.execute("""
        SELECT symbol from watchlist 
    """)
    rows = cursor.fetchall()
    
    #get current positions 
    cursor.execute("""
        SELECT stock from assets 
    """)
    assets = cursor.fetchall()

    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "assets":assets})

@app.post("/delete_asset")
async def index(request: Request, delete_stock: str = Form(...)):
    print(delete_stock)
    connection = sqlite3.connect(config.DB_FILE)

    connection.row_factory = sqlite3.Row
    
    cursor = connection.cursor()

    cursor.execute("""
            DELETE from assets where stock =  ?
        """, (delete_stock,))
    connection.commit()
    cursor.execute("""
        SELECT symbol from watchlist 
    """)
    rows = cursor.fetchall()
    
    #get current positions 
    cursor.execute("""
        SELECT stock from assets 
    """)
    assets = cursor.fetchall()

    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "assets": assets})


@app.get("/stock/{symbol}")
async def stock_detail(request: Request, symbol):
    stock_filter = request.query_params.get('filter', False)
    
    connection = sqlite3.connect(config.DB_FILE)

    connection.row_factory = sqlite3.Row
    
    cursor = connection.cursor()
    if stock_filter == 'confirm':
        cursor.execute("""
            DELETE from watchlist where symbol =  ?
        """, (symbol,))
        connection.commit()
    else:
        cursor.execute("""
            SELECT symbol from watchlist WHERE symbol = ?
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
                RSI = talib.RSI(prices,14)
                SMA_20 = talib.SMA(prices, timeperiod=20)
                SMA_50 = talib.SMA(prices, timeperiod=50)
                # for x in range(len(price)):
                #     if x >= 4:
                z = 0
                for x in range(len(prices)):
                    if x >= 4:
                        if prices[x] > prices[x-1]:
                            self.entry = True
                            self.current_price[z] = prices[x]
                            z = z+1

                            
                        #if price[x] > current_sma_20 and current_price > current_sma_50:
                        # if price[x] > price[x-1]+4 and price[x-1] > price[x-2]+4 and price[x-2] > price[x-3]:
                        #     print(talib.RSI(prices,14))

                            

        def next(self):
            if self.entry == True:
                print(self.current_price)
                self.buy_bracket(limitprice=self.current_price*.05+self.current_price, price=self.current_price, stopprice=self.current_price-self.current_price*.025)
                pass
        
    cerebro = bt.Cerebro()

    df =yf.download(ticker, start='2021-01-01', interval="1d",rounding = True)
    df.head()
    feed = bt.feeds.PandasData(dataname=df)

    cerebro.adddata(feed)
    cerebro.addstrategy(MyStrategy)
    cerebro.run()
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
