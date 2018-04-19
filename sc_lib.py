'''
Meiyi Ma, Timothy Davison
STL for Smart Cities
Object Library: Node, Edge, Graph

'''


import queue
from shapely.geometry import Point, Polygon
from shapely.geometry import MultiPoint



''' 
Streets will be saved as nodes.
Class attributes were selected based upon the available data from OSMNX.
'''
class node:
    
    def __init__(self, identifier):
        self.intersections = None
        self.sensor_states = set([])
        self.name = None
        self.length = None
        self.oneway = None
        self.type = None
        self.identifier = identifier
        self.lanes = None
        self.middle_coordinate = {}
        
        self.predecessors = set([])
        self.successors = set([])
    
    def add_intersection(self, intersections):
        self.intersections.add(intersections)
           
    def equals(self, node2):
        return (self.intersections == node2.intersections & self.identifier 
                == node2.identifier & self.sensor_states == node2.sensor_states)
        
    def add_successor(self, node):
        self.successors.add(node)
        
    def add_predecessor(self, node):
        self.predecessors.add(node)
    
    def print(self):
        print ("Intersections,", self.intersections, "| Name:", self.name, 
               "| ID", self.identifier)

'''
Intersections will be saved as edges.
Class attributes were selected based upon the available data from OSMNX.
'''
class edge:
    
    def __init__(self, identifier):
        self.coordinates = {}
        self.sensor_states = set([])
        self.id = identifier
        self.type = None
        self.inputs = set([])
        self.outputs = set([])
        
    def equals(self, edge2):
        return (self.coordinates == edge2.coordinates & self.id == edge2.id
                & self.sensor_states == edge2.sensor_states)
   
    def print(self):
        print ("Coordinates:", self.coordinates, "\n", "Connected Nodes:", self.connected_nodes)


'''
The graph class.
''' 
class graph:
    
    def __init__(self):
        self.nodes = set([])
        self.edges = set([])
        self.satisfaction_degree = 0.0
        self.node_intersections_dict = {}
        self.edge_dict = {}
        self.attribute_set = {}
        self.node_count = 0
        
    def add_node(self, node):
        self.nodes.add(node)
        
    def add_edge(self, edge):
        self.edges.add(edge)
    
    def print_nodes(self):
        for node in self:
            node.print()
    
    def print_edges(self):
        for edge in self:
            edge.print()
    
    def containsNode(self, node):
        if node in self.nodes:
            return True;
        return False;
    
    def containsEdge(self, edge):
        if edge in self.edges:
            return True;
        return False;  
    
    def bfs_set(self, start, i, j):
        visited = set([])
        q = queue.Queue()
        q.put(start)
        visited.add(start)
        distance_dict = {}
        distance_dict[start.intersections] = 0
        requested_nodes = set([])
        while q.not_empty:
           v = q.get()
           for successor in v.successors:
               if successor not in visited:
                  q.put(successor)
                  distance_dict[successor.intersections] = distance_dict[v.intersections] + 1
                  if distance_dict[successor.intersections] > j+1:
                      return requested_nodes
                  if distance_dict[successor.intersections] >= i and distance_dict[successor.intersections] <= j:
                      requested_nodes.add(successor)
           visited.add(v)
               
        
    def undirected_bfs_set(self, start, i, j):      
        visited = set([])
        q = queue.Queue()
        q.put(start)
        visited.add(start)
        distance_dict = {}
        distance_dict[start.intersections] = 0
        requested_nodes = set([])
        while q.not_empty:
           v = q.get()
           for successor in v.successors.union(v.predecessors):
               if successor not in visited:
                  q.put(successor)
                  distance_dict[successor.intersections] = distance_dict[v.intersections] + 1
                  if distance_dict[successor.intersections] > j+1:
                      return requested_nodes
                  if distance_dict[successor.intersections] >= i and distance_dict[successor.intersections] <= j:
                      requested_nodes.add(successor)
           visited.add(v)
               
    def nodes_in_polygon(self, nodes):
        tuples = []
        for node in nodes:
            tuples.append((node.middle_coordinate['x'], node.middle_coordinate['y']))
        poly = MultiPoint(tuples).convex_hull
        contained_nodes = set([])
        for node in self.nodes:
            if poly.contains(Point((node.middle_coordinate['x'], node.middle_coordinate['y']))):
                contained_nodes.add(node)
        return contained_nodes;
    
    def a_node(self):
        return self.node_intersections_dict[list(self.node_intersections_dict.keys())[0]]
    
    



        