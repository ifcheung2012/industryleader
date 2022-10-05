from datetime import datetime
import numpy as np
from sqlalchemy import create_engine
import akshare as ak
from functools import reduce
import pandas as pd
import random
import time

def get_trade_date(beg,end):
    cc_df = ak.tool_trade_date_hist_sina()
    cc_df['trade_date'] = pd.to_datetime(cc_df['trade_date'],format='%Y-%m-%d')
    df_tmp = cc_df.loc[(cc_df['trade_date'] >= beg)&(cc_df['trade_date'] <= end)]
    return df_tmp

def get_daily_info(beg:str,end:str):
    '''
    获取指定时间段的涨停行情：涨停、跌停、炸板、昨日涨停数据
    Parameters:
    beg:起始日期-字符串 格式:'2019-01-1';
    end:截止日期-字符串 格式:'2022-08-10'
    Return:
    DataFrameList[dfA,dfB,dfC,dfD]
    dfA:涨停股池
    dfB:昨日涨停今日表现股池
    dfC:炸板股池
    dfD:跌停股池
    '''
    dt_beg = datetime.strptime(beg,'%Y-%m-%d')
    dt_end = datetime.strptime(end,'%Y-%m-%d')

    df_res = get_trade_date(dt_beg,dt_end)
    j = 0
    df_zt_lst,df_zt_pre_lst,df_zbgc_lst,df_dtgc_lst = [],[],[],[]
    for i in df_res['trade_date']:
        dt_tmp = datetime.strftime(i,'%Y-%m-%d').replace('-','')

        df_zt = ak.stock_zt_pool_em(dt_tmp)
        df_zt['日期'] = i
        df_zt_lst.append(df_zt)

        df_zt_pre = ak.stock_zt_pool_previous_em(dt_tmp)
        df_zt_pre['日期'] = i
        df_zt_pre_lst.append(df_zt_pre)
        
        df_zbgc = ak.stock_zt_pool_zbgc_em(dt_tmp)
        df_zbgc['日期'] = i
        df_zbgc_lst.append(df_zbgc)

        df_dtgc = ak.stock_zt_pool_dtgc_em(dt_tmp)
        df_dtgc['日期'] = i
        df_dtgc_lst.append(df_dtgc)
        
        if j%4==1:
            time.sleep(random.randint(1,10))
        j += 1

    res_df_zt_lst = reduce(lambda x,y:pd.concat([x,y],ignore_index=True),df_zt_lst)
    res_df_zt_pre_lst = reduce(lambda x,y:pd.concat([x,y],ignore_index=True),df_zt_pre_lst)
    res_df_zbgc_lst = reduce(lambda x,y:pd.concat([x,y],ignore_index=True),df_zbgc_lst)
    res_df_dtgc_lst = reduce(lambda x,y:pd.concat([x,y],ignore_index=True),df_dtgc_lst)
    return [res_df_zt_lst,res_df_zt_pre_lst,res_df_zbgc_lst,res_df_dtgc_lst]

def get_stock_tick_data(code):
    df = ak.stock_zh_a_hist_pre_min_em(symbol=code, start_time="09:15:00", end_time="15:00:00")
    df['代码']=code
    df['差额']=df['收盘'].diff()
    df = df.fillna(0)
    price_kp = df[:1]['开盘'][0]
    df['涨幅']=df['差额'].cumsum()/price_kp
    return df

def get_tick_data(code):
    df = ak.stock_zh_a_hist_pre_min_em(symbol=code, start_time="09:15:00", end_time="15:00:00")
    df['代码']=code
    df['差额']=df['收盘'].diff()
    df = df.fillna(0)
    price_kp = df[:1]['开盘'][0]
    df['涨幅']=df['差额'].cumsum()/price_kp

    return df

def get_formated_ticks(codelst):
    df_lst = []
    for x in codelst:
        df=get_tick_data(x)
        df1 = df[['涨幅']]
        df2 = df1.T.reset_index()
        df2['代码'] = x
        del df2['index']
        df_lst.append(df2)

    return reduce(lambda x,y:pd.concat([x,y],ignore_index=True),df_lst)

def get_ticks_daily_info(lst_dfs):
    lst = []

    df_daily_info_all =  reduce(lambda x,y:pd.concat([x,y],ignore_index=True),lst_dfs)
    df_daily_info_all.drop_duplicates(subset=['代码','名称'],keep='first',inplace=True)

    for index,row in df_daily_info_all.iterrows():
        df_tmp = get_stock_tick_data(row['代码'])
        lst.append(df_tmp)

    df = reduce(lambda x,y:pd.concat([x,y],ignore_index=True),lst)
    return df

def info_change_history():
    engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')

    df_concept_ths_today = ak.stock_board_concept_name_ths()
    df_concept_ths_today = df_concept_ths_today.drop_duplicates(subset=['代码'])

    #概念成分股关系-今日
    dflist = []
    for concept in df_concept_ths_today['代码']:
        dft = ak.stock_board_cons_ths(symbol=concept)
        dft['概念代码'] = concept
        dft['概念名称'] = df_concept_ths_today.loc[(df_concept_ths_today.代码 == concept)]['概念名称'].iloc[0]
        dflist.append(dft)
        time.sleep(random.randint(1,10))

    df_concept_stock_today = reduce(lambda x,y:pd.concat([x,y]),dflist)
    df_concept_stock_today['日期']=datetime.today().strftime('%Y-%m-%d')

    #概念-昨日
    sql_concept_ths_yesterday = 'select * from concept_ths'
    df_concept_ths_yesterday =  pd.read_sql(sql_concept_ths_yesterday,engine)
    #概念成分股关系-昨日
    sql_concept_stock_yesterday = 'select * from concept_stock'
    df_concept_stock_yesterday =  pd.read_sql(sql_concept_stock_yesterday,engine)


    #今日概念清单入库
    df_concept_ths_today.to_sql('concept_ths', engine, index= False,if_exists='replace')
    #今日概念成分股关系入库
    df_concept_stock_today.to_sql('concept_stock', engine, index= False,if_exists='replace')

    #今日概念差异入库
    #概念-今日昨日差异
    df_c_x = df_concept_ths_today[['概念名称','代码']]
    df_c_y = df_concept_ths_yesterday[['概念名称','代码']]
    df_c_x['x'],df_c_y['x'] = 1,1
    df_c_x.set_index(['概念名称','代码'],inplace=True)
    df_c_y.set_index(['概念名称','代码'],inplace=True)
    df_c_y.sort_values(by=['代码'])
    df_c_x.sort_values(by=['代码'])
    c_left,c_right = df_c_x.align(df_c_y,join='outer',axis=0)
    # 昨日减少的 TODO 过滤ST 退市股票等
    df_concept_diff_1 = c_left[c_left['x'].isna()]
    df_concept_diff_1.reset_index(inplace=True)
    df_concept_diff_1['异动内容'] = '[概念删除]'+ df_concept_diff_1['概念名称']
    # 今日新增的
    df_concept_diff_2 = c_right[c_right['x'].isna()]
    df_concept_diff_2.reset_index(inplace=True)
    df_concept_diff_2['异动内容'] = '[概念新增]'+ df_concept_diff_2['概念名称']
    # 最终的概念差异结果
    df_concept_diff_res = pd.concat([df_concept_diff_1[['概念名称','代码']],df_concept_diff_2[['概念名称','代码']]])

    #概念成分股-今日昨日差异
    df_x = df_concept_stock_today[['代码','概念名称']]

    df_y = df_concept_stock_yesterday[['代码','概念名称']]
    df_x.rename({'代码':'股票代码'},axis=1,inplace=True)
    df_y.rename({'代码':'股票代码'},axis=1,inplace=True)
    df_x['x'],df_y['x'] = 1,1
    df_x.set_index(['股票代码','概念名称'],inplace=True)
    df_y.set_index(['股票代码','概念名称'],inplace=True)
    df_y.sort_values(by=['股票代码'])
    df_x.sort_values(by=['股票代码'])
    left,right = df_x.align(df_y,join='outer',axis=0)
    # 昨日减少的 TODO 过滤ST 退市股票等
    df_concept_stock_diff_1 = left[left['x'].isna()]
    df_concept_stock_diff_1.reset_index(inplace=True)
    df_concept_stock_diff_1['异动内容'] = '[个股删除概念]'+ df_concept_stock_diff_1['概念名称']
    # 今日新增的
    df_concept_stock_diff_2 = right[right['x'].isna()]
    df_concept_stock_diff_2.reset_index(inplace=True)
    df_concept_stock_diff_2['异动内容'] = '[个股添加概念]'+ df_concept_stock_diff_2['概念名称']
    # 最终的概念股票差异结果
    df_concept_stock_diff_res = pd.concat([df_concept_stock_diff_1[['股票代码','概念名称','异动内容']],df_concept_stock_diff_2[['股票代码','概念名称','异动内容']]])
    df_concept_stock_diff_res.rename({'股票代码':'代码'},axis=1,inplace=True)

    df_diff_res = pd.concat([df_concept_diff_res,df_concept_stock_diff_res])
    # 将标记差异日期并持久化
    df_diff_res['日期'] = datetime.today().strftime('%Y-%m-%d')
    df_diff_res.to_sql('concept_stock_change', engine, index= False,if_exists='append')

def data_to_sql(beg,end):
    
    # 持久化链接
    engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')
    # 获取涨停行情数据
    res_df_zt_lst, res_df_zt_pre_lst,res_df_zbgc_lst,res_df_dtgc_lst= get_daily_info(beg,end)
    #入库
    res_df_zt_lst.to_sql('stocks_limitup_history', engine, index= False,if_exists='append')
    res_df_zt_pre_lst.to_sql('stocks_limitup_history_previous', engine, index= False,if_exists='append')
    res_df_zbgc_lst.to_sql('stocks_limitup_history_zbgc', engine, index= False,if_exists='append')
    res_df_dtgc_lst.to_sql('stocks_limitup_history_dtgc', engine, index= False,if_exists='append')
    # 将今日涨停行情 涨停、跌停、昨日涨停、今日炸板的股票的每分钟成交额存入数据库
    res_df_daily_tick = get_ticks_daily_info([res_df_zt_lst, res_df_zt_pre_lst,res_df_zbgc_lst,res_df_dtgc_lst])
    res_df_daily_tick.to_sql('stocks_daily_ticks', engine, index= False,if_exists='append')
    # 比对今日和昨日的概念、个股概念有哪些异动，并持久化
    info_change_history()



if __name__ == '__main__' :
    import urllib3
    urllib3.disable_warnings()
    dt_today = datetime.now().strftime('%Y-%m-%d')

    data_to_sql(dt_today,dt_today)
    print('Data in %s has been inserted into sql' % dt_today)

    # res_df_zt_lst, res_df_zt_pre_lst,res_df_zbgc_lst,res_df_dtgc_lst= get_daily_info('2022-08-12','2022-08-12')
    # df = get_formated_ticks(res_df_zt_lst['代码'])
    # print(df)
    pass