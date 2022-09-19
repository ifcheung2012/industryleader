from app import app
from dash.dependencies import Input, Output
from datetime import datetime, timedelta
from dash import html

@app.callback(Output('live-update-text', 'children'),
              Input('interval-5s', 'n_intervals'))
def update_limitup_info(n):
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span(f'Longitude: {datetime.now()}', style=style)
    ]

