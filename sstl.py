'''
Timothy Davison, Eli Lifland
9/11/18
Preliminary Model Checking Functions
'''
import sc_lib
import pandas as pd
import numpy as np
import os
import datetime
import performance
import concurrent.futures
from multiprocessing import Pool,cpu_count
from itertools import repeat,product
from copy import deepcopy
from geopy import distance
from collections import defaultdict

class sstl_checker:
    def __init__(self, G, day, parallel=True, cache_locs=True, debug=False):
        self.graph = G
        self.loc = tuple()
        self.day = day
        self.path = 'data/{c}/{d}'.format(c=self.graph.city,d=day)
        self.cache_locs = cache_locs
        self.prep_for_comparisons()
        self.debug = debug
        self.parallel = parallel
        self.workers = cpu_count()

    def log(self,s):
        if self.debug:
            print(s)

    def set_location(self,coords):
        self.loc = coords

    def get_df(self,param):
        if param not in self.param_dfs:
            self.param_dfs[param] = pd.read_csv('{path}/{param}'.format(path=self.path,param=param),index_col=0)
        return self.param_dfs[param] 

    def prep_for_comparisons(self):
        params = os.listdir(self.path)
        self.param_dfs = dict()
        self.nodes_with_data = defaultdict(set)
        for param in params:
            df = self.get_df(param)
            for node in self.graph.nodes:
                if node.ID in df.columns:
                    self.nodes_with_data[param].add(node)
        self.cache_lookahead = False
        self.cache_parsing = False
        self.cache_timerange = False
        self.cache_agg = False
        self.lookahead_dict = dict()
        self.parsing_dict = dict()
        self.timerange_dict = dict()
        self.agg_dict = dict()

    def parse_range_and_tags(self,range_and_tags):
        rng = (float('-inf'),float('inf'))
        tags = set()
        while len(range_and_tags):
            if range_and_tags[0] == '[':
                range_str = range_and_tags.split(']')[0][1:]
                rng = self.range_str_to_tuple(range_str)
                range_and_tags = range_and_tags[len(range_str)+2:]
            elif range_and_tags[0] == '{':
                tags_str = range_and_tags.split('}')[0][1:]
                for tag in tags_str.split(','):
                    tags.add(tag)
                range_and_tags = range_and_tags[len(tags_str)+2:]
            else:
                print('unexpected range/tag str {}'.format(range_and_tags))
                return rng,tags
        return rng,tags

    def parse_spec_str(self,spec_str):
        if self.cache_parsing and spec_str in self.parsing_dict:
            return self.parsing_dict[spec_str]
        range_and_tags = spec_str.split('(')[0][1:]
        rng, tags = self.parse_range_and_tags(range_and_tags)
        next_spec_str = spec_str[len(range_and_tags)+2:-1]
        if self.cache_parsing:
            self.parsing_dict[spec_str] = rng,tags,next_spec_str
        return rng,tags,next_spec_str

    def get_datetime_range(self,time,time_range):
        dict_key = (str(time),time_range)
        if self.cache_timerange and dict_key in self.timerange_dict:
            return self.timerange_dict[dict_key]
        ref_time = time if time else pd.to_datetime(self.day)
        if time_range == (float('-inf'),float('inf')):
            start = ref_time
            end = ref_time+datetime.timedelta(days=1)
            ret = pd.date_range(start=start,end=end,freq='min')
        else:
            start = ref_time+datetime.timedelta(minutes=time_range[0])
            end = ref_time+datetime.timedelta(minutes=time_range[1])
            ret = pd.date_range(start=start,end=end,freq='min')
        if self.cache_timerange:
            self.timerange_dict[dict_key] = ret
        return ret

    def in_range(self,val,val_range):
        return val >= val_range[0] and val <= val_range[1]

    def dist_btwn(self,coordsA,coordsB):
        #distance.distance is more accurate but slower
        return distance.vincenty(coordsA,coordsB).km

    def get_nodes(self,node_ID,dist_range,last_spatial,param,tags=set()):
        dict_key = (dist_range,tuple(tags),last_spatial,param)
        node = self.graph.nodes_by_ID[node_ID] if node_ID else None
        if node and self.cache_locs and dict_key in node.loc_dict:
            return node.loc_dict[dict_key]
        ref_loc = node.coordinates if node else self.loc
        check_dist = dist_range != (float('-inf'),float('inf'))
        nodes = set()
        considered_nodes = self.nodes_with_data[param] if last_spatial else self.graph.nodes
        for n in considered_nodes:
            if len(tags) and not len(tags.intersection(n.tags)):
                continue
            if check_dist:
                dist = self.dist_btwn(n.coordinates,ref_loc)
                if not self.in_range(dist,dist_range):
                    continue
            nodes.add(n.ID)
        if node and self.cache_locs:
            node.loc_dict[dict_key] = nodes
        return nodes

    def look_ahead(self, spec_str):
        if self.cache_lookahead and spec_str in self.lookahead_dict:
            return self.lookahead_dict[spec_str]
        agg_str = spec_str.split('<')[1].split(')')[0]+')'
        aggregation_op,dist_range,param,val_range = self.parse_aggregation_str(agg_str)
        if aggregation_op:
            return False, param
        spatial_operators = set(['S','W'])
        for i in range(1,len(spec_str)):
            if spec_str[i] in spatial_operators:
                return False, param
        if self.cache_lookahead:
            self.lookahead_dict[spec_str] = True, param
        return True, param

    def parse_logical_operands(self,spec_str,agg=False,time=None,node_ID=None,parallelized=False):
        if_str = '->' if agg else '->->'
        or_str = '|' if agg else '||'
        and_str = '&' if agg else '&&'
        if_specs = spec_str.split(if_str)
        po = not agg
        assert(len(if_specs)<3)
        if len(if_specs) > 1:
            return not self.check_spec(if_specs[0],time=time,node_ID=node_ID,parse_ops=po,parallelized=parallelized) or self.check_spec(if_specs[1],time=time,node_ID=node_ID,parse_ops=po,parallelized=parallelized)
        or_specs = spec_str.split(or_str)
        if len(or_specs) > 1:
            return self.check_spec(or_specs[0],time=time,node_ID=node_ID,parse_ops=po,parallelized=parallelized) or self.check_spec(or_specs[1],time=time,node_ID=node_ID,parse_ops=po,parallelized=parallelized)
        and_specs = spec_str.split(and_str)
        if len(and_specs) > 1:
            return self.check_spec(and_specs[0],time=time,node_ID=node_ID,parse_ops=po,parallelized=parallelized) and self.check_spec(and_specs[1],time=time,node_ID=node_ID,parse_ops=po,parallelized=parallelized)
        return self.check_spec(spec_str,parse_ops=False,do_check=True,time=time,node_ID=node_ID,parallelized=parallelized)
   
    def get_nodes_lookahead(self,spec_str):
        if spec_str[0] == '<':
            return self.get_nodes_lookahead('W({})'.format(spec_str))
        dist_range,tags,_ = self.parse_spec_str(spec_str)
        last_spatial, param = self.look_ahead(spec_str)
        return self.get_nodes(None,dist_range,last_spatial,param,tags=tags)

    def check_spec(self,spec_str,node_ID=None,time=None,parallelized=False,parse_ops=True,nodes=None,do_check=False):
        self.log('node_ID: {}'.format(node_ID))
        self.log('spec_str: {}'.format(spec_str))
        if parse_ops and spec_str[0]!='<':
            return self.parse_logical_operands(spec_str,parallelized=parallelized)
        if spec_str[0] == '!':
            return not self.check_spec(spec_str[1:],node_ID=node_ID,time=time,parse_ops=False,parallelized=parallelized)
        #Always
        if spec_str[0] == 'A':
            perf = performance.performance_tester()
            time_range,tags,next_spec_str = self.parse_spec_str(spec_str)
            datetime_rng = self.get_datetime_range(time,time_range)
            if not node_ID and next_spec_str[0] in ['E','W','<']:
                nodes = self.get_nodes_lookahead(next_spec_str)
            for t in datetime_rng:
                result = self.check_spec(next_spec_str,node_ID=node_ID,nodes=nodes,time=t,parse_ops=False,parallelized=parallelized)
                if result != -1 and not result:
                    return False
            if self.debug:
                perf.checkpoint('finishing one node')
            return True
        #Eventually
        elif spec_str[0] == 'E':
            time_range,tags,next_spec_str = self.parse_spec_str(spec_str)
            datetime_rng = self.get_datetime_range(time,time_range)
            if not node_ID and next_spec_str[0] in ['E','W','<']:
                nodes = self.get_nodes_lookahead(next_spec_str)
            for t in datetime_rng:
                result = self.check_spec(next_spec_str,node_ID=node_ID,nodes=nodes,time=t,parse_ops=False,parallelized=parallelized)
                if result != -1 and result:
                    return True
            return False
        #Everywhere
        elif spec_str[0] == 'W':
            dist_range,tags,next_spec_str = self.parse_spec_str(spec_str)
            last_spatial, param = self.look_ahead(spec_str)
            if not nodes:
                nodes = self.get_nodes(node_ID,dist_range,last_spatial,param,tags=tags)
            if self.parallel and not parallelized:
                pool = Pool(processes=self.workers)
                for n,result in zip(nodes, pool.starmap(self.check_spec,product([next_spec_str],nodes,[time],[True],[False]))):
                    if result != -1 and not result:
                        pool.close()
                        pool.join()
                        return False
                pool.close()
                pool.join()
                return True
            for n in nodes:
                result = self.check_spec(next_spec_str,node_ID=n,time=time,parse_ops=False,parallelized=parallelized)
                if result != -1 and not result:
                    return False
            return True
        #Somewhere
        elif spec_str[0] == 'S':
            dist_range,tags,next_spec_str = self.parse_spec_str(spec_str)
            last_spatial, param = self.look_ahead(spec_str)
            if not nodes:
                nodes = self.get_nodes(node_ID,dist_range,last_spatial,param,tags=tags)
            if self.parallel and not parallelized:
                pool = Pool(processes=self.workers)
                for n,result in zip(nodes, pool.starmap(self.check_spec,product([next_spec_str],nodes,[time],[True],[False]))):
                    if result != -1 and result:
                        pool.close()
                        pool.join()
                        return True
                pool.close()
                pool.join()
                return False
            for n in nodes:
                result = self.check_spec(next_spec_str,node_ID=n,time=time,parse_ops=False,parallelized=parallelized)
                if result != -1 and result:
                    return True
            return False
        #Aggregation   
        elif spec_str[0] == '<':
            if not node_ID:
                return self.check_spec('W({})'.format(spec_str),node_ID=node_ID,nodes=nodes,time=time,parse_ops=False,parallelized=parallelized)
            if not time:
                return self.check_spec('A({})'.format(spec_str),node_ID=node_ID,nodes=nodes,time=time,parse_ops=False,parallelized=parallelized)
            if not do_check:
                return self.parse_logical_operands(spec_str,agg=True,node_ID=node_ID,time=time,parallelized=parallelized)
            aggregation_op,dist_range,param,val_range = self.parse_aggregation_str(spec_str[1:])
            return self.check_value(node_ID,time,aggregation_op,dist_range,param,val_range)
        else:
            print('Invalid spec: {}'.format(spec_str))
            return False

    def range_str_to_tuple(self,s):
        minVal = float(s.split(',')[0])
        maxVal = float(s.split(',')[1])
        return (minVal,maxVal)
    
    def parse_aggregation_str(self,aggregationStr):
        if self.cache_agg and aggregationStr in self.agg_dict:
            return self.agg_dict[aggregationStr]
        specification,valRange = aggregationStr.split('>')
        aggregation = None
        param = None
        specSplit = specification.split(',')
        if len(specSplit)>1:
            aggregation,param = specSplit[0]+','+specSplit[1],specSplit[2]
        else:
            param = specification
        aggregation_op = None 
        dist_range = None
        if aggregation:
            aggSplit = aggregation.split('[')
            aggregation_op = aggSplit[0]
            dist_range = self.range_str_to_tuple(aggSplit[1][:-1])
        ret = aggregation_op,dist_range,param,self.range_str_to_tuple(valRange[1:-1])
        self.agg_dict[aggregationStr] = ret
        return ret

    def check_aggregation(self,aggregation_op,param,dist_range,node_ID,time,val_range):
        check_nodes = self.get_nodes(node_ID,dist_range,True,param)
        if not len(check_nodes):
            return -1
        df = self.get_df(param)
        vals = []
        for check_node in check_nodes:
            val = df.at[str(time),check_node]
            if np.isnan(val):
                continue
            vals.append(val)
        if not len(vals):
            return -1
        #self.log('aggregating data from {} nodes'.format(len(vals)))
        val = 0
        if aggregation_op == 'min':
            val = min(vals)
        elif aggregation_op == 'max':
            val = max(vals)
        elif aggregation_op == 'avg':
            val = sum(vals)/len(vals)
        else:
            print('unrecognized aggregation operator: {}'.format(aggregation_op))
            return False
        return self.in_range(val,val_range) 
    
    def check_value(self,node_ID,time,aggregation_op,dist_range,param,val_range): 
        if aggregation_op:
            return self.check_aggregation(aggregation_op,param,dist_range,node_ID,time,val_range)
        df = self.get_df(param)
        val = df.at[str(time),node_ID]
        if np.isnan(val):
            return -1
        return self.in_range(val,val_range)


