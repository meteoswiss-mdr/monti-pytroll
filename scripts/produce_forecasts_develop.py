""" 30.06.2016 copied from "produce_forecasts_nrt.py"
which was operational on SatLive
"""

from datetime import datetime
import sys, string, os
import logging
sys.path.insert(0, "/home/lom/users/cll/pytroll/install/lib/python2.6/site-packages")
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from mpop.utils import debug_on
from pyresample import plot
import numpy as np
from pydecorate import DecoratorAGG
import aggdraw
from PIL import ImageFont, ImageDraw
from os.path import exists
from os import makedirs
from mpop.imageo.HRWimage import HRW_2dfield # , HRWstreamplot, HRWimage
from datetime import timedelta
from plot_msg import create_PIL_image, add_borders_and_rivers, add_title
from pycoast import ContourWriterAGG
from my_msg_module import check_near_real_time, format_name, fill_with_closest_pixel
from copy import deepcopy 
from my_msg_module import convert_NWCSAF_to_radiance_format, get_NWC_pge_name
from mpop.imageo.palettes import convert_palette2colormap
from plot_msg import load_products
import matplotlib.pyplot as plt
import time
import copy
from particles_displacement import particles_displacement
import numpy.ma as ma
import netCDF4
import pickle
from scipy import ndimage
from my_msg_module import check_input
from Cells import Cells
import imp

import scp_settings
scpOutputDir = scp_settings.scpOutputDir 
scpID = scp_settings.scpID 
import glob
import inspect

from pycoast import ContourWriterAGG

# debug_on()

import trollimage


def read_HRW(sat, sat_nr, instrument, time_slot, ntimes, dt=5, read_basic_or_detailed='detailed', 
             min_correlation=85, min_conf_nwp=80, min_conf_no_nwp=80, cloud_type=None, level=None, p_limits=None):
      
    """ Reads the High Resolution Wind (Nowcasting Saf) .

    Parameters
    ----------
    sat : satellite (string e.g. 'Meteosat') 
    sat_nr : satellite number (string e.g. '09')
    instrument : satellite instrument (string e.g. 'seviri')
    time_slot : datetime object
        the time of interest for which the extraction is wanted
    ntimes : int           
        number of dt timesteps before time_slot considered for the derivation of the wind vectors
    dt : int
        number of minutes in one timestep
    read_basic_or_detailed : "basic" or "detailed"
        ???
    min_correlation : int (0:100)
        correlation minimum required for a vector to be included
    min_conf_nwp : int(0,100)          
        min confidence for a vector to be included with NWP
    min_conf_no_nwp : int (0:100)
        min confidence for a vector to be included without NWP
    cloud_type : list of int
        the cloud types included 
    level : "seviri-levelX"          
        reader level
    p_limits : int in hPa          
        pressure limits for the vectors
    
    Returns : 
    ----------
    data : wind vectors extracted for given settings
        

    Raises
    ----------
         """

    #print time_slot
    data = GeostationaryFactory.create_scene(sat, sat_nr, instrument,  time_slot)
    data.load(['HRW'], reader_level="seviri-level5", read_basic_or_detailed=read_basic_or_detailed)
  
    # read data for previous time steps if needed
    for it in range(1,ntimes):
        time_slot_i = time_slot - timedelta( minutes = it*5 )
        data_i = GeostationaryFactory.create_scene(in_msg.sat_str(), in_msg.sat_nr_str(), "seviri", time_slot_i)
        data_i.load(['HRW'], reader_level="seviri-level5", read_basic_or_detailed=read_basic_or_detailed)
        # merge all datasets (addition of datasets defined in class HRW_class, see mpop/mpop/satin/nwcsaf_hrw_hdf.py)
        data['HRW'].HRW_detailed = data['HRW'].HRW_detailed + data_i['HRW'].HRW_detailed
        data['HRW'].HRW_basic    = data['HRW'].HRW_basic    + data_i['HRW'].HRW_basic
  
    # apply quality filter
    data['HRW'].HRW_detailed = data['HRW'].HRW_detailed.filter(min_correlation=min_correlation, \
                    min_conf_nwp=min_conf_nwp, min_conf_no_nwp=min_conf_no_nwp, cloud_type=cloud_type, level=level, p_limits=p_limits)
  
    return data

# ------------------------------------------

def m_to_pixel(value, size, conversion): #,coordinate):
    
    """ Converts coordinates from meters to pixels.

    Parameters
    ----------
    value : sequence
        coordinate to convert (in px or m)
    size : int
        number corresponding to the meter in one satellite pixel
    conversion : "to_pixel" or other
        conversion to apply, either px to m or viceversa

    Returns
    ----------
    m or px : number
        coordinate converted into meter or px

    Raises
    ----------
    """
         
    if conversion=='to_pixel':
        px =  np.round(value//size) 
        px[np.where(value==np.nan)] = np.nan
        px = px.astype(int)
        return px
    else:
        m = (value*size)+size/2
        m[value==np.nan] = np.nan
        return m

def string_date(t):
    
    """ Compute the product of a sequence of numbers.

    Parameters
    ----------
    t : datetime object
        datetime to convert in string

    Returns
    ----------
    yearS, monthS, dayS, hourS, minS : strings
        string corresponding to year, month, day, hour and minute.
        month, day, hour, minute all have 2 characters (with leading 0 if necessary).

    Raises
    ----------
    """

    yearS  = str(t.year)
    monthS = "%02d" % t.month
    dayS   = "%02d" % t.day
    hourS  = "%02d" % t.hour
    minS   = "%02d" % t.minute

    return yearS, monthS, dayS, hourS, minS

def check_cosmo_area (nc_cosmo, area):
    
    """ Compares the cosmo area with the wanted area and provides coordinates corners.
    
    Parameters
    ----------
    nc_cosmo : netcdf object, wind data cosmo
        example: netCDF4.Dataset(file_cosmo_1,'r',format='NETCDF4')
        netcdf must contain:
        - the coordinates (x_1, y_1)
    area : str
        string representing one of the areas present in area_def 
    
    Returns
    ----------
    x_min_cut, x_max_cut, y_min_cut, y_max_cut : int
        coordinates of the edges of the wanted area withing the cosmo area
    
    Raises
    ----------
    stops execution if:
        - area wanted is larger than the cosmo area
        - size of cosmo px in m is different from size of wanted area px in m
    """

    #reads the x and y coordinates from the netcdf cosmo file
    x = nc_cosmo.variables['y_1'][:]
    y = nc_cosmo.variables['x_1'][:]
    
    #obtains the coordinates corner pixels (+-500 because cosmo coordinates center of cell)
    # !!! !hau! improve this: does assume fixed pixel size of 1000m !!!  
    x_min_cosmo = x.min()-500
    x_max_cosmo = x.max()+500
    y_min_cosmo = y.min()-500
    y_max_cosmo = y.max()+500
    
    #gets the area definition and the coordinates of its corner pixels
    area_wanted = get_area_def(area)
    x_min_wanted = area_wanted.area_extent[1]
    x_max_wanted = area_wanted.area_extent[3]
    y_min_wanted = area_wanted.area_extent[0]
    y_max_wanted = area_wanted.area_extent[2]
    
    #obtains the pixel size of cosmo
    x = np.sort(x)
    dx_cosmo = x[1]-x[0]
    y = np.sort(y)
    dy_cosmo = y[1]-y[0]       
    
    #checks if the pixel size of the cosmo model and the wanted area match, if not quits
    if dy_cosmo != area_wanted.pixel_size_y or dx_cosmo != area_wanted.pixel_size_x:
        print "Error: the pixel size of the wind data doesn't match with the chosen area definition"
        quit()
    
    #checks if the area wanted is smaller or equal to the cosmo area, if not it quits
    if x_min_cosmo <= x_min_wanted and x_max_cosmo >= x_max_wanted and y_min_cosmo <= y_min_wanted and y_max_cosmo >= y_max_wanted:
        x_min_cut = abs(x_min_cosmo - x_min_wanted)/1000
        x_max_cut = abs(x_max_cosmo - x_max_wanted)/1000
        y_min_cut = abs(y_min_cosmo - y_min_wanted)/1000
        y_max_cut = abs(y_max_cosmo - y_max_wanted)/1000
    else:
        print "Error: the area chosen ("+area+") is larger than the wind data (cosmo) area available"
        quit()
 
    return x_min_cut, x_max_cut, y_min_cut, y_max_cut

def get_cosmo_filenames (t_sat, nrt=True, runs_before=0, area = "ccs4c2" ):
    
    """ Provides the cosmo filename.
    
    Parameters
    ----------
    t_sat : datetime object
        time for which the cosmo data is wanted (usually same as satellite images)
    nrt: boolean
        True if the system is run real time, false else (depending on realtime or not it will look for the
        cosmo data in different paths, and look for different cosmo models 
    runs_before: int
        It starts looking for the run runs_before*3hours earlier than t_sat (useful if latest run not yet available)
        
    Returns
    ----------
    cosmoDir+cosmo_file1, cosmoDir+cosmo_file2 : str (paths)
        returns the string corresponding to the paths where the two cosmo files are stored (the hour before and after t_sat)
    
    Raises
    ----------
    """
    
    # get COSMO model start time (assuming COSMO start each 3h, 0,3,6,9...UTC)
    hour_run = t_sat.hour //3 * 3 
    t_run = datetime(t_sat.year, t_sat.month, t_sat.day, hour_run, 0)

    # if runs_before is set to a value >0, it subtracts 3*runs_before hours to t_run
    if runs_before != 0:
        print "    try ", runs_before ," model start(s) before "
        t_run -= runs_before * timedelta(hours = 3) 

    # gets the forecasting time corresponding to the t_sat, given the t_run (hour before and hour after)
    dt = t_sat - t_run
    hour_forecast1 = "%02d" % int (dt.total_seconds() // 3600) # using integer devision, changed from / to // so it is Python 3 compatible
    hour_forecast2 = "%02d" % int (dt.total_seconds() // 3600 +1)  # using integer devision 

    yearS, monthS, dayS, hourS, minS = string_date(t_run)

    # sets model and path depending on offline or online version
    if nrt:          
        cosmo = "cosmo-1"
        cosmoDir='/data/cinesat/in/cosmo/' #2016052515_05_cosmo-1_UV_swissXXL
    elif t_sat.year < 2016:
        cosmo = "cosmo2"
        cosmoDir='/data/COALITION2/database/cosmo/test_wind/'+yearS+monthS+dayS+"_"+cosmo+"_"+area+"/" 
           #20150515_cosmo2_ccs4c2 / 2015051506_00_cosmo2_UVccs4c2.nc or 2015070706_00_cosmo2_UV_ccs4c2.nc
    else:
        cosmo = "cosmo-1"
        cosmoDir='/data/COALITION2/database/cosmo/wind/'+yearS+"/"+monthS+"/"+dayS+"/"
        
    cosmo_file1 = yearS+monthS+dayS+hourS+"_"+hour_forecast1+"_"+cosmo+"_UV*.nc"
    cosmo_file2 = yearS+monthS+dayS+hourS+"_"+hour_forecast2+"_"+cosmo+"_UV*.nc"

    return cosmoDir+cosmo_file1, cosmoDir+cosmo_file2

def interpolate_cosmo(year, month, day, hour, minute, layers, zlevel='pressure', area='ccs4', cosmo = None, nrt = False, rapid_scan_mode_satellite = True):
    
    """ Calculate linearly interpolated wind fields for a specific time of interest 
    
    Parameters
    ----------
    year, month, day, hour, minute : int
        year, month, day, hour, minute for which the cosmo wind is wanted wanted
    layers: list of int
        Pressure/model levels at which the cosmo wind is wanted
    zlevel : 'pressure' or 'model' !!!!!!!!!! for the moment only implemented 'pressure'
        It starts looking for the run runs_before*3hours earlier than t_sat (useful if latest run not yet available)
    area: str
        area identifier of the area over which the cosmo wind is wanted    
    cosmo : str
        identifier of the cosmo model wanted
    nrt: boolean
        True if the system is run real time, false else (depending on realtime or not, it will look for the
        cosmo data in different paths, and look for different cosmo models
    rapid_scan_mode_satellite: boolean
        True if the satellite is in rapid scan mode (scans every 5 minutes) and False else (every 15 minutes)
    
    Returns
    ----------
    u_d, v_d : dict
        dictionaries containing the u and v cosmo wind components. !!!!! THE ORDER OF THE PRESSURE IS OPPOSITE OF THOSE IN INPUT: u_d[0,:,:] corresponds to the last pressure in the input "layers"
    
    Raises
    ----------
    """
    #print "WARNING: the output wind levels will be in order opposite to that in the input 'layers' "

    # rough rule, if latest COSMO run is already available
    if nrt == False and hour % 3 == 0 :  # !!! !hau! this suggest to use 3 and 4h forecast, instead of Analysis and 1h forecast. Should it be like this?
        runs_before = 1
    else:
        runs_before = 0

    file1, file2 = get_cosmo_filenames ( datetime(year,month,day,hour,minute), nrt=nrt, runs_before = runs_before, area = area  )

    print "... search for ", file1, " and ", file2
    filename1 = glob.glob(file1)
    filename2 = glob.glob(file2)

    if len(filename1)>1 or len(filename2)>1:
        print "Warning, more than one cosmo file available!!"
        print "Files t1", filename1
        print "Files t2", filename2
            
    if len(filename1)<1 or len(filename2)<1:
        print "*** Warning, found no cosmo wind data "
        # look for the result of the COSMO run before
        file1, file2 = get_cosmo_filenames ( datetime(year,month,day,hour,minute),nrt = nrt, runs_before = runs_before + 1, area = area )

        print "... search for preveous COSMO run: ", file1, " and ", file2
        filename1 = glob.glob(file1)
        filename2 = glob.glob(file2)
        
        if len(filename1)>1 or len(filename2)>1:
            print "Warning, more than one cosmo file available!!"
            print "Files t1", filename1
            print "Files t2", filename2
        elif len(filename1)<1 or len(filename2)<1:
            print "*** Error, no cosmo wind data with model start " #, str(datetime(year,month,day,hour,minute))
            print file1
            print file2
            quit()
    
    file_cosmo_1 = filename1[0]
    file_cosmo_2 = filename2[0]
    
    #cosmoDir='/data/cinesat/in/cosmo' #2016052400_03_cosmo-1_UV_swissXXL.nc

    print '... read ', file_cosmo_1  
    print '... read ', file_cosmo_2
    
    nc_cosmo_1 = netCDF4.Dataset(file_cosmo_1,'r',format='NETCDF4') 
    nc_cosmo_2 = netCDF4.Dataset(file_cosmo_2,'r',format='NETCDF4') 
    
    pressure1 = nc_cosmo_1.variables['z_1'][:]
    pressure1 = pressure1.astype(int)
    
    pressure2 = nc_cosmo_2.variables['z_1'][:]
    pressure2 = pressure2.astype(int)    
    
    print "    pressure levels in file1: ", pressure1
    print "    pressure levels in file2: ", pressure2
    
    print "    pressures chosen: ", layers
    u_all1 = nc_cosmo_1.variables['U'][:]
    v_all1 = nc_cosmo_1.variables['V'][:]
    u_all2 = nc_cosmo_2.variables['U'][:]
    v_all2 = nc_cosmo_2.variables['V'][:]

    nx1 = u_all1.shape[2]
    ny1 = u_all1.shape[3] 
    
    nx2 = u_all2.shape[2]
    ny2 = u_all2.shape[3]
    
    # check if data in COSMO file covers the whole area of interest
    x_min_cut1, x_max_cut1, y_min_cut1, y_max_cut1 = check_cosmo_area (nc_cosmo_1, area)
    x_min_cut2, x_max_cut2, y_min_cut2, y_max_cut2 = check_cosmo_area (nc_cosmo_2, area) 
    
    if len(layers)>1:
        p_chosen = np.sort(layers)[::-1]
        print "layers ", layers
        print "p_chosen ", p_chosen
        #quit()
    else:
        p_chosen = layers
    #if nrt:
    #    p_chosen *= 100 # 100 == convert hPa to Pa
        
    u_d = np.zeros((len(p_chosen),nx1,ny1))
    v_d = np.zeros((len(p_chosen),nx1,ny1))

    # time it takes to scan the disk
    if rapid_scan_mode_satellite:
        dt = 2
    else:
        dt = 12

    position_t = (minute+dt)/5
    previous   = 1-(1./12*position_t)

    # !!! !hau! this is not nice
    if p_chosen[0] not in pressure1: # pressure1.all() != p_chosen[0]:
        print "no value in: ", pressure1, "is equal to p_chosen: ",p_chosen[0]
        for elem in range(len(p_chosen)):
            p_chosen[elem]*=100   # convert hPa to Pa
    
    for g in range(len(p_chosen)):
        #print "    interpolate wind for ", p_chosen[g]
        #print np.where(pressure1==p_chosen[g])
        #print pressure1
        # search index, where the pressure is equal to the pressure of interest (might be different for file1 and file2)
        i1 = np.where(pressure1==p_chosen[g])[0][0]
        i2 = np.where(pressure2==p_chosen[g])[0][0]
        print "... temporal interpolation for wind field at", p_chosen[g]
        print g, len(p_chosen), np.where(pressure1==p_chosen[g])[0][0]
        u1 = u_all1[0, i1, x_max_cut1 : nx1-x_min_cut1, y_min_cut1 : ny1 - y_max_cut1] 
        u2 = u_all2[0, i2, x_max_cut2 : nx2-x_min_cut2, y_min_cut2 : ny2 - y_max_cut2]     #### UH index changed i1 -> i2 !!! ###
        v1 = v_all1[0, i1, x_max_cut1 : nx1-x_min_cut1, y_min_cut1 : ny1 - y_max_cut1]     #### UH index changed i2 -> i1 !!! ###
        v2 = v_all2[0, i2, x_max_cut2 : nx2-x_min_cut2, y_min_cut2 : ny2 - y_max_cut2]
        u_d[g,:,:] = previous*u1 + (1-previous)*u2
        v_d[g,:,:] = previous*v1 + (1-previous)*v2      

    print "*** u_d[0].shape", u_d.shape[1], u_d.shape[2]
    print "previous ", previous
    return u_d, v_d, p_chosen
    

def calculate_displacement(u_d,v_d,n_levels,size_x,size_y,ForecastTime,NumComputationSteps):


    print "***"
    print "*** calculate displacement"

    dx_d = np.zeros(u_d.shape)
    dy_d = np.zeros(v_d.shape)

    for level in range(n_levels):   # !!!!!!!
    #for level in [0]:

          print "... calculate displacement for level ", level, n_levels
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
    print "*** add new particles for empty pixels"
    #store tracking coordinates for next step of this level
    print "xy2.shape, xy_new.shape", xy2.shape, xy_new.shape
    xy_new = np.vstack((xy2, xy_new))
    print "... number of particles for next step (xy_new.shape)", xy_new.shape
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

def load_rgb(satellite, satellite_nr, satellites_name, time_slot, rgb, area, in_msg, data_CTP):

    if rgb != 'CTP':
      # read the data we would like to forecast
      global_data_RGBforecast = GeostationaryFactory.create_scene(in_msg.sat_str(),in_msg.sat_nr_str(), "seviri",  time_slot)
      #global_data_RGBforecast = GeostationaryFactory.create_scene(in_msg.sat, str(10), "seviri", time_slot)

      # area we would like to read
      area_loaded = get_area_def("EuropeCanary95")#(in_windshift.areaExtraction)  
      # load product, global_data is changed in this step!
      area_loaded = load_products(global_data_RGBforecast, [rgb], in_msg, area_loaded)
      print '... project data to desired area ', area
      fns = global_data_RGBforecast.project(area, precompute=True)

    else:
      fns = deepcopy(data_CTP["CTP"].data)  
    
    return fns[rgb].data

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
    
    print '... calculate new particle positions'
    
    xy2 = np.zeros(xy1.shape)
    xy2[:,0] = xy1[:,0] + dx_ds[level, xy1_px[:,0], xy1_px[:,1] ]
    xy2[:,1] = xy1[:,1] + dy_ds[level, xy1_px[:,0], xy1_px[:,1] ]
    
    # remove particles outside the domain 
    print "... limits before removing: ", xy2.min(), xy2.max(),  


    ind_inside = np.where( np.logical_and( np.logical_and(0<=xy2[:,0],xy2[:,0]<max_x_m), np.logical_and(0<=xy2[:,1],xy2[:,1]<max_y_m) ) )
    print type(ind_inside)
    print np.array(ind_inside).max(), np.array(ind_inside).min()
    print np.array(ind_inside).shape

    xy2    = np.squeeze(xy2[ind_inside,:])
    xy1_px = np.squeeze(xy1_px[ind_inside,:])
    
    print "... limits after removing: ", xy2.min(), xy2.max(),  
    print "... number of particles after removing those outside (xy2_px.shape)", xy2.shape
    
    #convert xy2 in pixel to do the shift for each channel
    xy2_px = np.zeros(xy2.shape, dtype=np.int)   ### initialize as integer ###
    xy2_px[:,0] = m_to_pixel(xy2[:,0],size_x,'to_pixel')
    xy2_px[:,1] = m_to_pixel(xy2[:,1],size_y,'to_pixel')            
    
    return (xy1_px, xy2_px, xy2)

def mask_rgb_based_pressure(data,p_min,p_max,data_CTP):
    ####################################data[data.mask==True ] = no_data
    data = np.where(np.logical_or(data_CTP['CTP'].data>=p_max,data_CTP['CTP'].data<p_min),no_data,data)
    
    return data


########################################################################################## 
########################################################################################## 
def print_usage():
         print "***           "
         print "*** Error, not enough command line arguments"
         print "***        please specify at least an input file"
         print "***        possible calls are:"
         print "*** python "+inspect.getfile(inspect.currentframe())+" input_coalition2 "
         print "*** python "+inspect.getfile(inspect.currentframe())+" input_coalition2 2014 07 23 16 10 "
         print "                                 date and time must be completely given"
         print "***           "
         quit() # quit at this point
#----------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    time_start_TOT = time.time()
    detailed = True 

    from get_input_msg import get_date_and_inputfile_from_commandline
    in_msg = get_date_and_inputfile_from_commandline(print_usage=print_usage)

    print in_msg.dt_forecast1
    print in_msg.dt_forecast2

    if len(sys.argv) > 7:
        if len(sys.argv) <12:
            print_usage()
        else:
            yearSTOP   = int(sys.argv[7])
            monthSTOP  = int(sys.argv[8])
            daySTOP    = int(sys.argv[9])
            hourSTOP   = int(sys.argv[10])
            minuteSTOP = int(sys.argv[11])
            time_slotSTOP = datetime(yearSTOP, monthSTOP, daySTOP, hourSTOP, minuteSTOP) 
    else:
        time_slotSTOP = in_msg.datetime 

    time_slot = in_msg.datetime

    print "" 
    print "*** define more input parameters" 

    area = in_msg.area_forecast
 
    ntimes=2 #in_windshift.ntimes
    print "... aggregate winddata for ", ntimes, " timesteps" 
    min_correlation = 85 #in_windshift.min_correlation
    min_conf_nwp = 80 #in_windshift.min_conf_nwp
    min_conf_no_nwp = 80 #in_windshift.min_conf_no_nwp
    cloud_type = [5,6,7,8,9,10,11,12,13,14] #in_windshift.cloud_type

    delay = 5

    rgbs = ['CTT'] #['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134','CTT']  #in_windshift.rgb
    # in_msg.nwcsaf_calibrate = True

    rgbs_only15min = ['IR_039','IR_087','IR_120']
    #channel = rgb.replace("c","")
    name_tmp = "3layer"
    # load a few standard things 
    #from get_input_msg import get_input_msg
    #in_msg = get_input_msg('input_coalition2')
    in_msg.resolution = 'i'

    #in_msg.fill_value = None    # transparent
    #colormap='rainbow' 
    colormap='greys'

    rapid_scan_mode = in_msg.forecasts_in_rapid_scan_mode
        
    dt_forecast1 = in_msg.dt_forecast1
    dt_forecast2 = in_msg.dt_forecast2
        
    if rapid_scan_mode == True:
        print "... RAPID SCAN MODE"
    else:
        print "... NOT RAPID SCAN MODE"
    
    dt_forecast1S = "%02d" % dt_forecast1
    dt_forecast2S = "%02d" % dt_forecast2
    
    ForecastTime        = 5                 #time in minutes from observation at t=0 when you want each observation (first forecast after ForecastTime, second after 2*ForecastTime...)
    NumComputationSteps = 1                 #number of computation time steps: the number of steps when the velocity should be updated within each ForecastTime
    NumForecast = dt_forecast2/ForecastTime #number of forecasts you want to produce from observation at t=0

    
    mode_downscaling = in_msg.settingsLocal['mode_downscaling']

    if mode_downscaling != 'no_downscaling':
        downscaling_data = True
    else:
        downscaling_data = False
    method=in_msg.integration_method_velocity 

    pressure_limits = in_msg.pressure_limits
    n_levels=len(pressure_limits)+1
    
    wind_source = in_msg.wind_source
    zlevel = in_msg.zlevel

    if wind_source=="cosmo":
        if zlevel == 'pressure':
            #layers= [800,500,300]#[700,500,300]#[900,800,700,600,500,400,300,200,100] #[700,500,300]#[100] # [400,300,100]#[600,300,100]##pressure layers 
            layers= [800,700,600]
        elif zlevel == 'modellevel':
            layers=[36,24,16] #cosmo model layers
        else:
            print "*** Error in main ("+inspect.getfile(inspect.currentframe())+")"
            print "    unknown zlevel", zlevel
            quit()
        
    # ------------------------------------------
      
    outDir_completed = 0
    
    in_msg.mapDir = "/opt/users/common/shapes/"
    cw = ContourWriterAGG(in_msg.mapDir)
    # define area
    obj_area = get_area_def("ccs4")
    proj4_string = obj_area.proj4_string            
    # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
    area_extent = obj_area.area_extent              
    # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
    area_tuple = (proj4_string, area_extent)    

    print "in_msg.nwcsaf_calibrate ", in_msg.nwcsaf_calibrate

    print "" 
    print "*** start production of forecasts" 


    while time_slot <= time_slotSTOP:

          print "process "+str(time_slot)

          outputDir = time_slot.strftime(in_msg.outputDirForecasts)
                  
          in_msg.datetime = time_slot
          
          if False:
              if type(in_msg.sat_nr) is int:
                  if in_msg.sat[0:8]=="meteosat":
                      sat_nr_str = str(in_msg.sat_nr).zfill(2)
                  elif in_msg.sat[0:8]=="Meteosat":
                      sat_nr_str = str(in_msg.sat_nr)
              elif type(in_msg.sat_nr) is str:
                  sat_nr_str = in_msg.sat_nr
                  if in_msg.sat[0:8]=="Meteosat":
                      sat_nr_str = str(int(sat_nr_str)) # get rid of leading zeros (0) 
              else:
                  print "*** Waring, unknown type of sat_nr", type(in_msg.sat_nr)
                  sat_nr_str = in_msg.sat_nr
          #print in_msg.sat, " and ", sat_nr_str
          #in_msg.sat_nr_str = sat_nr_str
          year   = time_slot.year
          month  = time_slot.month
          day    = time_slot.day
          hour   = time_slot.hour
          minute = time_slot.minute
                    
          yearS  = str(year)
          #yearS = yearS[2:]
          monthS = "%02d" % month
          dayS   = "%02d" % day
          hourS  = "%02d" % hour
          minS   = "%02d" % minute
          dateS  = yearS+'-'+monthS+'-'+dayS
          timeS  = hourS+':'+minS+" UTC"
          
          # define area object 
          obj_area = get_area_def(area)#(in_windshift.ObjArea)
          size_x = obj_area.pixel_size_x
          size_y = obj_area.pixel_size_y  
          
          #print obj_area
          print "area extent:\n", obj_area.area_extent
          print "x min  ",        obj_area.area_extent[0]
          print "x size ",        obj_area.pixel_size_x
          
          # check if input data is complete 
          if in_msg.verbose:
              print "*** check input data", in_msg.RGBs
          #RGBs = check_input(in_msg, in_msg.sat+sat_nr_str, in_msg.datetime)  
          # in_msg.sat_nr might be changed to backup satellite
          
          for i_try in range(30):
              # check if 'CTH' file is present
              RGBs = check_input(in_msg, in_msg.sat_str()+in_msg.sat_nr_str(), in_msg.datetime, RGBs=in_msg.RGBs)
              if len(RGBs) > 0:
                  # exit loop, if input is found
                  break
              else:
                  # else wait 20s and try again
                  import time
                  time.sleep(25)
          
          for i_try in range(30):
              # check if 'CTH' file is present
              RGBs = check_input(in_msg, in_msg.sat_str()+in_msg.sat_nr_str(), in_msg.datetime, RGBs="CTP")
              if len(RGBs) > 0:
                  # exit loop, if input is found
                  break
              else:
                  # else wait 20s and try again
                  import time
                  time.sleep(25)          
          
          # read CTP to distinguish high, medium and low clouds
          print ("*** read data for ", in_msg.sat_str(), in_msg.sat_nr_str(), "seviri", time_slot)
          global_data_CTP = GeostationaryFactory.create_scene(in_msg.sat_str(),in_msg.sat_nr_str(), "seviri", time_slot)
          #global_data_CTP = GeostationaryFactory.create_scene(in_msg.sat, str(10), "seviri", time_slot)
          #area_loaded = get_area_def("EuropeCanary95")  #(in_windshift.areaExtraction)  
          area_loaded = load_products(global_data_CTP, ['CTP'], in_msg, get_area_def("ccs4"))
          data_CTP = global_data_CTP.project(area, precompute=True)
              
          [nx,ny]=data_CTP['CTP'].data.shape
          
          if 'pressure_levels' in in_msg.aux_results:
                tmp_press = deepcopy(in_msg.pressure_limits)
                tmp_press.append(1001)
                tmp_press.sort() #ordered decreasing
                
                print tmp_press
                n_levels_pressure = len(tmp_press)
                p_levels = np.zeros(data_CTP['CTP'].data.shape)
                p_levels[:,:]=np.nan
                p_min = 0

                print("    n_levels_pressure (should be 3): ", n_levels_pressure)
                print "    unique pressure levels: ",np.unique(p_levels)

                for i_plot_press in range(n_levels_pressure):
                    p_max = tmp_press[i_plot_press]
                    print("    p_min: ", p_min, "p_max: ",p_max)
                    p_levels[np.where(np.logical_and(data_CTP['CTP'].data>p_min,data_CTP['CTP'].data<=p_max))] = i_plot_press + 2
                    print "    unique: ",np.unique(p_levels)
                    print "    index: ", i_plot_press
                    p_min = deepcopy(p_max)
                if True:
                    fig = plt.figure()
                    plt.imshow(p_levels[20:nx-40,85:ny-135],cmap = plt.get_cmap("Blues"), vmin = 0)
                    plt.axis('off')
                    plt.colorbar()
                    plt.show()
                    plt.savefig("test_Pressure.png")
                    #plt.savefig("/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/channels_fig//PressureLevels_"+yearS+monthS+dayS+hourS+minS+".png")
                    plt.close(fig)
                    quit()
                else:
                    img = trollimage.image.Image(p_levels[20:nx-40,85:ny-135], mode="L", fill_value=None) #fill_value,[1,1,1], None
                    from trollimage.colormap import rdbu
                    #jet.set_range(
                    img.colorize(rdbu)
                    pil_im = img.pil_image()                    
                    
                    #pil_im = array2PIL(p_levels[20:nx-40,85:ny-135], p_levels[20:nx-40,85:ny-135].size)
                    pil_im = add_borders_and_rivers( pil_im, cw, area_tuple,
                                                     add_borders=in_msg.add_borders, border_color=in_msg.border_color,
                                                     add_rivers=in_msg.add_rivers, river_color=in_msg.river_color, 
                                                     resolution=in_msg.resolution, verbose=in_msg.verbose)

                    pil_im.save("test_Pressure.png")#"/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/channels_fig//PressureLevels_"+yearS+monthS+dayS+hourS+minS+".png")
                    quit()
    
                
                fig = plt.figure()
                plt.imshow(data_CTP['CTP'].data[20:nx-40,85:ny-135],cmap = plt.get_cmap("Blues_r"))
                plt.axis('off')
                plt.colorbar()
                plt.show()
                plt.savefig("/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/channels_fig//Pressure_"+yearS+monthS+dayS+hourS+minS+".png")
                plt.close(fig)
                print np.unique(p_levels)
          
          # read all rgbs
          print ("*** read data for ", in_msg.sat_str(),in_msg.sat_nr_str(), "seviri", time_slot)
          global_data = GeostationaryFactory.create_scene(in_msg.sat_str(), in_msg.sat_nr_str(), "seviri",  time_slot)
          #global_data_CTP = GeostationaryFactory.create_scene(in_msg.sat, str(10), "seviri", time_slot)
          area_loaded = get_area_def("EuropeCanary95")  #(in_windshift.areaExtraction)  
          area_loaded = load_products(global_data, rgbs, in_msg, area_loaded)
          data = global_data.project(area, precompute=True)
          
          if 'forecast_channels' in in_msg.aux_results:
              for rgb_plot in rgbs:
                  fig = plt.figure()
                  plt.imshow(data[rgb_plot].data[20:nx-40,85:ny-135], vmin=220, vmax=290) #forecasts_out[channel_nr[rgb],ind_time,:,:]>0)
                  plt.axis('off')
                  plt.colorbar()
                  plt.show()
                  plt.savefig("/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/channels_fig//"+rgb_plot+"_"+yearS+monthS+dayS+hourS+minS+"_Obs.png")
                  plt.close(fig)
          
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
               from plot_coalition2 import downscale  
               if "CTT" in rgbs:
                    mask_Safe = deepcopy(data['CTT'].data.mask)
               elif "CTP" in rgbs:
                    mask_Safe = deepcopy(data['CTP'].data.mask)
               else:
                    mask_Safe = deepcopy(data[rgbs[0]].data.mask)
               data = downscale(deepcopy(data), mode = mode_downscaling, mask = mask_Safe)
                         
          if 'forecast_channels' in in_msg.aux_results:
              for rgb_plot in rgbs:
                  fig = plt.figure()
                  plt.imshow(data[rgb_plot].data[20:nx-40,85:ny-135],vmin = 220, vmax = 290) #forecasts_out[channel_nr[rgb],ind_time,:,:]>0)
                  plt.axis('off')
                  plt.colorbar()
                  plt.show()
                  plt.savefig("/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/channels_fig//"+rgb_plot+"_"+yearS+monthS+dayS+hourS+minS+"_ObsDownscaled.png")
                  plt.close(fig)
          
          
          print "" 
          print "*** read wind fields"  
          
          if wind_source=="HRW":
              u_d=np.zeros((n_levels,nx,ny))
              v_d=np.zeros((n_levels,nx,ny))
              for level in range(n_levels):
                  p_max=p_min
                  if level==n_levels-1:
                      p_min=0
                  else:
                      p_min=pressure_limits[len(pressure_limits)-1-level]  
      
                  hrw_data = read_HRW(in_msg.sat_str(), in_msg.sat_nr_str(), "seviri", time_slot, ntimes, \
                                       min_correlation=min_correlation, min_conf_nwp=min_conf_nwp, \
                                       min_conf_no_nwp=min_conf_no_nwp, cloud_type=cloud_type, p_limits=[p_min,p_max])
      
      
                     # choose basic or detailed (and get a fresh copy) 
                  if detailed:
                      print '... calculate gridded 2d wind field High' 
                      hrw_detbas = hrw_data['HRW'].HRW_detailed                   
                  else:
                      print '... calculate gridded 2d wind field High' 
                      hrw_detbas =  hrw_data['HRW'].HRW_basic       
      
                  u_d[level,:,:], v_d[level,:,:] = HRW_2dfield( hrw_detbas, obj_area )
      
          elif wind_source=="cosmo":
              u_d, v_d, pressures_wind = interpolate_cosmo(year, month, day, hour, minute,
                                                layers, zlevel, area, nrt=in_msg.nrt, rapid_scan_mode_satellite = True)
          else:
              print "*** Error in main ("+inspect.getfile(inspect.currentframe())+")"
              print "    unknown wind source ", wind_source
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
          print "nx ",nx
          print "ny "
          forecasts_out = np.zeros((len(channel_nr),2,nx,ny))
          forecasts_NextStep = np.zeros((len(channel_nr),n_levels,nx,ny))
          
          max_x_m = nx*size_x
          max_y_m = ny*size_y
          
       
          for level in range(n_levels):
          
              print "... calculation for level ", level
      
              p_max = p_min
              
              if level==n_levels-1:
                  p_min = 0
              else:
                  p_min = pressure_limits[len(pressure_limits)-1-level]              
              
              if p_min == p_max:
                continue
              
              if pressures_wind[level] > p_max or pressures_wind[level] < p_min:
                    print "ERROR: you are moving the clouds at a certain level (%s-%s) with wind from another level (%s)"%(str(p_min),str(p_max),str(pressures_wind[level]))
                    quit()
              
              u = u_d[level,:,:]
              v = v_d[level,:,:]  
      
              for t in range(1,NumForecast+1):
                  print "*** timestep ",t," of ",NumForecast
                  if t==1: #if first timestep create x and y matrices covering entire image
                      xy_levels = initial_xy(x_matrixs,y_matrixs)
      
                  xy1 = deepcopy(xy_levels) #xy_levels[level,:,:] #take the initial coordinates from array storage (step before)
                  
                  (xy1_px, xy2_px, xy2) = compute_new_xy (xy1, dx_ds, dy_ds,  max_x_m, max_y_m)
                  
                  
                  for rgb_num in range(len(rgbs)):
                      rgb=rgbs[rgb_num]
                      if t==1:
                          forecasts_NextStep[channel_nr[rgb],level,:,:] = mask_rgb_based_pressure(data[rgb].data,p_min,p_max, data_CTP)
                      
                      #check if for current channel (rgb) you also need the 30 min forecast
                      if t*ForecastTime > dt_forecast1:
                          if any(rgb in s for s in rgbs_only15min):
                              continue
                      
                      forecast1 = forecasts_NextStep[channel_nr[rgb],level,:,:]
                      print "*** calculating the nowcasted values of ", rgb
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
                          print "forecast 2: ",forecast2.shape
                          print "forecast out: ",forecasts_out.shape
                          
                          #forecasts_out[channel_nr[rgb],ind_time,np.where(forecast2!=no_data)] = forecast2[np.where(forecast2!=no_data)]
                          temp = deepcopy(forecasts_out[channel_nr[rgb],ind_time,:,:])
                          temp [forecast2!=no_data] = forecast2[forecast2!=no_data]
                          print "temp ",temp.shape
                          forecasts_out[channel_nr[rgb],ind_time,:,:] = deepcopy(temp) #np.where(forecast2!=no_data,forecast2,forecasts_out)
                          if level == (n_levels-1) or p_min == 0:
                            
                            forecasts_out[channel_nr[rgb],ind_time,forecasts_out[channel_nr[rgb],ind_time,:,:]==no_data] = np.nan
                            forecasts_out[channel_nr[rgb],ind_time,:,:] = ma.masked_invalid(forecasts_out[channel_nr[rgb],ind_time,:,:])

                            # time_slot.strftime( outputDir )
                            if not in_msg.nrt and outDir_completed == 0:
                                outputDir = outputDir+"/"+ yearS+"-"+monthS+"-"+dayS+"/channels/"
                                outDir_completed = 1

                            outputFile = outputDir +"/"+ "%s_%s_%s_t%s.p" % (yearS+monthS+dayS,hourS+minS,rgb,str(t*ForecastTime))
                            #outputFile = "/opt/users/lel/PyTroll/scripts/channels/%s_%s_%s_t%s.p" % (yearS+monthS+dayS,hourS+minS,rgb,str(t*ForecastTime))
                            #####outputFile = "pickles/%s_%s_%s_t%s_%s.p" % (yearS+monthS+dayS,hourS+minS,rgb,str(t*ForecastTime),name_tmp)
                            
                            
                            print "... pickle data to file: ", outputFile
                            
                            PIK = []
                            if area == "ccs4":
                                    PIK.append( forecasts_out[channel_nr[rgb],ind_time,:,:])
                            elif area == "ccs4c2": 
                                    PIK.append( forecasts_out[channel_nr[rgb],ind_time,20:nx-40,85:ny-135])
                            else:
                                    print "unknown area, saving entire domain"
                                    PIK.append( forecasts_out[channel_nr[rgb],ind_time,:,:])
                                
                            PIK.append(mode_downscaling)
                            print mode_downscaling
                            
                            pickle.dump(PIK, open(outputFile,"wb"))
                            
                            plot_fore = forecasts_out[channel_nr[rgb],ind_time,:,:]
                            plot_fore = np.where (plot_fore>0,plot_fore,np.nan)
                            print("makes it before plot")
                            if 'forecast_channels' in in_msg.aux_results:
                                fig = plt.figure()
                                plt.imshow(plot_fore[20:nx-40,85:ny-135],vmin = 220, vmax = 290) #forecasts_out[channel_nr[rgb],ind_time,:,:]>0)
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
                                plt.axis('off')
                                #plt.tick_params(
                                #                axis='both',       # changes apply to both axis
                                #                which='both',      # both major and minor ticks are affected
                                #                bottom='off',      # ticks along the bottom edge are off
                                #                top='off',         # ticks along the top edge are off
                                #                labelbottom='off') # labels along the bottom edge are off
                                time_string = "%02d" % (t*ForecastTime)    
                                ####outputFig = "/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/channels_fig//%s_%s_t%s_%s_DisplMeter_%s.png"%(rgb,yearS+dayS+hourS+minS,time_string,method,name_to_save) #time_string,
                                outputFig = "/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/channels_fig//%s_%s_t%s_%s.png"%(rgb,yearS+dayS+hourS+minS,time_string,name_tmp) #time_string,
                                
                                fig.savefig(outputFig) 
                                plt.close(fig)
      
          print "TOTAL TIME: ", time.time()-time_start_TOT
          print "Final check lead time:", dt_forecast1
          print dt_forecast2
          time_slot = time_slot + timedelta(minutes=5)

