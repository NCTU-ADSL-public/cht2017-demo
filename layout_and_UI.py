import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from plotly import graph_objs as go
from datetime import datetime as dt
import json
import pandas as pd
import os
from flask import Flask
server = Flask('my app')
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash('cht2017-demo', server=server, url_base_pathname='/cht2017-demo/', csrf_protect=False)

mapbox_access_token = 'pk.eyJ1IjoiYWlrb2Nob3UiLCJhIjoiY2o1bWF2emI4M2ZoYjJxbnFmbXFrdHQ0ZCJ9.w0_1-IC0JCPukFL7Bpa92w'

BACKGROUND = 'rgb(230, 230, 230)'

app.layout = html.Div([
    html.A(['Home'], className="button", href="#", style=dict(position="absolute", top=-2, right=130)),
    html.Br([]),
    html.Br([]),
    html.Br([]),
    html.Div([
        # Row 1: Header and Intro text
        html.Div([
            html.Div([
                html.H5('Transportation Mode Detection'),
                html.H6('Public transportation mode detection with cellular data. Select different users and days using the dropdowns below', style=dict(color='#7F90AC')),
                ], className = "nine columns padded"),
            html.Div([
                html.H1([html.Span('TJ', style=dict(opacity=0.5)), html.Span('Miner')],),
                html.H6('NCTU-ADSLab'),
                ], className="three columns gs-header gs-accent-header padded", style=dict(float='right')),
            ], className="row gs-header gs-text-header"),
        html.Br([]),
        html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
        html.Br([]),
        # Row 2:
        html.Div([
            html.Div([
                html.Div([
                    html.Label('Select user:'),
                    dcc.Dropdown(
                        id='user-dropdown',
                        placeholder="Choose an user",
                    ),
                ]),
            ], className='six columns',),
            html.Div([
                html.Div([
                    html.Label('Select day:'),
                    dcc.Dropdown(
                        id='date-dropdown',
                        placeholder="Choose a day",
                    ),
                ], style={'position': 'relative', 'left': 30}),
            ], className='six columns'),
        ], className='row'),
        html.Br([]),
        # Row 3:
        html.Div([
            html.Div([
                html.Div([
                    dcc.RadioItems(
                        id='option-selector',
                        options=[
                            {'label': 'Cellular Raw Data ', 'value': 'r'},
                            {'label': 'Preprocessed Trajectory ', 'value': 'p'},
                            {'label': 'Mode Detection ', 'value': 'm'},
                        ],
                        value='r',
                        labelStyle={'display': 'inline-block'},
                    ),
                ]),
            ], className='six columns'),
            html.Div([
                html.Div([
                    dcc.Checklist(
                        id='lock-selector',
                        options=[
                            {'label': 'Lock camera', 'value': 'lock'}
                        ],
                        values=[],
                    ),
                ], style={'position': 'relative', 'left': 30}),
            ], className='six columns'),
        ], className='row'),
        # Row 4: main graph & individual graph
        html.Div([
            html.Div([
                dcc.Graph(id='main-graph')
            ], className='eight columns', style={'margin-top': 20}),
            html.Div([
                dcc.Graph(id='individual-graph')
            ], className='four columns', style={'margin-top': 20}),
        ], className='row'),
        # Row 5:
        html.Div([
            dcc.Dropdown(
                id='time-selector',
                options=[
                    {'label': '0:00', 'value': '0'},
                    {'label': '1:00', 'value': '1'},
                    {'label': '2:00', 'value': '2'},
                    {'label': '3:00', 'value': '3'},
                    {'label': '4:00', 'value': '4'},
                    {'label': '5:00', 'value': '5'},
                    {'label': '6:00', 'value': '6'},
                    {'label': '7:00', 'value': '7'},
                    {'label': '8:00', 'value': '8'},
                    {'label': '9:00', 'value': '9'},
                    {'label': '10:00', 'value': '10'},
                    {'label': '11:00', 'value': '11'},
                    {'label': '12:00', 'value': '12'},
                    {'label': '13:00', 'value': '13'},
                    {'label': '14:00', 'value': '14'},
                    {'label': '15:00', 'value': '15'},
                    {'label': '16:00', 'value': '16'},
                    {'label': '17:00', 'value': '17'},
                    {'label': '18:00', 'value': '18'},
                    {'label': '19:00', 'value': '19'},
                    {'label': '20:00', 'value': '20'},
                    {'label': '21:00', 'value': '21'},
                    {'label': '22:00', 'value': '22'},
                    {'label': '23:00', 'value': '23'}
                ],
                multi=True,
                placeholder="Select certain hours using \
                             the box-select/lasso tool or \
                             using the dropdown menu",
                className="bars"
            ),
            dcc.Graph(id="histogram"),
            html.P("", id="popupAnnotation", className="popupAnnotation", style={'color': 'grey'}),
        ], className="graph twelve coluns"),
        # Foot
        html.Br([]),
        html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
        html.Br([]),

        dcc.Markdown("[NCTU-ADSL/cht2017-demo](https://github.com/NCTU-ADSL-public/cht2017-demo)"),

    ], className='container'),
    html.Br([]),
])

# Create callbacks

# user-dropdown -> date-dropdown
@app.callback(Output("date-dropdown", "options"),
              [Input("user-dropdown", "value")])
def set_date_options(uid):
    pass

# histogram -> time-selector
@app.callback(Output("time-selector", "value"),
              [Input("histogram", "selectedData")])
def update_time_selector(value):
    holder = []
    if(value is None or len(value) is 0):
        return holder
    for x in value['points']:
        holder.append(str(int(x['x'])))
    return holder

# clear histogram if re-selecting user or date or option
@app.callback(Output("histogram", "selectedData"),
              [Input("user-dropdown", "value"),
              Input("date-dropdown", "value"),
              Input("option-selector", "value")])
def clear_histogram_selection(value1, value2, value3):
    #if(value is None or len(value) is 0):
    #    return None
    pass

# histogram prompt
@app.callback(Output("popupAnnotation", "children"),
              [Input("time-selector", "value")])
def set_histogram_prompt(value):
    if(value is None or len(value) is 0):
        return "Select any of the bars to section data by time"
    else:
        return ""

# update histogram
@app.callback(Output("histogram", "figure"),
              [Input("user-dropdown", "value"), Input("date-dropdown", "value"),
              Input("option-selector", "value"),
               Input("time-selector", "value")])
def update_histogram(uid, date_value, option, selection):
    pass

# update main-graph
@app.callback(Output("main-graph", "figure"),
              [Input("user-dropdown", "value"),
              Input("date-dropdown", "value"),
              Input("option-selector", "value"),
              Input("time-selector", "value")],
              [State('main-graph', 'relayoutData'),
               State('lock-selector', 'values')])
def update_main_graph(uid, date_value, option, selectedData, prevLayout, lockControls):
    pass

# main-graph -> individual-graph
@app.callback(Output('individual-graph', 'figure'),
              [Input('main-graph', 'hoverData')])
def update_individual_graph(main_graph_hover):
    pass



if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/0e463810ed36927caf20372b6411690692f94819/dash-drug-discovery-demo-stylesheet.css",
                 "https://cdn.rawgit.com/plotly/dash-app-stylesheets/5047eb29e4afe01b45b27b1d2f7deda2a942311a/goldman-sachs-report.css",
                 "https://cdn.rawgit.com/plotly/dash-app-stylesheets/62f0eb4f1fadbefea64b2404493079bf848974e8/dash-uber-ride-demo.css",
        "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]


for css in external_css:
    app.css.append_css({"external_url": css})



if __name__ == '__main__':
	app.server.run(host='127.0.0.1',port=8050,debug=True)
