# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 10:29:01 2020

@author: bydd1
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 15:11:45 2020
Pull Copernicus data from 
https://cds.climate.copernicus.eu/cdsapp#!/dataset/10.24381/cds.a4fdd6b9?tab=overview

Calculate 
    1. average of mean annual flow (per pixel) 
    2. average of peak annual flow (maximum per year, average maximum)
    3. average of minimum annual flow (min per year, average) 

@author: bydd1
"""

from netCDF4 import Dataset
import os 
import numpy as np 
import data_methods as dm 
import datetime as dt 
import time as python_time
import pickle 
start_time = python_time.time()

#%%
# #bounding box = [[lat_high, lat_low], [lon_left, lon_right]]

#mississippi basin (maybe?): 
# bbox = [[48, 25], [76 - 180,  105 - 180]]

#full world:
bbox = [[89.95, - 59.95], [-179.95, 179.95]]

def convert_datetime(val):
    origin = dt.datetime(1979, 1, 1)
    date = origin + dt.timedelta(hours = val)
    return date

#read in a list of filenames from the CDS dataset and reorder in order of date
def parse_filenames(f):
    datetimes = []
    for i in f:
        year = int(i[17:21])
        month = int(i[21:23])
        day =  int(i[23:25])
        datetimes.append(dt.datetime(year, month, day))
    return datetimes
        
#return all indices for a specific year for the list of filenames 
def get_year_indices(datetimes, spec_year):
    indices = []
    for i in datetimes:
        if i.year == spec_year:
            indices.append(datetimes.index(i))
    return indices 

#return all indices for a specific month in a list of datetimes
    #here used assuming we're feeding in a list of one year's indices 
def get_month_indices(datetimes, given_indexes, spec_month):
    indices = []
    for i in given_indexes:
        if datetimes[i].month == spec_month:
            indices.append(i)
            
            
    return indices 

directory = r'D:\CDS River Discharge\Data'
files = os.listdir(directory)

save_path = r'D:\CDS River Discharge\Pickles\river_analytics.pickle'
datetimes = parse_filenames(files)

available_years = np.arange(datetimes[0].year, datetimes[-1].year + 1).tolist()

#get initial data - all lat/lon arrays 
path = os.path.join(directory, files[0])
dataset = Dataset(path, 'r', format = 'NETCDF4')
lat = dataset['lat'][:].data #get latitude data (should be same for all files)
lon = dataset['lon'][:].data #get longitude data 

#find indices for bounding box 
for i in bbox:
    if bbox.index(i) == 0: coord = lat
    if bbox.index(i) == 1: coord = lon 
    for j in i:
        bbox[bbox.index(i)][i.index(j)] = dm.find_closest_val(j, coord)

lat = lat[bbox[0][0]:bbox[0][1]]
lon = lon[bbox[1][0]:bbox[1][1]]
#initialize overall mean/peak/min arrays 
mean_annual = np.empty((len(available_years), len(lat), len(lon)))
peak_annual = np.empty((len(available_years), len(lat), len(lon)))
min_annual = np.empty((len(available_years), len(lat), len(lon)))

#%%

#batch processing method because of memory issues 
for year in available_years: #iterate through one year at a time 
    
    #log statements 
    time_elapsed = python_time.time() - start_time
    print('beginning analysis of year ' +str(year) +' : ' + str(time_elapsed) + ' seconds elapsed')
    
    y_indices = get_year_indices(datetimes, year) #all indices of files with data in year 
    #what months are available within this file subset 
    available_months = np.arange(datetimes[y_indices[0]].month, datetimes[y_indices[-1]].month + 1).tolist()
    
    #initialize arrays to store means/peaks/mins for JUST THIS YEAR 
    yearly_means = np.empty((len(available_months), len(lat), len(lon)))
    yearly_peak = np.empty((len(available_months), len(lat), len(lon)))
    yearly_min = np.empty((len(available_months), len(lat), len(lon)))
    
    for m in available_months:  #iterate through each month, calculating statistics 
        
        m_indices = get_month_indices(datetimes, y_indices, m) #find indices for the months within
        monthly_data = np.empty((len(m_indices), len(lat), len(lon))) #store daily data for specified
        
        #iterate through each day in the specific month 
        for mm in m_indices: 
            name = files[mm] #get file name 
            path = os.path.join(directory, name) #get filepath 
            dataset = Dataset(path, 'r', format = 'NETCDF4') #open dataset 
            
            #get time 
            time = dataset['time'][:].data
            time = convert_datetime(time[0]) #convert time to datetime object 
            dis = dataset['dis24'][:,bbox[0][0]:bbox[0][1],bbox[1][0]:bbox[1][1]].data
            dis[dis == 1e+20] = np.nan
            monthly_data[m_indices.index(mm), :, :] = dis[0, :, :]
        
        #after collecting all data for one month, calculate statistics and store in yearly 
        mean = np.nanmean(monthly_data, axis = 0)
        peak = np.nanmax(monthly_data, axis = 0)
        mini = np.nanmin(monthly_data, axis = 0)
    
        yearly_means[available_months.index(m), :, :] = mean
        yearly_peak[available_months.index(m), :, :] = peak
        yearly_min[available_months.index(m), :, :] = mini
        
        print('month ' +str(m) +' analysis completed')
    
    #after collecting all monthly averages/peaks/mins, repeat and store for the year 
    mean = np.nanmean(yearly_means, axis = 0)
    peak = np.nanmax(yearly_peak, axis = 0)
    mini = np.nanmin(yearly_min, axis = 0)
    
    mean_annual[available_years.index(year), :, :] = mean
    peak_annual[available_years.index(year), :, :] = peak
    min_annual[available_years.index(year), :, :] = mini
    min_annual[available_years.index(year), :, :] = mini 

#%%
# save all data in pickle 
dictionary = {'mean_annual' : mean_annual,
              'peak_annual' : peak_annual,
              'min_annual' : min_annual,
              'year' : available_years,
              'lat' : lat,
              'lon' : lon}


#%%
pickle.dump(dictionary, open(save_path, "wb" ) )
#open with pickle.load( open( save_path, "rb" ) )

print("--- %s seconds ---" % (python_time.time() - start_time))