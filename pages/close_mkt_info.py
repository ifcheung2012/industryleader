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
from pages.subpages import (
    limitup_info,short_term_statics
)

color_1 = "#892421"


def create_layout():
    engine = create_engine(f'mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')

    sql_limitup_history = 'select * from stocks_limitup_history'
    sql_concept_stocks = 'select * from concept_stocks'
    #数据库取数
    df_concept_stocks =  pd.read_sql(sql_concept_stocks,engine)
    stocks_limitup_history =  pd.read_sql(sql_limitup_history,engine)
    #去除次新股和ST股后的连板高标数据
    stocks = df_concept_stocks.loc[(df_concept_stocks.概念名称 == '新股与次新股')|(df_concept_stocks.概念名称 == 'ST板块')]
    df = stocks_limitup_history[~stocks_limitup_history.名称.isin(stocks.名称)]
    dfa = df.groupby(['日期']).apply(lambda x:x[x.连板数==x.连板数.max()])
    dfa.index = dfa.index.droplevel()

    #历史高标走势-去除次新股和ST股后数据
    fig = px.line(dfa[100:],x='日期', y="连板数",color_discrete_sequence=px.colors.qualitative.Antique) # text="名称"
    fig.update_traces(line_color='rgb(200, 150, 150)', line_width=1)
    fig.update_yaxes(showgrid=True,autorange=True, showticklabels=True, visible=True)
    fig.update_layout(autosize=True,height=300,template='simple_white')
    # fig.update_layout({
    # 'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    # 'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    # })

    dt_yesterday = (datetime.today()- timedelta(days= 1)).strftime('%Y-%m-%d').replace('-','')
    
    #连板高度分布数据及可视化
    df_stock_lbgd = pd.read_excel('data/每日复盘2022-08-19.xlsx',sheet_name='连板高度')
    #涨停信息
    
    
    return html.Div(
                        [
                            html.Div([
                                html.Div(
                                [  
                                    html.Div(
                                        [
                                            html.Div(
                                                [html.H5("盘后整理")],
                                                className="seven columns main-title",
                                            ),
                                            html.Div(
                                                [
                                                    dcc.Link(
                                                        "08-19",
                                                        href="/dash-financial-report/full-view",
                                                        className="full-view-link",
                                                    )
                                                ],
                                                className="five columns",
                                            ),
                                        ],
                                        className="twelve columns",
                                        style={"padding-left": "0"},
                                    ),
                                    ],className='row'),
                                html.Div([
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["短线情绪"], className="subtitle padded"
                                            ),
                                            dcc.Graph(figure=fig),
                                        ],className='twelve columns'),
                                    ],className='row'),
                                html.Div([
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["连板高度"], className="subtitle padded"
                                            ),
                                            dash_table.DataTable(
                                                data=df_stock_lbgd.to_dict('records'),
                                                columns=[{'id': c, 'name': c} for c in df_stock_lbgd.columns],
                                                style_table={'overflowX': 'auto'},
                                                style_cell={
                                                    'height': 'auto',
                                                    # all three widths are needed
                                                    'minWidth': '20px', 'width': '20px', 'maxWidth': '20px',
                                                    'whiteSpace': 'normal',
                                                    'font_size': '13px',
                                                    'text_align': 'center'
                                                },
                                                style_header={
                                                                    "backgroundColor": color_1,
                                                                    "fontWeight": "bold",
                                                                    "color": "white",
                                                                },
                                                # page_current= 0,
                                                # page_size= 10,
                                                # fixed_rows={"headers": True},
                                            ),
                                            
                                        ],className='twelve columns'
                                    ),
                                    
                                    html.Div(id='live-update-text2'),
                                ],className='row'),
                                
                                limitup_info.create_layout(),
                                short_term_statics.create_layout(),
                            ],className='sub_page')
                        ],className='page'
                    )