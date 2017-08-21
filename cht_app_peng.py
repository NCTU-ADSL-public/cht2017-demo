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
                "https://fonts.googleapis.com/css?family=Overpass:300,300i",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/dab6f937fd5548cebf4c6dc7e93a10ac438f5efb/dash-technical-charting.css"
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/62f0eb4f1fadbefea64b2404493079bf848974e8/dash-uber-ride-demo.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
                ]
#"https://cdn.rawgit.com/plotly/dash-app-stylesheets/5047eb29e4afe01b45b27b1d2f7deda2a942311a/goldman-sachs-report.css"

for css in external_css:
    app.css.append_css({"external_url": css})


external_js = [ "https://code.jquery.com/jquery-3.2.1.min.js",
        "https://cdn.rawgit.com/plotly/dash-app-stylesheets/a3401de132a6d0b652ba11548736b1d1e80aa10d/dash-goldman-sachs-report-js.js" ]

for js in external_js:
    app.scripts.append_script({ "external_url": js })


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
                zoom=9,
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
            html.H2("Transportation Mode Detection Demo App",
                style={'font-family': 'Dosis', 'float': 'left', 'position': 'relative', 'top': '30px', 'fontSize': 60}),
            html.Img(src="https://is3-ssl.mzstatic.com/image/thumb/Purple71/v4/94/66/3e/94663eac-ba75-c839-eaa8-0211ffda6a90/source/266x200bb.jpeg",
                style={
                    'height': '150px',
                    'float': 'right',
                    'position': 'relative',
                    'top': '30px',
                    'left': '0px'
                    },
            ),
            html.P("Public transportation mode detection with cellular data.\
                    Select different users and days using the dropdowns below.\
                    ", className="explanationParagraph twelve columns",
                style={'float': 'left', 'position': 'relative', 'fontSize': 18}),
        ], className='row'),
        html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
        html.Div([
            html.Div([
                html.P('Select user:', style={'fontSize': 17, 'marginBottom': 1}),
                dcc.Dropdown(
                    id='user-dropdown',
                    options=[
                        {'label': 'WCPeng :)', 'value': 'u_466924201064380'}, #HSR
                        {'label': 'Piske', 'value': 'u_-35363411'}, #Bus
                        {'label': 'Usagi', 'value': 'u_-102396725'}, #Bus&MRT
                    ],
                    value="u_466924201064380",
                    placeholder="Please choose an user",
                    className="user-picker"
                ),
                html.Div([
                    dcc.RadioItems(
                        id='radio-selector',
                        options=[
                            {'label': 'Raw Cellular Data ', 'value': 'raw'},
                            {'label': 'Preprocessed Data ', 'value': 'prepro'},
                            {'label': 'Mode Detection ', 'value': 'mode'}
                        ],
                        value='raw',
                        labelStyle={'display': 'inline-block'}
                    ),
                ],style={'marginTop': '10', 'marginLeft': '7'}),
            ],className='six columns'),
            html.Div([
                html.P('Select day:', style={'fontSize': 17, 'marginBottom': 1}),
                dcc.Dropdown(
                        id='day-dropdown',
                        placeholder="Please choose a day",
                        value=1
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
                ],style={'marginTop': '10', 'marginLeft': '7'})
            ], className='six columns'),
        ], className='row'),
        html.Div([
            dcc.Graph(id='map-graph'),
        ])
    ], style={'margin': 'auto auto'}),
    dcc.Markdown("[NCTU-ADSL/cht2017-demo](https://github.com/NCTU-ADSL-public/cht2017-demo)",
             className="source"),
#], className='ten columns offset-by-one', style={
], style={
        'width': '85%',
        'max-width': '1200',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'font-family': 'overpass',
        'background-color': 'mistyrose',
        'padding': '40',
        'padding-top': '20',
        'padding-bottom': '20',
})


def fetch_raw_prepro_dataframe(uid, d_idx, selectedData):
    if uid == 'u_466924201064380':
        file_list = ['20161021','20161123','20161220','20170116','20170213','20170217','20170222','20170303','20170317','20170512']
    else:
        file_list = ['20170103','20170104','20170105','20170106','20170107','20170108','20170109','20170110','20170111','20170112']
    filename = uid + '_' + file_list[d_idx] + '_' + selectedData + '.csv'
    print('fetch: '+filename)
    if selectedData == 'raw':
        df = pd.read_csv(os.path.join('data', uid, selectedData, filename), dtype={'lon': str, 'lat': str})
    else:
        df = pd.read_csv(os.path.join('data', uid, selectedData, filename), dtype=str)

    return df


def fetch_mode_dataframe(uid, d_idx):
    if uid == 'u_466924201064380':
        file_list = ['20161021','20161123','20161220','20170116','20170213','20170217','20170222','20170303','20170317','20170512']
    else:
        file_list = ['20170103','20170104','20170105','20170106','20170107','20170108','20170109','20170110','20170111','20170112']

    result_df = pd.read_csv(os.path.join('data', uid, 'result.csv'), dtype={'uid':str, 'date':str})
    result_df = result_df[result_df.date == file_list[d_idx]]
    ntrips = result_df.shape[0]
    print result_df, ntrips

    trip_dfs = []
    trip_mode = []
    for i in range(ntrips):
        trip_start_t = result_df.iloc[i]['start_t']
        trip_end_t = result_df.iloc[i]['end_t']
        #filename = uid+'_'+file_list[d_idx]+'_prepro.csv'
        filename = file_list[d_idx]+'.csv'
        cellular_df = pd.read_csv(os.path.join('data', uid, 'cellular', filename), dtype=str)
        #trip_df = cellular_df[(cellular_df.ctime_unix.astype(int) >= trip_start_t)&(cellular_df.ctime_unix.astype(int) <= trip_end_t)]
        cellular_df.ctimestamp = pd.to_datetime(cellular_df.ctimestamp)
        trip_df = cellular_df[(cellular_df.ctimestamp >= pd.to_datetime(trip_start_t))&(cellular_df.ctimestamp <= pd.to_datetime(trip_end_t))]
        trip_df = trip_df.sort_values(by='ctimestamp')
        trip_dfs.append(trip_df)
        trip_mode.append(result_df.iloc[i]['mode'])

    return result_df, trip_dfs, trip_mode

@app.callback(Output('day-dropdown','options'),[
                Input('user-dropdown', 'value'), Input('radio-selector', 'value')])
def set_day_options(uid, selectedData):
    if selectedData == 'raw' or selectedData == 'prepro':
        if uid == 'u_466924201064380':
            date_marks = ['2016/10/21','2016/11/23','2016/12/20','2017/01/16',\
            '2017/02/13','2017/02/17','2017/02/22','2017/03/03', '2017/03/17', '2017/05/12']
            return [{'label': date_marks[i], 'value': i} for i in range(len(date_marks))]
        else:
            return [{'label': 'Jan {}'.format(i+3), 'value': i} for i in range(10)]
    else: #<debt>
        #result_df = pd.read_csv(os.path.join('data', uid, 'result.csv'), dtype={'uid':str, 'date':str})
        #result_df.date
        if uid == 'u_466924201064380':
            date_marks = ['2016/10/21','2016/11/23','2016/12/20','2017/01/16',\
            '2017/02/13','2017/02/17','2017/02/22','2017/03/03', '2017/03/17', '2017/05/12']
            return [{'label': date_marks[i], 'value': i} for i in range(len(date_marks))]
        else:
            return [{'label': 'Jan {}'.format(i+3), 'value': i} for i in range(10)]


@app.callback(Output("map-graph", "figure"),[
                Input("user-dropdown", "value"), Input("day-dropdown", "value"),
                Input("radio-selector", "value")],[
                State('lock-selector', 'values'),
                State('map-graph', 'relayoutData')])
def update_graph(uid, date, selectedData, lockSelector, prevLayout):
    if selectedData == 'raw':
        df = fetch_raw_prepro_dataframe(uid, date, selectedData)
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
        df = fetch_raw_prepro_dataframe(uid, date, selectedData)
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
        result_df, trip_dfs, trip_mode = fetch_mode_dataframe(uid, date)
        colors = {"hsr": "rgb(0,116,217)", "mrt": "rgb(255,65,54)", "bus": "rgb(133,20,75)", "train": "rgb(255,133,27)"}
        names = {"hsr": "HSR trip", "mrt": "MRT trip", "bus": "BUS trip", "train": "TRA trip"}
        #mrt_lines = {"BR": "Wenhu Line", "R": "Tamsui-Xinyi Line", "G": "Songshan-Xindian Line", "O": "Zhonghe-Xinlu Line", "BL": "Bannan Line"}
        endpt_size = 25
        trips = []
        for k in range(len(trip_dfs)):
            print trip_dfs[k]
            trip_df = trip_dfs[k]
            labels = [trip_df.ctime.loc[i].split(',')[0] for i in trip_df.index]
            labels[0] = result_df.iloc[k].s_id+' : '+result_df.iloc[k].s_name+'<br>'+labels[0]
            labels[-1]= result_df.iloc[k].e_id+' : '+result_df.iloc[k].e_name+'<br>'+labels[-1]
            trip = Scattermapbox(
                lat = [trip_df.y.loc[i] for i in trip_df.index],
                lon = [trip_df.x.loc[i] for i in trip_df.index],
                text= labels,
                mode= 'markers+lines',
                marker=Marker(
                    size=[endpt_size] + [10 for j in range(len(trip_df.index) - 2)] + [endpt_size],
                    color=colors[trip_mode[k]]
                ),
                name = names[trip_mode[k]]+': '+result_df.iloc[k].s_name+' --> ' + result_df.iloc[k].e_name,
                hoverinfo = "text",
            )
            trips.append(trip)
        data = Data(trips)
        #layout['mapbox']['center']['lon'] = np.mean([float(user_df.lon.loc[i]) for i in user_df.index])
        #layout['mapbox']['center']['lat'] = np.mean([float(user_df.lat.loc[i]) for i in user_df.index])

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
    #app.run_server(debug=True) #localhost
    app.run_server(host='0.0.0.0', port=8050, debug=False)
