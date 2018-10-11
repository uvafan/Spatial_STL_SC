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

def load_chicago_data(path, abridged=False, sample=float('inf')):
    perf = performance.performance_tester()
    data_filename = 'data.csv' if not abridged else 'abridged_data.csv'
    node_df = pd.read_csv('{}nodes.csv'.format(path))
    data_df = pd.read_csv(path+data_filename)
    data_df['timestamp'] = pd.to_datetime(data_df['timestamp'])
    data_df = data_df.set_index('timestamp')
    perf.checkpoint('loaded csvs')
    graph = sc_lib.graph()
    ctr = 0
    minLat = float('inf')
    maxLat = float('-inf')
    minLon = float('inf')
    maxLon = float('-inf')
    for index, row in node_df.iterrows():
        if isinstance(row['end_timestamp'],str):
            continue
        p = (row['lat'],row['lon'])
        minLat = min(minLat,row['lat'])
        minLon = min(minLon,row['lon'])
        maxLon = max(maxLon,row['lon'])
        maxLat = max(maxLat,row['lat'])
        node_df = data_df.loc[data_df['node_id']==row['node_id']]
        new_node = sc_lib.node(row['node_id'],p)
        graph.add_node(new_node)
        graph.add_OSMnx_pois(amenities=['school','theatre','hospital'],p=p)
        ctr+=1
        if ctr == sample:
            break 
    #graph.add_OSMnx_pois(amenities=['school'],north=maxLat,south=minLat,east=maxLon,west=minLon)
    perf.checkpoint('loaded osmnx data')
    return graph 

def load_parking_locs(path,graph):
    fin = '{}parking/aarhus_parking_address.csv'.format(path)
    df = pd.read_csv(fin)
    for index, row in df.iterrows():
        new_node = sc_lib.node(row['garagecode'],(row['latitude'],row['longitude']))
        new_node.add_tag('parking')
        graph.add_node(new_node)        

def midpoint(p1,p2):
    return ((p1[0]+p2[0])/2,(p1[1]+p2[1])/2)

def load_traffic_locs(path,graph):
    fin = '{}traffic/trafficMetaData.csv'.format(path)
    df = pd.read_csv(fin)
    for index, row in df.iterrows():
        p1 = (row['POINT_1_LAT'],row['POINT_1_LNG'])
        p2 = (row['POINT_2_LAT'],row['POINT_2_LNG'])
        new_node = sc_lib.node(row['extID'],midpoint(p1,p2))
        new_node.add_tag('traffic')
        graph.add_node(new_node)        

def load_library_locs(path,graph):
    fin = '{}library_events/aarhus_libraryEvents.csv'.format(path)
    df = pd.read_csv(fin)
    for index, row in df.iterrows():
        new_node = sc_lib.node(row['lid'],(row['latitude'],row['longitude']))
        new_node.add_tag('library')
        graph.add_node(new_node)        

def add_pois(graph):
    p = graph.centroid()
    graph.add_OSMnx_pois(amenities=['school','theatre','hospital'],p=p,dist=5000)

def load_aarhus_data(path):
    graph = sc_lib.graph()
    load_parking_locs(path,graph)
    load_traffic_locs(path,graph)
    load_library_locs(path,graph)
    add_pois(graph)
    return graph
