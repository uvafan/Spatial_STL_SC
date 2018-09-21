'''
Timothy Davison, Eli Lifland
9/11/18
Preliminary Model Checking Functions
'''
import sc_lib
import pandas as pd

'''
Arguments:
df - initial dataframe
requirements - list of requirements to check; each requirement is in following form:
(raw, low, high) where param is the param to check and low/high represent the range of allowed values
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
        raw, lo, hi = requirements
        column = 'value_raw' if raw else 'value_hrf'
        df = df.loc[(df[column]>=lo) & (df[column]<=hi)]
    return df

def tf_always(df, param, requirements, nodes=None):
    df = filter_df(df,param=param,nodes=nodes)
    numMeasurements = len(df.index)
    df = filter_df(df,requirements=requirements)
    return len(df.index) == numMeasurements

