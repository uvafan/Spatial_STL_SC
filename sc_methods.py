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

'''
Two functions which are useful when used together;
retrieves either all segments along a given street name (as streets are often spread
out across multiple nodes), and to provide all the intersections along a certain street.
'''
def intersections_along_street(graph, name):
    intersects = []
    segs = segments_in_street(graph, name)
    for item in graph.edges:
        for segment in segs:
            if item.id in segment.intersections:
                intersects.append(item)
    return intersects

def segments_in_street(graph, name):
    segs = []
    for item in graph.nodes:
        if name in item.name:
            segs.append(item)
    return segs

'''
Given a sc_lib graph, loads CSV data into nodes in the graph.
Customized to fit NYC OpenData (which uses street names), but can be improved
to match nodes with specific geographical coordinates/ more sohpisticated parsing
and node alignment. 
'''
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
    aot_nodes = dict() 
    ctr = 0
    for index, row in node_df.iterrows():
        if isinstance(row['end_timestamp'],str):
            continue
        p = (row['lat'],row['lon'])
        graph.add_OSMnx_data(p,data_id=row['node_id'])
        graph.add_OSMnx_pois(p,amenities=['school'],dist=1000)
        ctr+=1
        if ctr == sample:
            break 
    perf.checkpoint('loaded osmnx data')
    graph.chicago_df = data_df
    return graph 
