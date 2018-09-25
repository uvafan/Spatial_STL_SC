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


'''
Loads in nodes according to their coordinates, edges connecting those coordinates
    to a pandas dataframe. That dataframe is passed to/ plotted with geoplotlib.
    Green is used to represent nodes (using the tf_satisfied attribute of the node)
    which are satisfied, and red to represent those unsatisfied.
'''
def plot(graph,directed=True): 
    satisfied_plot_nodes = []
    unsatisfied_plot_nodes = []
    plot_edges = []
    for node in graph.nodes: 
        node_info = {'lon':node.coordinates[1], 'lat':node.coordinates[0]}
        #print(node_info)
        if node.tf_satisfied: 
            satisfied_plot_nodes.append(node_info)
        else: 
            unsatisfied_plot_nodes.append(node_info)

        neighbors = node.successors
        if not directed:
            neighbors = neighbors.union(node.predecessors)
        for successor in neighbors:
            plot_edges.append({'start_lon':node.coordinates[1], 'end_lon':successor.coordinates[1],
                               'start_lat':node.coordinates[0], 'end_lat':successor.coordinates[0]})
    
    satisfied_df_nodes = pd.DataFrame(satisfied_plot_nodes)
    unsatisfied_df_nodes = pd.DataFrame(unsatisfied_plot_nodes)
    df_edges = pd.DataFrame(plot_edges)
  
    if not df_edges.empty: 
        geoplotlib.graph(df_edges,
                        src_lat='start_lat',
                        src_lon='start_lon',
                        dest_lat='end_lat',
                        dest_lon='end_lon',
                        color='Dark2',
                        alpha=30,
                        linewidth=3)

    if not satisfied_df_nodes.empty:
        geoplotlib.dot(satisfied_df_nodes, 
                   color=[0,255,0,255]
                   )
    
    if not unsatisfied_df_nodes.empty:
        geoplotlib.dot(unsatisfied_df_nodes)
    
    geoplotlib.show()
