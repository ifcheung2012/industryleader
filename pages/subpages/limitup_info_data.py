from datetime import datetime, timedelta
from functools import reduce
import pandas as pd
from sqlalchemy import create_engine,text
from dash import dcc,html
from dash import dash_table
import plotly.express as px
import plotly.graph_objects as go
from utils import make_dash_table
import akshare as ak
from environment.settings import *

#连板高度分布数据及可视化
df_stock_zt_today = pd.read_excel('data/每日复盘2022-08-19.xlsx',sheet_name='今日涨停',converters={'股票代码':str})
df_table_zt_today = df_stock_zt_today[['所属行业','股票代码','股票名称','涨跌幅','成交额','封板资金','流通市值',
    '最新价','首次封板时间','最后封板时间','炸板次数','连板数','封成比','时间']]