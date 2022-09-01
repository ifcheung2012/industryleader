from datetime import datetime, timedelta
from dash import Dash
from dash import dcc,html
from dash import dash_table
import plotly as py
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output

import pandas as pd
from sqlalchemy import create_engine

import akshare as ak

# Colours
color_1 = "#892421"
color_2 = "#00ffff"
color_3 = "#002277"
color_b = "#F8F8FF"

engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')

sql_limitup_history = 'select * from stocks_limitup_history'
sql_concept_stocks = 'select * from concept_stocks'



def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table


app = Dash(__name__)
app.title = "奥利奥"

def server_layout():
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
    #央视一套新闻清单
    df_cctv = ak.news_cctv(dt_yesterday)
    df_t = df_cctv.loc[~df_cctv['title'].str.contains('快讯|联播')]
    del df_t['content']
    #财联社新闻清单
    df_cls_d = ak.stock_telegraph_cls()
    df_cls_d['发布日期'] = df_cls_d['发布日期'].replace('-','')
    df_cls = df_cls_d[['发布日期','标题']] #,'发布时间'
    df_cls_t = df_cls.head(10)

    #当日热股清单
    df_stock_hot = pd.read_excel('data/hotstock.xlsx',converters={'股票代码':str})
    df_table_hot = df_stock_hot[['序号','股票代码','股票简称']]
    df_h = df_table_hot.head(10)
    #异动板块、股票清单
    df_stock_yd = pd.read_excel('data/yidong.xlsx',converters={'代码':str})
    df_table_yd = df_stock_yd[['序号','代码','名称','异动日期','异动内容']]
    df_y = df_table_yd.head(10)
    #猪肉批发价行情
    df_zr = ak.futures_pig_info()
    #连板高度分布数据及可视化
    df_stock_lbgd = pd.read_excel('data/每日复盘2022-08-19.xlsx',sheet_name='连板高度')
    fig_zr = go.Figure()
    fig_zr_trace0 = go.Scatter(x=df_zr['date'],y=df_zr['value'],mode="lines",name='y1')
    fig_zr_trace1 = go.Bar(x=df_zr['date'],y=df_zr['value'], name='Y2', yaxis="y2",opacity=0.7)
    data = [fig_zr_trace0,fig_zr_trace1]
    layout = go.Layout(title="猪肉批发价",yaxis=dict(title="Y1"),yaxis2=dict(title="Y2", overlaying='y', side="right"),
    legend=dict(x=0, y=1, font=dict(size=9, color="black")),autosize=True,height=300,template='simple_white') 
    fig_zr = go.Figure(data=data, layout=layout)

    #涨停信息
    #连板高度分布数据及可视化
    df_stock_zt_today = pd.read_excel('data/每日复盘2022-08-19.xlsx',sheet_name='今日涨停',converters={'股票代码':str})
    df_talbe_zt_today = df_stock_zt_today[['所属行业','股票代码','股票名称','涨跌幅','成交额','封板资金','流通市值','最新价','首次封板时间','最后封板时间','炸板次数','连板数','封成比','时间']]

    

    return html.Div(
                children=[  
                    html.Div(
                        [
                            html.Div(
                            [
                                
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
                                            ),
                                        ],
                                        className="twelve columns",
                                        style={"padding-left": "0"},
                                    ),
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
                                                    ["CCTV[08-19]"], className="subtitle padded"
                                            ),
                                            html.Table(make_dash_table(df_t))
                                        ],className='six columns'
                                    ),
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["早盘资讯"], className="subtitle padded"
                                            ),
                                            html.Table(make_dash_table(df_cls_t))
                                        ],className='six columns'
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
                            ],className="sub_page")
                    ],
                    className="page"
                    ),
                    html.Div(
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
                                            
                                        ],className="eight columns"),
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["热点排名"], className="subtitle padded"
                                            ),
                                            html.Table(make_dash_table(df_h.tail(10)))
                                            
                                        ],className="four columns")
                                ],className="row"
                                ),
                                html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["猪肉行情"], className="subtitle padded"
                                            ),
                                            dcc.Graph(figure=fig_zr)
                                        ],className="twelve columns")
                                ],className='row'),
                            ],className="sub_page"
                            )   
                        ],className="page"
                    ),
                    html.Div(
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
                                            )
                                        ],className='twelve columns'
                                    )
                                ],className='row'),
                                html.Div([
                                    html.Div(
                                        [
                                            html.H6(
                                                    ["今日涨停"], className="subtitle padded"
                                            ),
                                             dash_table.DataTable(
                                                data=df_talbe_zt_today.to_dict('records'),
                                                columns=[{'id': c, 'name': c} for c in df_talbe_zt_today.columns],
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
                                                ),
                                        ],className='twelve columns'),
                                    ],className='row'),
                            ],className='sub_page')
                        ],className='page'
                    )
                ]
            )

app.layout = server_layout()

# @app.callback(
# Output('table-paging-and-sorting', 'data'),
# Input('table-paging-and-sorting', "page_current"),
# Input('table-paging-and-sorting', "page_size"),
# Input('table-paging-and-sorting', 'sort_by'))
# def update_table(page_current, page_size, sort_by):
#     if len(sort_by):
#         dff = df_talbe_zt_today.sort_values(
#             sort_by[0]['所属行业'],
#             ascending=sort_by[0]['direction'] == 'asc',
#             inplace=False
#         )
#     else:
#         # No sort is applied
#         dff = df_talbe_zt_today
#     return dff.iloc[
#         page_current*page_size:(page_current+ 1)*page_size
#     ].to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True,port=8058)