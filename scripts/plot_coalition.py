from __future__ import division
from __future__ import print_function

from datetime import datetime
import sys, string, os
import logging
sys.path.insert(0, "/home/lom/users/cll/pytroll/install/lib/python2.6/site-packages")
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from mpop.utils import debug_on
from pyresample import plot
import numpy as np
import aggdraw
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from os.path import dirname, exists
from os import makedirs
from mpop.imageo.HRWimage import HRW_2dfield # , HRWstreamplot, HRWimage
from datetime import timedelta
from plot_msg import create_PIL_image, add_borders_and_rivers, add_title
from pycoast import ContourWriterAGG
from pydecorate import DecoratorAGG
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
import subprocess

from trollimage.colormap import rainbow
from trollimage.image import Image as trollimage

from skimage import morphology
from scipy import ndimage

# ===============================

def create_dir(outputFile):

    path = dirname(outputFile)
    if not exists(path):
        if in_msg.verbose:
            print('... create output directory: ' + path)
        makedirs(path)
    return outputFile

# ===============================

def force_to_observed_cloud_mask(mod, obs):
    if np.any(mod.mask == True) == False:
        print("NO MASK ACTIVE!!!!!!!!!")
        if np.any(np.isnan(mod)):
            mod = ma.masked_where(np.isnan(mod), mod)
            print("the invalid are NAN")
        else:
            mod = ma.masked_where(mod <= 0, mod)
            print("the invalid are <= 0")
    mod[mod.mask==True] = np.nan
    mod = fill_with_closest_pixel(mod) 
    mod[obs.mask==True] = np.nan
    mod.mask = obs.mask

    #no_data = -10
    #
    #force observed mask on forecast
    #mod[obs.mask==True] = no_data 
    #print (type(mod), type(obs))
    #
    #mod[mod.mask==True] = np.nan
    #mod = fill_with_closest_pixel(mod)    
    #
    #mod[mod==no_data] = np.nan
    #mod.mask = obs.mask

    return mod

# ===============================


#def wind_shiftFun(in_windshift):
if __name__ == '__main__':
    # input 

    detailed = True 

    area = "ccs4" #c2"#"ccs4" #in_windshift.ObjArea

    title_color = (255,255,255)
    #layer = ''
    layer = ' 2nd layer'
    #layer = '3rd layer'
    add_rivers = False
    add_borders = False
    legend = True

    ntimes = 2 #in_windshift.ntimes
    print("... aggregate winddata for ", ntimes, " timesteps") 
    min_correlation = 85 #in_windshift.min_correlation
    min_conf_nwp = 80 #in_windshift.min_conf_nwp
    min_conf_no_nwp = 80 #in_windshift.min_conf_no_nwp
    cloud_type = [5,6,7,8,9,10,11,12,13,14] #in_windshift.cloud_type

    # satellite for HRW winds
    sat_nr = "08" #in_windshift.sat_nr

    channels = ['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134','CTP','CT']
    
    channels15 = ['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134']
    channels30 = ['WV_062','WV_073','IR_097','IR_108','IR_134']

    only_obs_noForecast = True

    plot_tests_glationation      = False
    plot_tests_optical_thickness = False
    plot_tests_updraft           = False
    plot_tests_small_ice         = False

    plot_indicator_optical_thickness = False
    plot_indicator_glationation      = False
    plot_indicator_updraft           = False
    plot_indicator_small_ice         = False

    plot_labelled_objects = False
    plot_final_mask       = False
    plot_forced_mask      = False
    plot_mature_mask      = False
    plot_developing_mask  = False


    # choose color combination
    #rgb_display = 'us-cd-gi'
    rgb_display = 'cd-us-gi'

    # choose saturation enhancement 
    #colour_enhancement_factor = 1   # 1 gives the original colour
    colour_enhancement_factor = 2   # 1 gives the original colour
    # colour_enhancement_factor = 3 # ??? 2 seems to be more colorful than 3 ???

    # choose saturation for each indictor
    cmax_cd =  255   
    cmin_cd =  -80   
    cmax_us =  255
    cmin_us =    0
    cmax_gi =   85  # 140 for 5 tests
    cmin_gi =    0  

    vmin_cd =    [-50.,    -20.,    210.,    -14.,    -32.,    - 3.]
    vmax_cd =    [  0.,      2.,    300.,      3.,      6.,     15.]
    
    th_cd   =    [-16.,    - 7.5,   250.,    - 2.,    -12.5,    2.2]


    vmin_gi =    [- 6.,    - 8.,    - 5.,    - 3.,   - 6.,     -32.,    -10.]
    vmax_gi =    [ 10.,      4.,      8.,      6.,     6.,      32.,      2.]
    
    th_gi   =    [  2.,    - 1.5,    1.5,    - 1.,   - 1.,       0.,    - 1.]


    vmin_us =    [-12.,    -50.,    -60.,    -15.,   - 8.,     -40.,    -40.,    -12.]
    vmax_us =    [ 20.,     50.,     60.,     20.,    10.,      50.,     40.,     12.]
    
    th_us   =    [  2.5,   -12.,    -10.,      2.5,    2.,      13.,     10.,    - 7.]


    # set mask 
    #show_clouds = 'all'
    #show_clouds = 'developing'
    #show_clouds = 'mature'
    show_clouds = 'developing_and_mature'
    

    
    #contour lines identifying objects
    detect_objects = True
    
    # additional test: test to pass for a px to be included in addition to cloud depth, updraft strength and glaciation
    #1#
    forth_mask = 'IR_039_minus_IR_108'
    mature_th_chDiff = 25
    developing_th_chDiff = 8
    #2#
    #forth_mask = 'CloudType'
    #mature_ct = [17,14,12]
    #developing_ct = [8,9,10,17,14,12]
    #3#
    #forth_mask = 'no_mask'
    
    
    if forth_mask == 'IR_039_minus_IR_108':
        name_4Mask = 'IRdiff'
    elif forth_mask == 'CloudType':
        name_4Mask = 'CT'
    elif forth_mask == 'no_mask':
        name_4Mask = 'none'
    else:
        print("*** Error in main (Mecikalski_test.py)")
        print("    unknown 4th mask", forced_mask) 
        quit()        
    
    
    
    # mask that force to include (in mature_mask) any pixel regardless of the other thresholds
    #1#
    #forced_mask = 'IR_039_minus_IR_108'
    #force_th_chDiff = 40
    #2#
    #forced_mask = 'CloudType'
    #cloud_type_forced = [17,14]
    #3#
    forced_mask = 'no_mask'
    
    if forced_mask == 'IR_039_minus_IR_108':
        name_ForcedMask = 'IRdiff'
    elif forced_mask == 'CloudType':
        name_ForcedMask = 'CT'
    elif forced_mask == 'no_mask':
        name_ForcedMask = 'no'
    else:
        print("    unknown forcing mask -> applying no forcing mask", forced_mask) 
        name_ForcedMask = 'no'    
    
    #mask that removed the thin cirrus
    mask_cirrus      = True
    plot_mask_cirrus = False
    th_cirrus        = 4
    
    #additional filter that removes small holes within clouds (max_holes = max number of px to fill with clouds) and small clouds (min_cloud = number px minimum to keep a cloud)
    clean_mask = 'skimage'
    #clean_mask = 'scipy'
    #clean_mask = 'both'
    #clean_mask = 'no_cleaning'
    min_cloud = 100
    max_holes = 500

    # backgroundcolor 
    background_color = [255,255,255]   # white
    background_color = [  0,  0,  0]   # black

    # foregroud and background opacity (== 1 - transparency)
    #foregroud_alpha  = 200      # pretty opaque
    foregroud_alpha  = 255      # opaque
    background_alpha =   0      # transparent
    #background_alpha = 255     # opaque

    # specify result plots
    plot_RGB             = True
    plot_RGB_HRV         = True

    # load a few standard things 
    from get_input_msg import get_input_msg
    in_msg = get_input_msg('input_template')
    in_msg.resolution = 'i'
    in_msg.sat_nr = 9
    in_msg.add_title = False
    in_msg.outputDir = './pics/'
    in_msg.outputFile = 'WS_%(rgb)s-%(area)s_%y%m%d%H%M'
    in_msg.fill_value = [0,0,0] # black
    #in_msg.reader_level = "seviri-level4"
    #in_msg.fill_value = None    # transparent
    #colormap = 'rainbow'
    colormap = 'greys'
    delay = 5
    
    if len(sys.argv) > 1:
        if len(sys.argv) < 6:
            print("***           ")
            print("*** Warning, please specify date and time completely, e.g.")
            print("***          python plot_radar.py 2014 07 23 16 10 ")
            print("***           ")
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
        if False:  # automatic choise of last 5min 
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
            year   = 2015          # 2014 09 15 21 35
            month  =  7           # 2014 07 23 18 30
            day    =  7
            hour   = 13
            minute = 00

    while time_slot <= time_slotSTOP:
    
          print(time_slot)
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
      
          nowcastDir="/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/channels/" #/opt/users/lel/PyTroll/scripts/channels_new//" #"2
      
          time_slot15 = time_slot - timedelta(minutes=15)
          
          time_slot30 = time_slot - timedelta(minutes=30)
      
          hour_forecast15S = "%02d" % (time_slot15.hour)
          min_forecast15S = "%02d" % (time_slot15.minute)
      
          hour_forecast30S = "%02d" % (time_slot30.hour)
          min_forecast30S = "%02d" % (time_slot30.minute)    
      
                
          # read data for the current time
          time_slot = datetime(year, month, day, hour, minute)
      
          # define area object 
          obj_area = get_area_def(area)#(in_windshift.ObjArea)
      
          # define area
          proj4_string = obj_area.proj4_string            
          # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
          area_extent = obj_area.area_extent              
          # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
          area_tuple = (proj4_string, area_extent)
          
          print(in_msg.sat, str(in_msg.sat_nr).zfill(2), "seviri", time_slot)
          
          # now read the data we would like to forecast
          global_data = GeostationaryFactory.create_scene(in_msg.sat, str(in_msg.sat_nr).zfill(2), "seviri", time_slot)
          #global_data_RGBforecast = GeostationaryFactory.create_scene(in_msg.sat, str(10), "seviri", time_slot)
      
          # area we would like to read
          area_loaded = get_area_def("EuropeCanary95")#(in_windshift.areaExtraction)  
      
          # load product, global_data is changed in this step!
          area_loaded = load_products(global_data, channels, in_msg, area_loaded)
          
      
          print('... project data to desired area ', area)
          
          data = global_data.project(area)
      
          # properly mask the CTP 
          data['CTP'].data = ma.masked_less(data['CTP'].data, 0)
          
          nx,ny = data['CTP'].data.shape
          
          if False:
              fig = plt.figure()
              plt.imshow(data['CT'].data)
              plt.colorbar()
              fig.savefig("Cloud_type.png")
              plt.close(fig)
          
          
          print("mask ", sum(sum(data['CTP'].data.mask)))
          print(data['CTP'].data.shape)
          print(data['CTP'].data.size)
          
          #out_dir = "/data/COALITION2/PicturesSatellite//LEL_results_wind/"+yearS+"-"+monthS+"-"+dayS+"/"
          #out_dir = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/Mecikalski2/"
          out_dir = "/opt/users/lel/PyTroll/scripts//Mecikalski/"
      
          if only_obs_noForecast == True:
              
              # now read the observations of the channels at -15 min
              
              global_data15 = GeostationaryFactory.create_scene(in_msg.sat, str(in_msg.sat_nr).zfill(2), "seviri", time_slot15)
              # area we would like to read
              area_loaded = get_area_def("EuropeCanary95")#(in_windshift.areaExtraction)  
              # load product, global_data is changed in this step!
              area_loaded = load_products(global_data15, channels15, in_msg, area_loaded)
              data15 = global_data15.project(area)              
              
              
              # now read the observations of the channels at -30 min
              
              global_data30 = GeostationaryFactory.create_scene(in_msg.sat, str(in_msg.sat_nr).zfill(2), "seviri", time_slot30)
              # area we would like to read
              area_loaded = get_area_def("EuropeCanary95")#(in_windshift.areaExtraction)  
              # load product, global_data is changed in this step!
              area_loaded = load_products(global_data30, channels30, in_msg, area_loaded)
              data30 = global_data30.project(area)           
              
              wv_062_t15 = deepcopy(data15['WV_062'])
              wv_062_t30 = deepcopy(data30['WV_062'])
                      
              wv_073_t15 = deepcopy(data15['WV_073'])
              wv_073_t30 = deepcopy(data30['WV_073'])            
          
              ir_097_t15 = deepcopy(data15['IR_097'])
              ir_097_t30 = deepcopy(data30['IR_097']) 
          
              ir_108_t15 = deepcopy(data15['IR_108'])
              ir_108_t30 = deepcopy(data30['IR_108']) 
          
              ir_134_t15 = deepcopy(data15['IR_134'])
              ir_134_t30 = deepcopy(data30['IR_134']) 
          
              ir_087_t15 = deepcopy(data15['IR_087'])
              
              ir_120_t15 = deepcopy(data15['IR_120'])
              
              ir_039_t15 = deepcopy(data15['IR_039'])
              
              
          else:
                                                             
              wv_062_t15 = pickle.load( open( nowcastDir+"%s_%s_WV_062_t15.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S), "rb" ) )
              wv_062_t30 = pickle.load( open( nowcastDir+"%s_%s_WV_062_t30.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S), "rb" ) )
                      
              wv_073_t15 = pickle.load( open( nowcastDir+"%s_%s_WV_073_t15.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S), "rb" ) )
              wv_073_t30 = pickle.load( open( nowcastDir+"%s_%s_WV_073_t30.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S), "rb" ) )            
          
              ir_097_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_097_t15.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S), "rb" ) )
              ir_097_t30 = pickle.load( open( nowcastDir+"%s_%s_IR_097_t30.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S), "rb" ) ) 
          
              ir_108_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_108_t15.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S), "rb" ) )
              ir_108_t30 = pickle.load( open( nowcastDir+"%s_%s_IR_108_t30.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S), "rb" ) ) 
          
              ir_134_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_134_t15.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S), "rb" ) )
              ir_134_t30 = pickle.load( open( nowcastDir+"%s_%s_IR_134_t30.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S), "rb" ) ) 
          
              ir_087_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_087_t15.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S), "rb" ) )
              
              ir_120_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_120_t15.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S), "rb" ) )
              
              ir_039_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_039_t15.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S), "rb" ) )
      
      
     
          # create a mask where CTP can be derived 
          # -------------------
      
          #print (type(data['CTP'].data))
          #mask_CTP = np.where(data['CTP'].data > 0.0)
          mask_CTP = data['CTP'].data.mask
          #if True:
          #      mask1 = deepcopy(data['CTP'].data)
          #      mask_CTP = np.zeros(mask1.shape)
          #      mask_CTP[mask1>0] = 1
          #else:
          #      mask_CTP = pickle.load( open( "mask_obs%s.p"%(yearS+monthS+dayS+hours+minS),"rb") )   
          #print (mask_CTP)   
      
          ir_120_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_120_t15), data['CTP'].data)
      
          wv_062_t15 = force_to_observed_cloud_mask(ma.masked_array(wv_062_t15), data['CTP'].data) #ma.masked_where(a <= 2, a)
      
          wv_062_t30 = force_to_observed_cloud_mask(ma.masked_array(wv_062_t30), data['CTP'].data)
                                                              
          wv_073_t15 = force_to_observed_cloud_mask(ma.masked_array(wv_073_t15), data['CTP'].data)
          wv_073_t30 = force_to_observed_cloud_mask(ma.masked_array(wv_073_t30), data['CTP'].data)
                                                              
          ir_097_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_097_t15), data['CTP'].data)
          ir_097_t30 = force_to_observed_cloud_mask(ma.masked_array(ir_097_t30), data['CTP'].data)
                                                              
          ir_108_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_108_t15), data['CTP'].data)
          ir_108_t30 = force_to_observed_cloud_mask(ma.masked_array(ir_108_t30), data['CTP'].data)
                                                              
          ir_134_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_134_t15), data['CTP'].data)
          ir_134_t30 = force_to_observed_cloud_mask(ma.masked_array(ir_134_t30), data['CTP'].data)
                                                              
          ir_087_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_087_t15), data['CTP'].data)
                                                              
          ir_120_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_120_t15), data['CTP'].data)
                                                              
          ir_039_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_039_t15), data['CTP'].data)
      
          if False:
              fig = plt.figure()
              plt.imshow(ir_108_t15)
              plt.colorbar()
              fig.savefig(yearS+monthS+dayS+"_"+hour_forecast15S+min_forecast15S+"_"+"ir_108_t15.png")
              plt.close( fig)
    
              fig = plt.figure()
              plt.imshow(ir_108_t30)
              plt.colorbar()
              fig.savefig(yearS+monthS+dayS+"_"+hour_forecast30S+min_forecast30S+"_"+"ir_108_t30.png")
              plt.close( fig)


          cirrus = np.zeros((nx,ny))
              
          # test for CLOUD OPTICAL DEPTH
          # -------------------
          cloud_depth = np.zeros((6,nx,ny))
          cloud_depth[0,:,:] = data['WV_062'].data - data['IR_108'].data
          cloud_depth[1,:,:] = data['WV_062'].data - data['WV_073'].data
          cloud_depth[2,:,:] = deepcopy(data['IR_108'].data)
          cloud_depth[3,:,:] = data['WV_073'].data - data['IR_134'].data
          cloud_depth[4,:,:] = data['WV_062'].data - data['IR_097'].data
          cloud_depth[5,:,:] = data['IR_087'].data - data['IR_120'].data
      
          cd = np.zeros((nx,ny))
          n_tests_cd = 0.
          cd = np.where( cloud_depth[0,:,:] >  th_cd[0], cd+1, cd );   n_tests_cd+=1. # !!! changed from - 16.0
          cd = np.where( cloud_depth[1,:,:] >  th_cd[1], cd+1, cd );   n_tests_cd+=1. # !!! changed from -7.5
          cd = np.where( cloud_depth[2,:,:] <  th_cd[2], cd+1, cd );   n_tests_cd+=1.
          cd = np.where( cloud_depth[3,:,:] >  th_cd[3], cd+1, cd );   n_tests_cd+=1.
          cd = np.where( cloud_depth[4,:,:] >  th_cd[4], cd+1, cd );   n_tests_cd+=1.
          #cd = np.where( cloud_depth[5,:,:] <  th_cd[5], cd+1, cd );   n_tests_cd+=1. # !!! changed DEACTIVATED
          
          cirrus = np.where( cloud_depth[5,:,:]           >  th_cirrus ,cirrus +1, cirrus)
          
          cd = np.where(mask_CTP == True, 0, cd)
      
          #cd = np.where( mask_CTP==1,0,cd)
      
          if plot_tests_optical_thickness:
              for i in range( 0,cloud_depth.shape[0]):
                
                    item = cloud_depth[i,:,:]
                    #item.data[mask_CTP==0] = np.nan
                    item[data['CTP'].data.mask == True ] = np.nan
                    fig = plt.figure()
                    plt.imshow( item, vmin = vmin_cd[i], vmax = vmax_cd[i])
                    plt.colorbar()
                    plt.contour( item, [th_cd[i]], linewidths=1, origin='lower' )  # , [0.0], colors='r'
                    plt.title( "Cloud_depth%s"%(str(i+1)) )
                    outputFile = out_dir +"/cosmo/Channels/indicators_in_time/all_indicators/%s_%s_Cloud_depth%s.png"%(yearS+monthS+dayS,hourS+minS,str(i+1))
                    fig.savefig( create_dir(outputFile) ) 
                    plt.close( fig)
                    print("... display ", outputFile, " &") 
              item = cloud_depth[5,:,:]
              #item.data[mask_CTP==0] = np.nan
              item[data['CTP'].data.mask == True ] = np.nan
              fig = plt.figure()
              plt.imshow( item, vmin = vmin_cd[5], vmax = vmax_cd[5])
              plt.colorbar()
              plt.contour( item, [th_cirrus], linewidths=1, origin='lower' )  # , [0.0], colors='r'
              plt.title( "Cloud_depth%s"%(str(i+1)) )
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/all_indicators/%s_%s_Cloud_depth%s_cirrus.png"%(yearS+monthS+dayS,hourS+minS,str(i+1))
              fig.savefig( create_dir(outputFile) ) 
              plt.close( fig)
              print("... display ", outputFile, " &")               
          if plot_indicator_optical_thickness:
              fig = plt.figure()
              plt.imshow( cd, vmin=0, vmax=5)
              plt.colorbar( )
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/CloudDepthTH/%s_%s_Cloud_Depth.png"%(yearS+monthS+dayS,hourS+minS)
              fig.savefig( create_dir(outputFile) )  
              plt.close(fig)  
      
      
          # test for GLACIATION 
          # -------------------
          glaciation_indicators = np.zeros( (7,nx,ny))
          trispectral     = (data['IR_087'].data-data['IR_108'].data) - (data['IR_108'].data-data['IR_120'].data)
          trispectral_t15 = (ir_087_t15         -ir_108_t15)          - (ir_108_t15         -ir_120_t15)
          glaciation_indicators[0,:,:] =  trispectral         - trispectral_t15
          glaciation_indicators[1,:,:] =  deepcopy(trispectral)
          glaciation_indicators[2,:,:] = (data['IR_087'].data - data['IR_108'].data)-(ir_087_t15-ir_108_t15)
          glaciation_indicators[3,:,:] =  data['IR_087'].data - data['IR_108'].data
          glaciation_indicators[4,:,:] = (data['IR_120'].data - data['IR_108'].data)-(ir_120_t15-ir_108_t15)
          glaciation_indicators[5,:,:] = (data['IR_039'].data - data['IR_108'].data)-(ir_039_t15-ir_108_t15)
          glaciation_indicators[6,:,:] =  data['IR_120'].data - data['IR_108'].data    
      
          gi = np.zeros( (nx,ny))
          n_tests_gi = 0.
          #gi = np.where( glaciation_indicators[0,:,:] >  th_gi[0], gi+1, gi );   n_tests_gi+=1.
          gi = np.where( glaciation_indicators[1,:,:] >  th_gi[1], gi+1, gi );   n_tests_gi+=1.
          #gi = np.where( glaciation_indicators[2,:,:] >  th_gi[2], gi+1, gi );   n_tests_gi+=1.
          gi = np.where( glaciation_indicators[3,:,:] >  th_gi[3], gi+1, gi );   n_tests_gi+=1.
          #gi= np.where( glaciation_indicators[4,:,:] >  th_gi[4], gi+1, gi );   n_tests_gi+=1.
          #gi= np.where( glaciation_indicators[5,:,:] >  th_gi[5], gi+1, gi );   n_tests_gi+=1.
          gi = np.where( np.logical_or(glaciation_indicators[6,:,:]<-5.0,glaciation_indicators[6,:,:]>-1.5) ,gi+1,gi);   n_tests_gi+=1.
          
          cirrus = np.where( glaciation_indicators[6,:,:] < -5.0 ,cirrus +1, cirrus)
          
          gi = np.where(mask_CTP == True, 0, gi)
          #gi = gi*mask_CTP
          #gi = np.where( mask_CTP==1,0,gi)
      
          if plot_tests_glationation:
              for i in range( 0,glaciation_indicators.shape[0]):
                  item = glaciation_indicators[i,:,:]
                  #item.data[mask_CTP==0] = np.nan
                  item[data['CTP'].data.mask == True ] = np.nan
                  fig = plt.figure()
                  plt.imshow( item, vmin = vmin_gi[i], vmax = vmax_gi[i])
                  plt.colorbar()
                  if i == 6:
                      plt.contour( item, [-5,-1.5], linewidths=1, origin='lower' )  # , [0.0], colors='r'
                  else:
                      plt.contour( item, [th_gi[i]], linewidths=1, origin='lower' )  # , [0.0], colors='r'
                  plt.title( "Glaciation_Indicators%s"%(str(i+1)))
                  outputFile = out_dir +"/cosmo/Channels/indicators_in_time/all_indicators/%s_%s_Glaciation_Indicators%s.png"%(yearS+monthS+dayS,hourS+minS,str(i+1))
                  fig.savefig( create_dir(outputFile) ) 
                  plt.close(fig)
                  print("... display ", outputFile, " &") 
      
          if plot_indicator_glationation:
              fig = plt.figure()
              plt.imshow( gi, vmin=0, vmax=3) # vmax=len( glaciation_indicators))
              plt.colorbar()
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/GlaciationIndicatorTH/%s_%s_Glaciation_indicators.png"%(yearS+monthS+dayS,hourS+minS)
              fig.savefig( create_dir(outputFile) )    
              plt.close(fig)
      



          # test for UPDRAFT STRENGTH 
          # -------------------
          updraft_strength = np.zeros((8,nx,ny))
          updraft_strength[0,:,:] = (data['WV_062'].data - data['WV_073'].data) - (wv_062_t30 - wv_073_t30)
          updraft_strength[1,:,:] =  data['IR_108'].data - ir_108_t15
          updraft_strength[2,:,:] =  data['IR_108'].data - ir_108_t30
          updraft_strength[3,:,:] = (data['WV_062'].data - data['WV_073'].data) - (wv_062_t15 - wv_073_t15)
          updraft_strength[4,:,:] = (data['IR_097'].data - data['IR_134'].data) - (ir_097_t30 - ir_134_t30)
          updraft_strength[5,:,:] = (data['WV_062'].data - data['IR_108'].data) - (wv_062_t30 - ir_108_t30)
          updraft_strength[6,:,:] = (data['WV_062'].data - data['IR_120'].data) - (wv_062_t15 - ir_120_t15)
          updraft_strength[7,:,:] = (data['WV_073'].data - data['IR_097'].data) - (wv_073_t15 - ir_097_t15)
          
          us = np.zeros( (nx,ny)) 
          n_tests_us = 0.
          us = np.where( updraft_strength[0,:,:] > th_us[0], us+1, us );   n_tests_us+=1.
          us = np.where( updraft_strength[1,:,:] > th_us[1], us+1, us );   n_tests_us+=1.
          us = np.where( updraft_strength[2,:,:] < th_us[2], us+1, us );   n_tests_us+=1.
          us = np.where( updraft_strength[3,:,:] > th_us[3], us+1, us );   n_tests_us+=1.
          us = np.where( updraft_strength[4,:,:] > th_us[4], us+1, us );   n_tests_us+=1.
          us = np.where( updraft_strength[5,:,:] > th_us[5], us+1, us );   n_tests_us+=1.
          us = np.where( updraft_strength[6,:,:] > th_us[6], us+1, us );   n_tests_us+=1.
          #us =np.where( updraft_strength[7,:,:] > th_us[7], us+1, us );   n_tests_us+=1.
          
          count_null = np.zeros( (nx,ny))
          count_null = np.where( mask_CTP==1,1,0)
          print(sum( sum( count_null)))
          
          us = np.where(mask_CTP == True, 0, us)
          #us = us*mask_CTP
          #us = np.where( mask_CTP==1,0,us)
          
          if plot_tests_updraft:
              for i in range( updraft_strength.shape[0]):
                  item = updraft_strength[i,:,:]
                  item[data['CTP'].data.mask == True ] = np.nan
                  #item = force_to_observed_cloud_mask(ma.masked_array(item), data['CTP'].data)
                  fig = plt.figure()
                  plt.imshow( item, vmin = vmin_us[i], vmax = vmax_us[i])
                  plt.colorbar()
                  plt.contour( item, [th_us[i]], linewidths=1, origin='lower' )  # , [0.0], colors='r'
                  plt.title( "Updraft_strength%s"%(str(i+1)))
                  outputFile = out_dir +"/cosmo/Channels/indicators_in_time/all_indicators/%s_%s_Updraft_strength%s.png"%(yearS+monthS+dayS,hourS+minS,str(i+1))
                  fig.savefig( create_dir(outputFile)) 
                  plt.close(fig)       
                  print("... display ", outputFile, " &") 
      
          if plot_indicator_updraft:
              fig = plt.figure()
              plt.imshow( us, vmin=0, vmax=7) # vmax=len( updraft_strength))
              plt.colorbar()
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/UpdraftStrengthTH/%s_%s_Updraft_strength.png"%(yearS+monthS+dayS,hourS+minS)
              fig.savefig( create_dir(outputFile) ) 
              plt.close(fig) 
          

      
          # test for SMALL ICE CRYSTALS 
          # -------------------
          IR_039_minus_IR_108 = deepcopy(data['IR_039'].data)-deepcopy(data['IR_108'].data)
          
          if plot_tests_small_ice:
              fig = plt.figure()
              plt.imshow(IR_039_minus_IR_108)
              plt.colorbar()
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/UpdraftStrengthTH/%s_%s_Small_ice.png"%(yearS+monthS+dayS,hourS+minS)
              fig.savefig( create_dir(outputFile)  )
              plt.close(fig)
          
          if plot_indicator_small_ice:
              fig = plt.figure()
              si = np.zeros( (nx,ny)) 
              si = np.where( IR_039_minus_IR_108 >= 28.0, si+1, si )
              plt.imshow( si, vmin=0, vmax=1) # vmax=len( updraft_strength))
              plt.colorbar()
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/SmallIceTH/%s_%s_Small_ice.png"%(yearS+monthS+dayS,hourS+minS)
              fig.savefig( create_dir(outputFile) )  
              plt.close(fig)
      
      
          mature_mask = np.zeros( (nx,ny)) 
          mature_mask[:,:] = -2
          mature_mask = np.where( gi>=2,                     mature_mask+1, mature_mask)
          mature_mask = np.where( cd>=4,                     mature_mask+1, mature_mask)   # !!! changed from 5 to 4 !!! NEW 01/04 changed to 3 because removed one cd indicator
          
          if forth_mask!='no_mask':      
                if forth_mask == 'CloudType':
                    for ct in range(0,len(mature_ct)):
                        cl_typ = mature_ct[ct]
                        mature_mask = np.where(data['CT'].data == cl_typ,mature_mask+1,mature_mask)                
                
                elif forth_mask == 'IR_039_minus_IR_108':
                        mature_mask = np.where( IR_039_minus_IR_108 >= mature_th_chDiff, mature_mask+1, mature_mask)   
                
                mature_mask = np.where( mature_mask==1, 1, 0) # start counting at -2  (so 1 = -2+1+1+1)
          else:
                mature_mask = np.where( mature_mask==0, 1, 0) # start counting at -2  (so 1 = -2+1+1+1)
          
          if plot_mature_mask:
              
              #img = np.where( gi<=2, np.nan, 2)
              #img[cd>=2] = 4 #cd[cd>=2]
              #img[us>=4] = 6 #us[us>=4]]
              fig = plt.figure()
              plt.imshow(mature_mask)
              plt.colorbar()
              plt.title( "Mature mask")
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_"+"4th"+name_4Mask+"_Mature_mask.png"
              fig.savefig( create_dir(outputFile))
              plt.close(fig)           
      
          
          developing_mask = np.zeros( (nx,ny)) 
          developing_mask[:,:] = -2
          developing_mask = np.where( us>=4, developing_mask+1, developing_mask)
          if False:
              fig = plt.figure()
              plt.imshow(developing_mask)
              plt.colorbar()
              plt.title( "Developing mask1")  
              fig.savefig("%s_%s_Developing_mask1.png"%(yearS+monthS+dayS,hourS+minS))
          developing_mask = np.where( cd>=3, developing_mask+1, developing_mask) # !!! NEW 01/04 changed to 3 because removed one cd indicator
          if False:
              plt.close(fig)
              fig = plt.figure()
              plt.imshow(developing_mask)
              plt.colorbar()
              plt.title( "Developing mask2")  
              fig.savefig("%s_%s_Developing_mask2.png"%(yearS+monthS+dayS,hourS+minS))
              plt.close(fig)         
          
          if forth_mask!='no_mask':
              if forth_mask == 'CloudType':
                  ct_devel_mask = np.zeros((nx,ny))
                  for ct in range(0,len(developing_ct)):
                      cl_typ = developing_ct[ct]
                      developing_mask = np.where(data['CT'].data == cl_typ,developing_mask+1,developing_mask)   
                      ct_devel_mask = np.where(data['CT'].data == cl_typ,ct_devel_mask+1,ct_devel_mask)             
              elif forth_mask == 'IR_039_minus_IR_108':
                      developing_mask = np.where( IR_039_minus_IR_108 > developing_th_chDiff,developing_mask+1, developing_mask)
            
              developing_mask = np.where( developing_mask==1, 1, 0 )
          else:
              developing_mask = np.where( developing_mask==0, 1, 0 ) 
           
          if False:
              fig = plt.figure()
              plt.imshow(ct_devel_mask)
              plt.colorbar()
              plt.title( "Developing mask CT")  
              fig.savefig("%s_%s_Developing_mask_CT.png"%(yearS+monthS+dayS,hourS+minS))
              plt.close(fig)            
          if plot_developing_mask:
              
              #img = np.where( gi<=2, np.nan, 2)
              #img[cd>=2] = 4 #cd[cd>=2]
              #img[us>=4] = 6 #us[us>=4]]
              fig = plt.figure()
              plt.imshow(developing_mask)
              plt.colorbar()
              plt.title( "Developing mask")
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_4th"+name_4Mask+"_Developing_mask.png"
              fig.savefig( create_dir(outputFile))
              plt.close(fig)     
              
                        
          cw = ContourWriterAGG( in_msg.mapDir)
      
          print("... create the false color composite (r-g-b) = (", rgb_display,")")

          if rgb_display == 'us-cd-gi':
              r = cmin_us + (us/n_tests_us) * (cmax_us - cmin_us)
              g = cmin_cd + (cd/n_tests_cd) * (cmax_cd - cmin_cd)
              b = cmin_gi + (gi/n_tests_gi) * (cmax_gi - cmin_gi)
          elif rgb_display == 'cd-us-gi':
              r = cmin_cd + (cd/n_tests_cd) * (cmax_cd - cmin_cd) 
              g = cmin_us + (us/n_tests_us) * (cmax_us - cmin_us)
              b = cmin_gi + (gi/n_tests_gi) * (cmax_gi - cmin_gi)
          else: 
              print("*** Error in main (Mecikalski_test.py)")
              print("    unknown rgb illustration", rgb_display)
              quit()

          # fix upper and lower limit of the color, if scaled beyond the range
          r[np.where(r>255)] = 255
          r[np.where(r<  0)] =   0
          g[np.where(g>255)] = 255
          g[np.where(g<  0)] =   0
          b[np.where(b>255)] = 255
          b[np.where(b<  0)] =   0

          

          force_mask = np.zeros((nx,ny))
          
          if forced_mask == 'CloudType':
              for ct in range(0,len(cloud_type_forced)):
                  cl_typ = cloud_type_forced[ct]
                  force_mask = np.where(data['CT'].data == cl_typ,1,force_mask)
          elif forced_mask == 'IR_039_minus_IR_108':  
                  force_mask = np.where(IR_039_minus_IR_108 >= force_th_chDiff,1,0)
          elif forced_mask !='no_mask': 
              print("*** Error in main (Mecikalski_test.py)")
              print("    unknown forcing mask -> applying no forcing mask", forced_mask)     
      
          if plot_forced_mask:
              fig = plt.figure()
              plt.imshow(force_mask)
              plt.title("Forcing mask")
              plt.colorbar()
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_4th"+name_4Mask+"_Forced_mask.png"
              fig.savefig( create_dir(outputFile))
              plt.close(fig)
              
              
          if show_clouds == 'all':
              mask  =  np.ones(wv_062_t15.shape, dtype=bool)
              maskS = '_all'
          elif show_clouds == 'developing':
              mask  = developing_mask
              maskS = '_dev'
          elif show_clouds == 'mature':
              mask  = mature_mask
              maskS = '_mat'
          elif show_clouds == 'developing_and_mature':
              mask  = np.logical_or(mature_mask==1,developing_mask==1)
              maskS = '_dam'
          else:
              print("*** Error in main (Mecikalski.py)")
              print("    unknown show_clouds: ", show_clouds)
              quit()
          
          mask = np.logical_or(mask==1,forced_mask==1)
          
          
          if mask_cirrus:
              cirrus = np.where( cirrus == 2,1,0)
              if plot_mask_cirrus:
                  fig = plt.figure()
                  plt.imshow(cirrus)
                  plt.title("Thin Cirrus mask")
                  plt.colorbar()
                  outputFile = out_dir +"/cosmo/Channels/indicators_in_time/masks/%s_%s_ThinCirrus_mask.png"%(yearS+monthS+dayS,hourS+minS)
                  fig.savefig( create_dir(outputFile))
                  plt.close(fig)
              not_cirrus = np.where(cirrus == 1,0,1)
              mask = np.logical_and(mask,not_cirrus)
              
                    
          if clean_mask == 'skimage':
              if show_clouds != 'all':
                  mask = morphology.remove_small_objects(mask, min_cloud,connectivity=2)
                  mask = morphology.remove_small_objects(-mask, max_holes)
                  mask = deepcopy(-mask)
          elif clean_mask == 'scipy':        
              if show_clouds != 'all':
                  # Remove small white regions
                  mask = ndimage.binary_opening(mask)
                  # Remove small black hole
                  mask = ndimage.binary_closing(mask)  
                  
          elif clean_mask == 'both':
              if show_clouds != 'all':
                  mask = morphology.remove_small_objects(mask, min_cloud,connectivity=2)
                  mask = morphology.remove_small_objects(-mask, max_holes)                            
                  # Remove small white regions
                  mask = ndimage.binary_opening(-mask)
                  # Remove small black hole
                  mask = ndimage.binary_closing(mask) 
          elif clean_mask != 'no_cleaning':
              print("*** Error in main (Mecikalski.py)")
              print("    unknown clean_mask: ", clean_mask)
              quit()          
          
          if plot_final_mask:
              fig = plt.figure()
              plt.imshow(mask)
              plt.title("Final mask")
              plt.colorbar()
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_4th"+name_4Mask+"_"+name_ForcedMask+"AdditionalMask_Final_mask.png"
              fig.savefig( create_dir(outputFile))
              plt.close(fig)

          labels, numobjects = ndimage.label(mask)
          
          pickle.dump( labels, open("labels_"+yearS+monthS+dayS+hourS+minS+".p", "wb" ) )
          
          if plot_labelled_objects:
                fig = plt.figure()
                plt.imshow(labels)
                plt.colorbar()
                outputFile = out_dir +"/cosmo/Channels/indicators_in_time/labelled/"+yearS+monthS+dayS+"_"+hourS+minS+"_4th"+name_4Mask+"_"+name_ForcedMask+"AdditionalMask.png"
                fig.savefig( create_dir(outputFile) ) 
                plt.close(fig)
          
          # copy red, green, blue to the rgbArray and apply mask  
          rgbArray = np.zeros( (nx,ny,4), 'uint8')
          rgbArray[..., 0] = r * mask
          rgbArray[..., 1] = g * mask
          rgbArray[..., 2] = b * mask
          rgbArray[..., 3] = foregroud_alpha
      
          #pickle.dump( mask, open("mask_dam_"+yearS+monthS+dayS+hourS+minS+".p", "wb" ) )
      
      
          # set background_color for "no clouds" 
          sum_array = rgbArray[...,0]+rgbArray[..., 1]+rgbArray[..., 2]
          rgbArray[sum_array<=0,0] = background_color[0] 
          rgbArray[sum_array<=0,1] = background_color[1] 
          rgbArray[sum_array<=0,2] = background_color[2] 
          # set transparency for "no clouds" 
          rgbArray[sum_array<=0,3] = background_alpha
      
          c2File = (out_dir+"/cosmo/Channels/indicators_in_time/RGB"+maskS+"/%s_%s_C2rgb"+maskS+"4th"+name_4Mask+"_"+name_ForcedMask+"AdditionalMask.png") % (yearS+monthS+dayS,hourS+minS)
          if plot_RGB or plot_RGB_HRV:
              img1 = Image.fromarray( rgbArray,'RGBA')
              #add_borders_and_rivers( img1, cw, area_tuple,
              #                        add_borders=in_msg.add_borders, border_color=in_msg.border_color,
              #                        add_rivers=in_msg.add_rivers, river_color=in_msg.river_color, 
              #                        resolution=in_msg.resolution, verbose=in_msg.verbose)
              print("... save image: display ", c2File, " &")
              img1.save( create_dir(c2File) ) 
              
              #pickle.dump( img1, open("RGB"+yearS+monthS+dayS+hourS+minS+".p", "wb" ) )
      
          if plot_RGB_HRV:
              hrvFile = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/"+yearS+"-"+monthS+"-"+dayS+"_HRV_ccs4/MSG_HRV-ccs4_15"+monthS+dayS+hourS+minS+".png" 
              out_file = create_dir( out_dir +"/cosmo/Channels/indicators_in_time/RGB-HRV"+maskS+"/"+yearS+monthS+dayS+"_"+hourS+minS+"_C2rgb-HRV_"+"4th"+name_4Mask+"_"+name_ForcedMask+"AdditionalMask.png" )
      
              print("... create composite "+c2File+" "+hrvFile+" "+out_file)
              subprocess.call("/usr/bin/composite "+c2File+" "+hrvFile+" "+out_file, shell=True)
              print("... saved composite: display ", out_file, " &")
      
          if detect_objects == True:
              
              im = np.array(Image.open(out_file).convert('L'))
              
              xpixels = im.shape[1]
              ypixels = im.shape[0]
              
              dpi = 72
              scalefactor = 1
              
              xinch = xpixels * scalefactor / dpi
              yinch = ypixels * scalefactor / dpi
              
              fig = plt.figure(figsize=(xinch,yinch))
              
              ax = plt.axes([0, 0, 1, 1], frame_on=False, xticks=[], yticks=[])
              
              plt.contour(mask, [0.5], linewidths=1, colors='r', origin='image')
              
              plt.savefig(out_dir +"/cosmo/Channels/indicators_in_time/RGB-HRV"+maskS+"/"+yearS+monthS+dayS+"_"+hourS+minS+"_C2rgb-HRV_contour"+"4th"+name_4Mask+"_"+name_ForcedMask+"AdditionalMask.png", dpi=dpi, transparent=True)
              fig.clf()
              plt.close(fig)
      
              if False:
                  img = Image.open('same_size.png')
                  img = img.convert("RGBA")
                  datas = img.getdata()
          
                  newData = []
                  for item in datas:
                      if item[0] == 255 and item[1] == 255 and item[2] == 255:
                          newData.append((255, 255, 255, 0))
                      else:
                          newData.append(item)
                  
                  img.putdata(newData)
                  img.save("mask_contours.png", "PNG")
                  
                  contourFile = "mask_contours.png"
                  out_file1 = create_dir( out_dir +"/cosmo/Channels/indicators_in_time/RGB-HRV"+maskS+"/"+yearS+monthS+dayS+"_"+hourS+minS+"_C2rgb-HRV_WithContours.png" )
                  
                  subprocess.call("/usr/bin/composite "+contourFile+" "+out_file+" "+out_file1, shell=True)
        

          time_slot = time_slot + timedelta(minutes=5)

    """
    plot_RGB             = False 
    plot_RGB_develop     = False 
    plot_RGB_mature      = False
    plot_RGB_all         = True
    plot_RGB_HRV         = False 
    plot_RGB_HRV_develop = False
    plot_RGB_HRV_mature  = False
    plot_RGB_HRV_all     = True

    # RGB for CONVECTIVE thunderstorms
    mask_convection = np.where( IR_039_minus_IR_108>=28,1,0)
    r = (us/5)*mask_convection
    g = (cd/6)*mask_convection
    b = (gi/5)*mask_convection
    rgbArray = np.zeros( (g.shape[0],g.shape[1],4), 'uint8')
    rgbArray[..., 0] = r*255
    rgbArray[..., 1] = g*255
    rgbArray[..., 2] = b*255
    rgbArray[..., 3] = 200
    sum_array = rgbArray[...,0]+rgbArray[..., 1]+rgbArray[..., 2]
    #count = np.zeros(sum_array.shape)
    #print (count.shape)
    #print (rgbArray[...,0].shape)
    #count[sum_array<=0] = 1
    #print (sum(sum(count)))
    rgbArray[sum_array<=0,0] = 255 #np.where( sum_array<=0,1,rgbArray[..., 0])
    rgbArray[sum_array<=0,1] = 255 #np.where( sum_array<=0,1,rgbArray[..., 1])
    rgbArray[sum_array<=0,2] = 255 #np.where( sum_array<=0,1,rgbArray[..., 2])
    rgbArray[sum_array<=0,3] = 0

    if plot_RGB:
        img1 = Image.fromarray( rgbArray,'RGBA')
        #add_borders_and_rivers( img1, cw, area_tuple,
        #                        add_borders=in_msg.add_borders, border_color=in_msg.border_color,
        #                        add_rivers=in_msg.add_rivers, river_color=in_msg.river_color, 
        #                        resolution=in_msg.resolution, verbose=in_msg.verbose)

        outputFile = out_dir+"/cosmo/Channels/indicators_in_time/RGBs/%s_%s_RGB.png"%(yearS+monthS+dayS,hourS+minS)
        print ("... save image: ", outputFile)
        img1.save( create_dir(outputFile) ) 

    if plot_RGB_HRV:
        file1 = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/"+yearS+"-"+monthS+"-"+dayS+"_HRV_ccs4/MSG_HRV-ccs4_15"+monthS+dayS+hourS+minS+".png" 
        file2 = out_dir +"/cosmo/Channels/indicators_in_time/RGBs/"+yearS+monthS+dayS+"_"+hourS+minS+"_RGB.png" 
        out_file = out_dir +"/cosmo/Channels/indicators_in_time/RGBs/"+yearS+monthS+dayS+"_"+hourS+minS+"_RGBCombined_BW.png"
        subprocess.call("/usr/bin/composite "+file2+" "+file1+" "+out_file, shell=True)
    

    # RGB for MATURE thunderstorms
    g = (cd/6)*mature_mask
    r = (us/5)*mature_mask
    b = (gi/5)*mature_mask
    rgbArray = np.zeros( (g.shape[0],g.shape[1],4), 'uint8')
    rgbArray[..., 0] = r*255
    rgbArray[..., 1] = g*255
    rgbArray[..., 2] = b*255
    rgbArray[..., 3] = 200
    sum_array = rgbArray[...,0]+rgbArray[..., 1]+rgbArray[..., 2]
    #count = np.zeros( sum_array.shape)
    #print (count.shape)
    #print (rgbArray[...,0].shape)
    #count[sum_array<=0] = 1
    #print (sum( sum(count)))
    rgbArray[sum_array<=0,0] = 255 #np.where( sum_array<=0,1,rgbArray[..., 0])
    rgbArray[sum_array<=0,1] = 255 #np.where( sum_array<=0,1,rgbArray[..., 1])
    rgbArray[sum_array<=0,2] = 255 #np.where( sum_array<=0,1,rgbArray[..., 2])
    rgbArray[sum_array<=0,3] = 0

    if plot_RGB_mature or plot_RGB_HRV_mature:
        img1 = Image.fromarray( rgbArray,'RGBA')
        #add_borders_and_rivers( img1, cw, area_tuple,
        #                        add_borders=in_msg.add_borders, border_color=in_msg.border_color,
        #                        add_rivers=in_msg.add_rivers, river_color=in_msg.river_color, 
        #                        resolution=in_msg.resolution, verbose=in_msg.verbose)
        print (out_dir +"/cosmo/Channels/indicators_in_time/RGBs/%s_%s_RGBmature.png"%(yearS+monthS+dayS,hourS+minS))
        img1.save(out_dir +"/cosmo/Channels/indicators_in_time/RGBs/%s_%s_RGBmature.png"%(yearS+monthS+dayS,hourS+minS))

    if plot_RGB_HRV_mature:
        file1 = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/"+yearS+"-"+monthS+"-"+dayS+"_HRV_ccs4/MSG_HRV-ccs4_15"+monthS+dayS+hourS+minS+".png" 
        file2 = out_dir +"/cosmo/Channels/indicators_in_time/RGBs/"+yearS+monthS+dayS+"_"+hourS+minS+"_RGBmature.png" 
        out_file = out_dir +"/cosmo/Channels/indicators_in_time/RGBs/"+yearS+monthS+dayS+"_"+hourS+minS+"_RGBmatureCombined_BW.png"
        subprocess.call( "/usr/bin/composite "+file2+" "+file1+" "+out_file, shell=True)
    

    # RGB for DEVELOPING thunderstorms
    r = (us/5)*developing_mask
    g = (cd/6)*developing_mask
    b = (gi/5)*developing_mask

    rgbArray = np.zeros( (g.shape[0],g.shape[1],4), 'uint8')
    rgbArray[..., 0] = r*255
    rgbArray[..., 1] = g*255
    rgbArray[..., 2] = b*255
    rgbArray[..., 3] = 200
    sum_array = rgbArray[...,0]+rgbArray[..., 1]+rgbArray[..., 2]
    #count = np.zeros(sum_array.shape)
    #print (count.shape)
    #print (rgbArray[...,0].shape)
    #count[sum_array<=0]=1
    #print (sum( sum(count)))
    rgbArray[sum_array<=0,0] = 255 #np.where( sum_array<=0,1,rgbArray[..., 0])
    rgbArray[sum_array<=0,1] = 255 #np.where( sum_array<=0,1,rgbArray[..., 1])
    rgbArray[sum_array<=0,2] = 255 #np.where( sum_array<=0,1,rgbArray[..., 2])
    rgbArray[sum_array<=0,3] = 0
    if plot_RGB_develop:
        img1 = Image.fromarray( rgbArray,'RGBA')
        #add_borders_and_rivers( img1, cw, area_tuple,
        #                        add_borders=in_msg.add_borders, border_color=in_msg.border_color,
        #                        add_rivers=in_msg.add_rivers, river_color=in_msg.river_color, 
        #                        resolution=in_msg.resolution, verbose=in_msg.verbose)
        print (out_dir +"/cosmo/Channels/indicators_in_time/RGBs/%s_%s_RGBdeveloping.png"%(yearS+monthS+dayS,hourS+minS))
        img1.save( out_dir +"/cosmo/Channels/indicators_in_time/RGBs/%s_%s_RGBdeveloping.png"%(yearS+monthS+dayS,hourS+minS))
    
    if plot_RGB_HRV_develop:
        file1 = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/"+yearS+"-"+monthS+"-"+dayS+"_HRV_ccs4/MSG_HRV-ccs4_15"+monthS+dayS+hourS+minS+".png" 
        file2 = out_dir +"/cosmo/Channels/indicators_in_time/RGBs/"+yearS+monthS+dayS+"_"+hourS+minS+"_RGBdeveloping.png" 
        out_file = out_dir +"/cosmo/Channels/indicators_in_time/RGBs/"+yearS+monthS+dayS+"_"+hourS+minS+"_RGBdevelopingCombined_BW.png"
        subprocess.call( "/usr/bin/composite "+file2+" "+file1+" "+out_file, shell=True)
    

    # RGB for DEVELOPING AND MATURE thunderstorms
    r = (cd/6)*all_mask
    g = (us/5)*all_mask
    b = (gi/5)*all_mask
    rgbArray = np.zeros( (g.shape[0],g.shape[1],4), 'uint8')
    rgbArray[..., 0] = r*255
    rgbArray[..., 1] = g*255
    rgbArray[..., 2] = b*140
    rgbArray[..., 3] = 200
    sum_array = rgbArray[...,0]+rgbArray[..., 1]+rgbArray[..., 2]
    #count = np.zeros( sum_array.shape)
    #print (count.shape)
    #print (rgbArray[...,0].shape)
    #count[sum_array<=0] = 1
    #print (sum( sum(count)))
    rgbArray[sum_array<=0,0] = 255 #np.where( sum_array<=0,1,rgbArray[..., 0])
    rgbArray[sum_array<=0,1] = 255 #np.where( sum_array<=0,1,rgbArray[..., 1])
    rgbArray[sum_array<=0,2] = 255 #np.where( sum_array<=0,1,rgbArray[..., 2])
    rgbArray[sum_array<=0,3] = 0
    if plot_RGB_all:
        img1 = Image.fromarray( rgbArray,'RGBA')

        if colour_enhancement_factor != 1:
            converter = ImageEnhance.Color(img1)
            img1 = converter.enhance( colour_enhancement_factor)
        #add_borders_and_rivers( img1, cw, area_tuple,
        #                        add_borders=in_msg.add_borders, border_color=in_msg.border_color,
        #                        add_rivers=in_msg.add_rivers, river_color=in_msg.river_color, 
        #                        resolution=in_msg.resolution, verbose=in_msg.verbose)
        outputFile =  create_dir( out_dir +"/cosmo/Channels/indicators_in_time/RGB-all/%s_%s_RGBallb.png"%(yearS+monthS+dayS,hourS+minS) )
        img1.save( outputFile )
    
    if plot_RGB_HRV_all:
        file1 = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/"+yearS+"-"+monthS+"-"+dayS+"_HRV_ccs4/MSG_HRV-ccs4_15"+monthS+dayS+hourS+minS+".png" 
        file2 = out_dir +"/cosmo/Channels/indicators_in_time/RGB-all/"+yearS+monthS+dayS+"_"+hourS+minS+"_RGBallb.png" 
        outputFile = create_dir( out_dir +"/cosmo/Channels/indicators_in_time/RGB-HRV-all/"+yearS+monthS+dayS+"_"+hourS+minS+"_RGBallCombined_BWb.png" )
        subprocess.call("/usr/bin/composite "+file2+" "+file1+" "+outputFile, shell=True)
        print (outputFile)
    

    """

    """
    #plot of edges areas where indicators (maybe contours)
    # http://www.scipy-lectures.org/advanced/image_processing/auto_examples/plot_find_edges.html#example-plot-find-edges-py
    img[np.isnan(img)] = 0
    img[img>0] = 1
    print (img)
    from scipy import ndimage
    sx = ndimage.sobel(img, axis=0, mode='constant')
    sy = ndimage.sobel(img, axis=1, mode='constant')
    sob=np.hypot(sx,sy)
    print (sob)
    sob=np.ma.masked_where(sob==0)
    """
    #file1="/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/"+yearS+"-"+monthS+"-"+dayS+"_HRV_ccs4/MSG_HRV-ccs4_15"+monthS+dayS+hourS+minS+".png" #2015-07-07_HRV_ccs4"_HRoverview_ccs4/MSG_HRoverview-ccs4_15"+monthS+dayS+hourS+minS+".png"
    """
    back = Image.load(file1)
    
    fig = plt.figure()

    plt.imshow(back)
    plt.imshow(sob)
    plt.axis('off')
    plt.savefig('attempt_edges.png')
    plt.close(fig)
    #
    """
    
    

    


"""
    img_cd = trollimage(cd,mode="L")
    #rainbow.set_range(0,len(cloud_depth))
    #img_cd.colorize(rainbow)
    
    img_cd = img_cd.pil_image()
    dc = DecoratorAGG(img_cd)

    cw = ContourWriterAGG(in_msg.mapDir)
    
    test = create_PIL_image(0, img_cd, in_msg, colormap='rainbow')
    test = add_borders_and_rivers( test, cw, area_tuple,
                                   add_borders=in_msg.add_borders, border_color=in_msg.border_color,
                                   add_rivers=in_msg.add_rivers, river_color=in_msg.river_color, 
                                   resolution=in_msg.resolution, verbose=in_msg.verbose)

    dc.add_scale(rainbow,extend=True)
    
    print (type(img_cd))
"""

#####################th1#####################
"""
    cd = np.zeros(wv_062_t15.shape)
    cd = np.where(cloud_depth[0]>-25,cd+1,cd)
    cd = np.where(cloud_depth[1]>-12.5,cd+1,cd)
    cd = np.where(cloud_depth[2]<250,cd+1,cd)
    cd = np.where(cloud_depth[3]>-2,cd+1,cd)
    cd = np.where(cloud_depth[4]>-12.5,cd+1,cd)
    cd = np.where(np.logical_and(cloud_depth[5]>-1.6,cloud_depth[5]<2.2),cd+1,cd)


    gi = np.zeros(wv_062_t15.shape)
    gi = np.where(glaciation_indicators[0]>-1.5,gi+1,gi)
    gi = np.where(glaciation_indicators[1]>-2,gi+1,gi)
    gi = np.where(glaciation_indicators[2]>-1,gi+1,gi)
    gi = np.where(glaciation_indicators[3]>-1.55,gi+1,gi)
    gi = np.where(glaciation_indicators[4]>-1,gi+1,gi)
    gi = np.where(glaciation_indicators[5]>-0.2,gi+1,gi)
    gi = np.where(glaciation_indicators[6]>-1,gi+1,gi)

    us = np.zeros(wv_062_t15.shape) 
    us = np.where(updraft_strength[0]>2,us+1,us)
    us = np.where(updraft_strength[1]>-22,us+1,us)
    us = np.where(updraft_strength[2]>-35,us+1,us)
    us = np.where(updraft_strength[3]>0.5,us+1,us)
    us = np.where(updraft_strength[4]>0.5,us+1,us)
    us = np.where(updraft_strength[5]>6,us+1,us)
    us = np.where(updraft_strength[6]>2,us+1,us)
    us = np.where(updraft_strength[7]>-7,us+1,us)
"""

#####################th2#####################
"""
    cd = np.zeros(wv_062_t15.shape)
    cd = np.where(cloud_depth[0]>-25,cd+1,cd)
    cd = np.where(cloud_depth[1]>-12.5,cd+1,cd)
    cd = np.where(cloud_depth[2]<250,cd+1,cd)
    cd = np.where(cloud_depth[3]>-2,cd+1,cd)
    cd = np.where(cloud_depth[4]>-12.5,cd+1,cd)
    cd = np.where(cloud_depth[5]>2.2,cd+1,cd)

    gi = np.zeros(wv_062_t15.shape)
    gi = np.where(glaciation_indicators[0]>2,gi+1,gi)
    gi = np.where(glaciation_indicators[1]>1,gi+1,gi)
    gi = np.where(glaciation_indicators[2]>1.5,gi+1,gi)
    gi = np.where(glaciation_indicators[3]>-1.5,gi+1,gi)
    #gi = np.where(glaciation_indicators[4]>-1,gi+1,gi)
    #gi = np.where(glaciation_indicators[5]>-0.2,gi+1,gi)
    gi = np.where(np.logical_and(glaciation_indicators[6]>-5,glaciation_indicators[6]<-1) ,gi+1,gi)
    
    us = np.zeros(wv_062_t15.shape) 
    us = np.where(updraft_strength[0]>2.5,us+1,us)
    #us = np.where(updraft_strength[1]>-22,us+1,us)
    us = np.where(updraft_strength[2]<-10,us+1,us)
    us = np.where(updraft_strength[3]>2.5,us+1,us)
    us = np.where(updraft_strength[4]>2,us+1,us)
    us = np.where(updraft_strength[5]>13,us+1,us)
    #us = np.where(updraft_strength[6]>2,us+1,us)
    #us = np.where(updraft_strength[7]>-7,us+1,us)    
"""



