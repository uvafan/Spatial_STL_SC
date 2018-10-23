'''
Timothy Davison, Eli Lifland
9/11/18
Preliminary Model Checking Functions
'''
import sc_lib
import pandas as pd
import numpy as np
import os
import geopy
import datetime
from collections import defaultdict

class sstl_checker:
    def __init__(self, G, day):
        self.graph = G
        self.loc = tuple()
        self.day = day
        self.path = 'data/{c}/{d}'.format(c=self.graph.city,d=day)
        self.prep_for_comparisons()

    def set_location(self,coords):
        self.loc = coords

    def prep_for_comparisons(self):
        params = os.listdir(self.path)
        self.param_dfs = dict()
        for param in params:
            self.param_dfs[param] = pd.read_csv('{path}/{param}'.format(path=self.path,param=param),index_col=0)

    def parse_range_and_tags(self,range_and_tags):
        rng = (float('-inf'),float('inf'))
        tags = set()
        while len(range_and_tags):
            if range_and_tags[0] == '(':
                range_str = range_and_tags.split(')')[0][1:]
                rng = range_str_to_tuple(range_str)
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
        return geopy.distance.vincenty(coordsA,coordsB).km

    def get_nodes(self,node,dist_range,tags):
        ref_loc = node.coordinates if node else self.loc
        check_dist = dist_range != (float('-inf'),float('inf'))
        nodes = set()
        for n in self.graph.nodes:
            if len(tags) and not len(tags.intersection(n.tags)):
                continue
            if check_dist and not self.in_range(self.dist_btwn(n.coordiantes,ref_loc),dist_range):
                continue
            nodes.add(n)
        return nodes

    def check_specification(self,spec_str,node=None,time=None):
        #Always
        if spec_str[0] == 'A':
            time_range,tags,next_spec_str = self.parse_spec_str(spec_str)
            datetime_rng = self.get_datetime_range(time,time_range)
            for t in datetime_rng:
                result = self.check_specification(next_spec_str,node=node,time=t)
                if result != -1 and not result:
                    return False
            return True
        #Eventually
        elif spec_str[0] == 'E':
            time_range,tags,next_spec_str = self.parse_spec_str(spec_str)
            datetime_rng = self.get_datetime_range(time,time_range)
            for t in datetime_rng:
                result = self.check_specification(next_spec_str,node=node,time=t)
                if result != -1 and result:
                    return True
            return False
        #Everywhere
        elif spec_str[0] == 'W':
            dist_range,tags,next_spec_str = self.parse_spec_str(spec_str)
            nodes = self.get_nodes(node,dist_range,tags)
            for n in nodes:
                result = self.check_specification(next_spec_str,node=n,time=time)
                if result != -1 and not result:
                    return False
            return True
        #Somewhere
        elif spec_str[0] == 'S':
            dist_range,tags,next_spec_str = self.parse_spec_str(spec_str)
            nodes = self.get_nodes(node,dist_range,tags)
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
            aggregation_op,dist_range,param,val_range = self.process_aggregation_str(spec_str[1:])
            return self.check_value(node,time,aggregation_op,dist_range,param,val_range)
        else:
            print('Invalid spec: {}'.format(spec_str))
            return False

    def range_str_to_tuple(self,s):
        minVal = float(s.split(',')[0])
        maxVal = float(s.split(',')[1])
        return (minVal,maxVal)
    
    def process_aggregation_str(self,aggregationStr):
        specification,valRange = aggregationStr.split('>')
        aggregation = None
        param = None
        specSplit = specification.split(',')
        if len(specSplit)>1:
            aggregation,param = specSplit[0],specSplit[1]
        else:
            param = specification
        aggregation_op = None 
        dist_range = None
        if aggregation:
            aggSplit = aggregation.split('[')
            aggregation_op = aggSplit[0]
            dist_range = self.range_str_to_tuple(aggSplit[1][:-1])
        return aggregation_op,dist_range,param,self.range_str_to_tuple(valRange[1:-1])

    def check_aggregation(aggregation_op,param,dist_range,node,time_range,val_range,all_times):
        return True
        '''
        satisfied = all_times
        for to_check in self.nodes_with_data:
            dist = node.dist_to(to_check)
            if dist < dist_range[0] or dist > dist_range[1]:
                continue
        return satisfied
        '''
    
    def check_value(self,node,time,aggregation_op,dist_range,param,val_range): 
        #does S(A()) rn
        if aggregation_op:
            return self.check_aggregation(aggregation_op,param,dist_range,node,time,val_range)
        df = self.param_dfs[param]
        if node.ID not in df.columns or str(time) not in df.index:
            return -1
        val = df.at[str(time),node.ID]
        if np.isnan(val):
            return -1
        return self.in_range(val,val_range)

