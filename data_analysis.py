import performance
import sc_lib
import pandas as pd
import numpy as np
import math
import osmnx as ox
import sys
import os
import datetime
import json
from collections import defaultdict
from copy import deepcopy

class SensorInfo:
    def __init__(self,subsystem,sensor,parameter,hrf_unit,hrf_minval,hrf_maxval):
        self.subsystem = subsystem
        self.sensor = sensor
        self.parameter = parameter 
        self.unit = hrf_unit
        self.minval = hrf_minval
        self.maxval = hrf_maxval
        self.measurements = 0
        self.out_of_range = 0
        self.non_numeric = 0
        self.last_tm = None
        self.waits = list()

    def add_measurement(self,tm,val):
        self.measurements += 1
        if val > self.maxval or val < self.minval:        
            self.out_of_range+=1
        if self.last_tm:
            self.waits.append((tm-self.last_tm).seconds)
        self.last_tm = tm

    def add_non_numeric(self,tm):
        self.measurements += 1
        if self.last_tm:
            self.waits.append((tm-self.last_tm).seconds)
        self.last_tm = tm
        self.non_numeric+=1

    def print_stats(self):
        if self.measurements > 0:
            print('subsystem {} sensor {} parameter {}'.format(self.subsystem,self.sensor,self.parameter))
            print('---------------------------------------------------------------------')
            print('In-range percentage: {}'.format((1-self.out_of_range/self.measurements)*100))
            print('Non-numeric percentage: {}'.format((self.non_numeric/self.measurements)*100))
            if len(self.waits):
                print('Avg frequency: {}'.format(sum(self.waits)/len(self.waits)))
            print('\n')

    def clear_last_tm(self):
        self.last_tm = None

def get_sensor_info_dict(path='/media/sf_D_DRIVE/chicago_raw/sensors.csv'):
    sensor_df = pd.read_csv(path)
    sensor_info_dict = dict()
    for index,row in sensor_df.iterrows():
        subsystem = row['subsystem']
        sensor = row['sensor']
        param = row['parameter']
        key = subsystem+sensor+param
        sensor_info_dict[key] = SensorInfo(subsystem,sensor,param,row['hrf_unit'],row['hrf_minval'],row['hrf_maxval'])
    return sensor_info_dict

def analyze_chicago_day(day, sample=float('inf'), path='/media/sf_D_DRIVE'):
    perf = performance.performance_tester()
    day_str = day.replace('-','_')
    node_df = pd.read_csv('{}/chicago_raw/nodes.csv'.format(path))
    data_df = pd.read_csv('{}/chicago_raw/{}.csv'.format(path,day_str),names=['timestamp','node_id','subsystem','sensor','parameter','value_raw','value_hrf'])
    perf.checkpoint('read csv')
    data_df['timestamp'] = pd.to_datetime(data_df['timestamp'])
    data_df = data_df.set_index('timestamp')
    ctr = 0
    sensor_info_dict = get_sensor_info_dict()
    for index, row in node_df.iterrows():
        node_id = row['node_id']
        new_node_df = data_df[data_df['node_id']==node_id]
        if new_node_df.empty:
            continue
        for index, row in new_node_df.iterrows():
            key = row['subsystem']+row['sensor']+row['parameter']
            if key not in sensor_info_dict:
                continue
            try:
                val = float(row['value_hrf'])
                sensor_info_dict[key].add_measurement(index,val)
            except ValueError:
                sensor_info_dict[key].add_non_numeric(index)
        ctr+=1
        if ctr==sample:
            break
        for key, sensor_info in sensor_info_dict.items():
            sensor_info.clear_last_tm()
    for key, sensor_info in sensor_info_dict.items():
        sensor_info.print_stats()
    perf.checkpoint('getting and printing stats')

analyze_chicago_day('2019-03-27',sample=10)
