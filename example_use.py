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

def get_chicago(path,plot=False):
    graph = sc_loading.create_chicago_graph(path)
    if plot:
        sc_plot.plot(graph,tagToColor)
    return graph

def load_chicago_day(path):
    sc_loading.load_chicago_data_day(path)

def test_sstl(graph):
    checker = sstl_methods.sstl_checker(graph)
    checker.set_location(graph.a_node().coordinates)
    checker.set_day('2018-09-08')
    checker.set_allowed_sensors('temperature',['at0','at1','at2','at3'])
    f = open('checks.txt','r')
    for line in f:
        spec = line[:-1]
        if spec == 'END':
            break
        ans = checker.check_specification(spec)
        print('result of {} is {}'.format(spec,ans))

#load_chicago_day('chicago-complete.daily.2018-09-08/')
graph = get_chicago('chicago-complete.daily.2018-09-08/')
#test_sstl(graph)
