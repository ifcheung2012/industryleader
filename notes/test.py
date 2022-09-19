import multiprocessing
import time

from datetime import datetime
import random
import time
import akshare as ak
import pandas as pd
from functools import reduce
from sqlalchemy import create_engine

import requests

proxypool_url = 'http://127.0.0.1:5555/random'
target_url = 'http://httpbin.org/get'

def get_random_proxy():
    """
    get random proxy from proxypool
    :return: proxy
    """
    return requests.get(proxypool_url).text.strip()

def crawl(url, proxy):
    """
    use proxy to crawl page
    :param url: page url
    :param proxy: proxy, such as 8.8.8.8:8888
    :return: html
    """
    proxies = {'http': 'http://' + proxy}
    return requests.get(url, proxies=proxies).text

def getdata():
    # engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')

    df_concept_ths_today = ak.stock_board_concept_name_ths()
    df_concept_ths_today = df_concept_ths_today.drop_duplicates(subset=['代码'])
    # l = len(df_concept_ths_today)
    return df_concept_ths_today

def getstock_f_concept(df_concept_ths_today):
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


def test1():
    result = 0
    for i in range(20000000):
        result += i
    print(result)


def test2():
    result = 0
    for i in range(20000000):
        result += i
    print(result)

def test3():
    result = 0
    for i in range(20000000):
        result += i
    print(result)


if __name__ == '__main__':
    start_time = time.time()
    proxy = get_random_proxy()
    proxies = {'http': 'http://' + proxy}
    print(proxies)
    # df = getdata()
    # l = len(df)
    # print(l)
    # t1 = multiprocessing.Process(target=getstock_f_concept,args=(df.iloc[:50,:],))
    # t2 = multiprocessing.Process(target=getstock_f_concept,args=(df.iloc[51:100,:],))
    # t3 = multiprocessing.Process(target=getstock_f_concept,args=(df.iloc[101:150,:],))
    # t4 = multiprocessing.Process(target=getstock_f_concept,args=(df.iloc[151:200,:],))
    # t5 = multiprocessing.Process(target=getstock_f_concept,args=(df.iloc[201:250,:],))
    # t6 = multiprocessing.Process(target=getstock_f_concept,args=(df.iloc[251:300,:],))
    # t7 = multiprocessing.Process(target=getstock_f_concept,args=(df.iloc[301:l,:],))
    # t1.start()
    # t2.start()
    # t3.start()
    # t4.start()
    # t5.start()
    # t6.start()
    # t7.start()
    # t1.join()
    # t2.join()
    # t3.join()
    # t4.join()
    # t5.join()
    # t6.join()
    # t7.join()
    end_time = time.time()
    total_time = end_time-start_time
    print('所有任务结束，总耗时为：'+str(total_time))