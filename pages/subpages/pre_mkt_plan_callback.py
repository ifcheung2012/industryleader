from app import app
from dash.dependencies import Input, Output, State

from dash import html

from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine,text

from environment.settings import *

@app.callback(
    Output('textarea-state-example-output', 'children'),
    Input('textarea-state-example-button', 'n_clicks'),
    State('textarea-state-example', 'value')
)
def update_output(n_clicks, value):
    if n_clicks > 0:
        engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/mysql?charset=utf8')
        df = pd.DataFrame({"详细内容":value.replace('\n',"<br>"), "类型":"早盘计划","日期":datetime.today().strftime('%Y-%m-%d')}, index=[0])
        df.to_sql('plan_and_conclusion',engine,if_exists='append',index= False)
        return 'You have entered: \n{}'.format(value)
