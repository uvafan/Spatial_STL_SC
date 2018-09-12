'''
Meiyi Ma, Timothy Davison, Eli Lifland
9/11/18
A short library of useful methods to supplement sc_lib.
'''


import sc_lib
import pandas as pd
import math
import osmnx as ox

'''
Automates OSM data download.
Returns: a directed graph containing OSM streets as nodes, OSM intersections as edges.
Should be modified to accomodate available data in adding features to nodes.
'''
def graph_from_OSMnx(graph):
    g = sc_lib.graph()

    for item in graph.node.data():
        edge = sc_lib.edge(item[0])
        edge.coordinates["x"] = item[1]["x"]
        edge.coordinates["y"] = item[1]["y"]
        if 'highway' in item[1].keys():
            edge.type = item[1]['highway']
        g.edges.add(edge)      
        g.edge_dict[item[0]] = edge
        
        
    for item in graph.edges(data=True):       
        node = sc_lib.node(item[2]["osmid"])
        node.intersections = (item[0], item[1])      
        if 'name' in item[2].keys():
            node.name = item[2]['name']
        if 'length' in item[2].keys():
            node.length = item[2]['length']
        if 'highway' in item[2].keys():
            node.type = item[2]['highway']
        if 'lanes' in item[2].keys():
            node.lanes = item[2]['lanes']
        if 'oneway' in item[2].keys():
            node.oneway = item[2]['oneway']        
            ''' SAMPLE ADDITION TO ATTRIVUTE DICTIONARY:
            if 'oneway' not in g.attribute_set.keys():
                g.attribute_set['oneway'] = {node}
            else:
                g.attribute_set['oneway'].add(node)
            '''
            
        node.middle_coordinate['x'] = ((g.edge_dict[node.intersections[0]].coordinates['x'] + 
                              g.edge_dict[node.intersections[1]].coordinates['x'])/2.0)
        node.middle_coordinate['y'] = ((g.edge_dict[node.intersections[0]].coordinates['y'] +
                          g.edge_dict[node.intersections[0]].coordinates['y'])/2.0)
        g.nodes.add(node)  
        g.node_intersections_dict[node.intersections] = node
    
    for node in g.nodes:
        g.node_count += 1
        for edge in graph.edges:
            if node.intersections[1] == edge[0]:
                node.add_successor(g.node_intersections_dict[(edge[0], edge[1])])
            if node.intersections[0] == edge[1]:
                node.add_predecessor(g.node_intersections_dict[(edge[0], edge[1])])
    return g;

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


'''
# SAMPLE
G = ox.graph_from_point((56.21728389, 10.2336194), distance=2000)
graph = graph_from_OSMnx(G)
'''
