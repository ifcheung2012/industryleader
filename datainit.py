from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd
import pandas.io.sql as psql
from blockstocks import get_stocks_block
from get_stock_limit import get_stock_limitup_daily
from stockcalendar import calendar_stock, get_calendar_lastday

engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')

def calendarinit(reset) -> pd.DataFrame:
    date = datetime.today().strftime('%Y-%m-%d')
    df = pd.DataFrame()

    sql = '''
    select * from stock_calendar;
    '''
    df = pd.read_sql_query(sql, engine)
    
    if df.shape[0]<1 or reset==1:
        df = calendar_stock('20050101', date.replace('-',''))
        df.to_sql('stock_calendar', engine, index= False,if_exists='replace')

    return df[['日期']]

def blockstocks(reset) -> pd.DataFrame:
    sql = '''
    select * from stocks_block;
    '''
    df = pd.read_sql_query(sql, engine)  
    #如果数据库没有数据，就重新获取
    if df.shape[0]<1 or reset==1:
        df = get_stocks_block()
        df.to_sql('db_stocks_block', engine, index= False,if_exists='replace')

    return df

def stocklimitup(dt_e,reset) -> pd.DataFrame:
    dt_e = get_calendar_lastday('20220101',1,dt_e)
    dt_e = dt_e.replace('-','')
    sql = 'select * from limitup_daily where 日期=\''+dt_e+'\''
    df = pd.DataFrame()
    df = pd.read_sql_query(sql, engine)  
    #如果数据库没有数据，就重新获取
    if df.shape[0]<1 or reset==1:
        df = get_stock_limitup_daily(1,dt_e)
        df.to_sql('limitup_daily', engine, index= False,if_exists='append')

    df1 = df.drop(['所属行业'],axis=1)
    df2 =  blockstocks(0)
    df3 = df2[['股票代码','行业编码','所属行业']]
    df =  df1.merge(df3,on='股票代码',how='left')

    return df


if __name__ == '__main__':
    # df = stocklimitup('20220620',0)
    # df = stocklimitup('20220619',0)
    # df = stocklimitup('20220616',0)
    df = calendarinit(0)
    print(df)
    pass