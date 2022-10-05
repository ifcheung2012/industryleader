
from dash import dcc,html
from dash import dash_table
from utils import make_dash_table
import akshare as ak
from datetime import datetime, timedelta
from pages.subpages import (
    pre_mkt_plan
)

def create_layout():
    dt_yesterday = (datetime.today()- timedelta(days= 1)).strftime('%Y-%m-%d').replace('-','')
    #央视一套新闻清单
    df_cctv = ak.news_cctv(dt_yesterday)
    df_t = df_cctv.loc[~df_cctv['title'].str.contains('快讯|联播')]
    del df_t['content']

    #财联社新闻清单
    df_cls_d = ak.stock_telegraph_cls()
    df_cls_d['发布日期'] = df_cls_d['发布日期'].replace('-','')
    df_cls = df_cls_d[['发布日期','标题']] #,'发布时间'
    df_cls_t = df_cls.loc[~(df_cls.标题.str.strip()=='')]
    df_cls_a = df_cls_t.head(10)
    
    return html.Div(
                    [
                            html.Div(
                            [
                                dcc.Interval(id='interval-5s',interval=5*1000,n_intervals=0),
                                dcc.Interval(id='interval-5m',interval=1*1000*300,n_intervals=0),
                                dcc.Interval(id='interval-15m',interval=1*1000*900,n_intervals=0),
                                dcc.Interval(id='interval-30m',interval=1*1000*1800,n_intervals=0),
                                dcc.Interval(id='interval-60m',interval=1*1000*3600,n_intervals=0),
                                
                                html.Div(
                                [  
                                    html.Div(
                                        [
                                            html.Div(
                                                [html.H5("盘前信息")],
                                                className="seven columns main-title",
                                            ),
                                            html.Div(
                                                [
                                                    dcc.Link(
                                                        "08-18",
                                                        href="/dash-financial-report/full-view",
                                                        className="full-view-link",
                                                    )
                                                ],
                                                className="five columns",
                                                style={"width": "24.625%"},
                                            ),
                                        ],id="wrapper",
                                        className="twelve columns",
                                        
                                    )
                                    ],className='row'),
                                html.Div(
                                [  
                                    html.Div(
                                            [
                                                html.H5("早盘信息观察"),
                                                html.Br([]),
                                                html.P(
                                                    "\
                                                每个交易日开盘前，先把你写的东西全部读一遍，警示自己不要重复跳坑，按交易模式，\
                                                在环境符合模式的前提下，再按照模式原则选择符合模式的那一个唯一的标的交易，环境 \
                                                不符合交易模式，必须空仓。昨日芯片从竞价开始分歧，大港盘中炸板 ，分歧比预期的 \
                                                要大，但是盘中资金又部分回流芯片。昨日收盘大港受到关注函，今日注定大港会大换手，\
                                                所以核吸大港才是最好的介入方式。",
                                                    style={"color": "#ffffff"},
                                                    className="row",
                                                ),
                                            ],
                                            className="product",
                                        ),
                                ],className='row'),
                                html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H6(
                                                    [f"CCTV[{dt_yesterday}]"], className="subtitle padded"
                                            ),
                                            html.Table(make_dash_table(df_t))
                                        ],className='six columns'
                                    ),
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["早盘资讯"], className="subtitle padded"
                                            ),
                                            html.Table(make_dash_table(df_cls_a))
                                        ],className='six columns',
                                    )
                                ],className='row'),
                                html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["历史行情"], className="subtitle padded"
                                            ),
                                            
                                        ],className="twelve columns")
                                ],className='row'),
                                html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["大盘走势"], className="subtitle padded"
                                            ),
                                            
                                        ],className="twelve columns")
                                ],className='row'),
                                html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["关注板块"], className="subtitle padded"
                                            ),
                                            
                                        ],className="twelve columns")
                                ],className='row'),
                                pre_mkt_plan.create_layout(),
                            ],className="sub_page")
                    ],
                    className="page"
                    )