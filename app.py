import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import plotly.plotly as py
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
import json
import numpy as np
import pandas as pd
import os
from flask import Flask
server = Flask('my app')
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash('cht2017-demo', server=server, url_base_pathname='/cht2017-demo/', csrf_protect=False)

mapbox_access_token = 'pk.eyJ1IjoiYWlrb2Nob3UiLCJhIjoiY2o1bWF2emI4M2ZoYjJxbnFmbXFrdHQ0ZCJ9.w0_1-IC0JCPukFL7Bpa92w'

BACKGROUND = 'rgb(230, 230, 230)'

# Global map layout
layout = dict(
            showlegend = True,
            legend={'x': 0, 'y': 1},
            height=500,
            margin=Margin(l=0, r=0, t=0, b=30),
            autosize=True,
            hovermode='closest',
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=24.709089,
                    lon=121.377034,
                ),
                pitch=0,
                zoom=8,
                style='streets'
            ),
            font=dict(
                family='Raleway',
            ),
        )

layout_individual_graph = go.Layout(
    title="Individual Time Distribution",
    titlefont=dict(
        family='Dosis',
        ),
    autosize=True,
    height=500,
    margin=Margin(l=30, r=20, t=30, b=45),
    plot_bgcolor="#D9E0EC",
    xaxis=dict(
        range=[-0.5, 23.5],
        showline=True,
        showticklabels=True,
        linewidth=2,
        ticks='outside',
        tickmode='array',
        tickvals=[0,4,8,12,16,20],
        tickwidth=2,
        ticklen=5,
        tickfont=dict(
            family='Raleway',
            size=12,
            color='rgb(82, 82, 82)',
        ),
        ticksuffix=":00",
        zeroline=False,
        gridcolor="white",
    ),
    yaxis=dict(
        #range=[0, max(yVal)*1.5],
        showline=True,
        showticklabels=True,
        linewidth=2,
        ticks='outside',
        tickwidth=2,
        ticklen=5,
        tickfont=dict(
            family='Raleway',
            size=12,
            color='rgb(82, 82, 82)',
        ),
        zeroline=False,
        gridcolor="white",
    ),

)

layout_histogram = go.Layout(
    bargap=0.1,
    bargroupgap=0,
    barmode='group',
    margin=Margin(l=10, r=00, t=0, b=30),
    showlegend=False,
    plot_bgcolor="#D9E0EC",
    #plot_bgcolor='#323130',
    #paper_bgcolor='rgb(66, 134, 244, 0)',
    height=250,
    dragmode="select",
    xaxis=dict(
        range=[-0.5, 23.5],
        tickfont=dict(
            family='Raleway',
            #size=12,
            #color='rgb(82, 82, 82)',
        ),
        showgrid=True,
        #gridcolor="white",
        nticks=25,
        fixedrange=True,
        ticksuffix=":00"
    ),
    yaxis=dict(
        #range=[0, max(yVal)+max(yVal)/4],
        showticklabels=False,
        showgrid=False,
        fixedrange=True,
        rangemode='nonnegative',
        zeroline='hidden'
    ),
)



app.layout = html.Div([
    html.A(['Home'], className="button", href="#", style=dict(position="relative", top=-2, left='75%')),
    html.Br([]),
    html.Br([]),
    html.Br([]),
    html.Div([
        # Row 1: Header and Intro text
        html.Div([
            html.Div([
                html.H4('Transportation Mode Detection'),
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
                        options=[
                            {'label': 'WC Peng :)', 'value': 'u_466924201064380'},
                            {'label': 'u_-35363411', 'value': 'u_-35363411'},
                            {'label': 'u_-102396725', 'value': 'u_-102396725'}, #MRT
                        ],
                        value="u_466924201064380",
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
                            {'label': 'Preprocessed Trajectory ', 'value': 'p'}, #<>
                            {'label': 'Mode Detection ', 'value': 'm'}, #<>
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
            ], className='eight columns', style={'margin-top': 0}),
            html.Div([
                dcc.Graph(id='individual-graph')
            ], className='four columns', style={'margin-top': 0}),
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
            html.Div([
                dcc.Graph(id="histogram"),
            ], style={'margin-top': 10}),
            html.P("", id="popupAnnotation", className="popupAnnotation", style={'color': 'black', 'fontSize': 15, 'font-family': 'Dosis'}),
        ], className="graph twelve coluns"),
        # Foot
        html.Br([]),
        html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
        html.Br([]),

        dcc.Markdown("[NCTU-ADSL/cht2017-demo](https://github.com/NCTU-ADSL-public/cht2017-demo)"),

    ], className='container'),
    html.Br([]),
])

def initialize():
    # demo users
    uid = ['u_466924201064380', 'u_-35363411', 'u_-102396725']
    # cellular raw data
    cellular = {}
    for u in uid:
        cellular[u] = {}
        files_list = os.listdir(os.path.join('data', u, 'cellular'))
        for f in files_list:
            df = pd.read_csv(os.path.join('data', u, 'cellular', f), header=None, sep='|',
                names=['imsi','timestamp','lon','lat', 'unix_t'],
                dtype={'imsi':str})
            df['Date/Time'] = df.timestamp.apply(lambda x: f +" "+ x[:8])
            df['Date/Time'] = pd.to_datetime(df['Date/Time'], format="%Y%m%d %H:%M:%S")
            df['Location'] = df['lon'].astype(str) + ',' + df['lat'].astype(str)
            df.index = df['Date/Time']
            df.drop('imsi', 1, inplace=True)
            df.drop('timestamp', 1, inplace=True)
            df.drop('unix_t', 1, inplace=True)
            cellular[u][f] = df
    return cellular

# Create callbacks


# user-dropdown -> date-dropdown
@app.callback(Output("date-dropdown", "options"),
              [Input("user-dropdown", "value")])
def set_date_options(uid):
    if uid == 'u_466924201064380':
        options=[
            {'label': '2016-10-21', 'value': '20161021'},
            {'label': '2016-11-23', 'value': '20161123'},
            {'label': '2016-12-20', 'value': '20161220'},
            {'label': '2017-01-16', 'value': '20170116'},
            {'label': '2017-02-13', 'value': '20170213'},
            {'label': '2017-02-17', 'value': '20170217'},
            {'label': '2017-02-22', 'value': '20170222'},
            {'label': '2017-03-03', 'value': '20170303'},
            {'label': '2017-03-17', 'value': '20170317'},
            {'label': '2017-05-12', 'value': '20170512'},
        ]
    else:
        options=[
            {'label': '2017-01-03', 'value': '20170103'},
            {'label': '2017-01-04', 'value': '20170104'},
            {'label': '2017-01-05', 'value': '20170105'},
            {'label': '2017-01-06', 'value': '20170106'},
        ]
    return options

@app.callback(Output("date-dropdown", "value"),
              [Input("user-dropdown", "value")])
def set_date_value(uid):
    if uid == 'u_466924201064380':
        value = '20161123'
    else:
        value = '20170103'
    return value

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

def get_selection(uid, date, option, selection):
    xVal = []
    yVal = []
    xSelected = []
    colorVal2 = ["#F4EC15", "#DAF017", "#BBEC19", "#9DE81B", "#80E41D", "#66E01F",
                "#4CDC20", "#34D822", "#24D249", "#25D042", "#26CC58", "#28C86D",
                "#29C481", "#2AC093", "#2BBCA4", "#2BB5B8", "#2C99B4", "#2D7EB0",
                "#2D65AC", "#2E4EA4", "#2E38A4", "#3B2FA0", "#4E2F9C", "#603099"]

    colorVal = ['#fae4b2','#f9ddb2','#f9d6b1','#f7d0b1','#f6c9b0','#f4c2b0',
                '#f2bcb0','#efb6af','#ecaeaf','#e9a9af','#e5a3ae','#e09eae',
                '#db98ae','#d693ae','#cf8eae','#c989ae','#c285ae','#ba81ae',
                '#b37dae','#ab79af','#a375af','#9971af','#906eb0','#866bb0']

    if (selection is not None):
        for x in selection:
            xSelected.append(int(x))
    for i in range(0, 24):
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = ('lightslategray')
            #colorVal[i] = ('#FFFFFF')
        xVal.append(i)
        if option == 'r':
            yVal.append(sum(cellular[uid][date].index.hour == i))

    return [np.array(xVal), np.array(yVal), np.array(xSelected), np.array(colorVal)]


# update histogram
@app.callback(Output("histogram", "figure"),
              [Input("user-dropdown", "value"), Input("date-dropdown", "value"),
              Input("option-selector", "value"),
               Input("time-selector", "value")])
def update_histogram(uid, date, option, selection):
    [xVal, yVal, xSelected, colorVal] = get_selection(uid, date, option, selection)
    data=Data([
            go.Bar(
                x=xVal,
                y=yVal,
                marker=dict(
                    color=colorVal
                ),
                hoverinfo="x"
            ),
            go.Scatter(
                opacity=0,
                x=xVal,
                y=yVal/2,
                hoverinfo="none",
                mode='markers',
                marker=Marker(
                    #color='rgb(66, 134, 244, 0)',
                    symbol="square",
                    size=40
                ),
                visible=True
            )
    ])

    layout_histogram['yaxis']['range'] = [0, max(yVal)+max(yVal)/4]
    layout_histogram['annotations'] = [dict(x=xi, y=yi,
                                             text=str(yi),
                                             xanchor='center',
                                             yanchor='bottom',
                                             showarrow=False,
                                             font=dict(
                                                family="Raleway",
                                                #color="white"
                                             ),
                                        ) for xi, yi in zip(xVal, yVal)]


    figure = go.Figure(data=data, layout=layout_histogram)

    return figure


def get_lon_lat(uid, date, option, selectedData):
    listStr = "cellular[uid][date]"
    if(selectedData is None or len(selectedData) is 0):
        return listStr
    elif(int(selectedData[len(selectedData)-1])-int(selectedData[0])+2 == len(selectedData)+1 and len(selectedData) > 2):
        listStr += "[(cellular[uid][date].index.hour>"+str(int(selectedData[0]))+") & \
                    (cellular[uid][date].index.hour<" + str(int(selectedData[len(selectedData)-1]))+")]"
    else:
        listStr += "["
        for point in selectedData:
            if (selectedData.index(point) is not len(selectedData)-1):
                listStr += "(cellular[uid][date].index.hour==" + str(int(point)) + ") | "
            else:
                listStr += "(cellular[uid][date].index.hour==" + str(int(point)) + ")]"

    return listStr



# update main-graph
@app.callback(Output("main-graph", "figure"),
              [Input("user-dropdown", "value"),
              Input("date-dropdown", "value"),
              Input("option-selector", "value"),
              Input("time-selector", "value")],
              [State('main-graph', 'relayoutData'),
               State('lock-selector', 'values')])
def update_main_graph(uid, date, option, selectedData, prevLayout, lockControls):
    listStr = get_lon_lat(uid, date, option, selectedData)
    df = eval(listStr)
    if option == 'r':
        occurence = np.array([len(p[1]) for p in df.groupby(df.Location)])
        total_occurence = sum(occurence)
        text = [str(j) + ' / ' + str(total_occurence) for j in occurence]
        data = Data([
            Scattermapbox(
                lon=[p[0].split(',')[0] for p in df.groupby(df.Location)],
                lat=[p[0].split(',')[1] for p in df.groupby(df.Location)],
                mode='markers',
                marker=dict(
                    #size=np.log2(occurence)*220,
                    size=occurence*21,
                    sizemode='area',
                    opacity=0.3,
                    color='black',
                ),
                hoverinfo='skip',
            ),
            Scattermapbox(
                lon=[p[0].split(',')[0] for p in df.groupby(df.Location)],
                lat=[p[0].split(',')[1] for p in df.groupby(df.Location)],
                text=text,
                customdata=[p[1].index.hour for p in df.groupby(df.Location)],
                mode='markers',
                marker=dict(
                    #size=np.log2(occurence)*200,
                    size=occurence*20,
                    sizemode='area',
                    opacity=0.8,
                    #color=occurence,
                    color='tomato',
                    #colorscale=[[0, 'aquamarine'],[0.3, '#7AC4C2'],[0.7, '#F1A1AD'],[1, 'tomato']],
                    #reversescale=True,
                    #colorbar=dict(
                    #    thickness=6,
                    #    title="Occurence",
                    #    x=0.935,
                    #    xpad=0,
                    #    nticks=10,
                    #    ),
                ),
                hoverinfo="lon+lat+text",
                #name="Cellular Raw Data"
            ),
        ])
        layout['showlegend'] = False

    if (prevLayout is not None and lockControls is not None and
        'lock' in lockControls):
        layout['mapbox']['center']['lon'] = float(prevLayout['mapbox']['center']['lon'])
        layout['mapbox']['center']['lat'] = float(prevLayout['mapbox']['center']['lat'])
        layout['mapbox']['zoom'] = float(prevLayout['mapbox']['zoom'])

    fig = dict(data=data, layout=layout)
    return fig



def fetch_individual(chosen):
    xVal = []
    yVal = []
    for i in range(0, 24):
        xVal.append(i)
        yVal.append(sum([int(j) == i for j in chosen]))
    return [np.array(xVal), np.array(yVal)]


# main-graph -> individual-graph
@app.callback(Output('individual-graph', 'figure'),
              [Input('main-graph', 'hoverData')])
def update_individual_graph(hoverData):
    if hoverData is None:
        hoverData = {'points': [{'customdata': []}]}
    chosen = [point['customdata'] for point in hoverData['points']]
    [xVal, yVal] = fetch_individual(chosen[0])

    data = Data([
         go.Scatter(
             x=xVal,
             y=yVal,
             mode='lines+markers',
             line=dict(
                 shape="spline",
                 smoothing=2,
                 width=3,
                 color='rgb(205, 12, 24)'
             ),
         ),
     ])
    layout_individual_graph['yaxis']['range'] = [0, max(yVal)*1.5]

    figure = go.Figure(data=data, layout=layout_individual_graph)
    return figure



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

@app.server.before_first_request
def loadData():
    global cellular
    cellular = initialize()

if __name__ == '__main__':
	app.server.run(host='127.0.0.1',port=8050,debug=True)
