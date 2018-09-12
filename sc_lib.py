'''
Meiyi Ma, Timothy Davison, Eli Lifland
STL for Smart Cities
Object Library: Node, Edge, Graph

'''
import queue
from shapely.geometry import Point
from shapely.geometry import MultiPoint


''' 
Streets will be saved as nodes.
Class attributes were selected based upon the available data from OSMNX;
    attributes may be added to/ modified as data about each node becomes available.
'''
class node:
    
    def __init__(self, identifier):
        self.intersections = None #The node represents the street segment between these two intersections
        self.data = [] #Later to be concatenated into a pandas dataframe holding sensor trace data
        self.name = "" #Name of the street
        self.length = None
        self.oneway = None
        self.type = None #OSM type, usually indicates type of street (ie, highway vs residential)
        self.identifier = identifier #'''OSMnx identifier key'''
        self.lanes = None
        self.middle_coordinate = {} #The middle lat/long between the street's intersections. Used for plotting
        self.predecessors = set([]) 
        self.successors = set([])
        self.tf_satisfied = True #State of satisfaction for a given req; simplified here for plotting, could later become a dictionary of data:satisfaction value
    
    '''
    Some potentially useful methods:
    '''
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
Once again, class attributes were selected based upon the available data from OSMNX.
'''
class edge:
    
    def __init__(self, identifier):
        self.coordinates = {} #Saved as an 'x','y' dictionary
        self.sensor_states = set([]) #In the event of data from intersections
        self.id = identifier
        self.type = None
        
    '''
    Potentially useful methods:
    '''
    def equals(self, edge2):
        return (self.coordinates == edge2.coordinates & self.id == edge2.id
                & self.sensor_states == edge2.sensor_states)
   
    def print(self):
        print ("Coordinates:", self.coordinates, "\n", "Connected Nodes:", self.connected_nodes)


'''
Custom graph class.
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
        self.dataframe = []
        
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
    
    '''
    Returns a single node from the graph. Helpful for testing/ development. 
    '''
    def a_node(self):
        return self.node_intersections_dict[list(self.node_intersections_dict.keys())[0]]
    
