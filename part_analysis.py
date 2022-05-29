from blockstocks import get_stocks_block

from datetime import datetime
import pandas as pd
from pandas import DataFrame
from get_stock_limit import get_stock_dbs_daily , get_stock_limitup_daily
from stockcalendar import get_calendar_lastday


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

def get_part_analysis_lbs_promotion(df_stock_block:pd.DataFrame, dt_e:str) -> pd.DataFrame:

    dt_l = get_calendar_lastday('20220101',1,dt_e)
    dt_s = datetime.strptime(dt_l,'%Y-%m-%d').strftime('%Y%m%d')

    df_s = get_part_analysis_blocklbs(df_stock_block,dt_s)
    df_e = get_part_analysis_blocklbs(df_stock_block,dt_e)

    # data_types_dict = {'Age': str}
    # df=df_s.rename({'11b':'12b','10b':'11b','9b':'10b','8b':'9b','7b':'8b','6b':'7b','5b':'6b','4b':'5b','3b':'4b','2b':'3b','1b':'2b'},axis=1)
    lst_col = ['11b','10b','9b','8b','7b','6b','5b','4b','3b','2b','1b']
    lsts,lste = [],[]
    for l in lst_col:
        lsts.append(l+dt_s)
        lste.append(l+dt_e)
        # df_s[l] = df_s[l].astype('float').astype('int')
        # df_e[l] = df_e[l].astype('float').astype('int')

    dic_res_s,dic_res_e = dict(zip(lst_col,lsts)),dict(zip(lst_col,lste))

    df_s.rename(columns=dic_res_s,inplace=True)
    df_e.rename(columns=dic_res_e,inplace=True)
    # del df['12b'] 

    df_s['日期'],df_e['日期']=dt_s,dt_e
    i:int = 1

    dfres= pd.merge(df_s,df_e,on=['行业编码','所属行业'],how='left')
    # dfres.fillna('',inplace=True)
    def fn(x,dt1,dt2,n):
        a = str(x[str(n)+'b'+dt1])
        b = ''  if x[str(n+1)+'b'+dt2] is None else str(x[str(n+1)+'b'+dt2])
        if a=='' and b=='':
            return '-'
        if b=='':
            return a+'|0'
        return a+'|'+b

    def fn_sb(x,dt1,dt2,n):
        a = str(x['1b'+dt1])
        c = '' if x['1b'+dt2] is None else x['1b'+dt2]
        b = ''  if str(x['1b'+dt2]) is None else str(c)
        if a=='' and b=='':
            return '-'
        if b=='':
            return a+'|0'
        return a+'|'+b

    while i<=10:
        dfres.loc[:,str(i+1)+'b晋级'] = dfres.apply(lambda x:fn(x,dt_s,dt_e,i),axis=1)
        i+=1

    dfres.loc[:,'首板变动'] = dfres.apply(lambda x:fn_sb(x,dt_s,dt_e,1),axis=1)

    return dfres

if __name__ == '__main__' :
    # import urllib3
    # urllib3.disable_warnings()
    # df_stock_block = get_stocks_block()
    dt_s,dt_e = '20220526','20220527'
    # df_s = get_part_analysis_blocklbs(df_stock_block,dt_s)
    # df_e = get_part_analysis_blocklbs(df_stock_block,dt_e)
    # df_s['日期'],df_e['日期']=dt_s,dt_e
    # # df_r = pd.concat([df_s,df_e],keys=['行业编码','所属行业'])
    # # n:int = 1
    # # while n<12:
    # fff = df_s[['日期','1b']].loc[(df_s.日期==dt_s)]
    # print(fff)
    # df_s.to_excel('12.xlsx')

    lst_col = ['11b','10b','9b','8b','7b','6b','5b','4b','3b','2b','1b']
    lsts,lste = [],[]
    for l in lst_col:
        lsts.append(l+dt_s)
        lste.append(l+dt_e)

    dic_res_s,dic_res_e = dict(zip(lst_col,lsts)),dict(zip(lst_col,lste))
    print(dic_res_s)
    print(dic_res_e)
    pass