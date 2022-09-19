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


color_1 = "#892421"
def maketable_zt():
    return  dash_table.DataTable(
                data=df_table_zt_today.to_dict('records'),
                columns=[{'id': c, 'name': c} for c in df_table_zt_today.columns],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'height': 'auto',
                    # all three widths are needed
                    'minWidth': '20px', 'width': '20px', 'maxWidth': '20px',
                    'whiteSpace': 'normal',
                    'font_size': '11px',
                    'text_align': 'center'
                },
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'left'
                    } for c in ['最新价', '成交额']
                ],
                style_header={
                                    "backgroundColor": color_1,
                                    # "fontWeight": "bold",
                                    "color": "white",
                                },
                # page_current= 0,
                # page_size= 10,
                # fixed_rows={"headers": True},
                # filter_action='native',
                sort_action='native',
                export_format='xlsx'
                )

def create_layout():
    return html.Div([
                html.Div(
                    [
                        html.H6(
                                ["今日涨停"], className="subtitle padded"
                        ),
                        maketable_zt(),
                    ],className='twelve columns'),
                
                html.Div(id='live-update-text'),
                ],className='row')


