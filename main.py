from urllib import request
from fastapi import FastAPI, Request, Form, File
from fastapi.templating import Jinja2Templates
import sqlite3, config
import alpaca_trade_api as api
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import psycopg2
import psycopg2.extras

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
database={'letstrade':'123'}



@app.route('/form_login',methods=['POST','GET'])
@app.get("/")
async def index(request: Request):
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


















#print("Code Completed")