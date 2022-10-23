from datetime import datetime, timedelta
from importlib import import_module
import os
from dash import Dash
from markupsafe import escape
from dash import dcc,html
from pages import (
    pre_mkt_info,
    open_mkt_info,
    close_mkt_info
    )
from  flask import Flask
from flask_caching import Cache


server = Flask(__name__)

app = Dash(
        __name__,
        server=server,
        suppress_callback_exceptions=True,
        url_base_pathname='/dash/',
        update_title='正在更新....'
        )

app.title = "行情跟踪分析"

def server_layout():
    return html.Div(
                children=[  
                    pre_mkt_info.create_layout(),
                    open_mkt_info.create_layout(),
                    close_mkt_info.create_layout(),
                ]
            )

app.layout = server_layout

@server.route("/dash")
def my_dash_app():
    return app.index()

if __name__ == '__main__':
    app.run_server(debug=True,port=8058)