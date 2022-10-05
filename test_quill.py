import dash_quill
import dash
from dash.dependencies import Input, Output, State
from dash import     html,dcc

app = dash.Dash(__name__)
quill_mods = [
    [{ 'header': '1'}, {'header': '2'}, { 'font': [] }],
    [{'size': []}],
    ['bold', 'italic', 'underline', 'strike', 'blockquote'],
    [{'list': 'ordered'}, {'list': 'bullet'}, 
        {'indent': '-1'}, {'indent': '+1'}],
    ['link', 'image'],
    ['clean']
]
app.layout = html.Div([
    dash_quill.Quill(
        id='input',
        value='my-value-is different',
        maxLength=70,
        modules={'toolbar':quill_mods,'clipboard':{'matchVisual': False,}}
#        label='my-label'
    ),
    html.Div(id='output'),
    dash_quill.Quill(
        id='input2',
        value='my-value',
        maxLength=70,
        modules={'toolbar':False,'clipboard':{'matchVisual': False,}}
#        label='my-label'
    ),
    html.Br(),
        dash_quill.Quill(
        id='input3',
        value='my-value',
        maxLength=70,
#        label='my-label'
    ),
    html.Br(),
    dcc.Textarea(id='test-text',value='PLACEHOLDER'),
    dcc.Textarea(
        id='textarea-example',
        value='Textarea content initialized\nwith multiple lines of text',
        style={'width': '100%', 'height': 300},
    ),
    html.Div(id='textarea-example-output', style={'whiteSpace': 'pre-line'})
])


@app.callback(
    Output('textarea-example-output', 'children'),
    Input('textarea-example', 'value')
)
def update_output(value):
    print(value)
    return 'You have entered: \n{}'.format(value)

@app.callback(Output('output', 'children'), [Input('input', 'value')],[State('input', 'charCount')])
def display_output(value,charCount):
    return 'You have entered {0} and nochars is {1}'.format(value,charCount)

@app.callback(Output('test-text', 'value'), [Input('input', 'value')],[State('input', 'charCount')])
def display_output2(value,charCount):

    # print(value.replace('\n','<br />'))
    res = value
    print(res)
    return 'You have entered {0} and nochars is {1}'.format(value,charCount)

@app.callback(Output('input3', 'value'), [Input('input', 'value')],[State('input', 'charCount')])
def display_output2(value,charCount):
    return 'You have entered {0} and nochars is {1}'.format(value,charCount)


if __name__ == '__main__':
    print(dash_quill.__version__)
    app.run_server(debug=True)