from functools import reduce
import akshare as ak
from datetime import datetime, timedelta
from sqlalchemy import create_engine,text
import pandas as pd

# TODO 添加以下几个条件限制
# 流通市值小于百亿 ；
# 当前价格处于低位;
# 整个周期在4个月内 最高价排名前2的两个交易日，两交易日相隔22个交易日；
# 该两个交易日相对缩量；
# 当前价已过年线 ；
def compare_price_volume(code,period,gap):
    # period = 15
    # gap = 15
    td = datetime.today()
    dt4 = td.strftime('%Y-%m-%d').replace('-','')
    dt3 = (td - timedelta(days= period)).strftime('%Y-%m-%d').replace('-','')
    dt2 = (td - timedelta(days=period+1)).strftime('%Y-%m-%d').replace('-','')
    dt1 = (td - timedelta(days=period*2)).strftime('%Y-%m-%d').replace('-','')
    # print(dt1,dt2,dt3,dt4)
    stock_zh_a_hist_df_a = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=dt1, end_date=dt2, adjust="")
    stock_zh_a_hist_df_b = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=dt3, end_date=dt4, adjust="")
    c_df = len(stock_zh_a_hist_df_a)
    # print(c_df)
    #剔除新股或交易时间较短的票
    if c_df<11:
        return None

    stock_zh_a_hist_df_b = stock_zh_a_hist_df_b
    
    df_a = stock_zh_a_hist_df_a['最高'].max()
    df_b = stock_zh_a_hist_df_b['最高'].max()


    df_a_l = stock_zh_a_hist_df_a[stock_zh_a_hist_df_a['最高']==stock_zh_a_hist_df_a['最高'].max()] #TODO 这里写错了 应该是最高价匹配的成交量 而不是其他成交量；
    df_b_l = stock_zh_a_hist_df_b[stock_zh_a_hist_df_b['最高']==stock_zh_a_hist_df_b['最高'].max()]
    df_a_l['代码'],df_b_l['代码']=code,code
    df_a_dt,df_b_dt = df_a_l['日期'].iat[0],df_b_l['日期'].iat[0]

    dt_a_b_delta = datetime.strptime(df_b_dt,'%Y-%m-%d')-datetime.strptime(df_a_dt,'%Y-%m-%d')
    # print('dt1 :%s,dt2:%s,dt3:%s,dt4:%s'%(dt1,dt2,dt3,dt4))
    # print(pd.concat([df_a_l,df_b_l], ignore_index=True))
    # print(abs((df_a-df_b)/df_b))
    # print('%s > %s' % (df_a_l['成交量'].tolist()[0],df_b_l['成交量'].tolist()[0]))
    # print('%s > %s' % (dt_a_b_delta.days,gap))
    if abs((df_a-df_b)/df_b) <= 0.015 and dt_a_b_delta.days >= gap and df_a_l['成交量'].tolist()[0]>df_b_l['成交量'].tolist()[0]*1.5:
        return pd.concat([df_a_l,df_b_l],ignore_index=False)
    else:
        return None

def get_stock_pool_model_A():
    engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')
    sql = """select 代码 from stocks_limitup_history 
            where 日期 > '2022-04-27' 
                and (代码 like '60%' or 代码 like '00%') 
                and 总市值< 10000000000 
            group by 代码 having count(*) < 3 """
    # sql = """select distinct 股票代码 from daily_stock where 日期 > '2022-04-27' and 股票代码 = '600493'"""
    df_stocks =  pd.read_sql(text(sql),engine)

    df_zb_lst = []
    for i in df_stocks['代码']:
        df_t = compare_price_volume(i,30,20)
        if df_t is not None:
            df_zb_lst.append(df_t)

    df_stock_pool = reduce(lambda x,y:pd.concat([x,y],ignore_index=True),df_zb_lst)
    df_stock_pool['创建日期'] = datetime.today().strftime('%Y-%m-%d')
    df_stock_pool['模型'] = '跟踪池-阶段底部价升量缩'
    return df_stock_pool

    return df_stock_pool
    
/Users/zif/Downloads/github/industryleader/tasks/stock_pool.py
if __name__ == '__main__':
    engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')
    df_stock_pool = get_stock_pool_model_A()
    df_stock_pool.to_sql('daily_stock_pool', engine, index= False,if_exists='append')
    pass