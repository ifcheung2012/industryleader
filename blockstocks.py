import pandas as pd
import requests
from datetime import datetime
from jsonpath import jsonpath
from blockinflow import get_block_inflow




def get_block_stocks_by_hybk(hybk: str = None) -> pd.DataFrame:
    """
    获取指定各板块下的股票代码
    Parameters
    ----------
        hybk :字符串  行业板块编码（东方财富） 如:BK0464
    Returns
    -------
    DataFrame
        指定日期板块主力资金净流入、板块涨跌幅行情
    Fields
    ------
    ``['板块涨跌幅','行业编码','上市板块','所属行业','主力资金净流入','今日主力净流入最大股名称','今日主力净流入最大股编码']``
    URL: https://push2.eastmoney.com/api/qt/clist/get?fid=f62&po=1&pz=500&pn=1&np=1&fltt=2&invt=2&ut=b2884a393a59ad64002292a3e90d46a5&fields=f12,f14&fs=b:BK0428
    """
    if hybk=='':
        return None

    params = (
        ('ut', 'b2884a393a59ad64002292a3e90d46a5'),
        ('pn', '1'),
        ('pz', '500'),
        ('po', '1'),
        ('np', '1'),
        ('fltt', '2'),
        ('invt', '2'),
        ('fields', 'f12,f14'),
        ('fid','f62'),
        ('fs','b:'+hybk),
    )
    


    response = requests.get(
        'https://push2.eastmoney.com/api/qt/clist/get', params=params,  verify=False)
    fields = {
        'f12': '股票代码',
        'f14': '股票名称',
    }
    items = jsonpath(response.json(), '$..diff[:]')
    if not items:
        df = pd.DataFrame(
            columns=['日期']+list(fields.values())+['统计天数', '涨停次数'])
        return df
    df = pd.DataFrame(items)
    
    df: pd.DataFrame = df.rename(columns=fields)[fields.values()]
    
    df['行业编码']=hybk
    return df


# 获取所有板块与股票及两者的对应关系
def get_stocks_block() -> pd.DataFrame:
    """
    获取 今天 所有行业板块下的股票代码 约4k多只 
    #todo 目前未区分 主板、创业板、科创板及ST
    #todo 这部分数据仅能每日获取 建议最好存到数据库里
    Parameters
    ----------
    Returns
    -------
    DataFrame
        今日个股与板块的对应关系，及板块主力资金净流入、板块涨跌幅行情
    Fields
    ------
    ``['股票代码','股票名称','行业编码','所属行业','板块涨跌幅','主力资金净流入','今日主力净流入最大股名称','今日主力净流入最大股编码']``
    """
    import os
    datafile = '板块股票清单.xlsx'
    if os.path.exists(datafile):
        return pd.DataFrame(pd.read_excel(datafile,converters={'股票代码':str}))
    df_res = pd.DataFrame(columns=['行业编码','股票代码','股票名称'])
    df_block = get_block_inflow()
    for hybm in df_block['行业编码']:
        df_tmp = get_block_stocks_by_hybk(hybm)
        df_res = pd.concat([df_res,df_tmp])
    df_r=pd.merge(df_res,df_block,on='行业编码',how='left')

    df_r.to_excel('板块股票清单.xlsx') #最新的板块股票对应关系表 下载到本地 下次直接加载excel

    return df_r
# df_res.to_excel('out.xls',sheet_name='板块股票')

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings()

    # df = get_stocks_block()
    # df['日期'] = '20220527'
    # # print(df)
    # print(df)
    datafile = '板块股票清单.xlsx'
    dd = pd.DataFrame(pd.read_excel(datafile,converters={'股票代码':str}))
    df_block = get_block_inflow()
    print(df_block)
    pass



