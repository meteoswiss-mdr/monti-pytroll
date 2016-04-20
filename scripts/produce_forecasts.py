""" NEW VERSION:
        - ONE: improved interpolation method (dealing with no_data interpolation)
        - TWO: option to use Runge Kutta/odeint to interpolate velocity field instead of Euler x=x0+vdt (using function particles_displacement)
        - THREE: implemented option to not always derive forecast from observation at t0 but from previous forecast
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
from plot_msg import create_PIL_image, add_border_and_rivers, add_title
from pycoast import ContourWriterAGG
from my_msg_module import format_name, fill_with_closest_pixel
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


import scp_settings
scpOutputDir = scp_settings.scpOutputDir
scpID = scp_settings.scpID 

# debug_on()


def read_HRW(sat, sat_nr, instrument, time_slot, ntimes, dt=5, read_basic_or_detailed='detailed', 
             min_correlation=85, min_conf_nwp=80, min_conf_no_nwp=80, cloud_type=None, level=None, p_limits=None):

    #print time_slot
    data = GeostationaryFactory.create_scene(sat, sat_nr, instrument, time_slot)
    data.load(['HRW'], reader_level="seviri-level5", read_basic_or_detailed=read_basic_or_detailed)

    # read data for previous time steps if needed
    for it in range(1,ntimes):
        time_slot_i = time_slot - timedelta( minutes = it*5 )
        data_i = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot_i)
        data_i.load(['HRW'], reader_level="seviri-level5", read_basic_or_detailed=read_basic_or_detailed)
        # merge all datasets
        data['HRW'].HRW_detailed = data['HRW'].HRW_detailed + data_i['HRW'].HRW_detailed
        data['HRW'].HRW_basic    = data['HRW'].HRW_basic    + data_i['HRW'].HRW_basic

    # apply quality filter
    data['HRW'].HRW_detailed = data['HRW'].HRW_detailed.filter(min_correlation=min_correlation, \
                    min_conf_nwp=min_conf_nwp, min_conf_no_nwp=min_conf_no_nwp, cloud_type=cloud_type, level=level, p_limits=p_limits)

    return data

# ------------------------------------------

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

def interpolate_cosmo(year, month, day, hour, minute, layers, zlevel='pressure', area='ccs4'):

    hour_run=hour//3 * 3
    if hour-hour_run<2:
        hour_run=hour_run-3
        if hour_run<0:
            day=day-1
            hour_run=24+hour_run
    if hour-hour_run>0:
        hour_forecast=hour-hour_run
    else:
        hour_forecast=hour+24-hour_run
    
    yearS = str(year)
    monthS = "%02d" % month
    dayS   = "%02d" % day
    hourS  = "%02d" % hour
    minS   = "%02d" % minute    
    
    hour_runS  = "%02d" % hour_run
    hour_forecastS  = "%02d" % hour_forecast
    hour_forecast_nextS = "%02d" % (hour_forecast+1)
    
    if area=='ccs4c2' or area=='ccs4':
        areaS = '_'+area
    else:
        areaS = ''

    if zlevel=='pressure':
        zlevelS=''
    elif zlevel=='model':
        zlevelS='_ML'
    else:
        print "*** Error in interpolate_cosmo (functionWSFN.py)"
        print "    unknown zlevel: ", zlevel
        quit()
        
    cosmoDir='/data/COALITION2/database/cosmo2/'

    file_cosmo_1 = (cosmoDir+'/%s_lm_fine'+areaS+zlevelS+'/%s_%s_cosmo2_UV'+areaS+zlevelS+'.nc') % (yearS+monthS+dayS,yearS+monthS+dayS+hour_runS,hour_forecastS)        
    file_cosmo_2 = (cosmoDir+'/%s_lm_fine'+areaS+zlevelS+'/%s_%s_cosmo2_UV'+areaS+zlevelS+'.nc') % (yearS+monthS+dayS,yearS+monthS+dayS+hour_runS,hour_forecast_nextS)        
    
    print '... read ', file_cosmo_1
    print '... read ', file_cosmo_2
    
    nc_cosmo_1 = netCDF4.Dataset(file_cosmo_1,'r',format='NETCDF4') 
    nc_cosmo_2 = netCDF4.Dataset(file_cosmo_2,'r',format='NETCDF4') 
    
    pressure1 = nc_cosmo_1.variables['z_1'][:]
    pressure1 = pressure1.astype(int)
    
    pressure2 = nc_cosmo_2.variables['z_1'][:]
    pressure2 = pressure2.astype(int)    
    
    print pressure1
    print pressure2

    u_all1 = nc_cosmo_1.variables['U'][:] 
    v_all1 = nc_cosmo_1.variables['V'][:]
    u_all2 = nc_cosmo_2.variables['U'][:] 
    v_all2 = nc_cosmo_2.variables['V'][:]
 
    
    nx = u_all1.shape[2]
    ny = u_all1.shape[3]


    
    p_chosen=np.sort(layers)[::-1]
    print '... p_chosen: ', p_chosen, layers

    u_d=np.zeros((len(p_chosen),nx,ny))
    v_d=np.zeros((len(p_chosen),nx,ny))

    position_t = minute/5
    previous   = 1-(1./12*position_t)
    
    for g in range(len(p_chosen)):
        print g, len(p_chosen), np.where(pressure1==p_chosen[g])[0][0]
        u1 = u_all1[0,np.where(pressure1==p_chosen[g])[0][0],:,:]
        u2 = u_all2[0,np.where(pressure1==p_chosen[g])[0][0],:,:]
        v1 = v_all1[0,np.where(pressure2==p_chosen[g])[0][0],:,:]
        v2 = u_all1[0,np.where(pressure2==p_chosen[g])[0][0],:,:]
        u_d[g,:,:] = previous*u1 + (1-previous)*u2
        v_d[g,:,:] = previous*v1 + (1-previous)*v2      

    print "*** u_d[0].shape", u_d.shape[1], u_d.shape[2]

    return u_d, v_d
    

def calculate_displacement(u_d,v_d,n_levels,size_x,size_y,ForecastTime,NumComputationSteps):


    print "***"
    print "*** calculate displacement"

    dx_d = np.zeros(u_d.shape)
    dy_d = np.zeros(v_d.shape)

    for level in range(n_levels):   # !!!!!!!
    #for level in [0]:

          print "... calculate displacement for level ", level
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

def load_rgb(satellite, satellite_nr, satellites_name, time_slot, rgb, area, in_msg,data_CTP):
    if rgb != 'CTP':
      # read the data we would like to forecast
      global_data_RGBforecast = GeostationaryFactory.create_scene(satellite, satellite_nr, satellites_name, time_slot)
      #global_data_RGBforecast = GeostationaryFactory.create_scene(in_msg.sat, str(10), "seviri", time_slot)

      # area we would like to read
      area_loaded = get_area_def("EuropeCanary95")#(in_windshift.areaExtraction)  
      # load product, global_data is changed in this step!
      area_loaded = load_products(global_data_RGBforecast, [rgb], in_msg, area_loaded)
      print '... project data to desired area ', area
      fns = global_data_RGBforecast.project(area)

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
    data[data.mask==True ] = no_data
    data = np.where(np.logical_or(data_CTP['CTP'].data>=p_max,data_CTP['CTP'].data<p_min),no_data,data)
    
    return data
# ------------------------------------------

#def wind_shiftFun(in_windshift):
if __name__ == '__main__':
    # input 
    
    time_start_TOT = time.time()
    detailed = True 

    area="ccs4c2" #"#"ccs4" #in_windshift.ObjArea

    title_color=(255,255,255)
    #layer=''
    layer=' 2nd layer'
    #layer='3rd layer'
    add_rivers=False
    add_borders=False
    legend=True

    ntimes=2 #in_windshift.ntimes
    print "... aggregate winddata for ", ntimes, " timesteps" 
    min_correlation = 85 #in_windshift.min_correlation
    min_conf_nwp = 80 #in_windshift.min_conf_nwp
    min_conf_no_nwp = 80 #in_windshift.min_conf_no_nwp
    cloud_type = [5,6,7,8,9,10,11,12,13,14] #in_windshift.cloud_type


    delta_t = 5 #in_windshift.ForecastTime
    delay = 0

    # satellite for HRW winds
    sat_nr = "08" #in_windshift.sat_nr

    plot_DisplMeter = True
    
    
    rgbs = ['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134']  #in_windshift.rgb
    rgbs_only15min = ['IR_039','IR_087','IR_120']
    #channel = rgb.replace("c","")

    # load a few standard things 
    from get_input_msg import get_input_msg
    in_msg = get_input_msg('input_template')
    in_msg.resolution = 'i'
    in_msg.sat_nr = 9
    in_msg.add_title=False
    in_msg.outputDir='./pics/'
    in_msg.outputFile='WS_%(rgb)s-%(area)s_%y%m%d%H%M'
    in_msg.fill_value = [0,0,0] # black
    #in_msg.fill_value = None    # transparent
    #colormap='rainbow'
    colormap='greys'

    NumForecast=6 #number of forecasts you want to produce from observation at t=0
    ForecastTime=5 #time in minutes from observation at t=0 when you want each observation (first forecast after ForecastTime, second after 2*ForecastTime...)
    NumComputationSteps=1 #number of computation time steps: the number of steps when the velocity should be updated within each ForecastTime
    
    
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
            layers=[800,500,300]#[700,500,300]#[900,800,700,600,500,400,300,200,100] #[700,500,300]#[100] # [400,300,100]#[600,300,100]##pressure layers 
        elif zlevel == 'modellevel':
            layers=[36,24,16] #cosmo model layers
        else:
            print "*** Error in main (functionWSFN.py)"
            print "    unknown zlevel", zlevel
            quit()
        
    # ------------------------------------------

    # possible High Resolution wind images
    HRWimages = ['channel','pressure','correlation','conf_nwp','conf_no_nwp']
    # alternatively also possible is the plot of 'stream' lines 

    ############################################################################

    ############################################################################
    
    if len(sys.argv) > 1:
        if len(sys.argv) < 6:
            print "***           "
            print "*** Warning, please specify date and time completely, e.g."
            print "***          python plot_radar.py 2014 07 23 16 10 "
            print "***           "
            quit() # quit at this point
        else:
            year   = int(sys.argv[1])
            month  = int(sys.argv[2])
            day    = int(sys.argv[3])
            hour   = int(sys.argv[4])
            minute = int(sys.argv[5])
            time_slot = datetime(year, month, day, hour, minute)
            
            if len(sys.argv) > 6:
                yearSTOP   = int(sys.argv[6])
                monthSTOP  = int(sys.argv[7])
                daySTOP    = int(sys.argv[8])
                hourSTOP   = int(sys.argv[9])
                minuteSTOP = int(sys.argv[10])
                time_slotSTOP = datetime(yearSTOP, monthSTOP, daySTOP, hourSTOP, minuteSTOP) 
            else:
                time_slotSTOP = time_slot 
    else:
        if True:  # automatic choise of last 5min 
            from my_msg_module import get_last_SEVIRI_date
            datetime1 = get_last_SEVIRI_date(True)
            if delay != 0:
                datetime1 -= timedelta(minutes=delay)
            year  = datetime1.year
            month = datetime1.month
            day   = datetime1.day
            hour  = datetime1.hour
            minute = datetime1.minute
        else: # fixed date for text reasons
            year=2014          # 2014 09 15 21 35
            month= 7           # 2014 07 23 18 30
            day= 23
            hour= 18
            minute=00
    
    
    
    
    while time_slot <= time_slotSTOP:
    
          print time_slot
          year = time_slot.year
          month = time_slot.month
          day = time_slot.day
          hour = time_slot.hour
          minute = time_slot.minute
                    
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
              
          # define area
          proj4_string = obj_area.proj4_string            
          # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
          area_extent = obj_area.area_extent              
          # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
          area_tuple = (proj4_string, area_extent)
      
          # read CTP to distinguish high, medium and low clouds
          global_data_CTP = GeostationaryFactory.create_scene(in_msg.sat, str(in_msg.sat_nr).zfill(2), "seviri", time_slot)
          #global_data_CTP = GeostationaryFactory.create_scene(in_msg.sat, str(10), "seviri", time_slot)
          area_loaded = get_area_def("EuropeCanary95")  #(in_windshift.areaExtraction)  
          area_loaded = load_products(global_data_CTP, ['CTP'], in_msg, area_loaded)
          data_CTP = global_data_CTP.project(area)
              
          [nx,ny]=data_CTP['CTP'].data.shape


          # read all rgbs
          global_data = GeostationaryFactory.create_scene(in_msg.sat, str(in_msg.sat_nr).zfill(2), "seviri", time_slot)
          #global_data_CTP = GeostationaryFactory.create_scene(in_msg.sat, str(10), "seviri", time_slot)
          area_loaded = get_area_def("EuropeCanary95")  #(in_windshift.areaExtraction)  
          area_loaded = load_products(global_data, rgbs, in_msg, area_loaded)
          data = global_data.project(area)


      
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
      
                  hrw_data = read_HRW("meteosat", sat_nr, "seviri", time_slot, ntimes, \
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
              u_d, v_d = interpolate_cosmo(year,month,day,hour,minute,layers,zlevel,area)
          else:
              print "*** Error in main (functionWSFN.py)"
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
                      if t*ForecastTime > 15:
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
                      
                      if t*ForecastTime == 15 or t*ForecastTime == 30:
                          if t*ForecastTime == 15:
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
                          if level == (n_levels-1):
                            
                            forecasts_out[channel_nr[rgb],ind_time,forecasts_out[channel_nr[rgb],ind_time,:,:]==no_data] = np.nan
                            forecasts_out[channel_nr[rgb],ind_time,:,:] = ma.masked_invalid(forecasts_out[channel_nr[rgb],ind_time,:,:])
                            #outputFile = "/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/channels/%s_%s_%s_t%s.p" % (yearS+monthS+dayS,hourS+minS,rgb,str(t*ForecastTime))
                            outputFile = "/opt/users/lel/PyTroll/scripts/channels/%s_%s_%s_t%s.p" % (yearS+monthS+dayS,hourS+minS,rgb,str(t*ForecastTime))
                            
                            
                            print "... pickle data to file: ", outputFile
                            if area == "ccs4":
                                pickle.dump( forecasts_out[channel_nr[rgb],ind_time,:,:], open(outputFile, "wb" ) )
                            else: 
                                pickle.dump( forecasts_out[channel_nr[rgb],ind_time,20:nx-40,85:ny-135], open(outputFile, "wb" ) )
                            
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
      
          print "TOTAL TIME: ", time.time()-time_start_TOT
          
          time_slot = time_slot + timedelta(minutes=5)

