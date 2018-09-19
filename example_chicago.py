'''
Eli Lifland
9/18/2018
'''

import osmnx as ox
import sc_methods
import sstl_methods
import sc_plot
import random


path = "chicago-complete.daily.2018-09-08/"
graph = sc_methods.load_chicago_data(path)
print(graph)
print(graph.a_node())
sc_plot.chicago_plot(graph)

'''
sample_bfs = graph.bfs_set(sample_node, 1, 4)
sample_distance = sc_methods.nodes_from_point(graph, sample_node, 50)
polygon_set = {(40.758896, -73.985130), (40.658896, -73.885130), (40.858896, -73.985130)}
sample_polygon = graph.nodes_in_polygon(polygon_set)


tf = sstl_methods.tf_everywhere(graph.dataframe, '6:00-7:00AM', '<=', 300)
robust = sstl_methods.robust_everywhere(graph.dataframe, '6:00-7:00AM', '<=', 300)
percent = sstl_methods.percent_everywhere(graph.dataframe, '6:00-7:00AM', '<=', 300)
integral = sstl_methods.sstl_integral_timeset(graph, ['6:00-7:00AM', '7:00-8:00AM'], '<=', 600)
'''
