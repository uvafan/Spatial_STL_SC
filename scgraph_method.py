import osmnx as ox
import sc_lib

'''
Automates OSM data download.
Returns: a graph containing OSM streets as nodes, OSM intersections as edges.
'''
#G = ox.graph_from_point((56.21728389, 10.2336194), distance=2000)
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
            
            ''' Sample use of an attribute:
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


def graph_statistics(graph):
    print ("Number of Nodes:", graph.nodes.size())
    print ("Number of Edges:", graph.edges.size())
    return None;

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






#graph = graph_from_OSMnx(G)

