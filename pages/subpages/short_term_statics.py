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
from pages.subpages.short_term_statics_data import get_data4layout


def fig_chart():
    
    df_zts ,df_dts ,df_scgd,df_lbs, ddf,df_res = get_data4layout(30)

    data = [
        go.Scatter(x=df_zts.日期, y=df_zts.涨停数, mode='markers+lines+text', name = '涨停数',text=df_zts.涨停数,marker_color='MediumPurple')
        ,go.Scatter(x=df_dts.日期, y=df_dts.跌停数, mode='lines', name = '跌停数')
        ,go.Bar(x=df_lbs.日期, y=df_lbs.连板数量, name = '连板数量', yaxis="y2",opacity=0.7,marker_color='rgb(26, 118, 255)')
        ,go.Scatter(x=df_scgd.日期, y=df_scgd.市场高度, mode='markers+lines+text',text=df_scgd.市场高度, name = '市场高度',yaxis='y2')
        ]   
    layout = go.Layout(yaxis2=dict(title='市场高度',range=[1,20],
    side='right',overlaying='y'),template='seaborn',
        margin={
            "r": 30,
            "t": 30,
            "b": 30,
            "l": 30,
        })
    dt_vals = [datetime.strftime(d,'%Y-%m-%d') for d in ddf['日期']]
    dt_breaks = [datetime.strftime(d,'%Y-%m-%d') for d in df_res['日期']]
    fig = go.Figure(data=data,layout=layout)
    fig.update_xaxes(title='日期',tickmode='array',tickvals=dt_vals,ticktext=dt_vals,rangebreaks=[dict(values=dt_breaks)])
    fig.update_layout(xaxis_tickangle=-90,bargap=0.3)
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="center",
    x=0.5,
    title_text=''
))

#     fig.update_layout(legend=dict(
#     yanchor="top",
#     y=0.99,
#     xanchor="left",
#     x=0.01
# ))
    return fig

def create_layout():
    return html.Div([
                html.Div(
                    [
                        html.H6(
                                ["短线情绪"], className="subtitle padded"
                        ),
                        dcc.Graph(figure=fig_chart(),config={"displayModeBar": False}),
                    ],className='twelve columns'),
                ],className='row')


