from datetime import datetime, timedelta
from functools import reduce
import pandas as pd
from sqlalchemy import create_engine,text


def get_pre_plan():
    engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')

    str_today = datetime.today().strftime('%Y-%m-%d')

    # sql_pre_plan = f"select 详细内容 from plan_and_conclusion where  日期 ='{str_today}'"
    sql_pre_plan = f"select 详细内容 from plan_and_conclusion where  日期 ='2022-09-22'"

    df_zts = pd.read_sql(sql_pre_plan,engine)
    return df_zts


if __name__ == '__main__' :
    print(get_pre_plan()['详细内容'])
    pass