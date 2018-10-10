'''
Meiyi Ma, Timothy Davison, Eli Lifland
STL for Smart Cities
Object Library: Node, Edge, Graph
'''
import queue
import pandas as pd
import numpy as np
import osmnx as ox
from collections import defaultdict
from datetime import datetime
from shapely.geometry import Point
from shapely.geometry import MultiPoint

class node:
    def __init__(self, ID, coordinates):
        if isinstance(ID,list):
            ID = tuple(sorted(ID))
        self.ID = ID
        self.coordinates = coordinates #(lat,lon)
        self.tf_satisfied = True # whether req is satisfied
        self.tags = set()
        self.predecessors = set()
        self.successors = set()
        self.data_id = None
        self.intersections = tuple()

    def __str__(self):
        return 'ID: {} Coordinates: {}'.format(self.ID,self.coordinates)

    def add_successor(self, node):
        self.successors.add(node)
        
    def add_predecessor(self, node):
        self.predecessors.add(node)

    def add_tag(self,tag):
        self.tags.add(tag)

    #for sets
    def __hash__(self):
        return hash(self.ID)
   
class edge:
    def __init__(self, ID, coordinates):
        if isinstance(ID,list):
            ID = tuple(sorted(ID))
        self.ID = ID
        self.coordinates = coordinates    

    #for sets
    def __hash__(self):
        return hash(self.ID)
    
class graph:
    def __init__(self):
        self.nodes = set()
        self.edges = set()
        self.node_dict = dict()
        self.edge_dict = dict()
        self.df = pd.DataFrame() 

    def add_edge(self,edge):
        if edge.ID not in self.edge_dict:
            self.edges.add(edge)
            self.edge_dict[edge.ID] = edge
            return True
        return False

    def add_node(self, node):
        if node.ID not in self.node_dict:
            self.nodes.add(node)
            self.node_dict[node.ID] = node
            return True
        return False

    def a_node(self):
        return next(iter(self.nodes))

    def add_OSMnx_pois(self,p,dist=5000,amenities=None):
        nearby_pois = ox.pois_from_point(p,distance=dist,amenities=amenities)
        for index, row in nearby_pois.iterrows():
            geo = row['geometry']
            point = (0,0)
            try:
                point = (geo.y,geo.x)
            except:
                point = (geo.centroid.y,geo.centroid.x)
            new_node = node(row['osmid'],point)
            new_node.add_tag(row['amenity'])
            self.add_node(new_node)

    def add_OSMnx_data(self,p,dist=100,data_id=None):
        try:
            osmnx_graph = ox.graph_from_point(p,distance=dist,network_type='drive')
        except:
            return
        node_data = osmnx_graph.node.data()

        for item in node_data:
            new_edge = edge(item[0],(item[1]["y"],item[1]["x"]))
            self.add_edge(new_edge)
        
        edge_data = osmnx_graph.edges(data=True)

        intersection_to_nodes = defaultdict(list)
        for item in edge_data:       
            intersection0Coords = self.edge_dict[item[0]].coordinates 
            intersection1Coords = self.edge_dict[item[1]].coordinates 
            lon = (intersection0Coords[1] + intersection1Coords[1])/2.0
            lat = (intersection0Coords[0] + intersection1Coords[0])/2.0
        
            new_node = node(item[2]['osmid'], (lat,lon))
            new_node.intersections = (item[0], item[1])      
            new_node.data_id = data_id
            if self.add_node(new_node):
                intersection_to_nodes[new_node.intersections[0]].append(new_node)
    
        for node_a in self.nodes:
            if not node_a.intersections:
                continue
            for node_b in intersection_to_nodes[node_a.intersections[1]]:
                node_a.add_successor(node_b)
                node_b.add_predecessor(node_a)

    def __str__(self):
        return str(self.chicag_df.head(5))

    '''
    Returns a set of nodes which sit between i and j (inclusive) connections away from 
        the given start node. Assumes the graph preserves direction.
    '''
    def bfs_set(self, start, i, j, directed=True):
        visited = set([])
        q = queue.Queue()
        q.put(start)
        visited.add(start)
        distance_dict = {}
        distance_dict[start.intersections] = 0
        requested_nodes = set([])
        while q.not_empty:
            v = q.get()
            neighbors = v.successors
            if not directed:
                neighbors = neighbors.union(v.predecessors)
            for successor in neighbors:
                if successor not in visited:
                   q.put(successor)
                   distance_dict[successor.intersections] = distance_dict[v.intersections] + 1
                   if distance_dict[successor.intersections] > j+1:
                       return requested_nodes
                   if distance_dict[successor.intersections] >= i and distance_dict[successor.intersections] <= j:
                       requested_nodes.add(successor)
            visited.add(v)
    
    '''
    Returns a set of nodes which sit within a polygon, given a set of boundary nodes.
    Can input any number (greater than or equal to three) of boundary nodes.
    '''         
    def nodes_in_polygon(self, nodes):
        tuples = []
        if isinstance(next(iter(nodes)),tuple):
            tuples = list(nodes) 
        else:
            for node in nodes:
                tuples.append((node.middle_coordinate['x'], node.middle_coordinate['y']))
        poly = MultiPoint(tuples).convex_hull
        contained_nodes = set([])
        for node in self.nodes:
            if poly.contains(Point((node.middle_coordinate['x'], node.middle_coordinate['y']))):
                contained_nodes.add(node)
        return contained_nodes;
