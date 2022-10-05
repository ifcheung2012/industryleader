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
from pages.subpages.limitup_info_data import df_table_zt_today
from pages.subpages.pre_mkt_plan_data import get_pre_plan

pre_plan = get_pre_plan()['详细内容'][0] 

def create_layout():
    return html.Div([
                html.Div(
                    [
                        html.H6(
                                ["盘前计划"], className="subtitle padded"
                        ),
                        html.Div(id='textarea-state-example-output', style={'whiteSpace': 'pre-line'}),
                        html.P(pre_plan),
                        
                    ],className='six columns'),
                html.Div(
                    [
                        dcc.Textarea(
                            id='textarea-state-example',
                            value='Textarea content initialized\nwith multiple lines of text',
                            style={'width': '100%', 'height': 200},
                        ),
                        html.Button('Submit', id='textarea-state-example-button', n_clicks=0),
                    ],className='six columns'),
                ],className='row')