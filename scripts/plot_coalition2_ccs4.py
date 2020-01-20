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
from my_msg_module import convert_NWCSAF_to_radiance_format, get_NWC_pge_name, check_input
from mpop.imageo.palettes import convert_palette2colormap
from plot_msg import load_products
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg')
import time
import copy
from particles_displacement import particles_displacement
import numpy.ma as ma
import netCDF4
import pickle
import subprocess
import mpop
from mpop.imageo.HRWimage import prepare_figure 
import shelve

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
    mod[obs==True] = np.nan
    mod.mask = obs
    return mod
    
# removed function 
# def downscale(data,mode = 'gaussian_225_125'):
# use the function in plot_coalition2.py instead everywhere
    
def make_figure(values, obj_area, outputFile, colorbar = True, text_to_write = None, vmin = False, vmax = False, contour_value = None, linewidth = 1):
    import matplotlib as mpl
    mpl.use('Agg')
    import pickle
    import matplotlib.pyplot as plt
    from mpop.projector import get_area_def
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    import numpy as np
    from mpop.imageo.TRTimage import fig2img    
    from mpop.imageo.HRWimage import prepare_figure
    
    if vmin == False:
        vmin = values.min()
    if vmax == False:
        vmax = values.max()
    
    obj_area = get_area_def(area)
    
    fig, ax = prepare_figure(obj_area) 
    
    mappable = plt.imshow(np.flipud(values), vmin = vmin, vmax = vmax, origin="lower")
    
    if contour_value != None:
        plt.contour( values, contour_value, linewidths=linewidth, origin='upper' )
        #plt.contour( values, contour_value, linewidths=linewidth, origin='lower' )
    
    if text_to_write != None:
        ax.text(0.95, 0.01, text_to_write,
                verticalalignment='bottom', horizontalalignment='right',
                transform=ax.transAxes,
                color='cyan', fontsize=15)
    position=fig.add_axes([0.93,0.2,0.02,0.35])  ## the parameters are the specified position you set: left, bottom, width, height
    if colorbar:
        color_bar = fig.colorbar(mappable,cax=position) ## 
        plt.setp(plt.getp(color_bar.ax.axes, 'yticklabels'), color='cyan')
    
    PIL_image = fig2img ( fig )
    PIL_image.save(create_dir(outputFile))
    print("... display ",outputFile," &")
    plt.close( fig)

# ===============================


#def wind_shiftFun(in_windshift):
if __name__ == '__main__':
    # input 

    detailed = True 

    area2load = "EuropeCanary95" #"ccs4" #c2"#"ccs4" #in_windshift.ObjArea
    area = "ccs4" # "ccs4" "blitzortung" #"eurotv" # "eurotv"

    europe_areas = ["eurotv","blitzortung","EuropeCanaryS95"]
    
    #if area.

    from get_input_msg import get_input_msg
    in_msg = get_input_msg('input_coalition2')
    
    #if area!= "eurotv" or area!= "blitzortung":

    if area not in europe_areas:
        scale = "local"
    else:
        scale = "europe"
        
    
    if scale == "europe" or len(sys.argv) < 2:
        only_obs_noForecast = True
        rapid_scan_mode = True
        clean_mask = 'no_cleaning'
        mask_labelsSmall_lowUS = False
        mode_downscaling = 'no_downscaling'
    else:
        #in_msg.reader_level = "seviri-level4"
        only_obs_noForecast = False
        rapid_scan_mode = False
        mask_labelsSmall_lowUS = True
        clean_mask = 'skimage' #clean_mask = 'scipy' #clean_mask = 'both' #clean_mask = 'no_cleaning'
        mode_downscaling = 'gaussian_225_125'
        #mode_downscaling = 'convolve_405_300'
        #mode_downscaling = 'gaussian_150_100'
        #mode_downscaling = 'no_downscaling'

    # !!! changes for ccs4 !!!
    only_obs_noForecast = False   ### temporary
    rapid_scan_mode = False       ### temporary
    mode_downscaling = 'gaussian_225_125'  ### temporary


        
    if scale != "europe" and len(sys.argv) < 2:
        clean_mask = 'skimage'
    
    forth_mask  = 'IR_039_minus_IR_108'      # 'CloudType'           # 'no_mask'
    forced_mask = 'no_mask'                  # 'IR_039_minus_IR_108' # 'CloudType' #
    mask_cirrus = True
    
    if rapid_scan_mode:
        rapid_scan_active = "active"
    else:
        rapid_scan_active = "not active"
    print("---Rapid scan mode ", rapid_scan_active)
    
    if clean_mask == 'no_cleaning':
        mask_labelsSmall_lowUS = False
    
    # additional parameters for forth_mask (test to pass for a px to be included in addition to cloud depth, updraft strength and glaciation)
    mature_th_chDiff     = 25.0
    developing_th_chDiff = 8.0
    
    mature_ct            = [17,14,12]
    developing_ct        = [8,9,10,17,14,12]
    
    # additional parameters for foced_mask (force to include (in mature_mask) any pixel regardless of the other thresholds)
    force_th_chDiff      = 40.0
    cloud_type_forced    = [17,14]
    
    #additional threshold for mask_cirrus (cd6 > th)
    th_cirrus            = 4.0

    #additional parameters for cleaning (if skimage) [removes small holes within clouds (max_holes = max number of px to fill with clouds) and small clouds (min_cloud = number px minimum to keep a cloud)]
    min_cloud = 20.0 #100.0 #
    max_holes = 500.0

    # set cloud mask 
    #show_clouds = 'all'
    #show_clouds = 'developing'
    #show_clouds = 'mature'
    show_clouds = 'developing_and_mature'
    
    
    # choose color combination
    #rgb_display = 'us-cd-gi'
    rgb_display = 'cd-us-gi'

    # choose saturation enhancement 
    #colour_enhancement_factor = 1   # 1 gives the original colour
    colour_enhancement_factor = 2   # 1 gives the original colour
    # colour_enhancement_factor = 3 # ??? 2 seems to be more colorful than 3 ???
    
    
    
    #PLOTTING OPTIONS:
    
    #contour lines identifying objects
    detect_objects = False
    
    #mask that removed the thin cirrus
    plot_mask_cirrus = True
    
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
    
    plot_108 = False
        
    title_color = (255,255,255)
    #layer = ''
    layer = ' 2nd layer'
    #layer = '3rd layer'
    add_rivers = False
    add_borders = False
    legend = True

    pickle_labels = False
    shelve_labels = True
    #labels_dir = "./labels/"
    labels_dir = "/data/cinesat/out/labels/"
    if scale == "europe":
        pickle_labels = False
        shelve_labels = False

    # choose saturation for each indictor
    cmax_cd =  255   
    cmin_cd =  -80   
    cmax_us =  255
    cmin_us =    0
    cmax_gi =   85  # 140 for 5 tests
    cmin_gi =    0  

    # backgroundcolor 
    background_color = [255,255,255]   # white
    background_color = [  0,  0,  0]   # black

    # foregroud and background opacity (== 1 - transparency)
    #foregroud_alpha  = 200      # pretty opaque
    foregroud_alpha  = 255      # opaque
    background_alpha =   50      # transparent
    #background_alpha = 255     # opaque

    # specify result plots
    plot_RGB             = True
    plot_RGB_HRV         = True

    # load a few standard things 
    
    in_msg.resolution = 'i'
    in_msg.sat_nr = 9
    in_msg.add_title = False
    in_msg.outputDir = './pics/'
    in_msg.outputFile = 'WS_%(rgb)s-%(area)s_%y%m%d%H%M'
    in_msg.fill_value = [0,0,0] # black
    
    #in_msg.fill_value = None    # transparent
    #colormap = 'rainbow'
    colormap = 'greys'
    delay = 5

    ntimes = 2 #in_windshift.ntimes
    print("... aggregate winddata for ", ntimes, " timesteps") 
    min_correlation = 85 #in_windshift.min_correlation
    min_conf_nwp = 80 #in_windshift.min_conf_nwp
    min_conf_no_nwp = 80 #in_windshift.min_conf_no_nwp
    cloud_type = [5,6,7,8,9,10,11,12,13,14] #in_windshift.cloud_type

    # satellite for HRW winds
    sat_nr = "08" #in_windshift.sat_nr
    
    if len(sys.argv) > 1 and scale != "europe":
        channels = ['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134','CTP','CT']
    else:
        channels = ['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134']

        
    #channels = ['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134']
    
    channels15 = ['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134']
    channels30 = ['WV_062','WV_073','IR_097','IR_108','IR_134']


    if forth_mask == 'IR_039_minus_IR_108':
        name_4Mask = 'IRdiff'
    elif forth_mask == 'CloudType':
        name_4Mask = 'CT'
    elif forth_mask == 'no_mask':
        name_4Mask = 'none'
    else:
        print("*** Error in main (Mecikalski_test.py)")
        print("    unknown 4th mask", forth_mask)
        quit() 

    if forced_mask == 'IR_039_minus_IR_108':
        name_ForcedMask = 'IRdiff'
    elif forced_mask == 'CloudType':
        name_ForcedMask = 'CT'
    elif forced_mask == 'no_mask':
        name_ForcedMask = 'no'
    else:
        print("    unknown forcing mask -> applying no forcing mask", forced_mask) 
        name_ForcedMask = 'no'   
        
    vmin_cd =    [-50.,    -20.,    210.,    -14.,    -32.,    - 3.]
    vmax_cd =    [ 1.,      2.,    300.,      3.,      6.,     15.]
    
    th_cd   =    [-16.,    - 7.5,   250.,    - 2.,    -12.5,    2.2]


    vmin_gi =    [- 6.,    - 8.,    - 5.,    - 3.,   - 6.,     -32.,    -10.]
    vmax_gi =    [ 10.,      4.,      8.,      6.,     6.,      32.,      2.]
    
    th_gi   =    [  2.,    - 1.5,    1.5,    - 1.,   - 1.,       0.,    - 1.]


    vmin_us =    [-12.,    -50.,    -60.,    -15.,   - 8.,     -40.,    -40.,    -12.]
    vmax_us =    [ 20.,     50.,     60.,     20.,    10.,      50.,     40.,     12.]
    
    th_us   =    [  2.5,   -12.,    -10.,      2.5,    2.,      13.,     10.,    - 7.]    
            
    dt_forecast1 = 15
    dt_forecast2 = 30
    
    if rapid_scan_mode ==True:
        for r in range(len(th_us)):
            th_us[r] = th_us[r]/ 3.
        dt_forecast1 = 5
        dt_forecast2 = 10
    
    dt_forecast1S = str(dt_forecast1) #"%02d" % dt_forecast1
    dt_forecast2S = str(dt_forecast2) #"%02d" % dt_forecast2



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
            
            time_slot = datetime(year, month, day, hour, minute)
            time_slotSTOP = time_slot                                     
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
      
          #nowcastDir="/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/channels/" #'/opt/users/'+in_msg.user+'/PyTroll/scripts/channels_new//' #"2
          nowcastDir="/data/cinesat/out/" #'/opt/users/'+in_msg.user+'/PyTroll/scripts/channels_new//' #"2
          

          time_slot15 = time_slot - timedelta(minutes=dt_forecast1)
          
          time_slot30 = time_slot - timedelta(minutes=dt_forecast2)
      
          hour_forecast15S = "%02d" % (time_slot15.hour)
          min_forecast15S = "%02d" % (time_slot15.minute)
      
          hour_forecast30S = "%02d" % (time_slot30.hour)
          min_forecast30S = "%02d" % (time_slot30.minute)    
      
                
          # define area object 
          obj_area = get_area_def(area)#(in_windshift.ObjArea)
      
          # define area
          proj4_string = obj_area.proj4_string            
          # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
          area_extent = obj_area.area_extent              
          # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
          area_tuple = (proj4_string, area_extent)
          
          print("*** read data for ", in_msg.sat, str(in_msg.sat_nr), "seviri", time_slot)

          in_msg.datetime = time_slot
          in_msg.RGBs = channels
          RGBs = check_input(in_msg, in_msg.sat+in_msg.sat_nr_str(), in_msg.datetime) 
          # in_msg.sat_nr might be changed to backup satellite

          # now read the data we would like to forecast
          global_data = GeostationaryFactory.create_scene(in_msg.sat_str(), in_msg.sat_nr_str(), "seviri", time_slot)
          #global_data_RGBforecast = GeostationaryFactory.create_scene(in_msg.sat, str(10), "seviri", time_slot)
      
          # area we would like to read
          area_loaded = get_area_def(area2load )#(in_windshift.areaExtraction)  

          # load product, global_data is changed in this step!
          area_loaded = load_products(global_data, channels, in_msg, area_loaded ) #
          
          print('... project data to desired area ', area)
          data = global_data.project(area, precompute=True)
          
          # print type(data)
          loaded_channels = [chn.name for chn in data.loaded_channels()]
          print("... loaded_channels: ", loaded_channels)
         
          data = downscale(data,mode_downscaling)

      
          if False:
              from trollimage.colormap import rainbow
              colormap = rainbow
              #chn = 'VIS006'
              chn = 'IR_108'
              #chn = 'CTP'
              min_data = data[chn].data.min()
              max_data = data[chn].data.max()
              colormap.set_range(min_data, max_data)
              from trollimage.image import Image as trollimage
              img = trollimage(data[chn].data, mode="L", fill_value=[0,0,0])
              img.colorize(colormap)
              img.show()
              quit()

          
          # create a mask where CTP can be derived 
          # -------------------
      
          nx,ny = data['IR_108'].data.shape
          print("    nx, ny= ", nx,ny)

          #print type(data['CTP'].data)
          if scale == "europe" or len(sys.argv) < 2:
              mask_CTP = np.where(data['IR_108'].data < -10.0)
          else:
              data['CTP'].data = ma.masked_less(data['CTP'].data, 0)
              mask_CTP = data['CTP'].data.mask
              print(data['CTP'].data.shape)
              print(data['CTP'].data.size) 
          #if True:
          #      mask1 = deepcopy(data['CTP'].data)
          #      mask_CTP = np.zeros(mask1.shape)
          #      mask_CTP[mask1>0] = 1
          #else:
          #      mask_CTP = pickle.load( open( "mask_obs%s.p"%(yearS+monthS+dayS+hours+minS),"rb") )   
          #print mask_CTP             


          
          if False:
              fig = plt.figure()
              plt.imshow(data['CT'].data)
              plt.colorbar()
              fig.savefig("Cloud_type.png")
              plt.close(fig)
          
          
          #print "mask ", sum(sum(data['CTP'].data.mask))
          
          
          #out_dir = "/data/COALITION2/PicturesSatellite//LEL_results_wind/"+yearS+"-"+monthS+"-"+dayS+"/"
          #out_dir = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/Mecikalski2/"
          
          if only_obs_noForecast == True:
              out_dir = '/opt/users/'+in_msg.user+'/PyTroll/scripts//Mecikalski_obs/'
          elif rapid_scan_mode == True:
              out_dir = '/opt/users/'+in_msg.user+'/PyTroll/scripts//Mecikalski_RapidScan/'
          else:
              out_dir = '/opt/users/'+in_msg.user+'/PyTroll/scripts//Mecikalski/'
              
              
          if False:
              from trollimage.colormap import rainbow
              colormap = rainbow
              #chn = 'VIS006'
              chn = 'IR_108'
              #chn = 'CTP'
              min_data = data[chn].data.min()
              max_data = data[chn].data.max()
              colormap.set_range(min_data, max_data)
              from trollimage.image import Image as trollimage
              img = trollimage(data[chn].data, mode="L", fill_value=[0,0,0])
              img.colorize(colormap)
              img.show()
              quit() 
             
          if only_obs_noForecast == True:
              
              # now read the observations of the channels at -30 min
              print("*** read data for ", in_msg.sat, str(in_msg.sat_nr), "seviri", time_slot30)
              global_data30 = GeostationaryFactory.create_scene(in_msg.sat, str(in_msg.sat_nr), "seviri", time_slot30)
              # area we would like to read
              area_loaded = get_area_def(area2load)#(in_windshift.areaExtraction)  
              # load product, global_data is changed in this step!
              area_loaded = load_products(global_data30, channels30, in_msg, area_loaded)
              data30 = global_data30.project(area, precompute=True)           
              data30 = downscale(data30,mode_downscaling)

              # now read the observations of the channels at -15 min
              print("*** read data for ", in_msg.sat, str(in_msg.sat_nr), "seviri", time_slot15)
              global_data15 = GeostationaryFactory.create_scene(in_msg.sat, str(in_msg.sat_nr), "seviri", time_slot15)
              # area we would like to read
              area_loaded15 = get_area_def(area2load)#(in_windshift.areaExtraction)  
              # load product, global_data is changed in this step!
              area_loaded15 = load_products(global_data15, channels15, in_msg, area_loaded15)
              data15 = global_data15.project(area, precompute=True)              
              data15 = downscale(data15,mode_downscaling)
              
              if False:
                  from trollimage.colormap import rainbow
                  colormap = rainbow
                  #chn = 'VIS006'
                  chn = 'IR_108'
                  #chn = 'CTP'
                  min_data = data[chn].data.min()
                  max_data = data[chn].data.max()
                  colormap.set_range(min_data, max_data)
                  from trollimage.image import Image as trollimage
                  img = trollimage(data[chn].data, mode="L", fill_value=[0,0,0])
                  img.colorize(colormap)
                  img.show()
                  quit()              
                
              wv_062_t15 = deepcopy(data15['WV_062'].data)
              wv_062_t30 = deepcopy(data30['WV_062'].data)
                      
              wv_073_t15 = deepcopy(data15['WV_073'].data)
              wv_073_t30 = deepcopy(data30['WV_073'].data)            
          
              ir_097_t15 = deepcopy(data15['IR_097'].data)
              ir_097_t30 = deepcopy(data30['IR_097'].data) 
          
              ir_108_t15 = deepcopy(data15['IR_108'].data)
              ir_108_t30 = deepcopy(data30['IR_108'].data) 
          
              ir_134_t15 = deepcopy(data15['IR_134'].data)
              ir_134_t30 = deepcopy(data30['IR_134'].data) 
          
              ir_087_t15 = deepcopy(data15['IR_087'].data)
              
              ir_120_t15 = deepcopy(data15['IR_120'].data)
              
              ir_039_t15 = deepcopy(data15['IR_039'].data)
              
              
          else:
              print("************** ", nowcastDir+"%s_%s_WV_062_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S))                                    
              wv_062_t15 = pickle.load( open( nowcastDir+"%s_%s_WV_062_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) ) 
              wv_062_t30 = pickle.load( open( nowcastDir+"%s_%s_WV_062_t%s.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S, dt_forecast2S), "rb" ) )
                      
              wv_073_t15 = pickle.load( open( nowcastDir+"%s_%s_WV_073_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) )
              wv_073_t30 = pickle.load( open( nowcastDir+"%s_%s_WV_073_t%s.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S, dt_forecast2S), "rb" ) )           
          
              ir_097_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_097_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) )
              ir_097_t30 = pickle.load( open( nowcastDir+"%s_%s_IR_097_t%s.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S, dt_forecast2S), "rb" ) )  
          
              ir_108_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_108_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) )
              ir_108_t30 = pickle.load( open( nowcastDir+"%s_%s_IR_108_t%s.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S, dt_forecast2S), "rb" ) )  
              
              ir_134_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_134_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) )
              ir_134_t30 = pickle.load( open( nowcastDir+"%s_%s_IR_134_t%s.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S, dt_forecast2S), "rb" ) ) 
          
              ir_087_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_087_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) ) 
              
              ir_120_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_120_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) ) 
              
              ir_039_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_039_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) ) 
      
              downscalings = [wv_062_t15[1],wv_062_t30[1],wv_073_t15[1],wv_073_t30[1],ir_097_t15[1],ir_097_t30[1],ir_108_t15[1],ir_108_t30[1],ir_134_t15[1],ir_134_t30[1],ir_087_t15[1],ir_120_t15[1],ir_039_t15[1]]
              
              #check if downscaling you are applying matches with the downscaling applied when producing the forecasts
              if True:
                  if any(bz != mode_downscaling for bz in downscalings):
                      print("The downscaling technique applied for the production of forecast differs from that chosen here")
                      print("current technique: ", mode_downscaling)
                      print("technique forecast: ", list(set(downscalings)))
                      quit()

              print("...correct downscaling: ", mode_downscaling)
              wv_062_t15 = wv_062_t15 [0]
              wv_062_t30 = wv_062_t30 [0]
                      
              wv_073_t15 = wv_073_t15 [0]
              wv_073_t30 = wv_073_t30 [0]          
          
              ir_097_t15 = ir_097_t15 [0]
              ir_097_t30 = ir_097_t30 [0] 
          
              ir_108_t15 = ir_108_t15 [0]
              ir_108_t30 = ir_108_t30 [0] 
              
              ir_134_t15 = ir_134_t15 [0]
              ir_134_t30 = ir_134_t30 [0]

              ir_087_t15 = ir_087_t15 [0]
              
              ir_120_t15 = ir_120_t15 [0]
              
              ir_039_t15 = ir_039_t15 [0]   
              
              
              
          ir_120_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_120_t15), mask_CTP)
      
          wv_062_t15 = force_to_observed_cloud_mask(ma.masked_array(wv_062_t15), mask_CTP) #ma.masked_where(a <= 2, a)
      
          wv_062_t30 = force_to_observed_cloud_mask(ma.masked_array(wv_062_t30), mask_CTP)
                                                              
          wv_073_t15 = force_to_observed_cloud_mask(ma.masked_array(wv_073_t15), mask_CTP)
          wv_073_t30 = force_to_observed_cloud_mask(ma.masked_array(wv_073_t30), mask_CTP)
                                                              
          ir_097_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_097_t15), mask_CTP)
          ir_097_t30 = force_to_observed_cloud_mask(ma.masked_array(ir_097_t30), mask_CTP)
                                                              
          ir_108_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_108_t15), mask_CTP)
          ir_108_t30 = force_to_observed_cloud_mask(ma.masked_array(ir_108_t30), mask_CTP)
                                                              
          ir_134_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_134_t15), mask_CTP)
          ir_134_t30 = force_to_observed_cloud_mask(ma.masked_array(ir_134_t30), mask_CTP)
                                                              
          ir_087_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_087_t15), mask_CTP)
                                                              
          ir_120_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_120_t15), mask_CTP)
                                                              
          ir_039_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_039_t15), mask_CTP)
      
          if plot_108:
              fig, ax = prepare_figure(obj_area) 
              plt.imshow(ir_108_t15)
              #plt.colorbar()
              #plt.title( "IR108 t=t plus %s"%(str(dt_forecast1)) )
              fig.savefig(yearS+monthS+dayS+"_"+hour_forecast15S+min_forecast15S+"_"+"ir_108_t"+dt_forecast1S+".png")
              plt.close( fig)
              pickle.dump( ir_108_t15, open("ir_108_t15.p", "wb" ) )
    
              fig, ax = prepare_figure(obj_area) 
              plt.imshow(ir_108_t30)
              #plt.colorbar()
              #plt.title( "IR108 t=t plus %s"%(str(dt_forecast2)) )
              fig.savefig(yearS+monthS+dayS+"_"+hour_forecast30S+min_forecast30S+"_"+"ir_108_t"+dt_forecast2S+".png")
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
          cd = np.where( cloud_depth[0,:,:] >  th_cd[0], cd+1, cd );   n_tests_cd+=1. ;   n_tests_cd+=1.# !!! changed from - 16.0
          cd = np.where( cloud_depth[1,:,:] >  th_cd[1], cd+1, cd );   n_tests_cd+=1. ;   n_tests_cd+=1.# !!! changed from -7.5
          cd = np.where( cloud_depth[2,:,:] <  th_cd[2], cd+1, cd );   n_tests_cd+=1. ;   n_tests_cd+=1.
          cd = np.where( cloud_depth[3,:,:] >  th_cd[3], cd+1, cd );   n_tests_cd+=1. ;   n_tests_cd=1.
          cd = np.where( cloud_depth[4,:,:] >  th_cd[4], cd+1, cd );   n_tests_cd+=1. ;   n_tests_cd+=1.
          #cd = np.where( cloud_depth[5,:,:] <  th_cd[5], cd+1, cd );   n_tests_cd+=1. ;   n_tests_cd=1. # !!! changed DEACTIVATED
          
          #cirrus = np.where( cloud_depth[5,:,:]           >  th_cirrus ,cirrus +1, cirrus)
          
          cd = np.where(mask_CTP == True, 0, cd)
          
          
          #cd = np.where( mask_CTP==1,0,cd)

          if plot_tests_optical_thickness:
              for i in range( 0,cloud_depth.shape[0]):
                
                    item = cloud_depth[i,:,:]
                    item[mask_CTP==True] = np.nan
                    outputFile = out_dir +"/cosmo/Channels/indicators_in_time/all_indicators/%s_%s_Cloud_depth%s.png"%(yearS+monthS+dayS,hourS+minS,str(i+1))
                    make_figure(item, obj_area,  outputFile,colorbar = True,text_to_write = "Cloud depth %s"%(str(i+1)), vmin = vmin_cd[i], vmax = vmax_cd[i], contour_value = [th_cd[i]], linewidth = 1)

                    #fig = plt.figure()
                    #plt.imshow( item, vmin = vmin_cd[i], vmax = vmax_cd[i])
                    #plt.colorbar()
                    #plt.contour( item, [th_cd[i]], linewidths=1, origin='lower' )  # , [0.0], colors='r'
                    #plt.title( "Cloud_depth%s"%(str(i+1)) )
                    
                    #fig.savefig( create_dir(outputFile) ) 
                    #plt.close( fig)
                    
                    #print "... display ", outputFile, " &" 
              item = cloud_depth[5,:,:]
              item[mask_CTP==True] = np.nan
              
              #fig = plt.figure()
              #plt.imshow( item, vmin = vmin_cd[5], vmax = vmax_cd[5])
              #plt.colorbar()
              #plt.contour( item, [th_cirrus], linewidths=1, origin='lower' )  # , [0.0], colors='r'
              #plt.title( "Cloud_depth%s"%(str(i+1)) )
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/all_indicators/%s_%s_Cloud_depth%s_cirrus.png"%(yearS+monthS+dayS,hourS+minS,str(i+1))
              make_figure(item, obj_area, outputFile, colorbar = True, text_to_write = "Cloud depth 6", vmin = vmin_cd[5], vmax = vmax_cd[5], contour_value = [th_cirrus], linewidth = 1)
              
              #fig.savefig( create_dir(outputFile) ) 
              #plt.close( fig)
              #print "... display ", outputFile, " &"               
          if plot_indicator_optical_thickness:
              
              #fig = plt.figure()
              #plt.imshow( cd, vmin=0, vmax=5)
              #plt.colorbar( )
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/CloudDepthTH/%s_%s_Cloud_Depth.png"%(yearS+monthS+dayS,hourS+minS)
              #fig.savefig( create_dir(outputFile) )  
              #plt.close(fig)  
              make_figure(cd, obj_area, outputFile, colorbar = True, text_to_write = "Cloud Depth", vmin = 0, vmax = n_tests_cd)
      
      
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
                  item[mask_CTP==True] = np.nan
                  
                  #fig = plt.figure()
                  #plt.imshow( item, vmin = vmin_gi[i], vmax = vmax_gi[i])
                  #plt.colorbar()
                  if i == 6:
                      contour_value = [-5.,-1.5]
                  else:
                      contour_value = [th_gi[i]]
                  #plt.title( "Glaciation_Indicators%s"%(str(i+1)))
                  outputFile = out_dir +"/cosmo/Channels/indicators_in_time/all_indicators/%s_%s_Glaciation_Indicators%s.png"%(yearS+monthS+dayS,hourS+minS,str(i+1))
                  make_figure(item,obj_area,  outputFile, colorbar = True, text_to_write = "Glaciation_Indicators%s"%(str(i+1)), vmin = vmin_gi[i], vmax = vmax_gi[i], contour_value = contour_value) 
                  #fig.savefig( create_dir(outputFile) ) 
                  #plt.close(fig)
                  #print "... display ", outputFile, " &" 
      
          if plot_indicator_glationation:
              #fig = plt.figure()
              #plt.imshow( gi, vmin=0, vmax=3) # vmax=len( glaciation_indicators))
              #plt.colorbar()
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/GlaciationIndicatorTH/%s_%s_Glaciation_indicators.png"%(yearS+monthS+dayS,hourS+minS)
              make_figure(gi, obj_area, outputFile,colorbar = True,text_to_write = "Glaciation Indicators", vmin = 0, vmax = n_tests_gi)
              #fig.savefig( create_dir(outputFile) )    
              #plt.close(fig)
      


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
          
          #count_null = np.zeros( (nx,ny))
          #count_null = np.where( mask_CTP==1,1,0)
          #print sum( sum( count_null))
          
          us = np.where(mask_CTP == True, 0, us)
          #us = us*mask_CTP
          #us = np.where( mask_CTP==1,0,us)
          
          if plot_tests_updraft:
              for i in range( updraft_strength.shape[0]):
                  item = updraft_strength[i,:,:]
                  item[mask_CTP==True] = np.nan
                  #fig = plt.figure()
                  #plt.imshow( item, vmin = vmin_us[i], vmax = vmax_us[i])
                  ##plt.colorbar()
                  #plt.contour( item, [th_us[i]], linewidths=1, origin='lower' )  # , [0.0], colors='r'
                  #plt.title( "Updraft_strength%s"%(str(i+1)))
                  outputFile = out_dir +"/cosmo/Channels/indicators_in_time/all_indicators/%s_%s_Updraft_strength%s.png"%(yearS+monthS+dayS,hourS+minS,str(i+1))
                  make_figure(item, obj_area, outputFile,colorbar = True,text_to_write = "Updraft Strength %s"%(str(i+1)), vmin = vmin_us[i], vmax = vmax_us[i], contour_value = [th_us[i]])
                  #fig.savefig( create_dir(outputFile)) 
                  #plt.close(fig)       
                  #print "... display ", outputFile, " &" 
      
          if plot_indicator_updraft:
              #fig = plt.figure()
              #plt.imshow( us, vmin=0, vmax=7) # vmax=len( updraft_strength))
              #plt.colorbar()
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/UpdraftStrengthTH/%s_%s_Updraft_strength.png"%(yearS+monthS+dayS,hourS+minS)
              make_figure(us, obj_area, outputFile,colorbar = True,text_to_write = "Updraft Strength", vmin = 0, vmax = n_tests_us)
              #fig.savefig( create_dir(outputFile) ) 
              #plt.close(fig) 
          

      
          # test for SMALL ICE CRYSTALS 
          # -------------------
          IR_039_minus_IR_108 = deepcopy(data['IR_039'].data)-deepcopy(data['IR_108'].data)
          
          if plot_tests_small_ice:
              #fig = plt.figure()
              #plt.imshow(IR_039_minus_IR_108)
              #plt.colorbar()
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/all_indicators/%s_%s_Small_ice.png"%(yearS+monthS+dayS,hourS+minS)
              make_figure(IR_039_minus_IR_108, obj_area, outputFile,colorbar = True,text_to_write = "IR039 minus IR108", vmin = False, vmax = False, contour_value = [developing_th_chDiff, mature_th_chDiff])
              #fig.savefig( create_dir(outputFile)  )
              #plt.close(fig)
          
          if plot_indicator_small_ice:
              #fig = plt.figure()
              si = np.zeros( (nx,ny)) 
              si = np.where( IR_039_minus_IR_108 >= mature_th_chDiff, si+1, si )
              #plt.imshow( si, vmin=0, vmax=1) # vmax=len( updraft_strength))
              #plt.colorbar()
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/SmallIceTH/%s_%s_Small_ice.png"%(yearS+monthS+dayS,hourS+minS)
              make_figure(si, obj_area, outputFile,colorbar = True,text_to_write = "Indicator small ice mask (>= %s)"%(str(mature_th_chDiff)), vmin = 0, vmax = 1)
              #fig.savefig( create_dir(outputFile) )  
              #plt.close(fig)
      
      
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
              
              #fig = plt.figure()
              #plt.imshow(mature_mask)
              #plt.colorbar()
              #plt.title( "Mature mask")
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_"+"4th"+name_4Mask+"_Mature_mask.png"
              make_figure(mature_mask, obj_area, outputFile,colorbar = True,text_to_write = "Mature mask", vmin = 0, vmax = 1)
              #fig.savefig( create_dir(outputFile))
              #plt.close(fig)           
      
          
          developing_mask = np.zeros( (nx,ny)) 
          developing_mask[:,:] = -2
          if False:
              developing_mask = np.where( us>=4, developing_mask+1, developing_mask)
              developing_mask = np.where( cd>=3, developing_mask+1, developing_mask) # !!! NEW 01/04 changed to 3 because removed one cd indicator
          else:
              developing_mask = np.where( cd+us>=7, developing_mask+2, developing_mask)
          
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
           
          if plot_developing_mask:
              #fig = plt.figure()
              #plt.imshow(developing_mask)
              #plt.colorbar()
              #plt.title( "Developing mask")
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_4th"+name_4Mask+"_Developing_mask.png"
              make_figure(developing_mask, obj_area, outputFile,colorbar = True,text_to_write = "Developing mask", vmin = 0, vmax = 1)
              #fig.savefig( create_dir(outputFile))
              #plt.close(fig)     
              
                        
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
          
          mask_black = np.where(np.logical_and(np.logical_and(us<=2, cd<=2),gi<=2),0,1) #np.ones(us.shape) #
          
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
              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_4th"+name_4Mask+"_Forced_mask.png"
              make_figure(force_mask, obj_area, outputFile,colorbar = True,text_to_write = "Forcing mask", vmin = 0, vmax = 1)
              
              
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
              cirrus = np.where( cirrus == 1,1,0)
              if plot_mask_cirrus:

                  outputFile = out_dir +"/cosmo/Channels/indicators_in_time/masks/%s_%s_ThinCirrus_mask.png"%(yearS+monthS+dayS,hourS+minS)
                  make_figure(mature_mask, obj_area, outputFile,colorbar = True,text_to_write = "Thin Cirrus mask\n1 Test (GI7)", vmin = 0, vmax = 1)

              not_cirrus = np.where(cirrus == 1,0,1)
              mask = np.logical_and(mask,not_cirrus)
              
                    
          if clean_mask == 'skimage':
              if show_clouds != 'all':
                  mask = morphology.remove_small_objects(mask, min_cloud) #,connectivity=2)
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
                  mask = morphology.remove_small_objects(mask, min_cloud) #,connectivity=2)
                  mask = morphology.remove_small_objects(-mask, max_holes)                            
                  # Remove small white regions
                  mask = ndimage.binary_opening(-mask)
                  # Remove small black hole
                  mask = ndimage.binary_closing(mask) 
          elif clean_mask != 'no_cleaning':
              print("*** Error in main (Mecikalski.py)")
              print("    unknown clean_mask: ", clean_mask)
              quit()          
          

          print("-------------------     r min-max",(r.min(),r.max()))
          
        
          # copy red, green, blue to the rgbArray and apply mask  
          rgbArray = np.zeros( (nx,ny,4), 'uint8')
          rgbArray[..., 0] = r * mask
          rgbArray[..., 1] = g * mask
          rgbArray[..., 2] = b * mask
          if clean_mask != "no_cleaning":
              rgbArray[..., 0] = rgbArray[..., 0] * mask_black
              rgbArray[..., 1] = rgbArray[..., 1] * mask_black
              rgbArray[..., 2] = rgbArray[..., 2] * mask_black

          rgbArray[..., 3] = foregroud_alpha      
          
          sum_array = rgbArray[...,0]+rgbArray[..., 1]+rgbArray[..., 2]
          
          cleaning_text = deepcopy(clean_mask)
          
          if clean_mask != "no_cleaning":
                sum_labels = np.where(sum_array>=0,1,0)
                
                labels, numobjects = ndimage.label(sum_array)
                labels_id = np.unique(labels)
                
                for i in labels_id:
                    mask_current_cell = np.where(labels == i,1,0)
                    mean_us = sum(sum(us * mask_current_cell))/sum(sum(mask_current_cell))
                    area_cell = sum(sum(mask_current_cell))
                    
                    if  mean_us <= 3 and area_cell<=500:
                        labels = np.where(mask_current_cell==1,0,labels)
                
                mask_labels = np.where(labels > 0,1,0)
                if mask_labelsSmall_lowUS:
                    rgbArray[..., 0] = rgbArray[..., 0] * mask_labels
                    rgbArray[..., 1] = rgbArray[..., 1] * mask_labels
                    rgbArray[..., 2] = rgbArray[..., 2] * mask_labels          
                    
                    sum_array = rgbArray[...,0]+rgbArray[..., 1]+rgbArray[..., 2]
                
                cleaning_text = "removed Area<=500 & mean US <=3"
                                    
          if clean_mask != "no_cleaning":
               mask = mask * mask_labels
               mask = mask * mask_black
               
          if plot_final_mask:

              outputFile = out_dir +"/cosmo/Channels/indicators_in_time/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_4th"+name_4Mask+"_"+name_ForcedMask+"AdditionalMask_Final_mask.png"
              text_to_write = "Forth mask: %s\nForcen mask: %s\nCleaning: %s"%(name_4Mask,name_ForcedMask,cleaning_text)
              make_figure(mask, obj_area, outputFile,colorbar = True,text_to_write = "Final mask", vmin = 0, vmax = 1)

                        
          labels, numobjects = ndimage.label(mask)
          
          metadata = {}
          metadata['sat_nr']       = in_msg.sat_nr
          metadata['seviri_level'] = in_msg.reader_level
          metadata['cleaning']     = clean_mask
          metadata['masks']        = [name_4Mask, name_ForcedMask]
          metadata['downscaling']  = mode_downscaling
          metadata['rapid_scan_mode'] = rapid_scan_mode
          metadata['cloud_depth']           = n_tests_cd
          metadata['glaciation_indicators'] = n_tests_gi
          metadata['updraft_strength']      = n_tests_us
          
          if shelve_labels:
                labels = labels.astype('uint32') 
                filename = labels_dir + '/Labels_%s.shelve'%(yearS+monthS+dayS+hourS+minS)
                print("*** writing variables ", filename)
                myShelve = shelve.open(filename)
                # write data as dictionary into the shelve
                dict_labels = {'labels': labels, 'metadata': metadata}
                myShelve.update(dict_labels)
                # close the shelve
                myShelve.close()
          elif pickle_labels:
                labels = labels.astype('uint32') 
                pickle.dump( labels, open(create_dir(labels_dir +"/cosmo/Channels/labels/labels_"+yearS+monthS+dayS+hourS+minS+".p"), "wb" ) )
          
          if plot_labelled_objects:
                outputFile = out_dir +"/cosmo/Channels/indicators_in_time/labelled/"+yearS+monthS+dayS+"_"+hourS+minS+"_4th"+name_4Mask+"_"+name_ForcedMask+"AdditionalMask.png"
                make_figure(labels, obj_area, outputFile,colorbar = False,text_to_write = "Forth mask: %s\nForcen mask: %s\nCleaning: %s"%(name_4Mask,name_ForcedMask,cleaning_text), vmin = False, vmax = False)

          # set background_color for "no clouds" 
          rgbArray[sum_array<=0,0] = background_color[0] 
          rgbArray[sum_array<=0,1] = background_color[1] 
          rgbArray[sum_array<=0,2] = background_color[2] 
          # set transparency for "no clouds" 
          rgbArray[sum_array<=0,3] = background_alpha
      
          #c2File = (out_dir+"/cosmo/Channels/indicators_in_time/RGB"+maskS+"/%s_%s_C2rgb"+maskS+"4th"+name_4Mask+"_"+name_ForcedMask+"AdditionalMask.png") % (yearS+monthS+dayS,hourS+minS)
          c2File = ("/data/cinesat/out/"+"/%s_%s_C2rgb"+maskS+"4th"+name_4Mask+"_"+name_ForcedMask+"AdditionalMask.png") % (yearS+monthS+dayS,hourS+minS)
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
              #hrvFile = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/"+yearS+"-"+monthS+"-"+dayS+"_HRV_ccs4/MSG_HRV-ccs4_15"+monthS+dayS+hourS+minS+".png"
              if area == "ccs4":
                  #type_image = "_HRV"
                  type_image = "_IR-108"
              else:
                  #type_image = "_overview"
                  #type_image = "_HRV"
                  type_image = "_IR-108"
          

              hrvFile = "/data/cinesat/out//MSG"+type_image+"-"+area+"_"+yearS[2:]+monthS+dayS+hourS+minS+".png"
              #hrvFile = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/"+yearS+"-"+monthS+"-"+dayS+type_image+"_"+area+"/MSG"+type_image+"-"+area+"_15"+monthS+dayS+hourS+minS+".png"
              #hrvFile = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/HRoverview/MSG_HRoverview-"+area+"_15"+monthS+dayS+hourS+minS+".png"
              #out_file = create_dir( out_dir +"/cosmo/Channels/indicators_in_time/RGB-HRV"+maskS+"/"+yearS+monthS+dayS+"_"+hourS+minS+"_C2rgb-HRV_"+"4th"+name_4Mask+"_"+name_ForcedMask+"AdditionalMask.png" )
              out_file = create_dir( "/data/cinesat/out//MSG_C2rgb-"+type_image[1:]+"-"+area+"_"+yearS[2:]+monthS+dayS+hourS+minS+".png" )



              print("... create composite "+c2File+" "+hrvFile+" "+out_file)
              subprocess.call("/usr/bin/composite "+c2File+" "+hrvFile+" "+out_file, shell=True)
              print("... saved composite: display ", out_file, " &")
     
              if True: 
                  if in_msg.verbose:
                      print("... secure copy "+out_file+ " to "+in_msg.scpOutputDir)
                  subprocess.call("scp "+in_msg.scpID+" "+out_file+" "+in_msg.scpOutputDir+" 2>&1 &", shell=True)


          time_slot = time_slot + timedelta(minutes=5)
