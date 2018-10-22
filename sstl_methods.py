'''
Timothy Davison, Eli Lifland
9/11/18
Preliminary Model Checking Functions
'''
import sc_lib
import pandas as pd
import numpy as np
import os
from collections import defaultdict

class sstl_checker:
    def __init__(self, G):
        self.graph = G
        self.loc = tuple()
        self.day = ''

    def set_location(self,coords):
        self.loc = coords

    def set_day(self,day):
        self.day = day
        self.path = 'data/{c}/{d}'.format(c=self.graph.city,d=day)

    def update_nodes_with_data(self):
        nodes = self.graph.data_nodes
        self.nodes_with_data = set()
        dirs = os.listdir(self.path)
        for node in nodes:
            if node.ID in dirs:
                self.nodes_with_data.add(node)

    def filter(self,spec_str,nodes,time_range,all_times,all_locs):
        pass 

    def check_specification(self,spec_str,nodes=None,time_range=None,all_times=True,all_locs=True):
        if not nodes:
            nodes = self.graph.nodes
            self.update_nodes_with_data()
        #Filter
        if spec_str[0] == 'A' or spec_str[0] == 'E' or spec_str[0] == 'W' or spec_str[0] == 'S':
            pass
            spec_str,nodes,time_range,all_times,all_locs = self.filter(spec_str,nodes,time_range,all_times,all_locs)
        #Aggregation   
        elif spec_str[0] == '<':
            aggregation_op,dist_range,param,val_range = self.processAggregationStr(spec_str[1:])
            return self.checkValues(nodes,time_range,aggregation_op,dist_range,param,val_range,all_times,all_locs)
        else:
            print('Invalid spec: {}'.format(specStr))
            return False

    def rangeStrToTuple(self,s):
        minVal = float(s.split(',')[0])
        maxVal = float(s.split(',')[1])
        return (minVal,maxVal)
    
    def processAggregationStr(self,aggregationStr):
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
            dist_range = self.rangeStrToTuple(aggSplit[1][:-1])
        return aggregation_op,dist_range,param,self.rangeStrToTuple(valRange[1:-1])

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

    def checkValues(self,nodes,time_range,aggregation_op,dist_range,param,val_range,all_times,all_locs): 
        satisfied = all_locs
        for node in nodes:
            loc_satisfied = all_times
            if not aggregation_op and node.data_node:
                df = pd.DataFrame()
                try:
                    df = pd.read_csv('{pat}/{n}/{par}'.format(pat=self.path,n=node.ID,par=param))
                except Exception:
                    continue
                if time_range:
                    df = df[time_range[0]:time_range[1]]
                minVal = np.min(df['value_hrf'].astype(float))
                maxVal = np.max(df['value_hrf'].astype(float))
                if all_times:
                    if minVal < val_range[0] or maxVal > val_range[1]:
                        loc_satisfied = False
                else:
                    if minVal >= val_range[0] or maxVal <= val_range[1]:
                        loc_satisfied = True
            if aggregation_op:
                loc_satisfied = check_aggregation(aggregation_op,param,dist_range,node,time_range,val_range,all_times)
            if all_locs and not loc_satisfied:
                return False
            if not all_locs and loc_satisfied:
                return True
        return satisfied
