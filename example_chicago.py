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
graph = sc_methods.load_chicago_data(path,abridged=True)
print(graph)
print(graph.a_node())
sc_plot.plot(graph)
'''
print(sstl_methods.tf_always(graph.df,param='intensity',requirements=(False,float('-inf'),float('inf'))))
'''
