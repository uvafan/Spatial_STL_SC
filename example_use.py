'''
Eli Lifland
9/29/2018
'''

import osmnx as ox
import sc_loading
import sstl
import sc_plot
import random
import performance

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
    graph = sc_loading.create_chicago_graph(path,dist=10000)
    if plot:
        sc_plot.plot(graph,tagToColor)
    return graph

trusted_sensors = {
    'temperature': {'at0','at1','at2','at3','sht25'}
}

use_sensor_as_param = {'concentration'}

def load_chicago_day(path,abridged=False):
    sc_loading.load_chicago_data_day(path,trusted_sensors,use_sensor_as_param,abridged=abridged)

def test_sstl(graph,parallel=False,cache_locs=True,debug=False):
    checker = sstl.sstl_checker(graph,'2018-09-08',parallel=parallel,cache_locs=cache_locs,debug=debug)
    checker.set_location(graph.a_node().coordinates)
    perf.checkpoint('creating checker')
    f = open('reqs.txt','r')
    for line in f:
        spec = line[:-1]
        if spec == 'END':
            break
        ans = checker.check_specification(spec)
        print('result of {s} is {a}'.format(s=spec,a=ans))
        perf.checkpoint('checked requirement')

perf = performance.performance_tester()
graph = get_chicago('chicago-complete.daily.2018-09-08')
perf.checkpoint('retreiving graph')
test_sstl(graph)
#load_chicago_day('chicago-complete.daily.2018-09-08/',abridged=False)
#sc_plot.plot_param('chicago','2018-09-08','h2s')
#sc_plot.plot_param('chicago','2018-09-08','no2')
#sc_plot.plot_param('chicago','2018-09-08','o3')
#sc_plot.plot_param('chicago','2018-09-08','humidity')
#sc_plot.plot_param('chicago','2018-09-08','visible_light_intensity')
