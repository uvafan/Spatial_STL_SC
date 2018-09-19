'''
Meiyi Ma, Timothy Davison, Eli Lifland
9/11/18
Two methods for plotting a SC graph using the library geoplotlib.
Includes a sample plot.
'''
import osmnx as ox
import pandas as pd
import sc_methods
import geoplotlib
import random


def chicago_plot(graph,directed=True): 
    satisfied_plot_nodes = []
    unsatisfied_plot_nodes = []
    for node in graph.nodes:
        node_info = {'ID':node.ID, 'lon':node.coordinates[1], 'lat':node.coordinates[0]}
        if node.tf_satisfied: 
            satisfied_plot_nodes.append(node_info)
        else: 
            unsatisfied_plot_nodes.append(node_info)
    satisfied_df_nodes = pd.DataFrame(satisfied_plot_nodes)
    unsatisfied_df_nodes = pd.DataFrame(unsatisfied_plot_nodes)

    if not satisfied_df_nodes.empty:
        geoplotlib.dot(satisfied_df_nodes, 
                   color=[0,255,0,255]
                   )
    
    if not unsatisfied_df_nodes.empty:
        geoplotlib.dot(unsatisfied_df_nodes)
    
    geoplotlib.show()

'''
Loads in nodes according to their middle coorinates, edges connecting those coordinates
    to a pandas dataframe. That dataframe is passed to/ plotted with geoplotlib.
    Green is used to represent nodes (using the tf_satisfied attribute of the node)
    which are satisfied, and red to represent those unsatisfied.
'''
def sc_plot(graph,directed=True): 
    satisfied_plot_nodes = []
    unsatisfied_plot_nodes = []
    for item in graph.nodes:
        '''
        item.middle_coordinate['x'] = ((graph.edge_dict[item.intersections[0]].coordinates['x'] + 
                                  graph.edge_dict[item.intersections[1]].coordinates['x'])/2.0)
        item.middle_coordinate['y'] = ((graph.edge_dict[item.intersections[0]].coordinates['y'] +
                              graph.edge_dict[item.intersections[0]].coordinates['y'])/2.0)
        '''
        if item.tf_satisfied: satisfied_plot_nodes.append({'Identifier': item.identifier, 'lon': item.middle_coordinate['x'], 
                           'lat': item.middle_coordinate['y']})
        else: unsatisfied_plot_nodes.append({'Identifier': item.identifier, 'lon': item.middle_coordinate['x'], 
                           'lat': item.middle_coordinate['y']})
    satisfied_df_nodes = pd.DataFrame(satisfied_plot_nodes)
    unsatisfied_df_nodes = pd.DataFrame(unsatisfied_plot_nodes)

    plot_edges = []
    for item in graph.nodes:
        neighbors = item.successors
        if not directed:
            neighbors = neighbors.union(item.predecessors)
        for successor in neighbors:
            plot_edges.append({'start_lon':item.middle_coordinate['x'], 'end_lon':successor.middle_coordinate['x'],
                               'start_lat':item.middle_coordinate['y'], 'end_lat':successor.middle_coordinate['y'],
                               'satisfied':item.tf_satisfied})
    df_edges = pd.DataFrame(plot_edges)
    
    geoplotlib.graph(df_edges,
                     src_lat='start_lat',
                     src_lon='start_lon',
                     dest_lat='end_lat',
                     dest_lon='end_lon',
                     color='Dark2',
                     alpha=30,
                     linewidth=3)
    # color=[0,0,255,255] sets blue, color default is red
    # [0,0,0,255] is black, [0,255,0,255] is green
    if not satisfied_df_nodes.empty:
        geoplotlib.dot(satisfied_df_nodes, 
                   color=[0,255,0,255]
                   )
    
    if not unsatisfied_df_nodes.empty:
        geoplotlib.dot(unsatisfied_df_nodes)
    geoplotlib.show()

'''
# SAMPLE
G = ox.graph_from_point((40.758896, -73.985130), distance=500) 
graph = sc_methods.graph_from_OSMnx(G)
for node in graph.nodes:
    tell = random.randint(0,2)
    if tell == 0:
        node.tf_satisfied = False
sc_plot(graph)
'''
