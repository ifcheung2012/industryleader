from distutils import errors
from distutils.log import error
from numpy import int64
from blockinflow import get_block_inflow
from blockstocks import get_stocks_block
import efinance as ef
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pandas import DataFrame, Int64Dtype
from get_stock_limit import get_stock_dbs_daily , get_stock_limitup_daily
from stockcalendar import calendar_stock, get_calendar_lastday
from pandas.io.formats.style import Styler
from sqlalchemy import create_engine
import pandas.io.sql as psql

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


def get_stock_limitup_gantt(days,lbs):
    """
    获取指定日期范围内，有过连板(连板数不低于lbs)的个股及其甘特图
    Parameters
    ----------
        days: Int  向前统计多少个交易日，比如：200 至今两百个交易日区间的数据
        lbs:  Int  连板数，即：连板数大于几的才纳入统计范围； 比如:连板3板
    Returns
    -------
    Styler,DataFrame
        带样式数据(格式：Styler)，不带样式的数据（格式：dataframe）
    """
    end_dt = datetime.today().strftime('%Y%m%d')
    tomorrow = (datetime.strptime(end_dt,'%Y%m%d') + timedelta(days= 1)).strftime('%Y%m%d')
    dt_r,i,n = [],1,days

    while i<n:
        dt_t = get_calendar_lastday('20210101',i,tomorrow)
        dt_r.append(dt_t.replace('-',''))
        i += 1

    dt_range = dt_r[::-1]
    df_res = pd.DataFrame()
    for dt in dt_range :
        df_limitup = get_stock_limitup_daily(lbs,dt)
        df_res = pd.concat([df_res,df_limitup])

    # df = pd.read_excel('~/Downloads/data.xlsx',sheet_name='Sheet2')
    df = df_res[['股票名称','日期','连板数']]
    df1 = df.dropna()
    df2 = df1.groupby(['日期','股票名称']).agg({'连板数':'mean'}).reset_index().sort_values(by=['股票名称','日期'])
    # df2.groupby(['股票名称']).get_group('中通客车')
    df3 =  df2.drop_duplicates(['股票名称'])
    df4 = pd.DataFrame(columns = dt_range)
    for i in df3['股票名称']:
        dft = df2.groupby(['股票名称']).get_group(i).T.reset_index().drop(1,axis=0)
        ar = np.array(dft)
        lst = ar.tolist()
        dft.columns = lst[0]
        dft['股票名称'] = i
        dft.reset_index().drop(index = 0,axis=0)
        df4 = pd.concat([dft,df4])

    df5 = df4.loc[(df4.日期!='日期')]
    df5.insert(0,'股票名称',df5.pop('股票名称'))
    df6 = df5.fillna(0).reindex(sorted(df5.columns), axis=1)

    df7 = df6.sort_values(by=dt_range[::-1],ascending=True)

    df8 = df7.drop(['日期'],axis=1).reset_index(drop=True)
    df8['max'] = df8[dt_range].max(axis=1)

    #设计渐变样式 gantt
    
    import seaborn as sns

    cm =  sns.light_palette('green',as_cmap=True)
    def color_negative_red(val):
        color = 'gray' if val < 1 else 'red'
        return 'color: %s' % color

    def makepretty(styler):
        styler.background_gradient(cmap=cm,subset=dt_range)
        c,i = [],0
        while i < len(dt_range):
            c.append('{:0}') 
            i += 1
        styler.format(dict(zip(dt_range,c)))
        # styler.set_caption("期间连板情况排行")
        # styler.hide_index()
        return styler
    df9 =  df8.loc[(df8['max']>=2)] #只统计有过4板及以上的股票

    return df9.style.pipe(makepretty),df9

def get_stock_destribute():
    engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')

    df = ef.stock.get_realtime_quotes(fs=['沪深A股'])
    df['股票代码']

    col = list(df.columns)
    col.remove('股票代码')
    col.remove('股票名称')
    col.remove('行情ID')
    col.remove('市场类型')
    df[col] = df[col].apply(pd.to_numeric,errors='coerce').fillna(0.0)
    # df.dtypes
    df[col].astype(float)
    df.dtypes
    # df.to_sql('stock_daily_info', engine, index= False,if_exists='append')
    sql =  'select * from db_stocks_block'
    df_bs = pd.read_sql(sql,engine)
    dx = df_bs.merge(df,on=['股票代码','股票名称'],how='inner')


    d1 = dx.groupby(['所属行业']).apply(lambda x : x[x.涨跌幅>=9])
    d2 = dx.groupby(['所属行业']).apply(lambda x : x[(x.涨跌幅>=5) & (x.涨跌幅<9)])
    d3 = dx.groupby(['所属行业']).apply(lambda x : x[(x.涨跌幅>=0) & (x.涨跌幅<5)])
    d4 = dx.groupby(['所属行业']).apply(lambda x : x[(x.涨跌幅>=-5) & (x.涨跌幅<0)])
    d5 = dx.groupby(['所属行业']).apply(lambda x : x[(x.涨跌幅<=-5) & (x.涨跌幅>-9)])
    d6 = dx.groupby(['所属行业']).apply(lambda x : x[(x.涨跌幅<=-9)])
    d1.index = d1.index.droplevel() #去除重复的index
    d2.index = d2.index.droplevel() #去除重复的index
    d3.index = d3.index.droplevel() #去除重复的index
    d4.index = d4.index.droplevel() #去除重复的index
    d5.index = d5.index.droplevel() #去除重复的index
    d6.index = d6.index.droplevel() #去除重复的index

    dr1 = d1.groupby(['所属行业']).agg({'股票名称':'count'}).reset_index()
    dr1.rename(columns={'股票名称':'>=9%'},inplace=True)
    dr2 = d2.groupby(['所属行业']).agg({'股票名称':'count'}).reset_index()
    dr2.rename(columns={'股票名称':'5%~9%'},inplace=True)
    dr3 = d3.groupby(['所属行业']).agg({'股票名称':'count'}).reset_index()
    dr3.rename(columns={'股票名称':'0%~5%'},inplace=True)
    dr4 = d4.groupby(['所属行业']).agg({'股票名称':'count'}).reset_index()
    dr4.rename(columns={'股票名称':'-5%~0%'},inplace=True)
    dr5 = d5.groupby(['所属行业']).agg({'股票名称':'count'}).reset_index()
    dr5.rename(columns={'股票名称':'-5%~-9%'},inplace=True)
    dr6 = d6.groupby(['所属行业']).agg({'股票名称':'count'}).reset_index()
    dr6.rename(columns={'股票名称':'<=-9%'},inplace=True)

    dfr = [dr1,dr2,dr3,dr4,dr5,dr6]

    from functools import reduce
    dfrr = reduce(lambda x,y:pd.merge(x,y,on='所属行业',how='outer'),dfr)

    return dfrr.sort_values(by=['>=9%','5%~9%','0%~5%','-5%~0%','-5%~-9%','<=-9%'],ascending=False)


if __name__ == '__main__' :
    import urllib3
    urllib3.disable_warnings()

    engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')

    end_dt = datetime.today().strftime('%Y%m%d')
    dt_t = get_calendar_lastday('20210101',0,end_dt)
    
    dt = dt_t.replace('-','')
    df_limitup = get_stock_limitup_daily(1,dt)

    df_limitup['首次封板时间'] = df_limitup['首次封板时间'].apply(lambda x:datetime.strptime(dt_t + ' '+x,'%Y-%m-%d %H:%M:%S'))
    df_limitup['最后封板时间'] = df_limitup['最后封板时间'].apply(lambda x:datetime.strptime(dt_t + ' '+x,'%Y-%m-%d %H:%M:%S'))
    

    df_limitup['成交额'] = df_limitup['成交额']/100000000
    df_limitup['封板资金'] = df_limitup['封板资金']/100000000
    df_limitup['流通市值'] = df_limitup['流通市值']/100000000
    df_limitup['封成比'] = df_limitup['封板资金'] / df_limitup['成交额']

    df = df_limitup.round(1)
    df = df.sort_values(by=['封板资金','成交额'],ascending=False)
    df['时间']=datetime.today()

    # 将新建的DataFrame储存为MySQL中的数据表，不储存index列
    df.to_sql('daily_limitup', engine, index= False,if_exists='append')

    print('Read from and write to Mysql table successfully!')

    #日期初始化:每日09:25分全量更新 这里加个option 命令行可以选择一下
    dt_t = datetime.today().strftime('%Y-%m-%d')
    tomorrow = (datetime.strptime(dt_t,'%Y-%m-%d') + timedelta(days= 1)).strftime('%Y-%m-%d')

    calendar = calendar_stock('20050101', tomorrow.replace('-',''))
    # print(calendar['日期'][-1:])
    calendar['日期'].to_sql('calendar',engine,if_exists='replace',index= False)

    # 每日 沪深A股 行情信息
    import efinance as ef
    dff = ef.stock.get_realtime_quotes(fs=['沪深A股'])
    dff['日期'] = datetime.today().strftime('%Y-%m-%d')
    dff.to_sql('daily_stock', engine, index= False,if_exists='append')

    # 各板块涨停分布
    from datetime import datetime, timedelta
    dt_t = datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(':','_')
    df1 = get_stock_destribute()

    days,lbs=10,1
    df2 =  pd.DataFrame()
    style_df,df2 =  get_stock_limitup_gantt(days,lbs)
    
    df_stock_block = get_stocks_block()

    from datetime import datetime, timedelta
    dt = datetime.today().strftime('%Y-%m-%d').replace('-','')
    dt_t = datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(':','_')
    df3 = get_part_analysis_lbs_promotion(df_stock_block,dt)

    with pd.ExcelWriter('~/Desktop/数据分析/每日复盘'+ dt_t +'.xlsx',engine='openpyxl') as writer:
        df.to_excel(writer,sheet_name='今日涨停',index=False)
        df1.to_excel(writer,sheet_name='行业梯队',index=False)
        style_df.to_excel(writer,sheet_name='甘特图',index=False)
        df3.to_excel(writer,sheet_name='连板晋级',index=False)
        


    pass