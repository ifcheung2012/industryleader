from distutils import errors
from distutils.log import error
from numpy import int64
from blockinflow import get_block_inflow
from blockstocks import get_stocks_block
import efinance as ef
from datetime import datetime
import pandas as pd
from pandas import DataFrame, Int64Dtype
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
    # dtypedic =  {'11b':'int64','10b','9b','8b','7b','6b','5b','4b','3b','2b','1b'}
    # ftmpp.astype({'11b':int64})
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
    # print(df_e)
    df_s['日期'],df_e['日期']=dt_s,dt_e
    i:int = 1

    dfres= pd.merge(df_s,df_e,on=['行业编码','所属行业'],how='left')
    
    dfres.fillna(0,inplace=True)
    def fn(x,dt1,dt2,n):
        a = str(x[str(n)+'b'+dt1])
        b = ''  if x[str(n+1)+'b'+dt2] is None else str(x[str(n+1)+'b'+dt2])
        if a=='' and b=='':
            return ''
        if b=='':
            return a+'->0'
        return a+'->'+b

    def fn_sb(x,dt1,dt2,n):
        a = str(x['1b'+dt1])
        c = '' if x['1b'+dt2] is None else x['1b'+dt2]
        b = ''  if str(x['1b'+dt2]) is None else str(c)
        if a=='' and b=='':
            return ''
        if b=='':
            return a+'|0'
        return a+'->'+b

    while i<=10:
        dfres.loc[:,str(i+1)+'b晋级'] = dfres.apply(lambda x:fn(x,dt_s,dt_e,i),axis=1)
        i+=1

    dfres.loc[:,'首板变动'] = dfres.apply(lambda x:fn_sb(x,dt_s,dt_e,1),axis=1)
    dfres.fillna('',inplace=True)
    return dfres


def get_block_stock_rise(df_stock_block:pd.DataFrame,block:str,rise_n) -> pd.DataFrame:
    df_stock_lst = df_stock_block.loc[(df_stock_block['行业编码']==block)]
    
    return df_stock_lst[['行业编码','所属行业','股票代码','股票名称']]

if __name__ == '__main__' :
    import urllib3
    urllib3.disable_warnings()
    df_stock_block = get_stocks_block()
    dt_s,dt_e = '20220601','20220602'
    # df_s = get_part_analysis_lbs_promotion(df_stock_block,dt_s)
    df_e = get_part_analysis_blocklbs(df_stock_block,dt_e)

    df_stocks_byblock = get_block_stock_rise(df_stock_block,'BK0464',2)
    # df_block = get_block_inflow()
    df_limit_byd = get_stock_limitup_daily(2,'20220602').sort_values(by=['连板数'],ascending=False)
    # dfres_e =  pd.merge(df_block,df_e,on='行业编码',how='left')
    df_res =  pd.merge(df_limit_byd.iloc[:,:13],df_stock_block.iloc[:,1:],on=['股票代码','股票名称'],how='left')
    # dfres_e.fillna(0,inplace=True)
    df_out = df_res.sort_values(by=['连板数','行业编码'],ascending=False)
    df_out = df_out[['连板数','股票名称','日期','成交额','封板资金','流通市值','炸板次数','最后封板时间','所属行业']]
    # df_out['成交额'] = df_out['成交额']/100000000
    # df_out['封板资金'] = df_out['成交额']/100000000
    # df_out['流通市值'] = df_out['成交额']/100000000
    df_out['封成比'] = df_out['封板资金']/df_out['成交额']
    df_out.round({'成交额':2,'封板资金':2,'流通市值':0,'封成比':0})
    # ef.stock.get_latest_quote('')
    from output_style_format import to_excel_auto_column_weight
    with pd.ExcelWriter('~/Downloads/xtxtxt.xlsx',engine="openpyxl") as writer:
        to_excel_auto_column_weight(df_out,writer,'板块涨停标的')
    # print(df_res)
    pass