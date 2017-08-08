import plotly as py
from plotly.graph_objs import *
import pandas as pd
import numpy as np
import sys
import csv
import math

import datetime
def unix2time(unix_t):
    return datetime.datetime.fromtimestamp(
        int(unix_t)
    ).strftime('%H:%M:%S')


def preprocessing(user_raw_data):
	#user_raw_data: [[user_imsi,unix_time,lon,lat]...]

    user_data = []
    user_data.append(user_raw_data[0])

    # remove oscillation data
    i = 1
    while i < len(user_raw_data) - 1:
        if str(user_raw_data[i-1][2]) + str(user_raw_data[i-1][3]) == str(user_raw_data[i+1][2]) + str(user_raw_data[i+1][3]) and\
            str(user_raw_data[i][2]) + str(user_raw_data[i][3]) != str(user_raw_data[i+1][2]) + str(user_raw_data[i+1][3]):
            user_data.append(user_raw_data[i+1])
            i = i + 2
        else:
            user_data.append(user_raw_data[i])
            i = i + 1

    if i < len(user_raw_data):
        user_data.append(user_raw_data[i])

    #merge data
    result_data = []
    start_time = user_data[0][1]
    end_time = user_data[0][1]
    imsi = user_data[0][0]
    lon = user_data[0][2]
    lat = user_data[0][3]
    for i in range(1,len(user_data)):
        if user_data[i][2] == lon and user_data[i][3] == lat:
            end_time = user_data[i][1]
        else:
            result_data.append([imsi,start_time,end_time,lon,lat])
            start_time = user_data[i][1]
            end_time = user_data[i][1]
            lon = user_data[i][2]
            lat = user_data[i][3]
    result_data.append([imsi,start_time,end_time,lon,lat])

	# result_data = [[imsi,start_time,end_time,lon,lat]...]
    return result_data

def initialize():
    '''from raw data [imsi, timestamp, lon, lat, unix_t]
        to df [imsi, start_unix_t, end_unix_t, lon, lat, start_t, end_t, stay_time]
    '''
    with open('data/'+date+'/'+uid, "r") as f:
        data = [[row[0], int(row[4]), row[2], row[3]] for row in csv.reader(f, delimiter='|')]
    data = sorted(data,key=lambda x:x[1])
    data = np.unique(np.array(data), axis=0)
    data = preprocessing(data)

    totalList = []
    for row in data:
        stay_t = int(row[2])-int(row[1])
        if stay_t:
            row.append(unix2time(row[1]))
            row.append(unix2time(row[2]))
            row.append(str(stay_t))
            totalList.append(row)

    df = pd.DataFrame(totalList, columns=['uid','start_unix_t','end_unix_t','lon','lat','start_t','end_t','stay_t'])
    df.sort_values(by='start_unix_t', ascending=True, inplace=True)
    return df


def plot_prepro(df):
    mapbox_access_token = 'pk.eyJ1IjoiYWlrb2Nob3UiLCJhIjoiY2o1bWF2emI4M2ZoYjJxbnFmbXFrdHQ0ZCJ9.w0_1-IC0JCPukFL7Bpa92w'
    endpt_size=20
    zoom=12.2
    scale=30
    data = Data([
        Scattermapbox(
            lat=[df.lat.loc[i] for i in df.index],
            lon=[df.lon.loc[i] for i in df.index],
            text=[df.start_t.loc[i]+' - '+df.end_t.loc[i]+'<br>Stayed '+df.stay_t.loc[i]+'s' for i in df.index],
            mode='markers+lines',
            marker=Marker(
                #color="grey",
                color=np.log(df.stay_t.astype(int))*scale,
                colorscale='Portland',
                size=15,
                #size=np.log(df.stay_t.astype(int))*scale,
                #sizemode='area',
                #autocolorscale=True
            ),
            hoverinfo = "lon+lat+text",
            name = "Cellular Trajectory"
        )
    ])
    layout = Layout(
        title='User Preprocessed Data'+'<br>'+uid,
        showlegend = True,
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            style='streets',
            center=dict(
                lat=np.mean([float(df.lat.loc[i]) for i in df.index]),
                lon=np.mean([float(df.lon.loc[i]) for i in df.index]),
            ),
            pitch=0,
            zoom=zoom
        ),
    )

    fig = dict(data=data, layout=layout)
    return fig


if __name__ == '__main__':
    uid = sys.argv[1]
    date = sys.argv[2]
    df = initialize()
    df.to_csv('data/'+date+'/'+uid+'_prepro.csv', index=False)
    #print(df)
    #fig = plot_prepro(df)
    #py.offline.plot(fig, filename='preprocess-data.html')
