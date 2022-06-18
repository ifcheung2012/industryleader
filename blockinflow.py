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
    ``上市板块    行业编码   所属行业  板块涨跌幅 主力资金净流入 今日主力净流入最大股名称 今日主力净流入最大股编码``
    ``0     90  BK1036    半导体   4.99   23.67         中芯国际       688981``
    ``1     90  BK1031   光伏设备   3.00   20.11         通威股份       600438``
    ``2     90  BK1029   汽车整车   4.33   19.40         长安汽车       000625``
    ``3     90  BK1027    小金属   3.25   17.77         五矿稀土       000831``
    4     90  BK1033     电池   3.41    9.41         蔚蓝锂芯       002245
    ..   ...     ...    ...    ...     ...          ...          ...
    81    90  BK0477   酿酒行业  -1.06  -13.18         燕京啤酒       000729
    82    90  BK0475     银行  -0.06  -13.39         杭州银行       600926
    83    90  BK0437   煤炭行业  -3.10  -13.91         靖远煤电       000552
    84    90  BK0451  房地产开发  -1.40  -15.80         万业企业       600641
    ``85    90  BK0486   文化传媒  -1.26  -16.02         分众传媒       002027``
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