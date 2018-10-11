'''
Eli Lifland
9/29/2018
'''

import osmnx as ox
import sc_loading
import sstl_methods
import sc_plot
import random

tagToColor = {
    'school': (0,0,255),
    'hospital': (255,0,0),
    'theatre': (0,255,0),
    'traffic': (0,0,0),
    'parking': (255,255,0),
    'library': (255,0,255)
}

def example_aarhus():
    path = "aarhus_data/"
    graph = sc_loading.load_aarhus_data(path)
    sc_plot.plot(graph,tagToColor)
    return graph

def example_chicago():
    path = 'chicago-complete.daily.2018-09-08/'
    graph = sc_loading.load_chicago_data(path,abridged=True,sample=50)
    sc_plot.plot(graph,tagToColor)
    return graph

def test_sstl(graph):
    checker = sstl_methods.sstl_checker(graph)
    checker.set_location(graph.a_node().coordinates)
    ans = checker.check_formula('<temperature>(15,inf)')
    print(ans)
    #ans = checker.check_formula('A[0,60](W{school}(<min[0,1],temperature>(15,inf)))')

graph = example_chicago()
#test_sstl(graph)
