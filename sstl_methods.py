'''
Timothy Davison, Eli Lifland
9/11/18
Preliminary Model Checking Functions
'''
import sc_lib
import pandas as pd

class sstl_checker:
    def __init__(self, G):
        self.graph = G
        self.loc = tuple()
        self.start_time = G.df.index[0]

    def set_location(self,coords):
        self.loc = coords

    def check_formula(self,formulaStr,df=None,check_all=True):
        if not df:
            graph = self.graph.df
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
            aggregationOp,distRange,param,valRange = self.processAggregationStr(formulaStr[1:])
            return self.checkValues(df,aggregationOp,distRange,param,valRange,check_all)
        else:
            print('Invalid formula: {}'.format(formulaStr))
            return False

    def rangeStrToTuple(self,s):
        minVal = float(s.split(',')[0])
        maxVal = float(s.split(',')[1])
        return (minVal,maxVal)
    
    def processAggregationStr(self,aggregationStr):
        specification,valRange = aggregationStr.split('>')
        aggregation = ''
        param = ''
        specSplit = specification.split(',')
        if len(specSplit)>1:
            aggregation,param = specSplit[0],specSplit[1]
        else:
            param = specification
        aggregationOp = ''
        distRange = None
        if len(aggregation):
            aggSplit = aggregation.split('[')
            aggregationOp = aggSplit[0]
            distRange = self.rangeStrToTuple(aggSplit[1][:-1])
        return aggregationOp,distRange,param,self.rangeStrToTuple(valRange[1:-1])

    def checkValues(self,df,aggregationOp,distRange,param,valRange,check_all): 
        pass    

    '''
    Arguments:
    df - initial dataframe
    requirements - list of requirements to check; each requirement is in following form:
    (hrf, low, high) where param is the param to check and low/high represent the range of allowed values
    time_range - time range of times to check in form of (start,end) 
    nodes - set of node IDs to check

    Return value:
    New dataframe with all fillters applied
    '''
    def filter_df(df, param=None, requirements=None, time_range=None, nodes=None):
        if time_range:
            df = df[time_range[0]:time_range[1]]
        if nodes:
            df = df.loc[df['node_id'].isin(nodes)]
        if param:
            df = df[df['parameter']==param]
        if requirements:
            hrf, lo, hi = requirements
            column = 'value_hrf' if hrf else 'value_raw'
            df = df.loc[(df[column]>=lo) & (df[column]<=hi)]
        return df

