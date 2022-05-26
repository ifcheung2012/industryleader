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

    Returns
    -------
    DataFrame
        指定日期板块主力资金净流入、板块涨跌幅行情
    Fields
    ------
    ``['板块涨跌幅','行业编码','上市板块','所属行业','主力资金净流入','今日主力净流入最大股名称','今日主力净流入最大股编码']``
    https://push2.eastmoney.com/api/qt/clist/get?fid=f62&po=1&pz=500&pn=1&np=1&fltt=2&invt=2&ut=b2884a393a59ad64002292a3e90d46a5&fields=f12,f14&fs=b:BK0428
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
    df_res = pd.DataFrame(columns=['行业编码','股票代码','股票名称'])
    df_block = get_block_inflow()
    for hybm in df_block['行业编码']:
        df_tmp = get_block_stocks_by_hybk(hybm)
        df_res = pd.concat([df_res,df_tmp])

    return df_res
# df_res.to_excel('out.xls',sheet_name='板块股票')

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings()

    get_stocks_block()
