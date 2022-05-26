import pandas as pd
import requests
from datetime import datetime
from jsonpath import jsonpath



def get_block_inflow(date: str = None) -> pd.DataFrame:
    """
    获取指定日期行业板块资金净流入流出行情
    Parameters
    ----------
    date : str
        指定日期，默认为当前日期 格式形如 ``'20220506'``
    Returns
    -------
    DataFrame
        指定日期板块主力资金净流入、板块涨跌幅行情
    Fields
    ------
    ``['板块涨跌幅','行业编码','上市板块','所属行业','主力资金净流入','今日主力净流入最大股名称','今日主力净流入最大股编码']``
    """
    if date is None:
        date = datetime.today().strftime('%Y%m%d')
    params = (
        ('ut', 'b2884a393a59ad64002292a3e90d46a5'),
        ('pn', '1'),
        ('pz', '500'),
        ('po', '1'),
        ('np', '1'),
        ('fltt', '2'),
        ('invt', '2'),
        ('fields', 'f3,f12,f13,f14,f62,f204,f205'),
        ('fid','f62'),
        ('fs','m:90+t:2'),
    )
  
    response = requests.get(
        'https://push2.eastmoney.com/api/qt/clist/get', params=params,  verify=False)
    fields = {
        'f13': '上市板块',
        'f12': '行业编码',
        'f14': '所属行业',
        'f3' :'板块涨跌幅',
        'f62': '主力资金净流入',
        'f204':'今日主力净流入最大股名称',
        'f205':'今日主力净流入最大股编码'
    }
    items = jsonpath(response.json(), '$..diff[:]')
    if not items:
        df = pd.DataFrame(
            columns=['日期']+list(fields.values())+['统计天数', '涨停次数'])
        return df
    df = pd.DataFrame(items)
    
    df: pd.DataFrame = df.rename(columns=fields)[fields.values()]
    
    df['主力资金净流入'] /= 100000000
    df['主力资金净流入'] = df['主力资金净流入'].apply(lambda x:format(x,'.2f')).sort_values()

    df.sort_values(by='主力资金净流入',ascending=False)

    return df

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings()

    df_block = get_block_inflow()
    print(df_block)