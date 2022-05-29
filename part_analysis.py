from blockstocks import get_stocks_block

from datetime import datetime
import pandas as pd
from pandas import DataFrame
from get_stock_limit import get_stock_dbs_daily , get_stock_limitup_daily


def get_part_analysis_blocklbs(df_stock_block:pd.DataFrame,date:str) -> pd.DataFrame:
    

    dfr = get_stock_limitup_daily(1,date) #连板数>=1,=1时即首板;

    fd = pd.merge(dfr,df_stock_block,on='股票代码',how='left').rename({'所属行业_x':'所属行业'},axis=1)

    ftmp:DataFrame = fd.groupby(['行业编码','所属行业']).agg({'股票代码':'count'}).reset_index()
    ftmpp = ftmp.rename({'股票代码':'涨停个股数量'},axis=1)  
    n:int = 1
    while n<=11:
        
        ff = fd.loc[(fd.连板数 == n)].groupby(['行业编码','所属行业']).agg({'连板数':'count'}).reset_index()
        ddd=ff.rename({'连板数':str(n)+'b'},axis=1)
        ftmpp = pd.merge(ftmpp,ddd,on=['行业编码','所属行业'],how='left') 
        n=n+1

    ftmpp.fillna('',inplace=True)
    ftmpp = ftmpp.sort_values(by=['11b','10b','9b','8b','7b','6b','5b','4b','3b','2b','1b'],ascending=True)

    return ftmpp


if __name__ == '__main__' :
    import urllib3
    urllib3.disable_warnings()
    df_stock_block = get_stocks_block()
    dt_s,dt_e = '20220526','20220527'
    df_s = get_part_analysis_blocklbs(df_stock_block,dt_s)
    df_e = get_part_analysis_blocklbs(df_stock_block,dt_e)
    df_s['日期'],df_e['日期']=dt_s,dt_e
    # df_r = pd.concat([df_s,df_e],keys=['行业编码','所属行业'])
    # n:int = 1
    # while n<12:
    fff = df_s[['日期','1b']].loc[(df_s.日期==dt_s)]
    print(fff)
    # df_s.to_excel('12.xlsx')
    pass