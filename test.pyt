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
from matplotlib import warnings



tradeing_client = api.REST(config.API_Key, config.API_Secret, config.URL_ENDPT)


x = 1
tradeing_client.get_account()
#orders = tradeing_client.list_positions()  

#list comprhension is not easy
#order_symbols = [order.symbol for order in orders if x == 1]
print(tradeing_client.get_account())