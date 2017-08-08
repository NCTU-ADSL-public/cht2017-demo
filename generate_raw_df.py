import plotly as py
from plotly.graph_objs import *
import pandas as pd
import numpy as np
import sys


def initialize():
    '''from raw data [imsi, unix_t, lon, lat]
    	to df [imsi, lon, lat, occurence, [timestamps]]
    '''
    df = pd.read_csv('data/'+date+'/'+uid, sep='|', header=None, names=['id', 'time', 'lon', 'lat', 'unix_t'])
    df.drop('time', axis=1, inplace=True)
    df['spatial'] = df['lon'].astype(str)+','+df['lat'].astype(str)

    totalList = []
    for s_point in df.groupby(df.spatial):
        timestamps = np.array(s_point[1].unix_t.sort_values().unique())
        lon = s_point[0].split(',')[0]
        lat = s_point[0].split(',')[1]
        pop = len(timestamps)
        #totalList.append([uid, lon, lat, pop, timestamps])
        totalList.append([uid, lon, lat, pop])
    #df = pd.DataFrame(totalList, columns=['uid','lon','lat','pop','timestamps'])
    df = pd.DataFrame(totalList, columns=['uid','lon','lat','pop'])
    df.sort_values(by='pop', ascending=False, inplace=True)
    return df

def plot_bubble3(df):
    mapbox_access_token = 'pk.eyJ1IjoiYWlrb2Nob3UiLCJhIjoiY2o1bWF2emI4M2ZoYjJxbnFmbXFrdHQ0ZCJ9.w0_1-IC0JCPukFL7Bpa92w'
    #print(df)
    count = df['pop'].count()
    total = df['pop'].sum()
    df['text'] = 'Occurrence ' + df['pop'].astype(str) + ' / ' + str(total)
    scale = 15
    scale_2 = 8
    zoom=12.2
    data = Data([
        Scattermapbox(
            lat=df['lat'],
            lon=df['lon'],
            text=df['text'],
            mode='markers',
            marker=dict(
                    size=df['pop']*scale,
                    sizemode = 'area',
                    color='rgb(255, 0, 0)'
                ),
            hoverinfo = "lon+lat+text"
        ),
        Scattermapbox(
            lat=df['lat'],
            lon=df['lon'],
            mode='markers',
            marker=dict(
                    size=df['pop']*scale_2,
                    sizemode = 'area',
                    color='rgb(242, 177, 172)',
                    opacity=0.7
                ),
            hoverinfo='skip',
        )
    ])

    layout = Layout(
        title='User Raw Cellular Data'+'<br>'+df['uid'].loc[0],
        showlegend = False,
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=df['lat'].astype(float).mean(),
                lon=df['lon'].astype(float).mean()
            ),
            pitch=0,
            zoom=zoom,
            style='streets'
        ),
    )
    fig = dict(data=data, layout=layout)
    py.offline.plot( fig, validate=False, filename='bubble-map-raw3.html')


def plot_bubble2(df):
    mapbox_access_token = 'pk.eyJ1IjoiYWlrb2Nob3UiLCJhIjoiY2o1bWF2emI4M2ZoYjJxbnFmbXFrdHQ0ZCJ9.w0_1-IC0JCPukFL7Bpa92w'
    #print(df)
    count = df['pop'].count()
    total = df['pop'].sum()
    df['text'] = 'Occurrence ' + df['pop'].astype(str) + ' / ' + str(total)
    limits = [(0,2),(3,10),(11,20),(21,50),(50,3000)]
    colors = ["rgb(0,116,217)","rgb(255,65,54)","rgb(133,20,75)","rgb(255,133,27)","lightgrey"]
    scale = 15
    traces = []
    for i in range(len(limits)):
        lim = limits[i]
        df_sub = df[lim[0]:lim[1]]
        if df_sub.empty:
            continue
        print(df_sub)
        trace = dict(
                type='scattermapbox',
                lon=df_sub['lon'],
                lat=df_sub['lat'],
                text=df_sub['text'],
                mode='markers',
                marker=dict(
                    size=df_sub['pop']*scale,
                    sizemode = 'area',
                    color="#4169E1"
                ),
                hoverinfo = "lon+lat+text"
            )
        traces.append(trace)

    layout = Layout(
        title='User Raw Cellular Data'+'<br>'+df['uid'].loc[0],
        showlegend = False,
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=df['lat'].astype(float).mean(),
                lon=df['lon'].astype(float).mean()
            ),
            pitch=0,
            zoom=12.2,
            style='streets'
        ),
    )
    fig = dict(data=traces, layout=layout)
    py.offline.plot( fig, validate=False, filename='bubble-map-raw2.html')

def plot_bubble(df):
    mapbox_access_token = 'pk.eyJ1IjoiYWlrb2Nob3UiLCJhIjoiY2o1bWF2emI4M2ZoYjJxbnFmbXFrdHQ0ZCJ9.w0_1-IC0JCPukFL7Bpa92w'
    print(df)
    data = Data([
        Scattermapbox(
            lat=df['lat'],
            lon=df['lon'],
            mode='markers',
            marker=Marker(
                size=17,
                color='rgb(255, 0, 0)',
                opacity=0.7
            ),
            showlegend=False
        ),
        Scattermapbox(
            lat=df['lat'],
            lon=df['lon'],
            mode='markers',
            marker=Marker(
                size=8,
                color='rgb(242, 177, 172)',
                opacity=0.7
            ),
            hoverinfo='skip',
            showlegend=False
        )
    ])

    layout = Layout(
        title='User Raw Cellular Data',
        autosize=True,
        hovermode='closest',
        showlegend=False,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=25,
                lon=121.5
            ),
            pitch=0,
            zoom=9,
            style='streets'
        ),
    )

    fig = dict(data=data, layout=layout)
    py.offline.plot( fig, validate=False, filename='bubble-map-raw.html')

if __name__ == '__main__':
    uid = sys.argv[1]
    date = sys.argv[2]
    df = initialize()
    df.to_csv('data/'+date+'/'+uid+'_raw.csv', index=False)
    #plot_bubble3(df)
