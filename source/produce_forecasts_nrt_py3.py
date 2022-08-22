""" NEW VERSION:
        - ONE: improved interpolation method (dealing with no_data interpolation)
        - TWO: option to use Runge Kutta/odeint to interpolate velocity field instead of Euler x=x0+vdt (using function particles_displacement)
        - THREE: implemented option to not always derive forecast from observation at t0 but from previous forecast
"""

from __future__ import division
from __future__ import print_function

import time
from datetime import datetime
from datetime import timedelta
import sys, string, os
import logging

from satpy.resample import get_area_def
from satpy.utils import debug_on

#from mpop.satellites import GeostationaryFactory
#from mpop.projector import get_area_def
#from mpop.utils import debug_on
#from mpop.imageo.HRWimage import HRW_2dfield # , HRWstreamplot, HRWimage
#from mpop.imageo.palettes import convert_palette2colormap

#from plot_msg import create_PIL_image, add_borders_and_rivers, add_title
#from plot_msg import load_products


from pyresample import plot
import numpy as np
from pydecorate import DecoratorAGG
import aggdraw
from PIL import ImageFont, ImageDraw
from os.path import exists, dirname
from os import makedirs
from pycoast import ContourWriterAGG

from my_msg_module_py3 import check_near_real_time
#from my_msg_module import format_name
from my_msg_module_py3 import fill_with_closest_pixel
#from my_msg_module_py3 import check_loaded_channels
#from my_msg_module import convert_NWCSAF_to_radiance_format
#from my_msg_module import get_NWC_pge_name
from my_msg_module_py3 import check_input
from my_msg_module_py3 import create_seviri_scene

from copy import deepcopy 
import matplotlib.pyplot as plt
import copy
from particles_displacement import particles_displacement
import numpy.ma as ma
import netCDF4
import pickle
from scipy import ndimage

import scp_settings
scpOutputDir = scp_settings.scpOutputDir
scpID = scp_settings.scpID 
import glob
import inspect
import warnings

from dask.array.core import Array as daskarray

current_file = inspect.getfile(inspect.currentframe())

# debug_on()


#----------------------------------------------------------------------------------------------------------------
def print_usage():
   
   print("***           ")
   print("*** Error, not enough command line arguments")
   print("***        please specify at least an input file")
   print("***        possible calls are:")
   print("*** python "+inspect.getfile(inspect.currentframe())+" input_coalition2_cronjob ")
   print("*** python "+inspect.getfile(inspect.currentframe())+" input_coalition2_cronjob 2020 07 23 16 10 ")
   print("                                 date and time must be completely given")
   print("***           ")
   quit() # quit at this point
#----------------------------------------------------------------------------------------------------------------
# ------------------------------------------

def read_HRW(sat, time_slot, ntimes, dt=5, read_basic_or_detailed='DS', 
             min_correlation=85, min_conf_nwp=80, min_conf_no_nwp=80, cloud_type=None, level=None, p_limits=None):
    """
    read_basic_or_detailed:
      "BS"  read HRW product with basic resolution
      "DS"  read HRW product with detailed resolution
    """

    data = create_seviri_scene(time_slot, base_dir_ctth, sat=MSG_str, reader='nwcsaf-geo', file_filter=read_basic_or_detailed)  
    data.load(['HRW'])
    
    # read data for previous time steps if needed
    for it in range(1,ntimes):
        time_slot_i = time_slot - timedelta( minutes = it*5 )

        data_i = create_seviri_scene(time_slot_i, base_dir_ctth, sat=MSG_str, reader='nwcsaf-geo', file_filter=read_basic_or_detailed)  
        data_i.load(['HRW'])
        
        # merge all datasets
        data['HRW'].HRW_detailed = data['HRW'].HRW_detailed + data_i['HRW'].HRW_detailed
        data['HRW'].HRW_basic    = data['HRW'].HRW_basic    + data_i['HRW'].HRW_basic

    # apply quality filter
    data['HRW'].HRW_detailed = data['HRW'].HRW_detailed.filter(min_correlation=min_correlation, \
                    min_conf_nwp=min_conf_nwp, min_conf_no_nwp=min_conf_no_nwp, cloud_type=cloud_type, level=level, p_limits=p_limits)

    return data


# ===============================

def downscale_array(array, mode='gaussian_225_125', mask=None):

    print ("    downscale with mode: ", mode)

    if not isinstance( array, (np.ndarray, np.generic, daskarray) ):
        print ("*** Warning in downscale_array ("+inspect.getfile(inspect.currentframe())+")")
        print ("    unexpected data format ", type(array), ", expected array format np.ndarray")
        return array

    # if no_downscaling return unmodified array
    if mode == 'no_downscaling':
        return array
    # else define downscale function and weights 
    elif mode == 'convolve_405_300': 
        weights = np.ones([5,3])
        weights = weights / weights.sum()   
        downscale_func = ndimage.convolve
    elif mode == 'gaussian_150_100':
        weights = 1/3.*np.array([4.5,3.0])  # conserves a bit better the maxima
        downscale_func = ndimage.filters.gaussian_filter
    elif mode == 'gaussian_225_125':
        weights = 1/2.*np.array([4.5,3.0])  # no artefacts more for shifted fields
        downscale_func = ndimage.filters.gaussian_filter
    else:
        print ("*** Error in downscale_array ("+inspect.getfile(inspect.currentframe())+")")
        print ("    unknown downscaling mode: "+mode)
        quit()
        
    # get suitable no data flag depending on 
    if (array.dtype == np.float) or (array.dtype == np.float32):
        print ("    downscale float array, no_data = np.nan")
        no_data = np.nan
    elif (array.dtype == np.int):    # for int or uint np.nan does not exists 
        print ("    downscale integer array, no_data = -1")
        no_data = -1
    elif (array.dtype == np.uint8):
        print ("    downscale unsigned integer array, no_data = 0")
        no_data = 0
    else:
        print ("*** Error in downscale_array ("+inspect.getfile(inspect.currentframe())+")")
        print ("    unknown data type: ", array.dtype)
        quit()

    # force mask and fill the whole array with closest pixel
    if mask is not None:
        print("... replaced masked data with not a number (for floats)")
        array[mask] = no_data
        array = fill_with_closest_pixel(array)

    # downscale array 
    array_downscaled = downscale_func(array, weights, mode='nearest')

    # restore mask
    if mask is not None:
        print("... mask out data in downscaled array")
        array_downscaled[mask] = no_data

    """
    # convert to mask array and change array.mask 
    if mask is not None:
        np.ma.masked_array(array, mask)
    """

    return array_downscaled

# ===============================
    
def downscale(data, mode='gaussian_225_125', mask=None):
    
    """ downscales the data to a finer grid

    Parameters
    ----------
    data : data to downscale 
           either np.ndarray (single array) or 
           satpy.Scene.scene (all loaded channels of the scene)
    mode : specific mode to downscale
           'gaussian_150_100', 'gaussian_225_125' or 'convolve_405_300'
    mask : optional, indices that should be masked
    
    Returns : 
    ----------
    data : downscaled version of the data
        
    Raises
    ----------
         """

    # assymetric downscaling as SEVIRI pixel size is approx 3kmx4.5km for Europe

    
    print("========")
    
    if isinstance(data, np.ndarray):
        downscale_array(data, mode=mode, mask=mask)
        
    #elif isinstance(data, Scene.Scene):    # TODO, how to identify Scene object? print(type(data)) -> <class 'satpy.scene.Scene'>
    else:

        #for chn in data.loaded_channels():   # mpop/python2 
        for chn in list(data.keys()):
    
            # do not downscale cloud classes 
            if chn["name"] == "CT":
                continue 
            # comment: Shoud we downscale chn.name != "CTP", "CTH", "CTT"?

            if hasattr(data[chn["name"]], 'data'):
                print ("... downscale "+chn["name"])
                data[chn["name"]].data = downscale_array(data[chn["name"]].data, mode=mode, mask=mask)
            else:
                print ("*** Warning in downscale ("+inspect.getfile(inspect.currentframe())+")")
                print ("    skip downscaling of ", chn.name, ", as this channel has no attribute: data" )

    return data
    
# ===============================


def m_to_pixel(value,size,conversion): #,coordinate):
            
    if conversion=='to_pixel':
        px =  np.round(value//size) 
        px[np.where(value==np.nan)] = np.nan
        px = px.astype(int)
        return px
    else:
        m = (value*size)+size/2
        m[value==np.nan] = np.nan
        return ms

def string_date(t):
    yearS  = str(t.year)
    monthS = "%02d" % t.month
    dayS   = "%02d" % t.day
    hourS  = "%02d" % t.hour
    minS   = "%02d" % t.minute
    
    return yearS, monthS, dayS, hourS, minS

def check_cosmo_area (nc_cosmo, nx, ny, area):

    """ check dimensions of the COSMO file 
        compare to the desired projection described by area
        return how many pixels needs to be skiped at the beginning and the end of the x and y axis to cover the desired area "area"
        (function assumes that the projection type of "area" and the cosmo file is the same)
    """
    
    # determine lengths in x and y in meter of the COSMO data
    x = nc_cosmo.variables['y_1'][:]
    y = nc_cosmo.variables['x_1'][:]
    x_min_cosmo = x.min()-500            # substract 500m (half a pixel size)
    x_max_cosmo = x.max()+500            # add       500m (half a pixel size)
    y_min_cosmo = y.min()-500            # substract 500m (half a pixel size)
    y_max_cosmo = y.max()+500            # add       500m (half a pixel size)

    # determine size in meter of the desired area
    area_wanted = get_area_def(area)
    x_min_wanted = area_wanted.area_extent[1]
    x_max_wanted = area_wanted.area_extent[3]
    y_min_wanted = area_wanted.area_extent[0]
    y_max_wanted = area_wanted.area_extent[2]

    # determine grid spacing 
    x = np.sort(x)
    dx_cosmo = x[1]-x[0]
    y = np.sort(y)
    dy_cosmo = y[1]-y[0]       

    # compare grid spacing 
    if dy_cosmo != area_wanted.pixel_size_y or dx_cosmo != area_wanted.pixel_size_x:
        print("Error: the pixel size of the wind data doesn't match with the chosen area definition")
        quit()

    # if COSMO file is larger than the desired area, get sub-area of the COSMO data
    if x_min_cosmo <= x_min_wanted and x_max_cosmo >= x_max_wanted and y_min_cosmo <= y_min_wanted and y_max_cosmo >= y_max_wanted:
        x_min_cut = abs(x_min_cosmo - x_min_wanted)/1000
        x_max_cut = abs(x_max_cosmo - x_max_wanted)/1000
        y_min_cut = abs(y_min_cosmo - y_min_wanted)/1000
        y_max_cut = abs(y_max_cosmo - y_max_wanted)/1000
    else:
        print("Error: the area chosen ("+area+") is larger than the wind data (cosmo) area available")
 
    return int(x_min_cut), int(x_max_cut), int(y_min_cut), int(y_max_cut)

def get_cosmo_filenames (t_sat, nrt=True, runs_before = 0 ):

    # get COSMO model start time
    hour_run = t_sat.hour //3 * 3 
    t_run = datetime(t_sat.year, t_sat.month, t_sat.day, hour_run, 0)

    if runs_before != 0:
        print("    try ", runs_before ," model start(s) before ")
        t_run -= runs_before * timedelta(hours = 3) 

    dt = t_sat - t_run
    hour_forecast1 = "%02d" % int (dt.total_seconds() / 3600) # using integer devision 
    hour_forecast2 = "%02d" % int (dt.total_seconds() / 3600 +1)  # using integer devision 

    yearS, monthS, dayS, hourS, minS = string_date(t_run)

    print("***get_cosmo_filenames***** nrt *******", nrt) 

    ### !!! NEED A PROPER FIX !!!!
    # before Oct 2020 ??? 
    #if nrt:          
    #    cosmo = "cosmo-1"
    #else:
    #    cosmo = "cosmo2"
    # after Oct 2020 ??? 
    #cosmo = "cosmo-1e"
    cosmo = "cosmo-1*"   #accepts "cosmo-1" and "cosmo-1e"
    
    if nrt:          
        cosmoDir='/data/cinesat/in/cosmo/' #2016052515_05_cosmo-1_UV_swissXXL
    else:
        cosmoDir=t_sat.strftime('/data/COALITION2/database/cosmo/wind/%Y/%m/%d/') #20150515_cosmo2_ccs4c2 / 2015051506_00_cosmo2_UVccs4c2.nc or 2015070706_00_cosmo2_UV_ccs4c2.nc
        #cosmoDir='/data/COALITION2/database/cosmo/test_wind/'

    cosmo_file1 = yearS+monthS+dayS+hourS+"_"+hour_forecast1+"_"+cosmo+"_UV*.nc"
    cosmo_file2 = yearS+monthS+dayS+hourS+"_"+hour_forecast2+"_"+cosmo+"_UV*.nc"

    return cosmoDir+cosmo_file1, cosmoDir+cosmo_file2


def interpolate_cosmo(year, month, day, hour, minute, layers, zlevel='pressure', area='ccs4', cosmo = None, nrt = False, rapid_scan_mode_satellite = True):

    # given the date, search for two COSMO files adjacent in time
    # containing wind data on pressure levels
    # read two consecutive cosmo files and interpolate temporal
    
    
    print("*** interpolate_cosmo nrt", nrt) 
    file1, file2 = get_cosmo_filenames ( datetime(year,month,day,hour,minute), nrt=nrt )

    print("... search for ", file1, " and ", file2)
    filename1 = glob.glob(file1)
    filename2 = glob.glob(file2)

    if len(filename1)>1 or len(filename2)>1:
        print("Warning, more than one cosmo file available!!")
        print("Files t1", filename1)
        print("Files t2", filename2)
            
    if len(filename1)<1 or len(filename2)<1:
        print("*** Warning, found no cosmo wind data, search for preveous COSMO run... ")
        file1, file2 = get_cosmo_filenames ( datetime(year,month,day,hour,minute), runs_before = 1 )
        print(file1, file2)

        print("... search for ", file1, " and ", file2)
        filename1 = glob.glob(file1)
        filename2 = glob.glob(file2)
        
        if len(filename1)>1 or len(filename2)>1:
            print("Warning, more than one cosmo file available!!")
            print("Files t1", filename1)
            print("Files t2", filename2)
        elif len(filename1)<1 or len(filename2)<1:
            print("*** Error, no cosmo wind data for time: ", str(datetime(year,month,day,hour,minute)))
            print(file1)
            print(file2)
            quit()
    
    file_cosmo_1 = filename1[0]
    file_cosmo_2 = filename2[0]
    
    #cosmoDir='/data/cinesat/in/cosmo' #2016052400_03_cosmo-1_UV_swissXXL.nc

    print('... read ', file_cosmo_1)  
    print('... read ', file_cosmo_2)
    
    nc_cosmo_1 = netCDF4.Dataset(file_cosmo_1,'r',format='NETCDF4') 
    nc_cosmo_2 = netCDF4.Dataset(file_cosmo_2,'r',format='NETCDF4') 
    
    pressure1 = nc_cosmo_1.variables['z_1'][:]
    if nc_cosmo_1.variables['z_1'].units=='hPa':
        fpress1 = 100
    elif nc_cosmo_1.variables['z_1'].units=='Pa':
        fpress1 = 1
    else:
        print("*** Warning, unknown unit for wind in ", file_cosmo_1)
        fpress1 = 1
    pressure1 = pressure1.astype(int) * fpress1
    
    pressure2 = nc_cosmo_2.variables['z_1'][:]
    if nc_cosmo_2.variables['z_1'].units=='hPa':
        fpress2 = 100
    elif nc_cosmo_2.variables['z_1'].units=='Pa':
        fpress2 = 1
    else:
        print("*** Warning, unknown unit for wind in ", file_cosmo_2)
        fpress2 = 1
    pressure2 = pressure2.astype(int) * fpress2
    
    print("    pressure levels in file1: ", pressure1)
    print("    pressure levels in file2: ", pressure2)

    u_all1 = nc_cosmo_1.variables['U'][:] 
    v_all1 = nc_cosmo_1.variables['V'][:]
    u_all2 = nc_cosmo_2.variables['U'][:] 
    v_all2 = nc_cosmo_2.variables['V'][:]

    # remove the dimension for the COSMO ensemble 
    if (u_all1.ndim == 5):
        u_all1 = u_all1[0]
    if (v_all1.ndim == 5):
        v_all1 = v_all1[0]
    if (u_all2.ndim == 5):
        u_all2 = u_all2[0]
    if (v_all2.ndim == 5):
        v_all2 = v_all2[0]
    
    nx1 = u_all1.shape[2]
    ny1 = u_all1.shape[3] 
    
    nx2 = u_all2.shape[2]
    ny2 = u_all2.shape[3]  

    if (nx1 != nx2) or (ny1 != ny2):
        print("*** ERROR in interpolate_cosmo ("+inspect.getfile(inspect.currentframe())+")")
        print("    COSMO files have different sizes: (",nx1,",",ny1,"), (",nx2,",",ny2,")")
        quit()
    
    x_min_cut1, x_max_cut1, y_min_cut1, y_max_cut1 = check_cosmo_area (nc_cosmo_1, nx1, ny1, area)
    x_min_cut2, x_max_cut2, y_min_cut2, y_max_cut2 = check_cosmo_area (nc_cosmo_2, nx2, ny2, area) 
    
    p_chosen = np.sort(layers)[::-1] * 100 # 100 == convert hPa to Pa

    #print(nx1, ny1, nx2, ny2)
    #print(x_min_cut1, x_max_cut1, y_min_cut1, y_max_cut1)
    #print(x_min_cut2, x_max_cut2, y_min_cut2, y_max_cut2)
    
    nx = (nx1 - x_min_cut1) - x_max_cut1
    ny = (ny1 - y_max_cut1) - y_min_cut1
    u_d = np.zeros((len(p_chosen),nx,ny))
    v_d = np.zeros((len(p_chosen),nx,ny))

    # account for the time difference in minutes
    # of scanning Switzerland compared to time stamp of SEVIRI files (end of scan)
    if rapid_scan_mode_satellite:
        dt = 2
    else:
        dt = 12

    position_t = (minute+dt)/5
    previous   = 1-(1./12*position_t)

    # loop over pressure levels and extract sub-region 
    for g in range(len(p_chosen)):
        print("... temporal interpolation for wind field at", p_chosen[g], "(",p_chosen,")")
        i1 = np.where(pressure1==p_chosen[g])[0][0]
        i2 = np.where(pressure2==p_chosen[g])[0][0]

        u1 = u_all1[0, i1, x_max_cut1 : nx1 - x_min_cut1, y_min_cut1 : ny1 - y_max_cut1]     #20:nx-40,85:ny-135
        u2 = u_all2[0, i2, x_max_cut2 : nx2 - x_min_cut2, y_min_cut2 : ny2 - y_max_cut2]     #### UH index changed i1 -> i2 !!! ###
        v1 = v_all1[0, i1, x_max_cut1 : nx1 - x_min_cut1, y_min_cut1 : ny1 - y_max_cut1]     #### UH index changed i2 -> i1 !!! ###
        v2 = v_all2[0, i2, x_max_cut2 : nx2 - x_min_cut2, y_min_cut2 : ny2 - y_max_cut2]
        u_d[g,:,:] = previous*u1 + (1-previous)*u2
        v_d[g,:,:] = previous*v1 + (1-previous)*v2 

    return u_d, v_d
    

def calculate_displacement(u_d,v_d,n_levels,size_x,size_y,ForecastTime,NumComputationSteps):


    print("***")
    print("*** calculate displacement")

    dx_d = np.zeros(u_d.shape)
    dy_d = np.zeros(v_d.shape)

    for level in range(n_levels):   # !!!!!!!
    #for level in [0]:

          print("... calculate displacement for level ", level)
          u = u_d[level,:,:]
          v = v_d[level,:,:]

          max_x = u.shape[0]
          max_y = u.shape[1] 

          x_matrix = np.array([[i*size_x+size_x/2 for i in range(u.shape[0])],]*max_y).transpose()
          y_matrix = np.array([[i*size_y+size_y/2 for i in range(u.shape[1])],]*max_x)        

          x = np.reshape(x_matrix,x_matrix.size)
          y = np.reshape(y_matrix,y_matrix.size)        

          xy1 = np.column_stack((x,y))

          dt = float(ForecastTime)/float(NumComputationSteps)

          a=np.zeros(xy1.shape)
          xy2=deepcopy(xy1)

          # !!! SLOW !!!
          for num_compSteps in range(NumComputationSteps):
                xy2 = particles_displacement(u_func=v*(-1), v_func=u,method=method,dt=dt*60,pts=xy2, size_x=size_x, size_y=size_y, wind_source=wind_source) #u_func=v*(-1)
                c = 0
                for item in xy2: #because output particles displacement is a list
                    a[c,:]=item
                    c+=1
                xy2=a

          x_matrix1 = np.reshape(xy2[:,0],x_matrix.shape)
          y_matrix1 = np.reshape(xy2[:,1],y_matrix.shape)

          dx_d[level,:,:] = x_matrix1-x_matrix
          dy_d[level,:,:] = y_matrix1-y_matrix

    return (xy1, xy2, dx_d, dy_d, x_matrix, y_matrix)

def add_points_outside(forecast,x_matrix,y_matrix, xy_inside):
    
    x_new = np.where(np.isnan(forecast),x_matrix,np.nan)
    y_new = np.where(np.isnan(forecast),y_matrix,np.nan)
    x_new = np.reshape(x_new,x_new.size)
    y_new = np.reshape(y_new,y_new.size)        
    xy_new = np.column_stack((x_new,y_new))  
    xy_new = xy_new[~np.isnan(xy_new).any(axis=1)]                      
    print("*** add new particles for empty pixels")
    #store tracking coordinates for next step of this level
    xy_new = np.vstack((xy2, xy_new))
    print("... number of particles for next step (xy_new.shape)", xy_new.shape)
    xy_levels = deepcopy(xy_new)
    return xy_levels    

def nowcastRGB(forecast1,xy1_py,xy2_px):
    forecast2 = deepcopy(forecast1)
    forecast2[:,:] = np.nan
    
    
    # search no clouds in the old data 
    ind_no_cl = np.where ( forecast1[xy1_px[:,0],xy1_px[:,1]] == no_data )
    
    # copy values only for not cloudy pixels
    forecast2[xy2_px[ind_no_cl,0],xy2_px[ind_no_cl,1]] = no_data
    
    # search clouds in the old data 
    ind_cl = np.where ( forecast1[xy1_px[:,0],xy1_px[:,1]] > 0 )
    
    # copy values only for cloudy pixels
    forecast2[xy2_px[ind_cl,0],xy2_px[ind_cl,1]] = forecast1[xy1_px[ind_cl,0],xy1_px[ind_cl,1]]
    
    return forecast2

def initial_xy(x_matrix,y_matrix):
      
      x = np.reshape(x_matrix,x_matrix.size)
      y = np.reshape(y_matrix,y_matrix.size)        
      
      xy1 = np.column_stack((x,y))
      
      return xy1 #store coordinate centers xy=[x_center,y_center] xy_levels[level,:,:]

def compute_new_xy(xy1, dx_ds, dy_ds,  max_x_m, max_y_m):                       
    xy2 = np.zeros(xy1.shape)
    
    #conversion to pixel to obtain corresponding dx and dy
    xy1_px = np.zeros(xy1.shape, dtype=np.int)   ### initialize as integer ###
    xy1_px[:,0] = m_to_pixel(xy1[:,0],size_x,'to_pixel')
    xy1_px[:,1] = m_to_pixel(xy1[:,1],size_y,'to_pixel')
    
    print('... calculate new particle positions')
    
    xy2 = np.zeros(xy1.shape)
    xy2[:,0] = xy1[:,0] + dx_ds[level, xy1_px[:,0], xy1_px[:,1] ]
    xy2[:,1] = xy1[:,1] + dy_ds[level, xy1_px[:,0], xy1_px[:,1] ]
    
    # remove particles outside the domain 
    print("... limits before removing: ", xy2.min(), xy2.max(), end=' ')  

    ind_inside = np.where( np.logical_and( np.logical_and(0<=xy2[:,0],xy2[:,0]<max_x_m), np.logical_and(0<=xy2[:,1],xy2[:,1]<max_y_m) ) )

    xy2    = np.squeeze(xy2[ind_inside,:])
    xy1_px = np.squeeze(xy1_px[ind_inside,:])
    
    print("... limits after removing: ", xy2.min(), xy2.max(), end=' ')  
    print("... number of particles after removing those outside (xy2_px.shape)", xy2.shape)
    
    #convert xy2 in pixel to do the shift for each channel
    xy2_px = np.zeros(xy2.shape, dtype=np.int)   ### initialize as integer ###
    xy2_px[:,0] = m_to_pixel(xy2[:,0],size_x,'to_pixel')
    xy2_px[:,1] = m_to_pixel(xy2[:,1],size_y,'to_pixel')            
    
    return (xy1_px, xy2_px, xy2)

def mask_rgb_based_pressure(data,p_min,p_max,data_CTP):
    ####################################data[data.mask==True ] = no_data
    data = np.where(np.logical_or(data_CTP['ctth_pres'].data>=p_max,data_CTP['ctth_pres'].data<p_min),no_data,data)
    
    return data
# ------------------------------------------

#def wind_shiftFun(in_windshift):
if __name__ == '__main__':
    # input 
    
    LOG = logging.getLogger(__name__)
    LOG.setLevel(30)

    time_start_TOT = time.time()
    detailed = True 
 
    area = "ccs4c2" #"ccs4" #"#in_windshift.ObjArea
 
    title_color=(255,255,255)
    #layer=''
    layer=' 2nd layer'
    #layer='3rd layer'
    add_rivers=False
    add_borders=False
    legend=True

    ntimes=2 #in_windshift.ntimes
    print("... aggregate winddata for ", ntimes, " timesteps") 
    min_correlation = 85 #in_windshift.min_correlation
    min_conf_nwp = 80 #in_windshift.min_conf_nwp
    min_conf_no_nwp = 80 #in_windshift.min_conf_no_nwp
    cloud_type = [5,6,7,8,9,10,11,12,13,14] #in_windshift.cloud_type

    delta_t = 5 #in_windshift.ForecastTime

    # satellite for HRW winds
    sat_nr = "08" #in_windshift.sat_nr

    plot_DisplMeter = False #if you want to plot the forecast for each channel
        
    rgbs = ['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134']  #in_windshift.rgb
    rgbs_only15min = ['IR_039','IR_087','IR_120']
    #channel = rgb.replace("c","")

    rapid_scan_mode = False
    
    dt_forecast1 = 15
    dt_forecast2 = 30
    
    if rapid_scan_mode ==True:
            dt_forecast1 = 5
            dt_forecast2 = 10
    if rapid_scan_mode == True:
        print("... RAPID SCAN MODE")
    else:
        print("... NOT RAPID SCAN MODE")
    
    dt_forecast1S = "%02d" % dt_forecast1
    dt_forecast2S = "%02d" % dt_forecast2
    
    ForecastTime = 5 #time in minutes from observation at t=0 when you want each observation (first forecast after ForecastTime, second after 2*ForecastTime...)
    NumComputationSteps = 1 #number of computation time steps: the number of steps when the velocity should be updated within each ForecastTime
    NumForecast = int(dt_forecast2/ForecastTime) #6number of forecasts you want to produce from observation at t=0

    downscaling_data = True
    mode_downscaling = 'gaussian_225_125'
    #mode_downscaling = 'convolve_405_300'
    #mode_downscaling = 'gaussian_150_100'
    #mode_downscaling = 'no_downscaling'    


#integration method, uncomment one
    #method="rk4"
    method="euler" 

    methodComput="internet"
    #methodComput="mine"
    
#the type of tracking desired, uncomment one
    #in_windshift.TrackingType="particles"
    TrackingType="field"
    
    separate_levels=True
    
    #wind_source="HRW"
    pressure_limits=[440,680]#[400,700] #[]#[150,250,350,450,550,650,750,850]# #[250,400] #[300,500]#
    n_levels=len(pressure_limits)+1
    
    wind_source="cosmo"
    zlevel = 'pressure' 
    #zlevel = 'modellevel'

    if wind_source=="cosmo":
        if zlevel == 'pressure':
            ### !!! check this, HAU !!!
            layers=[800,500,300]#[700,500,300]#[900,800,700,600,500,400,300,200,100] #[700,500,300]#[100] # [400,300,100]#[600,300,100]##pressure layers 
        elif zlevel == 'modellevel':
            layers=[36,24,16] #cosmo model layers
        else:
            print("*** Error in main ("+current_file+")")
            print("    unknown zlevel", zlevel)
            quit()
        
    # ------------------------------------------

    # possible High Resolution wind images
    HRWimages = ['channel','pressure','correlation','conf_nwp','conf_no_nwp']
    # alternatively also possible is the plot of 'stream' lines 

    ############################################################################

    ############################################################################


    from get_input_msg_py3 import get_date_and_inputfile_from_commandline
    in_msg = get_date_and_inputfile_from_commandline(print_usage=print_usage)

    # interpret additional command line arguments
    if len(sys.argv) > 7:
        if len(sys.argv) == 12:
            yearSTOP   = int(sys.argv[7])
            monthSTOP  = int(sys.argv[8])
            daySTOP    = int(sys.argv[9])
            hourSTOP   = int(sys.argv[10])
            minuteSTOP = int(sys.argv[11])
            time_slotSTOP = datetime(yearSTOP, monthSTOP, daySTOP, hourSTOP, minuteSTOP)
        else:
            print("*** ERROR in __main__ ("+current_file+")")
            print("    wrong number of command line arguments: ", len(sys.argv))
            quit()
    else:            
        time_slotSTOP = in_msg.datetime
     
    in_msg.resolution = 'i'
    in_msg.sat="Meteosat-"
    #in_msg.sat_nr = 9
    in_msg.add_title=False
    in_msg.outputDir='./pics/'
    in_msg.outputFile='WS_%(rgb)s-%(area)s_%y%m%d%H%M'
    in_msg.fill_value = [0,0,0] # black
    #in_msg.reader_level = "seviri-level2"
    
    #in_msg.fill_value = None    # transparent
    #colormap='rainbow' 
    colormap='greys'      
            
    # second argument is tolerance in minutes for near real time processing
    in_msg.nrt = check_near_real_time(in_msg.datetime, 120)
    print("... in_msg.nrt", in_msg.nrt)
    if in_msg.nrt:
        base_dir_sat = "/data/cinesat/in/eumetcast1/"
        base_dir_ctth = "/data/cinesat/in/safnwc/"        
    else:
        #base_dir_sat  = in_msg.datetime.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/%Y/%m/%d/")
        base_dir_sat  = in_msg.datetime.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/%Y/%m/%d/")
        base_dir_ctth = in_msg.datetime.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/CTTH/")   # NWCSAF produced by MeteoSwiss with RSS  
        #base_dir_ctth = in_msg.datetime.strftime("/data/OWARNA/hau/database/meteosat/SAFNWC/%Y/%m/%d/CTTH/")        # NWCSAF produced by EUMETSAT   with FDS
    
    if in_msg.nrt:
        outputDir = in_msg.nowcastDir
    else:
        # old outputDir="/data/COALITION2/PicturesSatellite/LEL_results_wind/"
        outputDir=in_msg.datetime.strftime("/data/COALITION2/database/meteosat/rad_forecast/%Y-%m-%d/channels/")

    if not exists(outputDir):
        makedirs(outputDir)

    while in_msg.datetime <= time_slotSTOP:
    
          print(str(in_msg.datetime))

          year = in_msg.datetime.year
          month = in_msg.datetime.month
          day = in_msg.datetime.day
          hour = in_msg.datetime.hour
          minute = in_msg.datetime.minute
                    
          yearS = str(year)
          #yearS = yearS[2:]
          monthS = "%02d" % month
          dayS   = "%02d" % day
          hourS  = "%02d" % hour
          minS   = "%02d" % minute
          dateS = yearS+'-'+monthS+'-'+dayS
          timeS = hourS+':'+minS+" UTC"
          
          # define area object 
          obj_area = get_area_def(area)#(in_windshift.ObjArea)
          size_x = obj_area.pixel_size_x
          size_y = obj_area.pixel_size_y  
          
          #print(obj_area)
          #print("area extent:\n",obj_area.area_extent)
          #print("x min ", obj_area.area_extent[0])
          #print("x size ", obj_area.pixel_size_x)

          print(in_msg.RGBs)
          # check if input data is complete 
          if in_msg.verbose:
              print("*** check input data", in_msg.RGBs, " for ", in_msg.sat_str()+in_msg.sat_nr_str())
          for i_try in range(30):
              RGBs = check_input(in_msg, in_msg.sat_str()+in_msg.sat_nr_str(), base_dir_sat, in_msg.datetime, RGBs=in_msg.RGBs)
              if len(RGBs) > 0:
                  # exit loop, if input is found
                  break
              else:
                  # else wait 20s and try again
                  import time
                  time.sleep(25)             
          # in_msg.sat_nr might be changed to backup satellite
          
          # define area
          proj4_string = obj_area.proj4_string            
          # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
          area_extent = obj_area.area_extent              
          # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
          area_tuple = (proj4_string, area_extent)
      
          # read CTP to distinguish high, medium and low clouds
          for i_try in range(30):
              RGBs = check_input(in_msg, in_msg.sat_str()+in_msg.sat_nr_str(), base_dir_ctth, in_msg.datetime, RGBs=['CTH'])
              if len(RGBs) > 0:
                  # exit loop, if input is found
                  break
              else:
                  # else wait 20s and try againf

                  time.sleep(25)

          # global data for radiances
          MSG_str = in_msg.msg_str(layout="%(msg)s%(msg_nr)s")
          global_data = create_seviri_scene(in_msg.datetime, base_dir_sat, sat=MSG_str)
          with warnings.catch_warnings():
              warnings.simplefilter("ignore")
              global_data.load(rgbs)
          
          global_data_CTP = create_seviri_scene(in_msg.datetime, base_dir_ctth, sat=MSG_str, reader='nwcsaf-geo')
          with warnings.catch_warnings():
              warnings.simplefilter("ignore")
              global_data_CTP.load(['ctth_pres'])  # "Cloud Top Pressure"

          ## resample to area
          data = global_data.resample(area, precompute=True)
          data_CTP = global_data_CTP.resample(area, precompute=True)
          # get the dimension of the target area "area": nx and ny (used later in the script) 
          [nx,ny]=data_CTP['ctth_pres'].data.shape
          
          ## check if all needed channels are loaded
          ##for rgb in rgbs:
          #if not check_loaded_channels(rgbs, data):
          #    print("*** Error in produce_forecast_nrt ("+current_file+")")
          #    print("    missing data")
          #    quit()

          if False:
              from trollimage.image import Image as trollimage
              from trollimage.colormap import rainbow
              prop = data["IR_108"].data
              min_data = prop.min()
              max_data = prop.max()
              colormap = deepcopy(rainbow)
              colormap.set_range(min_data, max_data)
              img = trollimage(prop, mode="L", fill_value=[0,0,0])
              img.colorize(colormap)
              img.show()
              quit()

          if downscaling_data == True:
               data = downscale(data, mode = mode_downscaling)
   
          # read wind field
          if wind_source=="HRW":
              u_d=np.zeros((n_levels,nx,ny))
              v_d=np.zeros((n_levels,nx,ny))
              for level in range(n_levels):
                  p_max=p_min
                  if level==n_levels-1:
                      p_min=0
                  else:
                      p_min=pressure_limits[len(pressure_limits)-1-level]  
      
                  hrw_data = read_HRW(in_msg.msg_str(layout="%(msg)s%(msg_nr)s"), in_msg.datetime, ntimes, \
                                       min_correlation=min_correlation, min_conf_nwp=min_conf_nwp, \
                                       min_conf_no_nwp=min_conf_no_nwp, cloud_type=cloud_type, p_limits=[p_min,p_max])
      
      
                     # choose basic or detailed (and get a fresh copy) 
                  if detailed:
                      print('... calculate gridded 2d wind field High') 
                      hrw_detbas = hrw_data['HRW'].HRW_detailed                   
                  else:
                      print('... calculate gridded 2d wind field High') 
                      hrw_detbas =  hrw_data['HRW'].HRW_basic       
      
                  u_d[level,:,:], v_d[level,:,:] = HRW_2dfield( hrw_detbas, obj_area )
      
          elif wind_source=="cosmo":
              print("********** in_msg.nrt *******", in_msg.nrt)
              print("year, month, day, hour, minute", year, month, day, hour, minute)
              u_d, v_d = interpolate_cosmo(year, month, day, hour, minute, layers, zlevel, area, nrt=in_msg.nrt, rapid_scan_mode_satellite=True)
          else:
              print("*** Error in main ("+current_file+")")
              print("    unknown wind source ", wind_source)
              quit()
      
      
          ### calculate particle displacement ###
          (xy1s,xy2s,dx_ds,dy_ds,x_matrixs,y_matrixs) = calculate_displacement(u_d,v_d,n_levels,size_x,size_y,ForecastTime,NumComputationSteps)
      
          ### prepare dictionary for channel numbers:
          channel_nr={}
          for i in range(len(rgbs)):
              rgb=rgbs[i]
              channel_nr[rgb]=i
          
          
          p_min = 1001
          no_data = -1000000000
          #xy_levels = np.zeros((n_levels,nx*ny,2))
          forecasts_out = np.zeros((len(channel_nr),2,nx,ny))
          forecasts_NextStep = np.zeros((len(channel_nr),n_levels,nx,ny))
          
          max_x_m = nx*size_x
          max_y_m = ny*size_y
          
       
          for level in range(n_levels):
          
              print("... calculation for level ", level)
      
              p_max = p_min
              
              if level==n_levels-1:
                  p_min = 0
              else:
                  p_min = pressure_limits[len(pressure_limits)-1-level]              
              
              u = u_d[level,:,:]
              v = v_d[level,:,:]  
      
              for t in range(1,NumForecast+1):
                  print("*** timestep ",t," of ",NumForecast)
                  if t==1: #if first timestep create x and y matrices covering entire image
                      xy_levels = initial_xy(x_matrixs,y_matrixs)
      
                  xy1 = deepcopy(xy_levels) #xy_levels[level,:,:] #take the initial coordinates from array storage (step before)
                  
                  (xy1_px, xy2_px, xy2) = compute_new_xy (xy1, dx_ds, dy_ds,  max_x_m, max_y_m)
                  
                  
                  for rgb_num in range(len(rgbs)):
                      rgb=rgbs[rgb_num]
                      if t==1:
                          with warnings.catch_warnings():
                              warnings.simplefilter("ignore")
                              forecasts_NextStep[channel_nr[rgb],level,:,:] = mask_rgb_based_pressure(data[rgb].data,p_min,p_max, data_CTP)
                          
                      #check if for current channel (rgb) you also need the 30 min forecast
                      if t*ForecastTime > dt_forecast1:
                          if any(rgb in s for s in rgbs_only15min):
                              continue
                          
                      forecast1 = forecasts_NextStep[channel_nr[rgb],level,:,:]
                      print("*** calculating the nowcasted values of ", rgb)
                      forecast2 = nowcastRGB(forecast1,xy1_px,xy2_px)
                  
                      #get coordinates of points that are nan before interpolation (are not in xy anymore because they went outside or come from outside)
                      if rgb_num == 0: #only need to do it once, same for all channels!!
                          xy_levels = add_points_outside(forecast2,x_matrixs,y_matrixs, xy2)
                          
                      forecast2 = fill_with_closest_pixel(forecast2)
                      forecasts_NextStep[channel_nr[rgb],level,:,:] = forecast2
                      
                      if t*ForecastTime == dt_forecast1 or t*ForecastTime == dt_forecast2:
                          if t*ForecastTime == dt_forecast1:
                              ind_time = 0
                              
                          else:
                              ind_time = 1
                          
                          #forecasts_out[channel_nr[rgb],ind_time,np.where(forecast2!=no_data)] = forecast2[np.where(forecast2!=no_data)]
                          temp = deepcopy(forecasts_out[channel_nr[rgb],ind_time,:,:])
                          temp [forecast2!=no_data] = forecast2[forecast2!=no_data]
                          forecasts_out[channel_nr[rgb],ind_time,:,:] = deepcopy(temp) #np.where(forecast2!=no_data,forecast2,forecasts_out)
                          if level == (n_levels-1):
                            
                            forecasts_out[channel_nr[rgb],ind_time,forecasts_out[channel_nr[rgb],ind_time,:,:]==no_data] = np.nan
                            forecasts_out[channel_nr[rgb],ind_time,:,:] = ma.masked_invalid(forecasts_out[channel_nr[rgb],ind_time,:,:])

                            # in_msg.datetime.strftime( outputDir )
                            outputFile = outputDir +"/"+ "%s_%s_%s_t%s.p" % (yearS+monthS+dayS,hourS+minS,rgb,str(t*ForecastTime))
                            #outputFile = "/opt/users/lel/PyTroll/scripts/channels/%s_%s_%s_t%s.p" % (yearS+monthS+dayS,hourS+minS,rgb,str(t*ForecastTime))
                            
                            print("... pickle data to file: ", outputFile)
                            
                            PIK = []
                            if area == "ccs4":
                                    PIK.append( forecasts_out[channel_nr[rgb],ind_time,:,:])
                            elif area == "ccs4c2": 
                                    PIK.append( forecasts_out[channel_nr[rgb],ind_time,20:nx-40,85:ny-135])
                            else:
                                    print("unknown area, saving entire domain")
                                    PIK.append( forecasts_out[channel_nr[rgb],ind_time,:,:])
                                
                            PIK.append(mode_downscaling)
                            print("mode_downscaling: ", mode_downscaling)
                            path = dirname(outputFile)
                            if not exists(path):
                                if in_msg.verbose:
                                    print('... create output directory: ' + path)
                                makedirs(path)
                            pickle.dump(PIK, open(outputFile,"wb"))
                            
                            plot_fore = forecasts_out[channel_nr[rgb],ind_time,:,:]
                            plot_fore = np.where (plot_fore>0,plot_fore,np.nan)
                            
                            if plot_DisplMeter:
                                fig = plt.figure()
                                plt.imshow(plot_fore) #forecasts_out[channel_nr[rgb],ind_time,:,:]>0)
                                plt.colorbar()
                                if wind_source=="HRW":
                                    plt.title("%s, %s, New Velocity every step,\n Displacement in Meters, (HRW %s min):\n t0 + %s"%(rgb,method,ntimes*5,str(t*ForecastTime)))
                                else:
                                    plt.title("%s, %s, New Velocity every step,\n Displacement in Meters, (cosmo):\n t0 + %s"%(rgb,method,str(t*ForecastTime)))
                                if wind_source=="HRW":
                                    name_to_save = "HRW%smin"%(ntimes*5)
                                elif zlevel == "pressure":
                                    name_to_save = "cosmoPL"
                                elif zlevel == "modellevel":
                                    name_to_save = "cosmoPL"
                                else:
                                    name_to_save = "cosmoML"
                                
                                time_string = "%02d" % (t*ForecastTime)    
                                outputFig = "/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/channels_fig//%s_%s_t%s_%s_DisplMeter_%s.png"%(rgb,yearS+dayS+hourS+minS,time_string,method,name_to_save) #time_string,
                                fig.savefig(outputFig) 
                                plt.close(fig)
      
          print("TOTAL TIME: ", time.time()-time_start_TOT)
          
          in_msg.datetime = in_msg.datetime + timedelta(minutes=5)

