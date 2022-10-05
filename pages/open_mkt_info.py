from datetime import datetime, timedelta
from functools import reduce
from random import randint, random
import pandas as pd
from sqlalchemy import create_engine,text
from dash import dcc,html
from dash import dash_table
import plotly.graph_objects as go
from utils import make_dash_table
import akshare as ak
from environment.settings import *

def get_fund_flow():
    fund_flow_df = ak.stock_fund_flow_concept(symbol="即时")
    fund_flow_df = fund_flow_df[['行业','净额','公司家数','行业指数']]
    fund_flow_df['期间']="即时"
    fund_flow_df3 = ak.stock_fund_flow_concept(symbol="3日排行")
    fund_flow_df3['期间']="3日排行"
    fund_flow_df5 = ak.stock_fund_flow_concept(symbol="5日排行")
    fund_flow_df5['期间']="5日排行"
    fund_flow_df10 = ak.stock_fund_flow_concept(symbol="10日排行")
    fund_flow_df10['期间']="10日排行"
    fund_flow_df20 = ak.stock_fund_flow_concept(symbol="20日排行")
    fund_flow_df20['期间']="20日排行"
    df_flow_lst = [fund_flow_df,fund_flow_df3,fund_flow_df5,fund_flow_df10,fund_flow_df20]
    df_flow_res = reduce(lambda x,y:pd.concat([x,y],ignore_index=False),df_flow_lst)
    except_lst = ['融资融券','深股通','标普道琼斯A股','MSCI概念','同花顺漂亮100','半年报预增','沪股通','证金持股','华为概念']
    df_flow_res = df_flow_res.loc[(~df_flow_res.行业.isin(except_lst))]

    return df_flow_res

def create_layout():
    engine = create_engine(f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8')
    sql_concept_change = """select aa.`代码`,bb.`股票名称`,cc.异动内容,aa.`近一周`,aa.`近20天`,aa.`近一个月` from (select a.`代码`,a.`近一周`,b.`近20天`,c.`近一个月` from 
                    (
                    select abc.代码,count(*) AS 近一周 from (
                    select 日期,代码,count(代码) from concept_stock_change 
                    where DATE_SUB(CURDATE(), INTERVAL 7 DAY) <= date(日期)
                    AND 代码 in (select distinct 代码 from concept_stock_change where TO_DAYS(NOW()) - TO_DAYS(日期) <1 )
                    GROUP BY 日期,代码 ) as abc GROUP BY abc.代码
                    ) as a
                    left join 
                    -- 近20天
                    (
                    select bbc.代码,count(*) AS 近20天 from (
                    select 日期,代码,count(代码)  from concept_stock_change 
                    where DATE_SUB(CURDATE(), INTERVAL 20 DAY) <= date(日期)
                    AND 代码 in (select distinct 代码 from concept_stock_change where TO_DAYS(NOW()) - TO_DAYS(日期) <1 )
                    GROUP BY 日期,代码) as bbc GROUP BY bbc.代码
                    ) as b on a.`代码`=b.`代码`
                    left join 
                    -- 近一个月
                    (
                    select cbc.代码,count(*) AS 近一个月 from (
                    select 日期,代码,count(代码)  from concept_stock_change 
                    where DATE_SUB(CURDATE(), INTERVAL 30 DAY) <= date(日期)
                    AND 代码 in (select distinct 代码 from concept_stock_change where TO_DAYS(NOW()) - TO_DAYS(日期) <1 )
                    GROUP BY 日期,代码) as cbc GROUP BY cbc.代码
                    ) as c on a.`代码`=c.`代码`
                    ) as aa
                    left join (select distinct 股票代码,股票名称 from  daily_stock) as bb on aa.`代码`=bb.`股票代码`
                    left join (select 代码,GROUP_CONCAT(异动内容) as '异动内容' from concept_stock_change where TO_DAYS(NOW()) - TO_DAYS(日期) <1
                    GROUP BY 代码) as cc on aa.`代码`=cc.`代码`
                    where
                        cc.异动内容 <> '[个股添加概念]标普道琼斯A股' 
                        AND bb.股票名称 NOT LIKE '%ST%' 
                        AND bb.股票名称 NOT LIKE '%退%' 
                        AND aa.代码 <> '暂无成份股数据' 
                        AND left(aa.代码,1) <> 8
                        AND left(aa.代码,1) <> 3
                        AND left(aa.代码,3) <> 688
                    ORDER BY 近一个月,近20天,近一周"""

    #当日热股清单
    df_stock_hot = pd.read_excel('data/hotstock.xlsx',converters={'股票代码':str})
    df_table_hot = df_stock_hot[['序号','股票代码','股票简称']]
    df_h = df_table_hot.head(10)
    #异动板块、股票清单
    df_stock_yd = pd.read_sql(text(sql_concept_change),engine)
    # df_table_yd = df_stock_yd[['代码','股票名称','日期','异动内容']]
    df_y = df_stock_yd

    #猪肉批发价行情
    df_zr = ak.futures_pig_info()
    #可视化猪肉批发价走势
    fig_zr = go.Figure()
    fig_zr_trace0 = go.Scatter(x=df_zr['date'],y=df_zr['value'],mode="lines",name='y1')
    fig_zr_trace1 = go.Bar(x=df_zr['date'],y=df_zr['value'], name='Y2', yaxis="y2",opacity=0.7)
    data = [fig_zr_trace0,fig_zr_trace1]
    layout = go.Layout(yaxis=dict(title="Y1"),yaxis2=dict(title="Y2", overlaying='y', side="right"),
    legend=dict(x=0, y=1, font=dict(size=9, color="black")),autosize=True,height=300,template='simple_white',
    margin={
           "r": 30,
           "t": 30,
           "b": 30,
           "l": 30,
       },) 
    fig_zr = go.Figure(data=data, layout=layout)

    # 概念资金流入热点图
    df_flow_res = get_fund_flow()
    fig2 = go.Figure(data=go.Heatmap(
        z=df_flow_res['净额'],
        x=df_flow_res['行业'],
        y=df_flow_res['期间'],
        colorscale='YlOrRd'))

    fig2.update_layout(
        margin={
           "r": 30,
           "t": 30,
           "b": 30,
           "l": 30,
       },
        )
    fig2.update_xaxes(
            tickangle = 300,
            title_text = "Month",
            title_font = {"size": 20},
            title_standoff = 25,
            # showticklabels=False
            )
            
    return html.Div(
                        [
                            html.Div(
                            [
                                html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["异动监测"], className="subtitle padded"
                                            ),
                                            html.Table(make_dash_table(df_y))
                                            
                                        ],className="twelves columns"),
                                ],className="row"
                                ),
                                html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["热点排名-同花顺"], className="subtitle padded"
                                            ),
                                            html.Table(make_dash_table(df_h.tail(10)))
                                            
                                        ],className="three columns"),
                                        
                                        html.Div(
                                         style={"padding": "0px", "margin": "0px", "width": "15px",
                                         "display": "block","flex-direction": "column","vertical-align": "top"}
                                        ),
                                        html.Div(
                                        [
                                            html.H6(
                                                    ["热点排名-淘股吧"], className="subtitle padded"
                                            ),
                                            html.Table(make_dash_table(df_h.head(10)))
                                            
                                        ],className="three columns"),
                                        html.Div(
                                        [],className="one columns"),
                                        html.Div(
                                        [
                                            html.H6(
                                                    ["热点排名-雪球"], className="subtitle padded"
                                            ),
                                            html.Table(make_dash_table(df_h.tail(10)))
                                            
                                        ],className="three columns"),
                                        html.Div(
                                        [
                                            html.H6(
                                                    ["热点排名-东财"], className="subtitle padded"
                                            ),
                                            html.Table(make_dash_table(df_h.tail(10)))
                                            
                                        ],className="three columns right-aligned"),
                                ],className="row"
                                ),
                                html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["猪肉行情"], className="subtitle padded"
                                            ),
                                            dcc.Graph(figure=fig_zr,config={"displayModeBar": False})
                                        ],className="twelve columns")
                                ],className='row'),
                                html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["概念资金流入情况"], className="subtitle padded"
                                            ),
                                            dcc.Graph(figure=fig2,config={"displayModeBar": False})
                                        ],className="twelve columns")
                                ],className='row'),
                            ],className="sub_page"
                            )   
                        ],className="page"
                    )