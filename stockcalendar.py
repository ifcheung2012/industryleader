
import pandas as pd
import efinance as ef
from datetime import datetime, timedelta
import urllib3
import numpy as np

def calendar_stock(beg:str,end:str) -> pd.DataFrame:
    '''
    获取股市的一段时间的交易日期，目前是以茅台的交易日获取的数据

    Parameters
    ----------
    beg: str
        开始日期：格式 '20220101'
    end: str
        结束日期：格式 '20220601'
    date : str
        指定日期，默认为当前日期 格式形如 ``'20220506'``

    Returns
    -------
    DataFrame
        所有交易日期

    Fields
    ------
    ``['索引index', '日期']``
    '''
    
    df=ef.stock.get_quote_history('600519',beg==beg,end=end)
    return df



def get_calendar_lastday(beg: str, N: int, date:  str = None) -> str:
    '''
    获取指定指定日期的上N个交易日
    由于网络抓取，还是框一下数据范围
    Parameters
    ----------
    beg: str
        开始日期：格式 '20220101'
    end: str
        结束日期：格式 '20220601'
    N: int
        前 N 个交易日
    date : str
        指定日期，默认为当前日期 格式形如 ``'20220526'``,格式和其他函数统一

    Returns
    -------
    str : 2022-05-25
    '''
    if date is None:
        date = datetime.today().strftime('%Y-%m-%d')
    else:
        date = datetime.strptime(date,'%Y%m%d').strftime('%Y-%m-%d')

    calendar = calendar_stock(beg, date.replace('-',''))

    dt_cur = calendar.loc[(calendar.日期 == date)]
    
    #当入参日期不是交易日，则向前检索，把前一个交易日作为基准日期(此时N同步调整为0 )
    i=1
    if dt_cur.empty:
        while i<20:

            yesterday = (datetime.strptime(date,'%Y-%m-%d') - timedelta(days= i)).strftime('%Y-%m-%d')
            dt_cur = calendar.loc[(calendar.日期 == yesterday)]
            if dt_cur.empty: 
                i   += 1
                continue
            N -= 1
            break

    ms = calendar.loc[(calendar.index==dt_cur.index[0])]
    dt_pre = calendar.loc[(calendar.index == ms.index[0] - N)]

    return dt_pre.日期.tolist()[0]

    def calenda_today():
        dt_td = datetime.today().strftime('%Y-%m-%d')

if __name__ == '__main__':
    
    urllib3.disable_warnings()

    end_dt = datetime.today().strftime('%Y%m%d')
    # dt2 = get_calendar_lastday('20220401',1,'20220503')

    dt_r = []
    i=1
    while i<10:
        dt_t = get_calendar_lastday('20220401',i,end_dt)
        
        dt_r.append(dt_t.replace('-',''))
        i += 1

    print(dt_r)
    
