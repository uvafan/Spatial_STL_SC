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
from copy import deepcopy
from geopy.distance import vincenty
from collections import defaultdict

class sstl_checker:
    def __init__(self, G, day, cache_locs=True):
        self.graph = G
        self.loc = tuple()
        self.day = day
        self.path = 'data/{c}/{d}'.format(c=self.graph.city,d=day)
        self.cache_locs = cache_locs
        self.prep_for_comparisons()

    def set_location(self,coords):
        self.loc = coords

    def prep_for_comparisons(self):
        params = os.listdir(self.path)
        self.param_dfs = dict()
        for param in params:
            self.param_dfs[param] = pd.read_csv('{path}/{param}'.format(path=self.path,param=param),index_col=0)
        self.data_nodes = set()
        for node in self.graph.nodes:
            if node.data_node:
                self.data_nodes.add(node)
        if self.cache_locs:
            self.loc_dict = defaultdict(set)

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
        range_and_tags = spec_str.split('(')[0][1:]
        rng, tags = self.parse_range_and_tags(range_and_tags)
        next_spec_str = spec_str[len(range_and_tags)+2:-1]
        return rng,tags,next_spec_str

    def get_datetime_range(self,time,time_range):
        ref_time = time if time else pd.to_datetime(self.day)
        if time_range == (float('-inf'),float('inf')):
            start = ref_time
            end = ref_time+datetime.timedelta(days=1)
            return pd.date_range(start=start,end=end,freq='min')
        else:
            start = ref_time+datetime.timedelta(minutes=time_range[0])
            end = ref_time+datetime.timedelta(minutes=time_range[1])
            return pd.date_range(start=start,end=end,freq='min')

    def in_range(self,val,val_range):
        return val >= val_range[0] and val <= val_range[1]

    def dist_btwn(self,coordsA,coordsB):
        return vincenty(coordsA,coordsB).km

    def get_nodes(self,node,dist_range,tags=set(),only_to_check=False):
        dict_key = (node,dist_range,tuple(tags),only_to_check)
        if self.cache_locs and dict_key in self.loc_dict:
            return self.loc_dict[dict_key]
        ref_loc = node.coordinates if node else self.loc
        check_dist = dist_range != (float('-inf'),float('inf'))
        nodes = set()
        considered_nodes = self.nodes_to_check if only_to_check else self.graph.nodes
        for n in considered_nodes:
            if len(tags) and not len(tags.intersection(n.tags)):
                continue
            dist = self.dist_btwn(n.coordinates,ref_loc)
            if check_dist and not self.in_range(dist,dist_range):
                continue
            nodes.add(n)
        if self.cache_locs:
            self.loc_dict[dict_key] = nodes
        return nodes

    def check_specification(self,spec_str,node=None,time=None):
        #Always
        if spec_str[0] == 'A':
            time_range,tags,next_spec_str = self.parse_spec_str(spec_str)
            datetime_rng = self.get_datetime_range(time,time_range)
            for t in datetime_rng:
                result = self.check_specification(next_spec_str,node=node,time=t)
                self.nodes_to_check = deepcopy(self.data_nodes)
                if result != -1 and not result:
                    return False
            return True
        #Eventually
        elif spec_str[0] == 'E':
            time_range,tags,next_spec_str = self.parse_spec_str(spec_str)
            datetime_rng = self.get_datetime_range(time,time_range)
            for t in datetime_rng:
                result = self.check_specification(next_spec_str,node=node,time=t)
                self.nodes_to_check = deepcopy(self.data_nodes)
                if result != -1 and result:
                    return True
            return False
        #Everywhere
        elif spec_str[0] == 'W':
            dist_range,tags,next_spec_str = self.parse_spec_str(spec_str)
            nodes = self.get_nodes(node,dist_range,tags=tags)
            for n in nodes:
                result = self.check_specification(next_spec_str,node=n,time=time)
                if result != -1 and not result:
                    return False
            return True
        #Somewhere
        elif spec_str[0] == 'S':
            dist_range,tags,next_spec_str = self.parse_spec_str(spec_str)
            nodes = self.get_nodes(node,dist_range,tags=tags)
            for n in nodes:
                result = self.check_specification(next_spec_str,node=n,time=time)
                if result != -1 and result:
                    return True
            return False
        #Aggregation   
        elif spec_str[0] == '<':
            if not time:
                return self.check_specification('A({})'.format(spec_str),node,time)
            if not node:
                return self.check_specification('W({})'.format(spec_str),node,time)
            aggregation_op,dist_range,param,val_range = self.parse_aggregation_str(spec_str[1:])
            return self.check_value(node,time,aggregation_op,dist_range,param,val_range)
        else:
            print('Invalid spec: {}'.format(spec_str))
            return False

    def range_str_to_tuple(self,s):
        minVal = float(s.split(',')[0])
        maxVal = float(s.split(',')[1])
        return (minVal,maxVal)
    
    def parse_aggregation_str(self,aggregationStr):
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
        return aggregation_op,dist_range,param,self.range_str_to_tuple(valRange[1:-1])

    def check_aggregation(self,aggregation_op,param,dist_range,node,time,val_range):
        check_nodes = self.get_nodes(node,dist_range,only_to_check=True)
        if not len(check_nodes):
            return -1
        df = self.param_dfs[param]
        vals = []
        for check_node in check_nodes:
            if check_node.ID not in df.columns:
                self.nodes_to_check.remove(check_node)
                continue
            val = df.at[str(time),check_node.ID]
            if np.isnan(val):
                continue
            vals.append(val)
        if not len(vals):
            return -1
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
    
    def check_value(self,node,time,aggregation_op,dist_range,param,val_range): 
        #does S(A()) rn
        if aggregation_op:
            return self.check_aggregation(aggregation_op,param,dist_range,node,time,val_range)
        if node not in self.data_nodes:
            return
        df = self.param_dfs[param]
        if node.ID not in df.columns:
            return -1
        val = df.at[str(time),node.ID]
        if np.isnan(val):
            return -1
        return self.in_range(val,val_range)

