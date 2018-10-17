'''
Timothy Davison, Eli Lifland
9/11/18
Preliminary Model Checking Functions
'''
import sc_lib
import pandas as pd
import numpy as np
import os

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

    def nodes_with_data(self,nodes):
        ret = set()
        dirs = os.listdir(self.path)
        for node in nodes:
            if node.ID in dirs:
                ret.add(node)
        return ret

    def check_specification(self,specStr,nodes=None,time_range=None,check_all=True):
        if not nodes:
            nodes = self.nodes_with_data(self.graph.data_nodes)
        #Always
        if specStr[0] == 'A':
            pass
        #Eventually
        elif specStr[0] == 'E':
            pass
        #Everywhere
        elif specStr[0] == 'W':
            pass
        #Somewhere
        elif specStr[0] == 'S':
            pass
        #Aggregation   
        elif specStr[0] == '<':
            aggregationOp,dist_range,param,val_range = self.processAggregationStr(specStr[1:])
            return self.checkValues(nodes,time_range,aggregationOp,dist_range,param,val_range,check_all)
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
        aggregationOp = None 
        distRange = None
        if aggregation:
            aggSplit = aggregation.split('[')
            aggregationOp = aggSplit[0]
            distRange = self.rangeStrToTuple(aggSplit[1][:-1])
        return aggregationOp,distRange,param,self.rangeStrToTuple(valRange[1:-1])

    def checkValues(self,nodes,time_range,aggregationOp,dist_range,param,val_range,check_all): 
        satisfied = check_all
        for node in nodes:
            df = pd.DataFrame()
            try:
                df = pd.read_csv('{pat}/{n}/{par}'.format(pat=self.path,n=node.ID,par=param))
            except:
                continue
            if time_range:
                df = df[time_range[0]:time_range[1]]
            if not aggregationOp:
                if check_all:
                    minVal = np.min(df['value_hrf'].astype(float))
                    print(minVal)
                    print(node)
                    maxVal = np.max(df['value_hrf'].astype(float))
                    if minVal < val_range[0] or maxVal > val_range[1]:
                        satisfied = False
        return satisfied
