'''
Meiyi Ma, Timothy Davison, Eli Lifland
9/11/18
A short library of useful methods to supplement sc_lib.
'''
import performance
import sc_lib
import pandas as pd
import numpy as np
import math
import osmnx as ox
import sys
import os
import datetime
from collections import defaultdict
from copy import deepcopy

def load_nyc_data(graph, fin):
    f = open(fin, 'r')
    cols = f.readline().strip().split(',')
    for line in f:
        for node in graph.nodes:
            
            if type(node.name) == str: 
                if line.split(",")[2].lower().strip() == node.name.lower().strip():
                    node.data.append(line.strip().split(','))
    
    for node in graph.nodes:
        node.data = pd.DataFrame(node.data, columns=cols)
        graph.dataframe.append(node.data)    
    graph.dataframe = pd.concat(graph.dataframe)

def make_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

def load_data(city, day):
    if city == 'chicago':
        load_chicago_day(day)
    elif city == 'aarhus':
        load_aarhus()

#hardcoded for now
use_params = {'intensity','concentration','humidity'}

ranges = {
    'co': (0,1000),
    'no2': (0,20),
    'o3': (0,20),
    'lightsense': (0,124),
    'humidity': (0,100)
}

trusted_sensors = {
    'temperature': {'at0','at1','at2','at3','sht25'},
    'intensity': {'tsl260rd'},
    'humidity': {'hih4030'}
}

use_sensor_as_param = {'concentration'}
use_subsystem_as_param = {'intensity'}

def load_chicago_day(day, sample=float('inf'), folder='/media/sf_D_DRIVE'):
    perf = performance.performance_tester()
    day_str = day.replace('-','_') 
    node_df = pd.read_csv('{}/chicago_raw/nodes.csv'.format(folder))
    data_df = pd.read_csv('{}/chicago_raw/{}.csv'.format(folder,day_str),names=['timestamp','node_id','subsystem','sensor','parameter','value_raw','value_hrf'])
    perf.checkpoint('read csv')
    data_df['timestamp'] = pd.to_datetime(data_df['timestamp'])
    data_df = data_df.set_index('timestamp')
    ctr = 0
    day_path = '{}/chicago_data/{}'.format(folder,day)
    make_dir(day_path)
    date_rng = pd.date_range(start=day,end=pd.to_datetime(day)+datetime.timedelta(days=1)-datetime.timedelta(minutes=1),freq='min')
    param_dfs = dict()
    data_df = data_df.loc[data_df['parameter'].isin(use_params)]
    for param in use_params:
        if param in use_sensor_as_param:
            sensors = data_df[data_df['parameter']==param]['sensor'].unique()
            for sensor in sensors:
                if sensor not in ranges:
                    continue
                param_dfs[sensor] = pd.DataFrame(index=date_rng)
        elif param in use_subsystem_as_param:
            systems = data_df[data_df['parameter']==param]['subsystem'].unique()
            for system in systems:
                if system not in ranges:
                    continue
                param_dfs[system] = pd.DataFrame(index=date_rng)
        else:
            param_dfs[param] = pd.DataFrame(index=date_rng)
    perf.checkpoint('starting node by node')
    for index, row in node_df.iterrows():
        node_id = row['node_id']
        new_node_df = data_df[data_df['node_id']==node_id]
        if new_node_df.empty:
            continue
        for param in new_node_df['parameter'].unique():
            param_df = new_node_df.loc[new_node_df['parameter']==param]
            if param in trusted_sensors:
                param_df = param_df[param_df['sensor'].isin(trusted_sensors[param])]
                if param_df.empty:
                    continue
            if param in use_sensor_as_param:
                sensors = param_df['sensor'].unique()
                for sensor in sensors:
                    if sensor not in ranges:
                        continue
                    sensor_df = param_df.loc[param_df['sensor']==sensor]
                    process_param_df(sensor,sensor_df,param_dfs,node_id)
            elif param in use_subsystem_as_param:
                systems = param_df['subsystem'].unique()
                for system in systems:
                    if system not in ranges:
                        continue
                    system_df = param_df[param_df['subsystem']==system]
                    process_param_df(system,system_df,param_dfs,node_id)
            else:
                process_param_df(param,param_df,param_dfs,node_id)
        ctr+=1
        #perf.checkpoint('processed node')
        if ctr==sample:
            break
    print('SUMMARY FOR {}; loaded {} nodes'.format(day,ctr))
    for param in param_dfs:
        print_summary(param,day,param_dfs[param])
        param_dfs[param].to_csv('{dp}/{p}.csv'.format(dp=day_path,p=param))

def print_summary(param, day, df):
    print('-----{} SUMMARY-----'.format(param))
    periods = [[7,10],[11,14],[16,19],[20,23]]
    for period in periods:
        print('PERIOD FROM {} to {}'.format(period[0],period[1]))
        s = pd.to_datetime(day)+datetime.timedelta(hours=period[0])
        e = pd.to_datetime(day)+datetime.timedelta(hours=period[1])
        pdf = df[s:e]
        pdf = pdf.assign(avg=pdf.mean(axis=1),ma=pdf.max(axis=1))
        print('Average: {}'.format(np.nanmean(pdf['avg'])))
        print('Max: {}'.format(np.nanmax(pdf['ma'])))
        print('SD: {}'.format(np.std(pdf['avg'])))
        sys.stdout.flush()


def process_param_df(param,param_df,param_dfs,node_id):
    hrf = True
    try:
        f = float(param_df['value_hrf'][0])
        param_dfs[param][node_id] = np.nan
    except ValueError:
        '''
        try:
            f = float(param_df['value_raw'][0])
            if np.isnan(f):
                raise ValueError
            param_dfs[param][node_id] = np.nan
            hrf=False
        except ValueError:
            #don't care about non-numeric for now
        '''
        return        
    keep = 'value_hrf' if hrf else 'value_raw'
    for col in param_df.columns:
        if col != keep:
            param_df = param_df.drop(col,axis=1)
    param_df.columns = ['value']
    for tm, prow in param_df.iterrows():
        minute = tm - datetime.timedelta(seconds=tm.second,microseconds=tm.microsecond)
        if np.isnan(param_dfs[param][node_id][minute]):
            try:
                val = float(prow['value'])
                if val >= ranges[param][0] and val <= ranges[param][1]:
                    param_dfs[param].at[minute,node_id] = val
            except ValueError:
                continue

def get_graph(city):
    if city == 'chicago':
        return create_chicago_graph()
    elif city == 'aarhus':
        return create_aarhus_graph('/media/sf_D_DRIVE/aarhus_raw') 
    elif city == 'new_york':
        return create_new_york_graph()

def create_chicago_graph():
    node_df = pd.read_csv('/media/sf_D_DRIVE/chicago_raw/nodes.csv')
    graph = sc_lib.graph('chicago')
    for index, row in node_df.iterrows():
        p = (row['lat'],row['lon'])
        new_node = sc_lib.node(row['node_id'],p)
        graph.add_node(new_node)
    add_pois(graph,amenities=['school','theatre','hospital'])
    graph.add_chi_parks()
    graph.add_chi_high_crime()
    return graph

def load_parking_locs(path,graph):
    fin = '{}/parking/aarhus_parking_address.csv'.format(path)
    df = pd.read_csv(fin)
    start = len(graph.nodes)
    for index, row in df.iterrows():
        new_node = sc_lib.node(row['garagecode'],(row['latitude'],row['longitude']))
        new_node.add_tag('parking')
        graph.add_node(new_node)        
    #print('parking: {} nodes'.format(len(graph.nodes)-start))

def midpoint(p1,p2):
    return ((p1[0]+p2[0])/2,(p1[1]+p2[1])/2)

def load_traffic_locs(path,graph):
    fin = '{}/traffic/trafficMetaData.csv'.format(path)
    df = pd.read_csv(fin)
    start = len(graph.nodes)
    for index, row in df.iterrows():
        p1 = (row['POINT_1_LAT'],row['POINT_1_LNG'])
        p2 = (row['POINT_2_LAT'],row['POINT_2_LNG'])
        new_node = sc_lib.node(row['extID'],midpoint(p1,p2))
        new_node.add_tag('traffic')
        graph.add_node(new_node)        
    #print('traffic: {} nodes'.format(len(graph.nodes)-start))

def load_library_locs(path,graph):
    fin = '{}/library_events/aarhus_libraryEvents.csv'.format(path)
    df = pd.read_csv(fin)
    start = len(graph.nodes)
    for index, row in df.iterrows():
        new_node = sc_lib.node(row['lid'],(row['latitude'],row['longitude']))
        new_node.add_tag('library')
        graph.add_node(new_node)        
    #print('library: {} nodes'.format(len(graph.nodes)-start))

def add_pois(graph,amenities=None,dist=15000):
    p = graph.centroid()
    graph.add_OSMnx_pois(amenities=['school','theatre','hospital'],p=p,dist=dist)

def load_parking_data(path,day_dfs):
    data_df = pd.read_csv('{}/aarhus_raw/aarhus_parking.csv'.format(path))

def load_traffic_data(path,day_dfs):
    pass

def load_weather_data(path,day_dfs):
    pass

def load_event_data(path,day_dfs):
    pass

def load_aarhus(path='/media/sf_D_DRIVE'):
    days = pd.date_range(start='2014-08-01',end='2014-09-30',freq='D')
    day_dfs = dict()
    for day in days:
        make_dir('{}/aarhus_data/{}'.format(path,str(day)))
        mins = pd.date_range(start=day,end=day+datetime.timedelta(days=1)-datetime.timedelta(minutes=1),freq='min')
        day_dfs[str(day)] = pd.DataFrame(index=mins)
    load_parking_data(path,deepcopy(day_dfs))
    load_traffic_data(path,deepcopy(day_dfs))
    load_weather_data(path,deepcopy(day_dfs))
    load_event_data(path,deepcopy(day_dfs))
    
def create_aarhus_graph(path):
    graph = sc_lib.graph('aarhus')
    load_parking_locs(path,graph)
    load_traffic_locs(path,graph)
    load_library_locs(path,graph)
    add_pois(graph,amenities=['school'],dist=10000)
    return graph

def create_new_york_graph():
    graph = sc_lib.graph('new_york')
    graph.add_OSMnx_data_within_dist((40.7831,-73.9712),dist=2000)
    add_pois(graph,amenities=['school','hospital','theatre'],dist=2000)
    graph.add_ny_parks()
    return graph

