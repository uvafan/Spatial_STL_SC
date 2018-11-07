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
import pandas as pd
import numpy as np
import time
from multiprocessing import Pool
from collections import defaultdict

params = {'co','o3','no2','lightsense'}

workdays = ['2018-04-02','2018-04-10','2018-04-18','2018-04-26','2018-04-27','2018-05-01','2018-05-09','2018-05-17','2018-05-21','2018-05-25','2018-06-01','2018-06-04','2018-06-12','2018-06-20','2018-06-28','2018-07-12','2018-07-17','2018-07-20','2018-07-25','2018-07-30','2018-08-01','2018-08-06','2018-08-14','2018-08-23','2018-08-31','2018-09-07','2018-09-11','2018-09-19','2018-09-24','2018-09-27']

weekends = ['2018-04-07','2018-04-08','2018-04-14','2018-04-15','2018-04-21','2018-05-05','2018-05-06','2018-05-12','2018-05-13','2018-05-20','2018-06-02','2018-06-03','2018-06-09','2018-06-10','2018-06-16','2018-07-08','2018-07-14','2018-07-21','2018-07-22','2018-07-29','2018-08-04','2018-08-05','2018-08-11','2018-08-12','2018-08-18','2018-09-08','2018-09-09','2018-09-22','2018-09-23','2018-09-30']

def load_work():
    to_load = workdays+weekends
    pool = Pool(processes=3)
    pool.map(load_day,to_load)

def test_work(parallel=True,cache_locs=True,debug=False):
    to_test = workdays
    #to_test = weekends
    #no args: ASSTL, -p: PASSTL, -c: SSTL
    method = 'PASSTL'
    df = pd.DataFrame()
    req_satisfied = defaultdict(int)
    filename = '{}_stats/{}.csv'.format(args.city,method)
    try:
        df = pd.read_csv(filenamd,index_col=0)
    except Exception:
        pass
    graph = get_graph(args.city)
    reqs = list()
    for day in to_test:
        checker = sstl.sstl_checker(graph,day,parallel=parallel,cache_locs=cache_locs,debug=debug,params=params)
        f = open(args.req_file,'r')
        reqs = list()
        for line in f:
            if line == 'END\n':
                break
            name,spec = line.split(':')
            reqs.append(name)
            if name not in df.columns:
                df[name] = np.nan
            s = time.time()
            ans = checker.check_spec(spec[:-1])
            check_time = time.time()-s
            if ans:
                req_satisfied[name]+=1
            df.at[day,name] = check_time
        print('Finished day {}'.format(day))
    for req in reqs:
        pct_satisfied = (req_satisfied[req]/len(to_test))*100
        print('Req {} is {} pct satisfied'.format(req,pct_satisfied))
    df.to_csv(filename)

tagToColor = {
    'school': (0,0,255),
    'hospital': (255,0,0),
    'theatre': (0,255,0),
    'traffic': (0,0,0),
    'parking': (255,255,0),
    'library': (255,0,255)
}

def example_aarhus():
    path = 'aarhus_data/'
    graph = sc_loading.load_aarhus_data(path)
    sc_plot.plot(graph,tagToColor)
    return graph

def get_graph(city,plot=False):
    graph = sc_loading.get_graph(city)
    if plot:
        sc_plot.plot(graph,tagToColor)
    return graph

def load_day(day):
    sc_loading.load_data(args.city,day)

def test_sstl(graph,fin,parallel=True,cache_locs=True,debug=False):
    checker = sstl.sstl_checker(graph,args.day,parallel=parallel,cache_locs=cache_locs,debug=debug,params=params)
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
parser.add_argument('-w',dest='work',action='store_true')
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
elif args.work and args.load:
    load_work()
elif args.work:
    test_work()
elif args.load:
    load_day(args.day)    
else:
    graph = get_graph(args.city,args.day,plot=args.plot)
    perf.checkpoint('retreiving graph')
    test_sstl(graph,args.req_file,args.parallel,args.cache_locs,args.debug)
