'''
Meiyi Ma, Timothy Davison, Eli Lifland
STL for Smart Cities
Object Library: Node, Edge, Graph
'''
import queue
import pandas as pd
import numpy as np
from datetime import datetime
from shapely.geometry import Point
from shapely.geometry import MultiPoint

class node:
    def __init__(self, ID, coordinates):
        self.ID = ID
        self.coordinates = coordinates #(lat,lon)
        self.tf_satisfied = True # whether req is satisfied
        self.tags = set()
        self.predecessors = set([]) 
        self.successors = set([])

    def __str__(self):
        return 'ID: {} Coordinates: {}'.format(self.ID,self.coordinates)

    def add_successor(self, node):
        self.successors.add(node)
        
    def add_predecessor(self, node):
        self.predecessors.add(node)
   
class edge:
    def __init__(self, ID, coordinates):
        self.ID = ID
        self.coordinates = coordinates    
    
class graph:
    def __init__(self):
        self.nodes = set()
        self.edges = set()
        self.edge_dict = dict()
        self.df = pd.DataFrame() 

    def add_edge(self,edge):
        self.edges.add(edge)
        self.edge_dict[edge.ID] = edge

    def add_node(self, node):
        self.nodes.add(node)

    def a_node(self):
        return next(iter(self.nodes))

    def __str__(self):
        return str(self.df.head(5))

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
