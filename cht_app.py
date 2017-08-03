import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py              ###
from plotly import graph_objs as go
from plotly.graph_objs import *
from flask import Flask
import pandas as pd
import numpy as np
import os
import copy
import functools32

server = Flask('my app')
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash('CHTApp', server=server, url_base_pathname='/cht2017', csrf_protect=False)

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/62f0eb4f1fadbefea64b2404493079bf848974e8/dash-uber-ride-demo.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

mapbox_access_token = 'pk.eyJ1IjoiYWlrb2Nob3UiLCJhIjoiY2o1bWF2emI4M2ZoYjJxbnFmbXFrdHQ0ZCJ9.w0_1-IC0JCPukFL7Bpa92w'

# Global map layout
layout = dict(
            showlegend = True,
            legend={'x': 0, 'y': 1},
            height=700,
            margin=Margin(l=0, r=0, t=0, b=0),
            autosize=True,
            hovermode='closest',
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=25.032969,
                    lon=121.565418
                ),
                pitch=0,
                zoom=11,
                style='streets'
            ),
        )


def initialize():
    #--/* raw mode */--
    #uid = "u_-35363411"
    #raw_df = pd.read_csv('data/'+uid+'_raw.csv', dtype={'lon': str, 'lat': str})
    uni_output = pd.read_csv('data/integrated_output.csv', header=None,
                    names=['uid','date','mode','trip_start_t','trip_end_t'],
                    dtype={'uid':str, 'date':str})
    '''
    bus_output = pd.read_csv('data/bus_20170104.csv', header=None,
                    names=['uid','trip_start_t','trip_end_t','rid','direction','s_idx','e_idx'],
                    dtype={'uid':str, 'rid':str, 'direction':str})
    bus_output.index = bus_output['uid']
    bus_output = bus_output.to_dict(orient='index')
    '''
    route_df = pd.read_csv('data/bus_stop_infomation.csv', header=None,
                     names=['rid','route_name','direction','sid','stop_name','order','lon','lat'],
                     dtype=str)

    #prepro_df = pd.read_csv('data/'+uid+'_prepro.csv', dtype=str)
    #user_ddf = prepro_df[(prepro_df.start_unix_t.astype(int) >= trip_start_t)&(prepro_df.end_unix_t.astype(int) <= trip_end_t)]

    return uni_output, route_df

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H2("Transportation Mode Detection App",
                style={'font-family': 'Dosis', 'float': 'left', 'position': 'relative', 'top': '30px', 'left': '10px'}),
            html.Img(src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png",
                style={
                    'height': '100px',
                    'float': 'right',
                    'position': 'relative',
                    'left': '5px'
                    },
            ),
            html.P("Public transportation mode detection with cellular data.\
                    Select different users and days using the dropdown and the slider\
                    below", className="explanationParagraph twelve columns",
                style={'float': 'left', 'position': 'relative', 'left': '15px'}),
        ], className='row'),
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='my-dropdown',
                    options=[
                        {'label': 'Charlie', 'value': 'u_-35363411'},
                        {'label': 'Sally', 'value': 'u_-102396725'}, #MRT
                        {'label': 'Patty', 'value': 'u_1673597718'}, #MRT
                        {'label': 'Snoopy', 'value': 'u_1503609993'},
                        {'label': 'Woodstock', 'value': 'u_-281531961'}, #MRT
                    ],
                    value="u_-35363411",
                    placeholder="Please choose an user",
                    className="user-picker"
                ),
                html.Div([
                    dcc.RadioItems(
                        id='my-selector',
                        options=[
                            {'label': 'Raw Cellular Data ', 'value': 'raw'},
                            {'label': 'Preprocessed Data ', 'value': 'prepro'},
                            {'label': 'Mode Detection ', 'value': 'mode'}
                        ],
                        value='raw',
                        labelStyle={'display': 'inline-block'}
                    ),
                ],style={'margin-top': '10', 'margin-left': '7'})
            ],className='six columns'),
            html.Div([
                dcc.Dropdown(
                        id='multi-selector',
                        multi=True,
                        placeholder="This selector only showes when you choose mode detection.",
                ),
                html.Div([
                    dcc.Checklist(
                        id='lock-selector',
                        options=[
                            {'label': 'Lock camera', 'value': 'lock'}
                        ],
                        values=[],
                        inputStyle={"z-index": "3"}
                    ),
                ],style={'margin-top': '10', 'margin-left': '7'})
            ], className='six columns'),
        ], className='row'),
        html.Div([
            dcc.Graph(id='map-graph'),
        ])
    ], style={'margin': 'auto auto'}),
    html.Div([
        dcc.Slider(
            id="my-slider",
            marks = {i: ('Jan {}'.format(i) if i==1 or i==31 else '{}'.format(i)) for i in range(1, 32)},
            min=1,
            max=31,
            step=1,
            value=4
        ),
    ], style={'margin-top': '10'}),
    dcc.Markdown("Data Source: [ChunghwaTelecom](http://www.cht.com.tw/)",
             className="source"),
], className='ten columns offset-by-one')


def fetch_raw_dataframe(uid, date):
    date = '201701'+'{:02d}'.format(date)
    raw_df = pd.read_csv('data/'+date+'/'+uid+'_raw.csv', dtype={'lon': str, 'lat': str})
    return raw_df

def fetch_prepro_dataframe(uid, date):
    date = '201701'+'{:02d}'.format(date)
    prepro_df = pd.read_csv('data/'+date+'/'+uid+'_prepro.csv', dtype=str)
    return prepro_df

def fetch_mode_dataframe(uid, date):
    ## <debt> multiple routes
    #--/* filter bus route */
    date = '201701'+'{:02d}'.format(date)
    bus_output = pd.read_csv('data/bus_'+date+'.csv', header=None,
                    names=['uid','trip_start_t','trip_end_t','rid','direction','s_idx','e_idx'],
                    dtype={'uid':str, 'rid':str, 'direction':str})
    bus_output.index = bus_output['uid']
    bus_output = bus_output.to_dict(orient='index')

    rid = bus_output[uid[2:]]['rid']
    direction = bus_output[uid[2:]]['direction']
    s_index = bus_output[uid[2:]]['s_idx']
    e_index = bus_output[uid[2:]]['e_idx']
    route_ddf = route_df[(route_df.rid == rid)&(route_df.direction == direction)]
    route_ddf = route_ddf[(route_ddf.order.astype(int) >= s_index)&(route_ddf.order.astype(int)<=e_index)]
    #--/* filter user path */
    trip_start_t = bus_output[uid[2:]]['trip_start_t']
    trip_end_t = bus_output[uid[2:]]['trip_end_t']
    prepro_df = pd.read_csv('data/'+date+'/'+uid+'_prepro.csv', dtype=str)
    user_ddf = prepro_df[(prepro_df.start_unix_t.astype(int) >= trip_start_t)&(prepro_df.end_unix_t.astype(int) <= trip_end_t)]

    return prepro_df, route_ddf, user_ddf

def get_detection_modes(uid, date):
    date = '201701'+'{:02d}'.format(date)
    return uni_output[(uni_output['uid'] == uid[2:])&(uni_output['date'] == date)]['mode'].unique()

@app.callback(Output('multi-selector', 'options'),[
                Input("my-dropdown", "value"), Input("my-slider", "value"),
                Input('my-selector', 'value'), ])
def set_selector_options(uid, date, selectedData):
    if selectedData == 'mode':
        options = get_detection_modes(uid, date)
        return [{'label': i, 'value': i.lower()} for i in options]
    else:
        return []

@app.callback(Output('multi-selector', 'value'),[
                Input("multi-selector", "options"), ])
def set_selector_value(available_options):
        return [ i['value'] for i in available_options]

@app.callback(Output("map-graph", "figure"),[
                Input("my-dropdown", "value"), Input("my-slider", "value"),
                Input("my-selector", "value")],[
                State('lock-selector', 'values'),
                State('map-graph', 'relayoutData')])
def update_graph(uid, date, selectedData, lockSelector, prevLayout):

    if selectedData == 'raw':
        df = fetch_raw_dataframe(uid, date)
        total = df['pop'].sum()
        df['text'] = 'Occurrence ' + df['pop'].astype(str) + ' / ' + str(total)
        scale = 15
        data = Data([
            Scattermapbox(
                lat=df['lat'],
                lon=df['lon'],
                text=df['text'],
                mode='markers',
                marker=dict(
                        size=df['pop']*scale,
                        sizemode = 'area',
                        #color='orangered'
                        color=df['pop'],
                        colorscale='Portland',
                        colorbar=dict(
                            thickness=15,
                            title="Occurence<br>of points",
                            x=0.935,
                            xpad=0,
                            nticks=10,
                            ),
                    ),
                hoverinfo = "text",
                name = "Cellular Points",
            ),
        ])
        layout['mapbox']['center']['lon'] = df['lon'].astype(float).mean()
        layout['mapbox']['center']['lat'] = df['lat'].astype(float).mean()

    elif selectedData == 'prepro':
        df = fetch_prepro_dataframe(uid, date)
        endpt_size=20
        scale=30
        data = Data([
            Scattermapbox(
                lat=[df.lat.loc[i] for i in df.index],
                lon=[df.lon.loc[i] for i in df.index],
                text=[df.start_t.loc[i]+' - '+df.end_t.loc[i]+'<br>Stayed '+df.stay_t.loc[i]+'s' for i in df.index],
                mode='markers+lines',
                marker=Marker(
                    #color="royalblue",
                    color=np.log(df.stay_t.astype(int)),
                    colorscale='Portland',
                    #size=np.log(df.stay_t.astype(int))*scale,
                    #sizemode='area',
                    size=15,
                    colorbar=dict(
                        thickness=15,
                        title="Logarithm of<br>stay time",
                        x=0.935,
                        xpad=0,
                        nticks=10,
                        ),
                ),
                hoverinfo = "text",
                name = "Cellular Trajectory"
            )
        ])
        layout['mapbox']['center']['lon'] = np.mean([float(df.lon.loc[i]) for i in df.index])
        layout['mapbox']['center']['lat'] = np.mean([float(df.lat.loc[i]) for i in df.index])

    elif selectedData == 'mode':
        user_df, route_ddf, user_ddf = fetch_mode_dataframe(uid, date)
        endpt_size=20
        data = Data([
            Scattermapbox(
                lat=[user_df.lat.loc[i] for i in user_df.index],
                lon=[user_df.lon.loc[i] for i in user_df.index],
                mode='markers+lines',
                marker=Marker(
                    color="silver",
                    size=4,
                    opacity=0.5
                ),
                name = "Cellular Trajectory",
                hoverinfo = "skip",
            ),
            Scattermapbox(
                lat=[route_ddf.lat.loc[i] for i in route_ddf.index],
                lon=[route_ddf.lon.loc[i] for i in route_ddf.index],
                text=[route_ddf.route_name.loc[i]+'<br>'+route_ddf.order.loc[i]+'/'+route_ddf.stop_name.loc[i] for i in route_ddf.index],
                mode='markers+lines',
                marker=Marker(
                    size=[endpt_size] + [4 for j in range(len(route_ddf.index) - 2)] + [endpt_size],
                    color="rgb(0,116,217)"
                ),
                name = "Bus Route",
                hoverinfo = "text",
            ),
            Scattermapbox(
                lat=[user_ddf.lat.loc[i] for i in user_ddf.index],
                lon=[user_ddf.lon.loc[i] for i in user_ddf.index],
                text=[user_ddf.start_t.loc[i]+' - '+user_ddf.end_t.loc[i]+'<br>Stayed '+user_ddf.stay_t.loc[i]+'s' for i in user_ddf.index],
                mode='markers+lines',
                marker=Marker(
                    color="rgb(255,65,54)",
                    size=[endpt_size] + [4 for j in range(len(user_ddf.index) - 2)] + [endpt_size]
                ),
                name = "Detected Trajectory",
                hoverinfo = "text",
            )
        ])
        layout['mapbox']['center']['lon'] = np.mean([float(user_df.lon.loc[i]) for i in user_df.index])
        layout['mapbox']['center']['lat'] = np.mean([float(user_df.lat.loc[i]) for i in user_df.index])

    if (prevLayout is not None and lockSelector is not None and 
        'lock' in lockSelector):
        layout['mapbox']['center']['lon'] = float(prevLayout['mapbox']['center']['lon'])
        layout['mapbox']['center']['lat'] = float(prevLayout['mapbox']['center']['lat'])
        layout['mapbox']['zoom'] = float(prevLayout['mapbox']['zoom'])

    fig = dict(data=data, layout=layout)
    return fig


@app.server.before_first_request
def defineTotalList():
    global uni_output, route_df
    uni_output, route_df = initialize()


if __name__ == '__main__':
    app.run_server(debug=True)
