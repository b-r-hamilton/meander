# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 10:45:07 2020
Methods used to extract and format data products
@author: bydd1
"""
import pandas as pd 
import pickle 
import numpy as np 
import time 

#find the closest value to some specified value in an array 
def find_closest_val(val, arr):
    diff = [abs(x - val) for x in arr]
    index = diff.index(min(diff))
    return index     
    
#generate compressed version of river_analytics.pickle
    #averages file temporally (first axis)
def compress_ra(ra_path, write_to):

    start_time = time.time() #start a timer 
    
    dictionary = pickle.load( open(ra_path, "rb" ) )

    mean_annual = dictionary['mean_annual']
    peak_annual = dictionary['peak_annual']
    min_annual = dictionary['min_annual']
    lat = dictionary['lat']
    lon = dictionary['lon']
    year = dictionary['year']
    
    #overwrite dictionary, average temporally 
    dictionary = {'mean_annual' : np.mean(mean_annual, axis = 0),
                  'peak_annual' : np.mean(peak_annual, axis = 0),
                  'min_annual' : np.mean(min_annual, axis = 0),
                  'year' : year,
                  'lat' : lat,
                  'lon' : lon}
    
    pickle.dump(dictionary, open(write_to, "wb" ) )
    
    print("--- %s seconds ---" % (time.time() - start_time))
    
    
#takes original Frasson file and adds a mean/min/max discharge column 
    #based on nearest neighbor approach (not as-the-crow-flies)
def assign_cop_to_latlon(sin_path, dis_path):
    # sin_path = r'D:\MS Sinuosity Data\MS_segments_recovered.xlsx'
    # dis_path = r'D:\CDS River Discharge\Pickles\compressed_ra.pickle'
    
    
    start_time = time.time() #start a timer 

    #import data , get lat, lon 
    df = pd.read_excel(sin_path)
    dic = pickle.load(open(dis_path, "rb" ) )
    
    lat = dic['lat'].tolist()
    lon = dic['lon'].tolist()
    
    #initialize lists 
    means = []
    maxs = []
    mins = []
    
    #iterate through dataframe from Frasson file and find the closest neighbor within GFAS 
    for ind in df.index:
        
        if ind % 1000 == 0: #print a progress statement 
            print('entry ' + str(ind))
        x = df['lat'][ind]
        y = df['lon'][ind]
        
        ind_x = find_closest_val(x, lat)
        ind_y = find_closest_val(y, lon)
        
        #get mean, max, min from the GFAS file 
        means.append(dic['mean_annual'][ind_x, ind_y])
        maxs.append(dic['peak_annual'][ind_x, ind_y])
        mins.append(dic['min_annual'][ind_x, ind_y])
    
    print('writing new columns to dataframe...')
    #add columns to dataframe 
    df['mean_dis'] = means
    df['min_dis'] = mins
    df['max_dis'] = maxs 
    
    #temporally convert -9999 values to nan, so that they can be processed by np.log
    df[df == -9999.0 ] = np.nan
    
    #add log columns to dataframe 
    df['log_sinuosity'] = np.log(df['Sinuosity'])
    df['log_mw'] = np.log(df['Meandwave'])
    df['log_mean_dis'] = np.log(df['mean_dis'])
    df['log_min_dis'] = np.log(df['min_dis'])
    df['log_max_dis'] = np.log(df['max_dis'])
    df['log_QWBM'] = np.log(df['QWBM'])
    
    #convert nan values back to -9999.0, so this file can be easily shared to non-Python friends 
    df.fillna(-9999.0)
    
    print('rewriting excel file with 9 new columns...')
    #rewrite excel file 
    df.to_excel(sin_path)
    
    #print time 
    print("--- %s seconds ---" % (time.time() - start_time))
    
#average the original file by SegmentID
def segment_frasson(original_frasson, output_file):
    
    #import data 
    df = pd.read_excel(original_frasson)
    df = df.replace(-9999, np.nan)
    df = df.dropna()
    
    unique = np.unique(df['SegmentID']) #find all unique SegmentID 
    df_new = df[0:0] #initialize dataframe 
    lengths = []
    
    for u in unique: #iterate through unique SegmentID
        x = df.loc[df['SegmentID'] == u] #find all values within original dataframe with iterated value 
        lengths.append(len(x))
        x = x.mean(axis = 0) #average along first axis 
        df_new = df_new.append(x, ignore_index = True) #append new dataframe 
    
    df_new['vals_in_seg'] = lengths
    df_new = df_new.drop(df_new.columns[:4], axis=1) #scummy fix 
    df_new.to_excel(output_file)
    
def perform_correlations(x_vals, y_vals, df):

    x_ind = 0
    
    correlations = np.zeros([len(x_vals), len(y_vals)])
    
    for x in x_vals:
        
        y_ind = 0
        for y in y_vals:
            
            corr = np.corrcoef(df[x], df[y])
            correlations[x_ind, y_ind] = corr[0, 1]
            y_ind = y_ind + 1
            
        x_ind = x_ind + 1
    df = pd.DataFrame(correlations, columns = y_vals, index = x_vals)
    print('Correlation Matrix')
    print(df)