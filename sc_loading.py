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

def load_chicago_data_day(path, trusted_sensors, use_sensor_as_param, abridged=False, sample=float('inf')):
    perf = performance.performance_tester()
    data_filename = 'data.csv' if not abridged else 'abridged_data.csv'
    node_df = pd.read_csv('{}nodes.csv'.format(path))
    data_df = pd.read_csv(path+data_filename)
    data_df['timestamp'] = pd.to_datetime(data_df['timestamp'])
    data_df = data_df.set_index('timestamp')
    perf.checkpoint('loaded csvs')
    ctr = 0
    make_dir('data')
    make_dir('data/chicago')
    day_str = str(data_df.index[0]).split()[0]
    day_path = 'data/chicago/{}'.format(day_str)
    make_dir(day_path)
    date_rng = pd.date_range(start=day_str,end=pd.to_datetime(day_str)+datetime.timedelta(days=1),freq='min')
    param_dfs = dict()
    for param in data_df['parameter'].unique():
        if param in use_sensor_as_param:
            sensors = data_df.loc[data_df['parameter']==param]['sensor'].unique()
            for sensor in sensors:
                param_dfs[sensor] = pd.DataFrame(index=date_rng)
        else:
            param_dfs[param] = pd.DataFrame(index=date_rng)
    for index, row in node_df.iterrows():
        perf.checkpoint('processed node')
        node_id = row['node_id']
        new_node_df = data_df.loc[data_df['node_id']==node_id]
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
                    sensor_df = param_df.loc[param_df['sensor']==sensor]
                    process_param_df(sensor,sensor_df,param_dfs,node_id)
            else:
                process_param_df(param,param_df,param_dfs,node_id)
        ctr+=1
        if ctr==sample:
            break
    for param in param_dfs:
        param_dfs[param].to_csv('{dp}/{p}'.format(dp=day_path,p=param))
    perf.checkpoint('wrote param dfs to csvs')

def process_param_df(param,param_df,param_dfs,node_id):
    hrf = True
    try:
        f = float(param_df['value_hrf'][0])
        if np.isnan(f):
            raise ValueError
        param_dfs[param][node_id] = np.nan
    except ValueError:
        try:
            f = float(param_df['value_raw'][0])
            if np.isnan(f):
                raise ValueError
            param_dfs[param][node_id] = np.nan
            hrf=False
        except ValueError:
            #don't care about non-numeric for now
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
                param_dfs[param].at[minute,node_id] = prow['value']
            except ValueError:
                continue

def create_chicago_graph(path,dist=5000):
    node_df = pd.read_csv('{}/nodes.csv'.format(path))
    graph = sc_lib.graph('chicago')
    for index, row in node_df.iterrows():
        p = (row['lat'],row['lon'])
        new_node = sc_lib.node(row['node_id'],p)
        graph.add_node(new_node)
    add_pois(graph,amenities=['school','theatre','hospital'],dist=dist)
    return graph

def load_parking_locs(path,graph):
    fin = '{}parking/aarhus_parking_address.csv'.format(path)
    df = pd.read_csv(fin)
    start = len(graph.nodes)
    for index, row in df.iterrows():
        new_node = sc_lib.node(row['garagecode'],(row['latitude'],row['longitude']))
        new_node.add_tag('parking')

def load_parking_locs(path,graph):
    fin = '{}parking/aarhus_parking_address.csv'.format(path)
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
    fin = '{}traffic/trafficMetaData.csv'.format(path)
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
    fin = '{}library_events/aarhus_libraryEvents.csv'.format(path)
    df = pd.read_csv(fin)
    start = len(graph.nodes)
    for index, row in df.iterrows():
        new_node = sc_lib.node(row['lid'],(row['latitude'],row['longitude']))
        new_node.add_tag('library')
        graph.add_node(new_node)        
    #print('library: {} nodes'.format(len(graph.nodes)-start))

def add_pois(graph,amenities=None,dist=5000):
    p = graph.centroid()
    graph.add_OSMnx_pois(amenities=['school','theatre','hospital'],p=p,dist=dist)

def load_aarhus_data(path):
    graph = sc_lib.graph()
    load_parking_locs(path,graph)
    load_traffic_locs(path,graph)
    load_library_locs(path,graph)
    add_pois(graph,amenities=['school','theatre','hospital'])
    return graph
