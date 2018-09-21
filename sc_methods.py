'''
Meiyi Ma, Timothy Davison, Eli Lifland
9/11/18
A short library of useful methods to supplement sc_lib.
'''
import performance
import sc_lib
import pandas as pd
import numpy
import math
import osmnx as ox
from collections import defaultdict

'''
Automates OSM data download.
Returns: a directed graph containing OSM streets as nodes, OSM intersections as edges.
Should be modified to accomodate available data in adding features to nodes.
'''
def graph_from_OSMnx(graph):
    g = sc_lib.graph()

    node_data = graph.node.data()
    print('{} nodes'.format(len(node_data)))

    for item in graph.node.data():
        edge = sc_lib.edge(item[0],(item[1]["y"],item[1]["x"]))
        g.add_edge(edge)
        
    edge_data = graph.edges(data=True)
    print('{} edges'.format(len(edge_data)))

    intersection_to_nodes = defaultdict(list)
    for item in edge_data:       
        node.intersections = (item[0], item[1])      
        intersection0Coords = g.edge_dict[item[0]].coordinates 
        intersection1Coords = g.edge_dict[item[1]].coordinates 
        lon = (intersection0Coords['x'] + intersection1Coords['x'])/2.0
        lat = (intersection0Coords['y'] + intersection1Coords['y'])/2.0
        
        node = sc_lib.node(item[2]["osmid"], (lat,lon))
        g.add_node(node)  
        intersection_to_nodes[node.intersections[0]].append(node)
    
    for node_a in g.nodes:
        for node_b in intersection_to_nodes[node_a.intersections[1]]:
            node_a.add_successor(node_b)
            node_b.add_predecessor(node_a)

    return g

'''
To be improved/ modified based upon what useful information is available.
'''
def graph_statistics(graph):
    print ("Number of Nodes:", graph.nodes.size())
    print ("Number of Edges:", graph.edges.size())
    return None;


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
    return intersects;

def segments_in_street(graph, name):
    segs = []
    for item in graph.nodes:
        if name in item.name:
            segs.append(item)
    return segs;


'''
Given a sc_lib graph, loads CSV data into nodes in the graph.
Customized to fit NYC OpenData (which uses street names), but can be improved
to match nodes with specific geographical coordinates/ more sohpisticated parsing
and node alignment. 
'''
def load_nyc_data(graph, file):
    f = open(file, 'r')
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

def load_chicago_data(path, abridged=False):
    perf = performance.performance_tester()

    data_filename = 'data.csv' if not abridged else 'abridged_data.csv'
    node_df = pd.read_csv(path+'nodes.csv')
    data_df = pd.read_csv(path+data_filename)
    data_df['timestamp'] = pd.to_datetime(data_df['timestamp'])
    data_df = data_df.set_index('timestamp')

    perf.checkpoint('loaded csvs')

    minLat = float('inf')
    maxLat = float('-inf')
    minLon = float('inf')
    maxLon = float('-inf')
    aot_nodes = dict() 
    for index, row in node_df.iterrows():
        aot_nodes[row['node_id']] = (row['lat'],row['lon'])
        minLat = min(row['lat'],minLat)
        maxLat = max(row['lat'],maxLat)
        minLon = min(row['lon'],minLon)
        maxLon = max(row['lon'],maxLon)

    perf.checkpoint('found min/max')
    print('maxLat: {} minLat: {} maxLon: {} minLon: {}'.format(maxLat,minLat,maxLon,minLon))

    G = ox.graph_from_bbox(maxLat,minLat,maxLon,minLon)
    
    perf.checkpoint('osmnx loaded graph')
    
    graph = graph_from_OSMnx(G)

    perf.checkpoint('converted graph')
   
    graph.df = data_df
    
    #TODO: match data to nodes based on coords
    
    return graph 

'''
Returns a set of nodes which lie within a Euclidian distance from a provided center point.
Note -- Currently distance measured in geographical minutes, not in Km or Mi. 
        To be adjusted in the future as necessary.
'''
def nodes_from_point(graph, point, d): 
        if type(point) == sc_lib.node:
            coordinates = (point.middle_coordinate['x'], point.middle_coordinate['y'])
        else: 
            coordinates = (point[0], point[1])
        return_nodes = set([])
        for node in graph.nodes:
            euclidian = math.sqrt(((coordinates[0]-node.middle_coordinate['x'])**2 + (coordinates[1]-node.middle_coordinate['y'])**2))
            if euclidian <= d:
                return_nodes.add(node)
        return return_nodes;

