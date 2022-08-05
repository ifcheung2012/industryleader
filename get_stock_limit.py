import pandas as pd
import requests
from datetime import datetime, timedelta
from jsonpath import jsonpath
import numpy as np

from stockcalendar import get_calendar_lastday


def get_zt_stock_rank(date: str = None) -> pd.DataFrame:
    """
    获取指定日期涨停股票行情

    Parameters
    ----------
    date : str
        指定日期，默认为当前日期 格式形如 ``'20220506'``

    Returns
    -------
    DataFrame
        指定日期涨停股票行情

    Fields
    ------
    ``['日期', '股票代码', '股票名称', '涨跌幅', '成交额', '封板资金', '流通市值', '最新价', '换手率','首次封板时间', '最后封板时间', '炸板次数', '连扳数', '所属行业']``
    """
    if date is None:
        date = datetime.today().strftime('%Y%m%d')
    params = (
        ('ut', '7eea3edcaed734bea9cbfc24409ed989'),
        ('dpt', 'wz.ztzt'),
        ('Pageindex', '0'),
        ('pagesize', '10000'),
        ('sort', 'fbt:asc'),
        ('date', date),
    )

    response = requests.get(
        'http://push2ex.eastmoney.com/getTopicZTPool', params=params,  verify=False)
    fields = {
        'c': '股票代码',
        'n': '股票名称',
        'zdp': '涨跌幅',
        'amount': '成交额',
        'fund': '封板资金',
        'ltsz': '流通市值',
        'p': '最新价',
        'hs': '换手率',
        'fbt': '首次封板时间',
        'lbt': '最后封板时间',
        'zbc': '炸板次数',
        'lbc': '连板数',
        'hybk': '所属行业'
    }
    items = jsonpath(response.json(), '$..pool[:]')
    if not items:
        df = pd.DataFrame(
            columns=['日期']+list(fields.values())+['统计天数', '涨停次数'])
        return df
    df = pd.DataFrame(items)
    extra_df: pd.DataFrame = pd.DataFrame.from_records(df['zttj']).rename(columns={
        'days': '统计天数',
        'ct': '涨停次数'
    })
    df: pd.DataFrame = pd.concat([df, extra_df], axis=1)
    df: pd.DataFrame = df.rename(columns=fields)[fields.values()]
    df['首次封板时间'] = df['首次封板时间'].apply(lambda x: pd.to_datetime(
        str(x), format='%H%M%S').strftime('%H:%M:%S'))
    df['最后封板时间'] = df['最后封板时间'].apply(lambda x: pd.to_datetime(
        str(x), format='%H%M%S').strftime('%H:%M:%S'))
    df['最新价'] /= 1000
    df['涨跌幅'] = df['涨跌幅'].apply(lambda x: round(x, 2))
    df.insert(0, '日期', date)
    
    return df

def grade(x,dt1,dt2):
    score = 0
    # if x['首次封板时间'] > x['最后封板时间']:
    #     score += 10
    # else:
    #     score -=10
    return score

# df3['封板评分'+dt2]=df3.apply(lambda x:grade(x,dt1,dt2),axis=1)
# df4=df3.loc[('首次封板时间'+dt2)]
# 


'''
# 哪些股票今日2进3，3进4等：where 今日连板=3 昨日连板10个，成功晋级4个，那数据在2->3 显示4/10
# 昨日2板，今日3板；
# def up(x,dt1,dt2):
#     if pd.isna(x['连板数'+dt2]):
#         return '止步于:'+ str(x['连板数'+dt1]) +'板'
#     else:
#         return '晋级成功:'+str(x['连板数'+dt1])+'进'+str(x['连板数'+dt2])

# df3.loc[:,'晋级']=df3.apply(lambda x:up(x,dt1,dt2),axis=1)
# df3.to_csv('20220524.csv',encoding='utf_8_sig')
# 首版晋级成功率
# def compr(a,b,df,dt1,dt2):
#     x = str(df.loc[(df['连板数'+dt1]==a)].count()['连板数'+dt1])
#     y = str(df.loc[(df['连板数'+dt2]==b)].count()['连板数'+dt2])
#     return y+'/'+x
'''


#指定日期的断板数,lbs:连板数,dt1/dt2相连两天; 统计有哪些股票昨天连板今日止步的；
def get_stock_dbs_daily(lbs:int,dt_end) -> pd.DataFrame:
    """
    999
    """

    dt_end  = datetime.today().strftime('%Y%m%d') if (dt_end == '') else dt_end
    
    dt_last = get_calendar_lastday('20220501',1,dt_end)  #todo 这里优化一下
    dt_last= datetime.strptime(dt_last,'%Y-%m-%d').strftime('%Y%m%d') 

    df_last = get_zt_stock_rank(dt_last)
    df_end  = get_zt_stock_rank(dt_end)

    dftp = df_last.loc[(df_last.连板数==lbs)]
    dfres = dftp[~dftp.股票代码.isin(df_end.股票代码)]

    return dfres


#统计今日连板
def get_stock_limitup_daily(lbs:int,date:str) -> pd.DataFrame:

    tomorrow = (datetime.strptime(date,'%Y%m%d') + timedelta(days= 1)).strftime('%Y%m%d')
    
    dt_s = get_calendar_lastday('20220101',1,tomorrow).replace('-','')
    
    df = get_zt_stock_rank(dt_s)
    dd = df.loc[(df.连板数 >= lbs)]

    return dd

# dfres = today_lb(1,'20220526')
# dfr=dfres.merge(df_res,on='股票代码',how='left')

if __name__ == '__main__' :
    # print(get_stock_dbs_daily(3,'20220504'))
    df = get_stock_limitup_daily(1,'20220802').sort_values(by=['连板数','炸板次数'],ascending=False)
    
    # df = dfr.groupby('所属行业').apply(lambda x: x[x.封板资金==x.封板资金.max()])
    # df.index = df.index.droplevel() #去除重复的index

    # df['成交额'] = df['成交额']/100000000
    # df['封板资金'] = df['封板资金']/100000000
    # df['流通市值'] = df['流通市值']/100000000
    # df['封成比'] = df['封板资金'] / df['成交额']
    # df = df.round(1)
    # print(df.loc[(~df['股票名称'].str.contains('N'))&(~df['股票名称'].str.contains('ST'))&(~df['股票名称'].str.contains('退'))]) #非新股、非ST、非退市股票
    # df.to_excel('~/Downloads/limitup20220630-6.xlsx',index=False)
    
    print(df)
    pass







