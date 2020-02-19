# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 08:55:05 2020
Methods for visualizing data 
@author: bydd1
"""
import numpy as np 
import matplotlib.pyplot as plt 
import cartopy.crs as ccrs 
import cartopy

def plot_lat_lon_data(lat, lon, vals, title, cbar_label):
    plt.figure()
    
    ax = plt.subplot(projection = ccrs.PlateCarree())
    ax.coastlines()
    ax.add_feature(cartopy.feature.OCEAN)
    ax.add_feature(cartopy.feature.LAND, edgecolor='black')
    ax.add_feature(cartopy.feature.LAKES, edgecolor='black')
    
    scat = plt.scatter(lon, lat, c = vals, s = 10, cmap = 'coolwarm')
    cbar = plt.colorbar(scat)
    cbar.set_label(cbar_label)
    plt.xlabel('lon')
    plt.ylabel('lat')
    plt.title(title)
    
    