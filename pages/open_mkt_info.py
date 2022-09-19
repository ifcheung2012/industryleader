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
    sql_concept_change = """select a.*,f.`股票名称` from concept_stock_change a 
INNER JOIN ( SELECT DISTINCT 股票代码,股票名称 FROM daily_stock ) AS f ON a.代码 = f.股票代码 
where a.日期 in (select max(日期) from concept_stock_change) and  a.代码 in 
                            ( SELECT 代码
                                FROM
                                    (
                                    SELECT
                                        concept_stock_change.日期,
                                        concept_stock_change.代码,
                                        b.名称,
                                        concept_stock_change.异动内容,
                                        substring(concept_stock_change.异动内容,9) as 异动
                                    FROM
                                        concept_stock_change
                                        INNER JOIN ( SELECT DISTINCT 代码,名称 FROM concept_stock ) AS b ON concept_stock_change.代码 = b.代码 
                                    ) AS c 
                                WHERE
                                    c.异动内容 <> '[个股添加概念]标普道琼斯A股' 
                                    AND c.名称 NOT LIKE '%ST%' 
                                    AND c.名称 NOT LIKE '%退%' 
                                    AND c.代码 <> '暂无成份股数据' 
                                    AND left(c.代码,1) <> 8
                                    AND left(c.代码,1) <> 3
                                    AND left(c.代码,1) <> 6
                                    AND c.日期 in (select max(日期) from concept_stock_change)
                                GROUP BY c.日期,c.代码,c.名称,c.异动
                                HAVING count(*)<2
                            ) """

    #当日热股清单
    df_stock_hot = pd.read_excel('data/hotstock.xlsx',converters={'股票代码':str})
    df_table_hot = df_stock_hot[['序号','股票代码','股票简称']]
    df_h = df_table_hot.head(10)
    #异动板块、股票清单
    df_stock_yd = pd.read_sql(text(sql_concept_change),engine)
    df_table_yd = df_stock_yd[['代码','股票名称','日期','异动内容']]
    df_y = df_table_yd
    df_y['近一周异动次数']=randint(1,10)
    df_y['近一个月异动次数']=randint(1,10)
    df_y['近两个月异动次数'] = randint(1,10)
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