'''
Eli Lifland
9/29/2018
'''

import osmnx as ox
import sc_methods
import sstl_methods
import sc_plot
import random

path = "aarhus_data/"
graph = sc_methods.load_aarhus_data(path)
sc_plot.plot(graph)
#checker = sstl_methods.sstl_checker(graph)
#checker.set_location(graph.a_node().coordinates)
#ans = checker.check_formula('A[0,60](W{school}(<min[0,1],temperature>(15,inf)))')
