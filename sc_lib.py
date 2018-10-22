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
import geopy

class node:
    def __init__(self, ID, coordinates):
        if isinstance(ID,list):
            ID = tuple(sorted(ID))
        self.ID = str(ID)
        self.coordinates = coordinates #(lat,lon)
        self.tf_satisfied = True # whether req is satisfied
        self.tags = list()
        self.predecessors = set()
        self.successors = set()
        self.intersections = tuple()
        self.data_node = True

    #returns distance between self and other in km
    def dist_to(self,other):
        return geopy.distance.vincenty(self.coordinates,other.coordinates).km

    def __str__(self):
        ret = 'ID: {} Coordinates: {}'.format(self.ID,self.coordinates)
        ret += '\ntags: {}'.format(self.tags)
        return ret

    def add_successor(self, node):
        self.successors.add(node)
        
    def add_predecessor(self, node):
        self.predecessors.add(node)

    def add_tag(self,tag):
        self.tags.append(tag)

    def set_df(self,df):
        self.df = df

    #for sets
    def __eq__(self,other):
        return self.ID == other.ID and self.coordinates == other.coordinates

    def __hash__(self):
        return hash(self.ID) ^ hash(self.coordinates)
   
class edge:
    def __init__(self, ID, coordinates):
        if isinstance(ID,list):
            ID = tuple(sorted(ID))
        self.ID = ID
        self.coordinates = coordinates    

    #for sets
    def __eq__(self,other):
        return self.ID == other.ID and self.coordinates == other.coordinates

    def __hash__(self):
        return hash(self.ID) ^ hash(self.coordinates)
    
class graph:
    def __init__(self,city):
        self.nodes = set()
        self.data_nodes = set()
        self.edges = set()
        self.edge_dict = dict()
        self.city = city

    def add_edge(self,edge):
        if edge not in self.edges:
            self.edges.add(edge)
            self.edge_dict[edge.ID] = edge
            return True
        return False

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.add(node)
            if node.data_node:
                self.data_nodes.add(node)
            return True
        return False

    def a_node(self):
        return next(iter(self.nodes))

    #add OSM points of interest to graph within distance dist of point p
    def add_OSMnx_pois(self,amenities=None,p=None,dist=2500,north=None,south=None,east=None,west=None):
        nearby_pois = None
        if p:
            nearby_pois = ox.pois_from_point(p,distance=dist,amenities=amenities)
        else:
            nearby_pois = ox.osm_poi_download(north=north,south=south,east=east,west=west,amenities=amenities)
        for index, row in nearby_pois.iterrows():
            if not isinstance(row['amenity'],str):
                continue
            geo = row['geometry']
            point = (0,0)
            try:
                point = (geo.y,geo.x)
            except:
                point = (geo.centroid.y,geo.centroid.x)
            new_node = node(row['osmid'],point)
            new_node.add_tag(row['amenity'])
            new_node.data_node = False
            self.add_node(new_node)

    #add OSM nodes within distance dist of p, assign data to them 
    def add_OSMnx_data_within_dist(self,p,dist=250,data_id=None,data_df=None):
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
            new_node.df = data_df
            if self.add_node(new_node):
                intersection_to_nodes[new_node.intersections[0]].append(new_node)
    
        for node_a in self.nodes:
            if not node_a.intersections:
                continue
            for node_b in intersection_to_nodes[node_a.intersections[1]]:
                node_a.add_successor(node_b)
                node_b.add_predecessor(node_a)

    def centroid(self):
        lat_sum = 0
        lon_sum = 0
        for node in self.nodes:
            lat_sum += node.coordinates[0]
            lon_sum += node.coordinates[1]
        return (lat_sum/len(self.nodes),lon_sum/len(self.nodes))
