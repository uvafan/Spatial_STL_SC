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
        self.loc_dict = dict()

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
        self.nodes_by_ID = dict()
        self.nodes = set()
        self.data_nodes = set()
        self.edges = set()
        self.edge_dict = dict()
        self.city = city
        self.test = 1

    def add_edge(self,edge):
        if edge not in self.edges:
            self.edges.add(edge)
            self.edge_dict[edge.ID] = edge
            return True
        return False

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes_by_ID[node.ID] = node
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

    def add_chi_parks(self):
        parks = [(41.882419,-87.619292),(41.886293,-87.717201),(41.882591,-87.622543),(41.835649,-87.607340),(41.874336,-87.769523),(41.872181,-87.618754),(41.854334,-87.653914),(41.920975,-87.645624),(41.868139,-87.629830),(41.870542,-87.654764),(41.811451,-87.634616),(41.943953,-87.738916),(41.906938,-87.702270),(41.850048,-87.716968),(41.930524,-87.653400),(41.886097,-87.617916),(41.922837,-87.634413),(41.833970,-87.634935),(41.913902,-87.668320),(41.811520,-87.719006),(41.888146,-87.761837),(41.936619,-87.679609),(41.879856,-87.650227),(41.921880,-87.685120),(41.906436,-87.663423),(41.840795,-87.647557),(41.905948,-87.645240),(41.856888,-87.673073),(41.874406,-87.692707),(41.916247,-87.641779),(41.814034,-87.610283)]
        id_str = 'park'
        c = 0
        for p in parks:
            new_node = node('{}{}'.format(id_str,str(c)),p)
            new_node.add_tag('park')
            new_node.data_node = False
            self.add_node(new_node)
            c+=1

    def add_chi_high_crime(self):
        df = pd.read_csv('crime_data.csv')
        id_str = 'crime'
        c = 0
        for index,row in df.iterrows():
            new_node = node('{}{}'.format(id_str,str(c)),(row['latitude'],row['longtitude']))
            new_node.add_tag('high_crime')
            new_node.data_node = False
            self.add_node(new_node)
            c+=1

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
