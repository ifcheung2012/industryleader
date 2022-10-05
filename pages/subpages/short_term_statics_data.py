from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine,text
import akshare as ak
from environment.settings import *


def get_data4layout(period=20):
    td = datetime.today()
    str_end = td.strftime('%Y-%m-%d')
    start = td - timedelta(days= period)
    str_start = start.strftime('%Y-%m-%d')
    dt_rng = pd.date_range(start=str_start,end=str_end,freq='D')
    dt_df = dt_rng.to_frame()
    dt_df.rename({0:'日期'},axis=1,inplace=True)

    dt_dt = ak.tool_trade_date_hist_sina()
    dt_dt['日期'] = dt_dt['trade_date'].astype('datetime64')
    ds = dt_dt.loc[(dt_dt['日期']>=start) & (dt_dt['日期']<=td)]
    ds.set_index('日期',inplace=True)
    dd = ds.resample('D').max().reset_index()
    df_res = dd.loc[(dd.trade_date.isna())]
    ddf = ds.reset_index()
    engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')

    sql_zts = f"select 日期,count(*) as 涨停数 from stocks_limitup_history where 日期>='{str_start}' and 日期<='{str_end}' GROUP BY 日期 order by 日期"
    sql_dts = f"select 日期,count(*) as 跌停数 from stocks_limitup_history_dtgc  where  日期>='{str_start}' and 日期<='{str_end}' GROUP BY 日期 order by 日期"
    sql_scgd =f"select 日期, max(连板数) as 市场高度 from stocks_limitup_history  where 日期>='{str_start}' and 日期<='{str_end}' GROUP BY 日期 order by 日期"
    sql_lbs = f"select 日期 ,count(*) as 连板数量 from stocks_limitup_history where 连板数>1 and 日期>='{str_start}' and 日期<='{str_end}' GROUP BY 日期 order by 日期"

    df_zts = pd.read_sql(sql_zts,engine)
    df_dts = pd.read_sql(sql_dts,engine)
    df_scgd= pd.read_sql(sql_scgd,engine)
    df_lbs = pd.read_sql(sql_lbs,engine)
    # print(sql_zts)
    return df_zts ,df_dts ,df_scgd,df_lbs, ddf,df_res