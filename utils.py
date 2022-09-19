from dash import html


def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []

    html_row1 = []
    for c in df.columns:
        html_row1.append(html.Td([c]))
    table.append(html.Tr(html_row1))

    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    
    return table

#画蜡烛图-plotly版本1
def can_vol(dataframe=None, start=80,end=180, name='Candlestick'):
    import plotly
    import numpy as np
    import plotly.graph_objects as go
    data1 = dataframe.iloc[start:end, :]  # 区间，这里我只是测试，并没有真正用时间来选
    data1 = data1.sort_index(axis=0, ascending=True)
    # 生成新列，以便后面设置颜色
    data1['diag']=np.empty(len(data1))  
    # 设置涨/跌成交量柱状图的颜色
    data1.diag[data1.Close>data1.Open]='#fcf8b3'
    data1.diag[data1.Close<=data1.Open]='#80ef91'  
    layout = go.Layout(title_text=name,title_font_size=30, autosize=True, margin=go.layout.Margin(l=10, r=1, b=10),
                       xaxis=dict(title_text="Candlesticck", type='category'),
                       yaxis=dict(title_text="<b>Price</b>"),
                       yaxis2 = dict(title_text="<b>Volume</b>", anchor="x", overlaying="y",side="right"))  
    # layout的参数超级多，因为它用一个字典可以集成所有图的所有格式
    #这个函数里layout值得注意的是 type='category'，设置x轴的格式不是candlestick自带的datetime形式，
    #因为如果用自带datetime格式总会显示出周末空格，这个我找了好久才解决周末空格问题。。。       
    candle = go.Candlestick(x=data1.index,
                       open=data1.Open, high=data1.High,
                       low=data1.Low, close=data1.Close, increasing_line_color='#f6416c',
                       decreasing_line_color='#7bc0a3', name="Price")
    vol = go.Bar(x=data1.index,
                 y=data1.Volume, name="Volume", marker_color=data1.diag, opacity=0.5, yaxis='y2')  
    # 这里一定要设置yaxis=2, 确保成交量的y轴在右边，不和价格的y轴在一起
    data = [candle, vol]
    fig = go.Figure(data, layout)
    plotly.offline.init_notebook_mode() 
    # 如果不是在jupyter notebook 里运行，最后两行用plotly.offline.plot(fig)代替，输出到浏览器里面
    plotly.offline.iplot(fig, filename='Candlestick')

