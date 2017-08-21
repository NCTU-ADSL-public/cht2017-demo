import os
import pandas as pd
import plotly as py
from plotly.graph_objs import *

mapbox_access_token = 'pk.eyJ1IjoiYWlrb2Nob3UiLCJhIjoiY2o1bWF2emI4M2ZoYjJxbnFmbXFrdHQ0ZCJ9.w0_1-IC0JCPukFL7Bpa92w'

def plot_multi_modes(uid, d_idx):
    if uid == 'u_466924201064380':
        file_list = ['20161021','20161123','20161220','20170116','20170213','20170217','20170222','20170303','20170317','20170512']
    else:
        file_list = ['20170103','20170104','20170105','20170106','20170107','20170108','20170109','20170110','20170111','20170112']

    result = pd.read_csv(os.path.join('data', uid, 'result.csv'), dtype={'uid':str, 'date':str})
    result = result[result.date == file_list[d_idx]]
    ntrips = result.shape[0]
    print result, ntrips

    trip_dfs = []
    trip_mode = []
    for i in range(ntrips):
        trip_start_t = result.iloc[i]['start_t']
        trip_end_t = result.iloc[i]['end_t']
        #filename = uid+'_'+file_list[d_idx]+'_prepro.csv'
        filename = file_list[d_idx]+'.csv'
        cellular_df = pd.read_csv(os.path.join('data', uid, 'cellular', filename), dtype=str)
        #trip_df = cellular_df[(cellular_df.ctime_unix.astype(int) >= trip_start_t)&(cellular_df.ctime_unix.astype(int) <= trip_end_t)]
        cellular_df.ctimestamp = pd.to_datetime(cellular_df.ctimestamp)
        trip_df = cellular_df[(cellular_df.ctimestamp >= pd.to_datetime(trip_start_t))&(cellular_df.ctimestamp <= pd.to_datetime(trip_end_t))]
        trip_df = trip_df.sort_values(by='ctimestamp')
        trip_dfs.append(trip_df)
        trip_mode.append(result.iloc[i]['mode'])

    colors = {"hsr": "rgb(0,116,217)", "mrt": "rgb(255,65,54)", "bus": "rgb(133,20,75)", "train": "rgb(255,133,27)"}
    names = {"hsr": "HSR trip", "mrt": "MRT trip", "bus": "Bus trip", "train": "Train trip"}
    endpt_size = 20
    trips = []
    for k in range(len(trip_dfs)):
        #k = 2
        print trip_dfs[k]
        trip_df = trip_dfs[k]
        labels = [trip_df.ctime.loc[i].split(',')[0] for i in trip_df.index]
        labels[0] = result.iloc[k].s_name+'<br>'+labels[0]
        labels[-1]= result.iloc[k].e_name+'<br>'+labels[-1]
        trip = Scattermapbox(
            lat = [trip_df.y.loc[i] for i in trip_df.index],
            lon = [trip_df.x.loc[i] for i in trip_df.index],
            text= labels,
            mode= 'markers+lines',
            marker=Marker(
                size=[endpt_size] + [10 for j in range(len(trip_df.index) - 2)] + [endpt_size],
                color=colors[trip_mode[k]]
            ),
            name = names[trip_mode[k]]+': '+result.iloc[k].s_name+' --> ' + result.iloc[k].e_name,
            hoverinfo = "text",
        )
        trips.append(trip)
        #break
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
    data = Data(trips)
    fig = dict(data=data, layout=layout)
    return fig


if __name__ == '__main__':
    fig = plot_multi_modes("u_466924201064380", 9)
    py.offline.plot(fig, filename='multi-mode_20170512.html')
