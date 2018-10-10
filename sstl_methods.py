'''
Timothy Davison, Eli Lifland
9/11/18
Preliminary Model Checking Functions
'''
import sc_lib
import pandas as pd
import numpy as np

class sstl_checker:
    def __init__(self, G):
        self.graph = G
        self.loc = tuple()

    def set_location(self,coords):
        self.loc = coords

    def check_formula(self,formulaStr,nodes=None,time_range=None,check_all=True):
        if not nodes:
            nodes = self.graph.nodes
        #Always
        if formulaStr[0] == 'A':
            pass
        #Eventually
        elif formulaStr[0] == 'E':
            pass
        #Everywhere
        elif formulaStr[0] == 'W':
            pass
        #Somewhere
        elif formulaStr[0] == 'S':
            pass
        #Aggregation   
        elif formulaStr[0] == '<':
            aggregationOp,dist_range,param,val_range = self.processAggregationStr(formulaStr[1:])
            return self.checkValues(nodes,time_range,aggregationOp,dist_range,param,val_range,check_all)
        else:
            print('Invalid formula: {}'.format(formulaStr))
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
        satisfied = True
        data_ids_checked = set()
        for node in nodes:
            if node.data_id in data_ids_checked:
                continue
            data_ids_checked.add(node.data_id)
            df = node.df
            if df.empty:
                continue
            df = df.loc[df['parameter']==param]
            if time_range:
                df = df[time_range[0]:time_range[1]]
            if not aggregationOp:
                if check_all:
                    minVal = np.min(df['value_hrf'].astype(float))
                    maxVal = np.max(df['value_hrf'].astype(float))
                    if minVal < val_range[0] or maxVal > val_range[1]:
                        satisfied = False
        return satisfied
