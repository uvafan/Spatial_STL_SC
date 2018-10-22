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

def load_chicago_data_day(path, abridged=False, sample=float('inf')):
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
    agg_dfs = dict()
    for param in data_df['parameter'].unique():
        agg_dfs[param] = pd.DataFrame(index=date_rng)
    for index, row in node_df.iterrows():
        perf.checkpoint('processed node')
        new_node_df = data_df.loc[data_df['node_id']==row['node_id']]
        if new_node_df.empty:
            continue
        node_path = '{dp}/{i}'.format(dp=day_path,i=row['node_id'])
        make_dir(node_path)
        for param in new_node_df['parameter'].unique():
            param_df = new_node_df.loc[new_node_df['parameter']==param]
            param_df.to_csv('{np}/{p}'.format(np=node_path,p=param))
            try:
                f = float(param_df['value_hrf'][0])
                agg_dfs[param][row['node_id']] = np.nan
            except ValueError:
                #don't care about non-numeric for now
                continue
            for tm, prow in param_df.iterrows():
                minute = tm - datetime.timedelta(seconds=tm.second,microseconds=tm.microsecond)
                if np.isnan(agg_dfs[param][row['node_id']][minute]):
                    try:
                        agg_dfs[param].at[minute,row['node_id']] = prow['value_hrf']
                    except ValueError:
                        continue
        ctr+=1
        if ctr==sample:
            break
    for param in data_df['parameter'].unique():
        agg_dfs[param].to_csv('{dp}/{p}'.format(dp=day_path,p=param))
    perf.checkpoint('loaded data')

def create_chicago_graph(path):
    perf = performance.performance_tester()
    node_df = pd.read_csv('{}nodes.csv'.format(path))
    graph = sc_lib.graph('chicago')
    for index, row in node_df.iterrows():
        p = (row['lat'],row['lon'])
        new_node = sc_lib.node(row['node_id'],p)
        graph.add_node(new_node)
    add_pois(graph,amenities=['school','theatre','hospital'],dist=1000)
    perf.checkpoint('created graph')
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
