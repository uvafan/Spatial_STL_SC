'''
Eli Lifland
9/29/2018
'''
import argparse
import osmnx as ox
import sc_loading
import sstl
import sc_plot
import random
import performance
from multiprocessing import Pool

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

def get_graph(city,day,plot=False):
    graph = sc_loading.get_graph(city,day)
    if plot:
        sc_plot.plot(graph,tagToColor)
    return graph

def load_day(day):
    sc_loading.load_data(args.city,day)

def test_sstl(graph,fin,parallel=True,cache_locs=True,debug=False):
    checker = sstl.sstl_checker(graph,'2018-09-08',parallel=parallel,cache_locs=cache_locs,debug=debug)
    checker.set_location(graph.a_node().coordinates)
    perf.checkpoint('creating checker')
    f = open(fin,'r')
    for line in f:
        spec = line[:-1]
        if spec == 'END':
            break
        ans = checker.check_spec(spec)
        print('result of {s} is {a}'.format(s=spec,a=ans))
        perf.checkpoint('checked requirement')

parser = argparse.ArgumentParser(description='Example SSTL')
parser.add_argument('-l',dest='load',action='store_true')
parser.add_argument('-p',dest='parallel',action='store_true')
parser.add_argument('-f',dest='req_file',default='reqs.txt')
parser.add_argument('-c',dest='city',default='chicago')
parser.add_argument('-d',dest='day',default='2018-04-01')
parser.add_argument('-m',dest='month',action='store_true')
parser.add_argument('--plot',dest='plot',action='store_true')
parser.add_argument('--debug',dest='debug',action='store_true')
parser.add_argument('--cache',dest='cache_locs',action='store_false')
args = parser.parse_args()
perf = performance.performance_tester()
if args.month:
    pool = Pool(processes=3)
    d_strs = list()
    for d in range(1,31):
        d_str = str(d)
        if len(d_str) == 1:
            d_str = '0'+d_str
        d_strs.append('2018-04-{}'.format(d_str))
    pool.map(load_day,d_strs)
elif args.load:
    load_day(args.day)    
else:
    graph = get_graph(args.city,args.day,plot=args.plot)
    perf.checkpoint('retreiving graph')
    test_sstl(graph,args.req_file,args.parallel,args.cache_locs,args.debug)
