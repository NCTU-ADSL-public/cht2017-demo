import pandas as pd
import numpy as np
import sys, os, math, datetime, csv

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


def generate_raw_df(date):
    uid = 'u_466924201064380'
    filename = date + '.csv'
    df = pd.read_csv('data/Peng/'+filename)
    df['spatial'] = df['x'].astype(str)+','+df['y'].astype(str)
    totalList = []
    for s_point in df.groupby(df.spatial):
        timestamps = np.array(s_point[1].ctime_unix.sort_values().unique())
        lon = s_point[0].split(',')[0]
        lat = s_point[0].split(',')[1]
        pop = len(timestamps)
        #totalList.append([uid, lon, lat, pop, timestamps])
        totalList.append([uid, lon, lat, pop])
    #df = pd.DataFrame(totalList, columns=['uid','lon','lat','pop','timestamps'])
    df = pd.DataFrame(totalList, columns=['uid','lon','lat','pop'])
    df.sort_values(by='pop', ascending=False, inplace=True)
    df.to_csv('data/Peng/'+uid+'_'+date+'_raw.csv', index=False)



def generate_prepro_df(date):
    uid = 'u_466924201064380'
    filename = date + '.csv'
    with open('data/Peng/'+filename, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the headers
        data = [[row[0], row[6], row[3], row[4]] for row in reader]
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
    df.to_csv('data/Peng/'+uid+'_'+date+'_prepro.csv', index=False)


def generate_raw_raw_data(date):
    uid = 'u_466924201064380'
    filename = date + '.csv'
    with open(os.path.join('data', uid, 'cellular', filename),"r") as f:
        reader = csv.reader(f)
        next(reader, None)
        raw_data = [[row[0], row[5], row[3], row[4], row[6]] for row in reader]
        df = pd.DataFrame(raw_data)
        df.to_csv(os.path.join('data', uid, 'cellular',date), index=False, header=False)

if __name__ == '__main__':
    
    date_list = ['20161021', '20161123', '20161220', '20170116', '20170213', '20170217', '20170222', '20170303', '20170317', '20170512']

    for date in date_list:
        #generate_raw_df(date)
        #generate_prepro_df(date)
        generate_raw_raw_data(date)