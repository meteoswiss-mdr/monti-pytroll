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
from mpop.imageo.geo_image import GeoImage
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
import matplotlib as mpl
mpl.use('Agg')
import time
from time import strftime
import copy
from particles_displacement import particles_displacement
from properties_cells import properties_cells
from test_forecast import plot_forecast_area
from Cells import Cells
import numpy.ma as ma
import netCDF4
import pickle
import subprocess
import mpop
from mpop.imageo.HRWimage import prepare_figure 
import shelve

from trollimage.colormap import rainbow
from trollimage.image import Image as trollimage

from scipy import ndimage
from my_msg_module import check_input
#from astropy.convolution import MexicanHat2DKernel

from postprocessing import postprocessing

import inspect 

# ===============================

def _image2array(im):
    '''
    Utility function that converts an image file in 3 or 4 np arrays
    that can be fed into 'geo_image.GeoImage' in order to generate
    a PyTROLL GeoImage object.
    '''
    #im = Pimage.open(filepath).convert('RGB')
    (width, height) = im.size

    if im.mode == 'L':
        _grey = np.array(list(im.getdata(0)))/255.0; _grey = _grey.reshape((height, width))
        return _grey
    if im.mode == 'LA':
        _grey = np.array(list(im.getdata(0)))/255.0; _grey = _grey.reshape((height, width))
        _a    = np.array(list(im.getdata(1)))/255.0; _a = _a.reshape((height, width))
        return _grey, _a
    elif im.mode == 'RGB':
        _r = np.array(list(im.getdata(0)))/255.0; _r = _r.reshape((height, width))
        _g = np.array(list(im.getdata(1)))/255.0; _g = _g.reshape((height, width))
        _b = np.array(list(im.getdata(2)))/255.0; _b = _b.reshape((height, width))
        return _r, _g, _b
    elif im.mode == 'RGBA':
        _r = np.array(list(im.getdata(0)))/255.0; _r = _r.reshape((height, width))
        _g = np.array(list(im.getdata(1)))/255.0; _g = _g.reshape((height, width))
        _b = np.array(list(im.getdata(2)))/255.0; _b = _b.reshape((height, width))
        _a = np.array(list(im.getdata(3)))/255.0; _a = _a.reshape((height, width))
        return _r, _g, _b, _a
    else:
        "*** Error in  _image2array ("+inspect.getfile(inspect.currentframe())+")"
        "    unknown PIL_image mode: ", im.mode
        quit()

# ===============================

def pilimage2geoimage(pimage, area, timeslot):
    print (pimage.mode)
    if pimage.mode == 'L':
        (grey) = _image2array(pimage)
        gi = GeoImage((grey), area, timeslot, mode=pimage.mode)
    elif pimage.mode == 'LA':
        (grey,a) = _image2array(pimage)
        gi = GeoImage((grey,a), area, timeslot, mode=pimage.mode)
    elif pimage.mode == 'RGB':
        (r,g,b) = _image2array(pimage)
        gi = GeoImage((r,g,b), area, timeslot, mode=pimage.mode)
    elif pimage.mode == 'RGBA':
        (r,g,b,a) = _image2array(pimage)
        gi = GeoImage((r,g,b,a), area, timeslot, mode=pimage.mode)
    else:
        print ("*** Error in pilimage2geoimage ("+inspect.getfile(inspect.currentframe())+")")
        print ("    unknown PIL_image mode: ", pimage.mode)
        quit()
    return gi

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
        #if verbose:
         #   print("NO MASK ACTIVE!!!!!!!!!")
        if np.any(np.isnan(mod)):
            mod = ma.masked_where(np.isnan(mod), mod)
            #print("the invalid are NAN")
        else:
            mod = ma.masked_where(mod <= 0, mod)
            #if verbose:
            #    print("the invalid are <= 0")
    mod[mod.mask==True] = np.nan
    mod = fill_with_closest_pixel(mod) 
    mod[obs==True] = np.nan
    mod.mask = obs
    return mod
    
# ===============================

def downscale_array(array, mode='gaussian_225_125', mask=None):

    print ("    downscale with mode: ", mode)

    if not isinstance( array, (np.ndarray, np.generic) ):
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
        array[mask] = no_data
        array = fill_with_closest_pixel(array)

    # downscale array 
    array_downscaled = downscale_func(array, weights, mode='nearest')

    # restore mask
    if mask is not None:
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
           mpop.scene.SatelliteInstrumentScene (all loaded channels of the scene)
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


    if isinstance(data, np.ndarray):
        downscale_array(data, mode=mode, mask=mask)
        
    elif isinstance(data, mpop.scene.SatelliteInstrumentScene):  
        
        for chn in data.loaded_channels():

            # do not downscale cloud classes 
            if chn.name == "CT":
                continue 
            # comment: Shoud we downscale chn.name != "CTP", "CTH", "CTT"?

            print ("... downscale "+chn.name)
            if hasattr(data[chn.name], 'data'):
                data[chn.name].data = downscale_array(data[chn.name].data, mode=mode, mask=mask)
            else:
                print ("*** Warning in downscale ("+inspect.getfile(inspect.currentframe())+")")
                print ("    skip downscaling of ", chn.name, ", as this channel has no attribute: data" )

    return data
    
# ===============================

def make_figure(values, obj_area, outputFile, 
                colorbar=True, text_to_write=None, vmin=False, vmax=False, contour_value=None, linewidth=1):
    import matplotlib as mpl
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

    #obj_area = get_area_def(area)

    fig, ax = prepare_figure(obj_area) 

    mappable = plt.imshow(np.flipud(values), vmin = vmin, vmax = vmax, origin="lower")

    if contour_value is not None:
        plt.contour( values, contour_value, linewidths=linewidth, origin='upper' )
        #plt.contour( values, contour_value, linewidths=linewidth, origin='lower' )

    if text_to_write is not None:
        ax.text(0.95, 0.01, text_to_write,
                verticalalignment='bottom', horizontalalignment='right',
                transform=ax.transAxes,
                color='cyan', fontsize=15)
    position=fig.add_axes([0.93,0.2,0.02,0.35])  ## the parameters are the specified position you set: left, bottom, width, height
    if colorbar:
        color_bar = fig.colorbar(mappable,cax=position) ## 
        plt.setp(plt.getp(color_bar.ax.axes, 'yticklabels'), color='cyan')
        
    PIL_image = fig2img ( fig )

    PIL_image.save(create_dir(outputFile))                    # automatic choise of mode 
    #PIL_image.convert('RGBA').save(create_dir(outputFile))   # RGBA (4x8-bit pixels, true colour with transparency mask)
    #PIL_image.convert('I').save(create_dir(outputFile))      # I (32-bit signed integer pixels)
    print("... display ",outputFile," &")
    plt.close( fig)
    
    
def check_area(area_wanted):
    
    area_forecast = get_area_def("ccs4") #if you change this, because able larger forecast, make check based on NWC SAF!!!!!            
    x_min_forecast = area_forecast.area_extent[1]
    x_max_forecast = area_forecast.area_extent[3]
    y_min_forecast = area_forecast.area_extent[0]
    y_max_forecast = area_forecast.area_extent[2]
        
    area_wanted = get_area_def(area_wanted)
    x_min_wanted = area_wanted.area_extent[1]
    x_max_wanted = area_wanted.area_extent[3]
    y_min_wanted = area_wanted.area_extent[0]
    y_max_wanted = area_wanted.area_extent[2]
    
    if x_min_forecast <= x_min_wanted and y_min_forecast <= y_min_wanted and x_max_forecast >= x_max_wanted and y_max_forecast >= y_max_wanted:
        scale = "local"
    else:
        scale = "broad"
    
    print("*** the scale is being set to: ", scale)
    
    return scale

# ===============================



# ===============================


#if __name__ == '__main__':

def plot_coalition2(in_msg, time_slot, time_slotSTOP):
    
    import logging
    logging.basicConfig(level=logging.WARNING)
    #DEBUG - debug message
    #INFO - info message
    #WARNING - warn message
    #ERROR - error message
    #CRITICAL - critical message

    while time_slot <= time_slotSTOP:
      

          print("current time: ", str(time_slot))
          
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
      
          in_msg.datetime = time_slot
          
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
              print ("*** Waring, unknown type of sat_nr", type(in_msg.sat_nr))
              sat_nr_str = in_msg.sat_nr
                
          #RGBs = check_input(in_msg, in_msg.sat+sat_nr_str, in_msg.datetime)  # in_msg.sat_nr might be changed to backup satellite
          #if len(RGBs) != len(in_msg.RGBs):
          #    print ("*** Warning, input not complete.")
          #    print ("*** Warning, process only: ", RGBs)

          #print ("*** read data for ", in_msg.sat, str(in_msg.sat_nr), "seviri", time_slot)
          
          for i_try in range(30):

              RGBs = check_input(in_msg, in_msg.sat_str()+in_msg.sat_nr_str(), in_msg.datetime, RGBs=in_msg.RGBs)
              if len(RGBs) > 0:
                  # exit loop, if input is found
                  break
              else:
                  # else wait 20s and try again
                  import time
                  time.sleep(25)
                  
          
          # now read the data we would like to forecast
          global_data = GeostationaryFactory.create_scene(in_msg.sat_str(), in_msg.sat_nr_str(), "seviri", time_slot)
          #global_data_RGBforecast = GeostationaryFactory.create_scene(in_msg.sat, str(10), "seviri", time_slot)
      
          # area we would like to read
          area2load = "EuropeCanary95" #"ccs4" #c2"#"ccs4" #in_windshift.ObjArea
          area_loaded = get_area_def(area2load )#(in_windshift.areaExtraction)  

          print ("*** load data for ", in_msg.sat_str(), in_msg.sat_nr_str(), str(time_slot))
          # load product, global_data is changed in this step!
          area_loaded = load_products(global_data, in_msg.RGBs, in_msg, area_loaded, load_CTH=False) 

          for area in in_msg.areas:

                # see get_input_msg.py
                chosen_settings = in_msg.choose_coalistion2_settings(area)
                
                print ("  *******SETTINGS*******")
                print ("      nrt: ", in_msg.nrt)
                print ("      area: ", area)
                print ("      scale: ", chosen_settings['scale'])
                print ("      use_TB_forecast: ", chosen_settings['use_TB_forecast'])
                print ('      mode_downscaling: ', chosen_settings['mode_downscaling'])
                print ('      mask_labelsSmall_lowUS: ', chosen_settings['mask_labelsSmall_lowUS'])
                print ('      clean_mask: ', chosen_settings['clean_mask'])
                print ('      rapid_scan_mode: ', chosen_settings['rapid_scan_mode'])
                print ('      forth_mask: ', chosen_settings['forth_mask'])
                print ('      forced_mask: ', chosen_settings['forced_mask'])
                print ('      mask_cirrus: ', chosen_settings['mask_cirrus'])
                print ('      dt_forecast1: ', chosen_settings['dt_forecast1'])
                print ('      dt_forecast2: ', chosen_settings['dt_forecast2'])

                area_def = get_area_def(area)
                
                time_slot15 = time_slot - timedelta(minutes=chosen_settings['dt_forecast1'])
                time_slot30 = time_slot - timedelta(minutes=chosen_settings['dt_forecast2'])
                
                hour_forecast15S = "%02d" % (time_slot15.hour)
                min_forecast15S = "%02d" % (time_slot15.minute)
                
                hour_forecast30S = "%02d" % (time_slot30.hour)
                min_forecast30S = "%02d" % (time_slot30.minute)  
                
                dt_forecast1S = str(chosen_settings['dt_forecast1'])  
                dt_forecast2S = str(chosen_settings['dt_forecast2'])
                                
                if chosen_settings['forced_mask'] == 'IR_039_minus_IR_108':
                    in_msg.name_ForcedMask = 'IRdiff'
                elif chosen_settings['forced_mask'] == 'CloudType':
                    in_msg.name_ForcedMask = 'CT'
                elif chosen_settings['forced_mask'] == 'no_mask':
                    in_msg.name_ForcedMask = 'no'
                else:
                    print ("    unknown forcing mask -> applying no forcing mask", chosen_settings['forced_mask'])
                    in_msg.name_ForcedMask = 'no'
                
                # load satellte data
                if chosen_settings['scale'] == 'local' and in_msg.no_NWCSAF == False:
                    print ("... check for CTH observation (scale=", chosen_settings['scale']," no_NWCSAF=", in_msg.no_NWCSAF, ")")

                    for i_try in range(30):
                        # check if 'CTH' file is present
                        RGBs = check_input(in_msg, in_msg.sat_str()+in_msg.sat_nr_str(), in_msg.datetime, RGBs="CTH")
                        if len(RGBs) > 0:
                            # exit loop, if input is found
                            break
                        else:
                            # else wait 20s and try again
                            import time
                            time.sleep(25)
                    # load the cloud top height data
                    area_loaded = load_products(global_data, ['CTH'], in_msg, area_loaded )
                
                print ('... project data to desired area ', area)
                data = global_data.project(area, precompute=True)
                
                # fill placeholders in directory names with content
                outputDir = format_name(in_msg.outputDir, time_slot, area=area, rgb='C2rgb', sat=data.satname, sat_nr=data.sat_nr()) # !!! needs change
                labelsDir = format_name(in_msg.labelsDir, time_slot, area=area, rgb='label', sat=data.satname, sat_nr=data.sat_nr()) # !!! needs change
                    
                # determined 4th mask (small ice crystal or cloud type): get string for filename and load CloudType
                if chosen_settings['forth_mask'] == 'IR_039_minus_IR_108':
                    in_msg.name_4Mask = 'IRdiff'
                elif chosen_settings['forth_mask'] == 'IR_039_minus_IR_108_day_only':
                    in_msg.name_4Mask = 'IRdiffday'
                elif chosen_settings['forth_mask'] == 'NWCSAF':
                    in_msg.name_4Mask = 'NWCSAF'
                elif chosen_settings['forth_mask'] == 'CloudType' or chosen_settings['forth_mask'] == 'combined':
                    if chosen_settings['forth_mask'] == 'CloudType':
                        in_msg.name_4Mask = 'CT'
                    elif chosen_settings['forth_mask'] == 'combined':
                        in_msg.name_4Mask = 'com'
                    # load CloudType
                    scale = check_area(area)
                    if (scale == "local"):
                        global_CT_data = GeostationaryFactory.create_scene('Meteosat-9', "", "seviri", time_slot)
                    elif (scale == "broad"):    
                        from my_msg_module import get_last_SEVIRI_date
                        time_slot_MSG3 = get_last_SEVIRI_date(False, time_slot=time_slot)
                        global_CT_data = GeostationaryFactory.create_scene('Meteosat-10', "", "seviri", time_slot_MSG3)
                    else:
                        print ("*** Error in plot_coalition2 ("+inspect.getfile(inspect.currentframe())+")")
                        print ("    unknown area scale", area, scale )
                        quit() 
                    load_products(global_CT_data, ['CT'], in_msg, area_loaded ) 
                    CT_data = global_CT_data.project(area, precompute=True)
                    if "CloudType" in in_msg.aux_results:
                        outputFile = outputDir +"/aux_results/%s_%s_CloudType.png"%(yearS+monthS+dayS,hourS+minS)
                        img = GeoImage( CT_data['CT'].data, CT_data['CT'].area, CT_data.time_slot, mode="P", palette=CT_data['CT'].palette, fill_value=0 )
                        PIL_image = img.pil_image()
                        PIL_image.save(create_dir(outputFile))                    # automatic choise of mode 
                        print("... display ",outputFile," &")

                elif chosen_settings['forth_mask'] == 'no_mask':
                    in_msg.name_4Mask = 'none'
                else:
                    print ("*** Error in plot_coalition2 ("+inspect.getfile(inspect.currentframe())+")")
                    print ("    unknown 4th mask", chosen_settings['forth_mask'])
                    quit() 

                # print type(data)
                loaded_channels = [chn.name for chn in data.loaded_channels()]
                print ("... loaded_channels: ", loaded_channels)               
                if "CTH" in loaded_channels:
                    print ("    take CTH mask for downscaling")
                    mask_downscale = data['CTH'].data.mask
                else:
                    print ("    take "+loaded_channels[0]+" mask for downscaling")
                    mask_downscale = data[loaded_channels[0]].data.mask #to avoid error on Europe, anyway on Europe there shouldn't be downscaling

                print ('... downscaling', chosen_settings['mode_downscaling'])
                data = downscale(data, chosen_settings['mode_downscaling'], mask=mask_downscale)

                if 'IR_108' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results/"+yearS+monthS+dayS+"_"+hourS+minS+"_IR-108_"+area+".png"
                    print ("... save aux result: display "+outputFile)
                    make_figure(data['IR_108'].data, area_def, outputFile, colorbar=True,text_to_write = "IR_108 ", linewidth = 1)

                if 'mask_downscale' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results/"+yearS+monthS+dayS+"_"+hourS+minS+"_mask_downscale_"+area+".png"
                    print ("... save aux result: display "+outputFile)
                    make_figure(mask_downscale, area_def, outputFile, colorbar=True,text_to_write = "mask_downscale ", vmin=0, vmax=1, linewidth = 1)


                # create a cloud mask: if scale local based on CTH, else based on  where CTP can be derived 
                # -------------------
            
                nx,ny = data['IR_108'].data.shape
      
                #print type(data['CTP'].data)
                if chosen_settings['scale'] != 'local' or in_msg.no_NWCSAF == True:
                    mask_NoClouds = np.where(data['IR_108'].data < -10.0) # does this actually work??? (also no clouds should have BT)
                else:
                    data['CTH'].data = ma.masked_less(data['CTH'].data, 1) #1 to make sure 0 is also masked
                    mask_NoClouds = data['CTH'].data.mask
          
                nowcastDir = format_name(in_msg.nowcastDir, time_slot, area=area, rgb='channels', sat=data.satname, sat_nr=data.sat_nr()) # !!! needs change

                # read old brightness temperatures (if possible shifted by lagrangian cell movement)
                if chosen_settings['use_TB_forecast'] == True:
      
                    print ("*** read forecasted brightness temperatures")
                    print ("    ", nowcastDir+"%s_%s_WV_062_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S) )
                    wv_062_t15 = pickle.load( open( nowcastDir+"%s_%s_WV_062_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) ) 
                    print ("    ", nowcastDir+"%s_%s_WV_062_t%s.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S, dt_forecast2S) )                               
                    wv_062_t30 = pickle.load( open( nowcastDir+"%s_%s_WV_062_t%s.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S, dt_forecast2S), "rb" ) )
                            
                    print ("    ", nowcastDir+"%s_%s_WV_073_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S) )
                    wv_073_t15 = pickle.load( open( nowcastDir+"%s_%s_WV_073_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) )
                    wv_073_t30 = pickle.load( open( nowcastDir+"%s_%s_WV_073_t%s.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S, dt_forecast2S), "rb" ) )           
                
                    print ("    ", nowcastDir+"%s_%s_IR_097_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S) )
                    ir_097_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_097_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) )
                    ir_097_t30 = pickle.load( open( nowcastDir+"%s_%s_IR_097_t%s.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S, dt_forecast2S), "rb" ) )  
                
                    print ("    ", nowcastDir+"%s_%s_IR_108_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S) )
                    ir_108_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_108_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) )
                    ir_108_t30 = pickle.load( open( nowcastDir+"%s_%s_IR_108_t%s.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S, dt_forecast2S), "rb" ) )  
                    
                    print ("    ", nowcastDir+"%s_%s_IR_134_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S) )
                    ir_134_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_134_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) )
                    ir_134_t30 = pickle.load( open( nowcastDir+"%s_%s_IR_134_t%s.p"%(yearS+monthS+dayS,hour_forecast30S+min_forecast30S, dt_forecast2S), "rb" ) ) 
                
                    print ("    ", nowcastDir+"%s_%s_IR_087_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S) )
                    ir_087_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_087_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) ) 
                    
                    print ("    ", nowcastDir+"%s_%s_IR_120_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S) )
                    ir_120_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_120_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) ) 
                    
                    print ("    ", nowcastDir+"%s_%s_IR_039_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S) )
                    ir_039_t15 = pickle.load( open( nowcastDir+"%s_%s_IR_039_t%s.p"%(yearS+monthS+dayS,hour_forecast15S+min_forecast15S, dt_forecast1S), "rb" ) ) 

                    downscalings = [wv_062_t15[1], wv_062_t30[1], wv_073_t15[1], wv_073_t30[1], ir_097_t15[1], ir_097_t30[1],
                                    ir_108_t15[1], ir_108_t30[1], ir_134_t15[1], ir_134_t30[1], ir_087_t15[1], ir_120_t15[1], ir_039_t15[1]]
    
                    #check if downscaling you are applying matches with the downscaling applied when producing the forecasts
                    if True:
                        if any(bz != chosen_settings['mode_downscaling'] for bz in downscalings):
                            print ("The downscaling technique applied for the production of forecast differs from that chosen here")
                            print ("current technique: ", chosen_settings['mode_downscaling'], "; in input ", in_msg.chosen_settings['mode_downscaling'])
                            print ("technique forecast: ", list(set(downscalings)) )
                            quit()
      
                    print("...correct downscaling: ", chosen_settings['mode_downscaling'])
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
      
                else:
                    # no forecasted brightness temperature available, use old observations 
                    
                    # now read the observations of the channels at -30 min
                    print ("*** read data for ", in_msg.sat_str(),in_msg.sat_nr_str(), "seviri", time_slot30)
                    
                    global_data30 = GeostationaryFactory.create_scene(in_msg.sat_str(),in_msg.sat_nr_str(), "seviri", time_slot30)
                    # area we would like to read
                    area_loaded = get_area_def(area2load)#(in_windshift.areaExtraction)  
                    # load product, global_data is changed in this step!
                    area_loaded = load_products(global_data30, in_msg.channels30, in_msg, area_loaded)
                    data30 = global_data30.project(area, precompute=True)           
                    data30 = downscale(data30,chosen_settings['mode_downscaling'],mask = mask_NoClouds) #mask = data30[in_msg.channels30[0].data.mask)      
                    
                    # read the observations of the channels at -15 min
                    print ("*** read data for ", in_msg.sat_str(),in_msg.sat_nr_str(), "seviri", time_slot15)
                    global_data15 = GeostationaryFactory.create_scene(in_msg.sat_str(),in_msg.sat_nr_str(), "seviri", time_slot15)
                    # area we would like to read
                    area_loaded15 = get_area_def(area2load)#(in_windshift.areaExtraction)  
                    # load product, global_data is changed in this step!
                    area_loaded15 = load_products(global_data15, in_msg.channels15, in_msg, area_loaded15)
                    data15 = global_data15.project(area, precompute=True)              
                    data15 = downscale(data15,chosen_settings['mode_downscaling'],mask = mask_NoClouds) #mask = data30[in_msg.channels30[0].data.mask)
                    
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
                    
                if 'IR_108_t1' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results/"+yearS+monthS+dayS+"_"+hourS+minS+"_IRR-108-t1_"+area+".png"
                    print ("... save aux result: display "+outputFile)
                    make_figure(ir_108_t15, area_def, outputFile, colorbar=True, text_to_write="IRR_108 "+str(chosen_settings['dt_forecast1']), linewidth = 1)
                if 'IR_108_t2' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results/"+yearS+monthS+dayS+"_"+hourS+minS+"_IRR-108-t2_"+area+".png"
                    print ("... save aux result: display "+outputFile)
                    make_figure(ir_108_t30, area_def, outputFile, colorbar=True, text_to_write="IRR_108 "+str(chosen_settings['dt_forecast2']), linewidth = 1)   
                    
                # force the brightness temperatures to the current (observed) cloud mask 
                ir_120_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_120_t15), mask_NoClouds)
            
                wv_062_t15 = force_to_observed_cloud_mask(ma.masked_array(wv_062_t15), mask_NoClouds) #ma.masked_where(a <= 2, a)
            
                wv_062_t30 = force_to_observed_cloud_mask(ma.masked_array(wv_062_t30), mask_NoClouds)
                                                                    
                wv_073_t15 = force_to_observed_cloud_mask(ma.masked_array(wv_073_t15), mask_NoClouds)
                wv_073_t30 = force_to_observed_cloud_mask(ma.masked_array(wv_073_t30), mask_NoClouds)
                                                                    
                ir_097_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_097_t15), mask_NoClouds)
                ir_097_t30 = force_to_observed_cloud_mask(ma.masked_array(ir_097_t30), mask_NoClouds)
                                                                    
                ir_108_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_108_t15), mask_NoClouds)
                ir_108_t30 = force_to_observed_cloud_mask(ma.masked_array(ir_108_t30), mask_NoClouds)
                                                                    
                ir_134_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_134_t15), mask_NoClouds)
                ir_134_t30 = force_to_observed_cloud_mask(ma.masked_array(ir_134_t30), mask_NoClouds)
                                                                    
                ir_087_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_087_t15), mask_NoClouds)
                                                                    
                ir_120_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_120_t15), mask_NoClouds)
                                                                    
                ir_039_t15 = force_to_observed_cloud_mask(ma.masked_array(ir_039_t15), mask_NoClouds)
            
                if 'IR_108_t1' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results/"+yearS+monthS+dayS+"_"+hourS+minS+"_IR-108-t1_"+area+".png"
                    print ("... save aux result: display "+outputFile)
                    make_figure(ir_108_t15, area_def, outputFile, colorbar=True, text_to_write="IR_108 "+str(chosen_settings['dt_forecast1']), linewidth = 1)
                if 'IR_108_t2' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results/"+yearS+monthS+dayS+"_"+hourS+minS+"_IR-108-t2_"+area+".png"
                    print ("... save aux result: display "+outputFile)
                    make_figure(ir_108_t30, area_def, outputFile, colorbar=True, text_to_write="IR_108 "+str(chosen_settings['dt_forecast2']), linewidth = 1)      
      
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
                cd = np.where( cloud_depth[0,:,:] >  th_cd[0], cd+1, cd );   n_tests_cd+=1. ;   #n_tests_cd+=1.# !!! changed from - 16.0
                cd = np.where( cloud_depth[1,:,:] >  th_cd[1], cd+1, cd );   n_tests_cd+=1. ;   #n_tests_cd+=1.# !!! changed from -7.5
                cd = np.where( cloud_depth[2,:,:] <  th_cd[2], cd+1, cd );   n_tests_cd+=1. ;   #n_tests_cd+=1.
                cd = np.where( cloud_depth[3,:,:] >  th_cd[3], cd+1, cd );   n_tests_cd+=1. ;   #n_tests_cd=1.
                cd = np.where( cloud_depth[4,:,:] >  th_cd[4], cd+1, cd );   n_tests_cd+=1. ;   #n_tests_cd+=1.
                #cd = np.where( cloud_depth[5,:,:] <  th_cd[5], cd+1, cd );   n_tests_cd+=1. ;   #n_tests_cd=1. # !!! changed DEACTIVATED
                
                #cirrus = np.where( cloud_depth[5,:,:]           >  th_cirrus ,cirrus +1, cirrus)
                
                cd = np.where(mask_NoClouds == True, 0, cd)
                
                
                #cd = np.where( mask_NoClouds==1,0,cd)
      
                if 'tests_optical_thickness' in in_msg.aux_results:
                    for i in range( 0,cloud_depth.shape[0]):
                          item = cloud_depth[i,:,:]
                          item[mask_NoClouds==True] = np.nan
                          outputFile = outputDir +"/aux_results/%s_%s_Cloud_depth%s.png"%(yearS+monthS+dayS,hourS+minS,str(i+1))
                          make_figure(item, area_def,  outputFile,colorbar = True,text_to_write = "Cloud depth %s"%(str(i+1)), vmin = vmin_cd[i], vmax = vmax_cd[i], contour_value = [th_cd[i]], linewidth = 1)
                          print ("... display ", outputFile, " &")
       
                    item = cloud_depth[5,:,:]
                    item[mask_NoClouds==True] = np.nan
                    
                    outputFile = outputDir +"/aux_results/%s_%s_Cloud_depth%s_cirrus.png"%(yearS+monthS+dayS,hourS+minS,str(i+1))
                    make_figure(item, area_def, outputFile, colorbar = True, text_to_write = "Cloud depth 6", vmin = vmin_cd[5], vmax = vmax_cd[5], contour_value = [th_cirrus], linewidth = 1)
                    print ("... display ", outputFile, " &")   
                
                if 'indicator_optical_thickness' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results//%s_%s_Cloud_Depth.png"%(yearS+monthS+dayS,hourS+minS)
                    make_figure(cd, area_def, outputFile, colorbar = True, text_to_write = "Cloud Depth", vmin = 0, vmax = n_tests_cd)
            
            
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
                gi = np.where( np.logical_or(glaciation_indicators[6,:,:]<-5.0, glaciation_indicators[6,:,:]>-1.5), gi+1, gi);   n_tests_gi+=1.
                
                cirrus = np.where( glaciation_indicators[6,:,:] < -5.0 ,cirrus +1, cirrus)
                
                gi = np.where(mask_NoClouds == True, 0, gi)
                #gi = gi*mask_NoClouds
                #gi = np.where( mask_NoClouds==1,0,gi)
            
                if 'tests_glationation' in in_msg.aux_results:
                    for i in range( 0,glaciation_indicators.shape[0]):
                        item = glaciation_indicators[i,:,:]
                        item[mask_NoClouds==True] = np.nan
                        
                        #fig = plt.figure()
                        #plt.imshow( item, vmin = vmin_gi[i], vmax = vmax_gi[i])
                        #plt.colorbar()
                        if i == 6:
                            contour_value = [-5.,-1.5]
                        else:
                            contour_value = [th_gi[i]]
                        #plt.title( "Glaciation_Indicators%s"%(str(i+1)))
                        outputFile = outputDir +"/aux_results/%s_%s_Glaciation_Indicators%s.png"%(yearS+monthS+dayS,hourS+minS,str(i+1))
                        make_figure(item,area_def,  outputFile, colorbar = True, text_to_write = "Glaciation_Indicators%s"%(str(i+1)), vmin = vmin_gi[i], vmax = vmax_gi[i], contour_value = contour_value) 
                        #fig.savefig( create_dir(outputFile) ) 
                        #plt.close(fig)
                        #print ("... display ", outputFile, " &")
            
                if 'indicator_glationation' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results//%s_%s_Glaciation_indicators.png"%(yearS+monthS+dayS,hourS+minS)
                    make_figure(gi, area_def, outputFile,colorbar = True,text_to_write = "Glaciation Indicators", vmin = 0, vmax = n_tests_gi)      
      
      
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
                #count_null = np.where( mask_NoClouds==1,1,0)
                #print sum( sum( count_null))
                
                us = np.where(mask_NoClouds == True, 0, us)
                #us = us*mask_NoClouds
                #us = np.where( mask_NoClouds==1,0,us)
                
                if 'tests_updraft' in in_msg.aux_results:
                    for i in range( updraft_strength.shape[0]):
                        item = updraft_strength[i,:,:]
                        item[mask_NoClouds==True] = np.nan
                        outputFile = outputDir +"/aux_results/%s_%s_Updraft_strength_test%s.png"%(yearS+monthS+dayS,hourS+minS,str(i+1))
                        make_figure(item, area_def, outputFile,colorbar = True,text_to_write = "Updraft Strength %s"%(str(i+1)), vmin = vmin_us[i], vmax = vmax_us[i], contour_value = [th_us[i]])
            
                if 'indicator_updraft' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results/%s_%s_Updraft_strength_mask.png"%(yearS+monthS+dayS,hourS+minS)
                    make_figure(us, area_def, outputFile,colorbar = True,text_to_write = "Updraft Strength", vmin = 0, vmax = n_tests_us)
                
            
                # test for SMALL ICE CRYSTALS (this test works only at daytime) 
                # -------------------------------------------------------------
                IR_039_minus_IR_108 = data['IR_039'].data - data['IR_108'].data  # also needed in code later
                if 'tests_small_ice' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results/%s_%s_Small_ice_test.png"%(yearS+monthS+dayS,hourS+minS)
                    make_figure(IR_039_minus_IR_108, area_def, outputFile, colorbar=True, 
                                text_to_write="IR039 minus IR108", vmin=False, vmax=False, contour_value = [developing_th_chDiff, mature_th_chDiff])

                # calculate the mask for mature thunderstorms: sufficient ice (gi glaciantion indicators), sufficient cd (cloud depth), and forth mask (small ice crystals or cloud tpye)
                mature_mask = np.zeros( (nx,ny)) 
                mature_mask[:,:] = -2
                mature_mask = np.where( gi>=2,                     mature_mask+1, mature_mask)
                mature_mask = np.where( cd>=4,                     mature_mask+1, mature_mask)   # !!! changed from 5 to 4 !!! NEW 01/04 changed to 3 because removed one cd indicator
                
                if chosen_settings['forth_mask'] != 'no_mask': 
 
                    print ("... check forth mask, ", chosen_settings['forth_mask'] )
                    # initialize the mask with zeros
                    si = np.zeros( (nx,ny) ) 

                    if chosen_settings['forth_mask'] == 'CloudType':
                        ## search if CloudType is in marture_ct, if so set si to True (==1) 
                        si = np.in1d(CT_data['CT'].data, mature_ct).reshape(CT_data['CT'].data.shape[0],CT_data['CT'].data.shape[1])
                        outputFile = outputDir +"/aux_results/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_"+"CTmask_for_mature_clouds.png"
                        make_figure(si, area_def, outputFile,colorbar=True, text_to_write="CT mask for mature clouds", vmin=0, vmax=1 )
                        mature_mask += si
                      
                    elif chosen_settings['forth_mask'] == 'IR_039_minus_IR_108':
                        si = np.where( IR_039_minus_IR_108 >= mature_th_chDiff, si+1, si )
                        mature_mask += si

                    elif chosen_settings['forth_mask'] == 'IR_039_minus_IR_108_day_only':
                        from pyorbital.astronomy import sun_zenith_angle
                        lonlats = data['IR_108'].area.get_lonlats()
                        sza = sun_zenith_angle(time_slot, lonlats[0], lonlats[1])
                        # for sza > 72 degree the channel diff is not good anymore...
                        si = np.where( ((IR_039_minus_IR_108 >= mature_th_chDiff) | (sza > 72)), si+1, si )    
                        mature_mask += si

                    elif chosen_settings['forth_mask'] == 'NWCSAF':
                        # NWCSAF uses following three criteria to identify semitransparent clouds:
                        # T10.8-T12.0, T8.7-T10.8     or T3.9-T10.8 (last one is different during day)
                        si = np.where( (data['IR_120'].data - data['IR_108'].data) >= -1.0, si+1, si )  # glaciation indicator 7 test == -1.0
                        #si = np.where( (data['IR_087'].data - data['IR_120'].data) <=  2.6 , si+1, si )   # cloud depth 6 test == 2.2
                        mature_mask += si

                    elif chosen_settings['forth_mask'] == 'combined':
                        from pyorbital.astronomy import sun_zenith_angle
                        lonlats = data['IR_108'].area.get_lonlats()
                        sza = sun_zenith_angle(time_slot, lonlats[0], lonlats[1])
                        # for sza < 72 degree, check the channel difference ...
                        mask_day   = np.where( ((IR_039_minus_IR_108 >= mature_th_chDiff) & (sza < 72)), True, False )
                        outputFile = outputDir +"/aux_results/%s_%s_mask_day.png"%(yearS+monthS+dayS,hourS+minS)
                        make_figure(mask_day, area_def, outputFile, colorbar=True, text_to_write = "mask day", vmin=0, vmax=1)
                        # for sza >= 72 degree, check the cloud types  
                        mask_night_ct = np.in1d(CT_data['CT'].data, mature_ct).reshape(CT_data['CT'].data.shape[0],CT_data['CT'].data.shape[1])
                        mask_night = np.where( mask_night_ct & (sza > 72), True, False )
                        outputFile = outputDir +"/aux_results/%s_%s_mask_night.png"%(yearS+monthS+dayS,hourS+minS)
                        make_figure(mask_night, area_def, outputFile, colorbar=True, text_to_write = "mask night", vmin=0, vmax=1)
                        # combine both masks with bitwise logical or
                        si = np.where( mask_day | mask_night, 1, 0) 
                        outputFile = outputDir +"/aux_results/%s_%s_mask_combined.png"%(yearS+monthS+dayS,hourS+minS)
                        make_figure(si, area_def, outputFile, colorbar=True, text_to_write = "mask combined", vmin=0, vmax=1)
                        mature_mask += si

                    else:
                        print ("*** Error in plot_coalition2 ("+inspect.getfile(inspect.currentframe())+")")
                        print ("    unknown input option: forth_mask", chosen_settings['forth_mask'] )
                        quit()
                        
                    if 'fourth_mask' in in_msg.aux_results:
                        outputFile = outputDir +"/aux_results/%s_%s_fourth_mask.png"%(yearS+monthS+dayS,hourS+minS)
                        make_figure(si, area_def, outputFile, colorbar=True, text_to_write="forth_mask = %s"%chosen_settings['forth_mask'] , vmin = 0, vmax = 1)

                    mature_mask = np.where( mature_mask==1, 1, 0) # start counting at -2  (so 1 is mature thunderstorms = -2+1+1+1)
                else:
                    si = np.zeros( (nx,ny) )
                    si = np.where(data['IR_108'].data>0, si+1, si)  # just a mask to get rid of the space outside the MSG disk 
                    mature_mask += si
                    mature_mask = np.where( mature_mask==1, 1, 0) # start counting at -2  (so 1 is mature thunderstorms = -2+1+1+1)
                    #mature_mask = np.where( mature_mask==0, 1, 0) # start counting at -2  (so 0 is mature thunderstorms = -2+1+1  )
                
                if 'mature_mask' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_"+"4th"+in_msg.name_4Mask+"_Mature_mask.png"
                    make_figure(mature_mask, area_def, outputFile,colorbar=True, text_to_write="Mature mask", vmin=0, vmax=1 )
            
                
                developing_mask = np.zeros( (nx,ny)) 
                developing_mask[:,:] = -2
                if False: #older version, changed because indicators almost the same but one "more dangerous" (closer to interesting areas)
                    developing_mask = np.where( us>=4, developing_mask+1, developing_mask)
                    developing_mask = np.where( cd>=3, developing_mask+1, developing_mask) # !!! NEW 01/04 changed to 3 because removed one cd indicator
                else:
                    developing_mask = np.where( cd+us>=7, developing_mask+2, developing_mask)
                

                if chosen_settings['forth_mask']!='no_mask':
                    si = np.zeros( (nx,ny) ) 
                    if chosen_settings['forth_mask'] == 'CloudType':
                        ## search if CloudType is in developing_ct, if so set si to True (==1) 
                        si = np.in1d(CT_data['CT'].data, developing_ct).reshape(CT_data['CT'].data.shape[0],CT_data['CT'].data.shape[1])
                        outputFile = outputDir +"/aux_results/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_"+"CTmask_for_developing_clouds.png"
                        make_figure(si, area_def, outputFile,colorbar=True, text_to_write="CT mask for developing clouds", vmin=0, vmax=1 )
                        developing_mask += si

                    elif chosen_settings['forth_mask'] == 'IR_039_minus_IR_108':
                            developing_mask = np.where(  IR_039_minus_IR_108 > developing_th_chDiff,               developing_mask+1, developing_mask)

                    elif chosen_settings['forth_mask'] == 'IR_039_minus_IR_108_day_only':
                            developing_mask = np.where( (IR_039_minus_IR_108 > developing_th_chDiff) | (sza > 72), developing_mask+1, developing_mask)

                    elif chosen_settings['forth_mask'] == 'NWCSAF':
                        # NWCSAF uses following three criteria to identify semitransparent clouds:
                        #     T10.8-T12.0, T8.7-T10.8     or T3.9-T10.8 (last one is different during day)
                        si = np.where( (data['IR_120'].data - data['IR_108'].data) >= -1.0, si+1, si )  # glaciation indicator 7 test == -1.0
                        #si = np.where( (data['IR_087'].data - data['IR_120'].data) <=  2.6 , si+1, si )   # cloud depth 6 test == 2.2
                        developing_mask += si

                    elif chosen_settings['forth_mask'] == 'combined':
                        #from pyorbital.astronomy import sun_zenith_angle
                        #lonlats = data['IR_108'].area.get_lonlats()
                        #sza = sun_zenith_angle(time_slot, lonlats[0], lonlats[1])
                        # for sza < 72 degree, check the channel difference ...
                        mask_day   = np.where( ((IR_039_minus_IR_108 >= developing_th_chDiff) | (sza < 72)), True, False )
                        # for sza >= 72 degree, check the cloud types  
                        mask_night = np.in1d(CT_data['CT'].data, developing_ct).reshape(CT_data['CT'].data.shape[0],CT_data['CT'].data.shape[1])
                        # combine both masks with bitwise logical or
                        si = np.where( mask_day | mask_night, 1, 0) 
                        developing_mask += si
                    else:
                        print ("*** Error in plot_coalition2 ("+inspect.getfile(inspect.currentframe())+")")
                        print ("    unknown input option: forth_mask", chosen_settings['forth_mask'] )
                        quit()
                    developing_mask = np.where( developing_mask==1, 1, 0 )  # start counting at -2  (so 1 is developing thunderstorms = -2+1+1+1)
                else:
                    developing_mask = np.where( developing_mask==0, 1, 0 )  # start counting at -2  (so 0 is developing thunderstorms = -2+1+1  )
                 

                print ("*******************************************!!!!!!!!!!!!!!!!!!!!!!!")
                if 'developing_mask' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_4th"+in_msg.name_4Mask+"_Developing_mask.png"
                    make_figure(developing_mask, area_def, outputFile,colorbar = True,text_to_write = "Developing mask", vmin = 0, vmax = 1)              
                              
                cw = ContourWriterAGG( in_msg.mapDir )
            
                print ("... create the false color composite (r-g-b) = (", rgb_display,")")
      
                if rgb_display == 'us-cd-gi':
                    r = cmin_us + (us/n_tests_us) * (cmax_us - cmin_us)
                    g = cmin_cd + (cd/n_tests_cd) * (cmax_cd - cmin_cd)
                    b = cmin_gi + (gi/n_tests_gi) * (cmax_gi - cmin_gi)
                elif rgb_display == 'cd-us-gi':
                    # this is the currect pre-operational setting
                    r = cmin_cd + (cd/n_tests_cd) * (cmax_cd - cmin_cd)
                    g = cmin_us + (us/n_tests_us) * (cmax_us - cmin_us)
                    b = cmin_gi + (gi/n_tests_gi) * (cmax_gi - cmin_gi)
                else: 
                    print ("*** Error in main ("+inspect.getfile(inspect.currentframe())+")")
                    print ("    unknown rgb illustration", rgb_display)
                    quit()
                
                mask_black = np.where(np.logical_and(np.logical_and(us<=2, cd<=2),gi<=2),0,1) #np.ones(us.shape) #
                
                # fix upper and lower limit of the color, if scaled beyond the range
                r[np.where(r>255)] = 255
                r[np.where(r<  0)] =   0
                g[np.where(g>255)] = 255
                g[np.where(g<  0)] =   0
                b[np.where(b>255)] = 255
                b[np.where(b<  0)] =   0
      
                # modify colors for day tests only
                if in_msg.modify_day_color:
                    print ("*** Modify day colors")
                    from pyorbital.astronomy import sun_zenith_angle
                    lonlats = data['IR_108'].area.get_lonlats()
                    sza = sun_zenith_angle(time_slot, lonlats[0], lonlats[1])
                    # for daytime (sza < 72 degree) do channel check the channel diff is not good anymore...
                    index_day = np.where( (IR_039_minus_IR_108 >= mature_th_chDiff) & (0 < sza) & (sza < 72) & mature_mask & (us < 3) )  ### test mature_mask & (not developing_mask)
                    # add 100 to the blue channel (max saturation at 255)
                    b[index_day] = np.where(b[index_day]+110<255, b[index_day]+110, 255)
                    # substract 50 from the red channel (min saturation is 0)
                    r[index_day] = np.where(r[index_day]- 70<0,   0,    r[index_day]-70)

                force_mask = np.zeros((nx,ny))
                
                if chosen_settings['forced_mask'] == 'CloudType':
                    for ct in range(0,len(cloud_type_forced)):
                        cl_typ = cloud_type_forced[ct]
                        force_mask = np.where(data['CT'].data == cl_typ,1,force_mask)
                elif chosen_settings['forced_mask'] == 'IR_039_minus_IR_108':  
                        force_mask = np.where(IR_039_minus_IR_108 >= force_th_chDiff,1,0)
                elif chosen_settings['forced_mask'] !='no_mask': 
                    print ("*** Error in main ("+inspect.getfile(inspect.currentframe())+")")
                    print ("    unknown forcing mask -> applying no forcing mask", chosen_settings['forced_mask'])     
            
                if 'forced_mask' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_4th"+in_msg.name_4Mask+"_Forced_mask.png"
                    make_figure(force_mask, area_def, outputFile,colorbar = True,text_to_write = "Forcing mask", vmin = 0, vmax = 1)
                    
                    
                if in_msg.show_clouds == 'all':
                    mask  =  np.ones(wv_062_t15.shape, dtype=bool)
                    maskS = '_all'
                elif in_msg.show_clouds == 'developing':
                    mask  = developing_mask
                    maskS = '_dev'
                elif in_msg.show_clouds == 'mature':
                    mask  = mature_mask
                    maskS = '_mat'
                elif in_msg.show_clouds == 'developing_and_mature':
                    mask  = np.logical_or(mature_mask==1,developing_mask==1)
                    maskS = '_dam'
                else:
                    print ("*** Error in main ("+inspect.getfile(inspect.currentframe())+")")
                    print ("    unknown show_clouds: ", in_msg.show_clouds)
                    quit()
                
                mask = np.logical_or(mask==1,force_mask==1)
                
                
                if chosen_settings['mask_cirrus']:
                    cirrus = np.where( cirrus == 1,1,0)
                    if 'mask_cirrus' in in_msg.aux_results: 
                        outputFile = outputDir +"/aux_results/masks/%s_%s_ThinCirrus_mask.png"%(yearS+monthS+dayS,hourS+minS)
                        make_figure( mature_mask, area_def, outputFile, colorbar = True, text_to_write = "Thin Cirrus mask\n1 Test (GI7)", vmin = 0, vmax = 1 )
      
                    not_cirrus = np.where(cirrus == 1,0,1)
                    mask = np.logical_and( mask, not_cirrus )

                
                          
                if chosen_settings['clean_mask'] == 'skimage':
                    if in_msg.show_clouds != 'all':
                        from skimage import morphology
                        mask = morphology.remove_small_objects(mask, min_cloud) #,connectivity=2)
                        mask = morphology.remove_small_objects(~mask, max_holes)
                        mask = deepcopy(~mask)
                elif chosen_settings['clean_mask'] == 'scipy':        
                    if in_msg.show_clouds != 'all':
                        # Remove small white regions
                        mask = ndimage.binary_opening(mask)
                        # Remove small black hole
                        mask = ndimage.binary_closing(mask)  
                elif chosen_settings['clean_mask'] == 'both':
                    if in_msg.show_clouds != 'all':
                        from skimage import morphology
                        mask = morphology.remove_small_objects(mask, min_cloud) #,connectivity=2)
                        mask = morphology.remove_small_objects(~mask, max_holes)                            
                        # Remove small white regions
                        mask = ndimage.binary_opening(~mask)
                        # Remove small black hole
                        mask = ndimage.binary_closing(mask) 
                elif chosen_settings['clean_mask'] != 'no_cleaning':
                    print ("*** Error in main ("+inspect.getfile(inspect.currentframe())+")")
                    print ("    unknown clean_mask: ", chosen_settings['clean_mask'])
                    quit()          
                
      
                print ("-------------------     r min-max",(r.min(),r.max()))
                
              
                if in_msg.parallax_correction:
                    from mpop.channel import Channel
                        # add rgb array as channel to a GeostationaryFactory object
                    c2_data = GeostationaryFactory.create_scene(in_msg.sat_str(), in_msg.sat_nr_str(), "seviri", time_slot)
                    c2_data.channels.append(Channel(name='r',   wavelength_range=[0.,0.,0.], resolution=1000., data=r,                area=area))  
                    c2_data.channels.append(Channel(name='g',   wavelength_range=[0.,0.,0.], resolution=1000., data=g,                area=area))
                    #print ("type(g)",type(g), g.dtype, g.shape)
                    c2_data.channels.append(Channel(name='b',   wavelength_range=[0.,0.,0.], resolution=1000., data=b,                area=area))
                    #print ("type(data['CTH'].data)",type(data['CTH'].data.data), data['CTH'].data.dtype, data['CTH'].data.shape )
                    #c2_data.channels.append(Channel(name='CTH', wavelength_range=[0.,0.,0.], resolution=1000., data=data['CTH'].data.data, area=area))

                    loaded_products = [chn.name for chn in c2_data.loaded_channels()]
                    if in_msg.verbose:
                        print ("    perform parallax correction for loaded channels: ", loaded_products)

                    c2_data = c2_data.parallax_corr(cth=data['CTH'].data, fill=in_msg.parallax_gapfilling, estimate_cth=in_msg.estimate_cth, replace=True)
                    r = c2_data['r'].data
                    g = c2_data['g'].data
                    b = c2_data['b'].data
                    del c2_data


                # copy red, green, blue to the rgbArray and apply mask  
                rgbArray = np.zeros( (nx,ny,4), 'uint8')
                rgbArray[..., 0] = r * mask
                rgbArray[..., 1] = g * mask
                rgbArray[..., 2] = b * mask

                if chosen_settings['clean_mask'] != "no_cleaning":
                    rgbArray[..., 0] = rgbArray[..., 0] * mask_black
                    rgbArray[..., 1] = rgbArray[..., 1] * mask_black
                    rgbArray[..., 2] = rgbArray[..., 2] * mask_black
      
                rgbArray[..., 3] = foregroud_alpha      
                
                sum_array = rgbArray[...,0]+rgbArray[..., 1]+rgbArray[..., 2]
                
                cleaning_text = deepcopy(chosen_settings['clean_mask'])
                
                if chosen_settings['clean_mask'] != "no_cleaning":
                      sum_labels = np.where(sum_array>=0,1,0)
                      
                      labels, numobjects = ndimage.label(sum_array)
                      labels_id = np.unique(labels)
                      
                      for i in labels_id:
                          mask_current_cell = np.where(labels == i,1,0)
                          mean_us = sum(sum(us * mask_current_cell))/sum(sum(mask_current_cell))
                          area_cell = sum(sum(mask_current_cell))
                          
                          if  mean_us <= mask_labelsSmall_lowUS_maxUS and area_cell<=mask_labelsSmall_lowUS_maxArea:
                          
                              labels = np.where(mask_current_cell==1,0,labels)
                      
                      mask_labels = np.where(labels > 0,1,0)
                      if chosen_settings['mask_labelsSmall_lowUS']:
                          rgbArray[..., 0] = rgbArray[..., 0] * mask_labels
                          rgbArray[..., 1] = rgbArray[..., 1] * mask_labels
                          rgbArray[..., 2] = rgbArray[..., 2] * mask_labels          
                          
                          sum_array = rgbArray[...,0]+rgbArray[..., 1]+rgbArray[..., 2]
                      
                      cleaning_text = "removed Area<=500 & mean US <=3"
                                          
                if chosen_settings['clean_mask'] != "no_cleaning":
                     mask = mask * mask_labels
                     mask = mask * mask_black
                     
                if 'final_mask' in in_msg.aux_results:
                    outputFile = outputDir +"/aux_results/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_4th"+in_msg.name_4Mask+"_"+in_msg.name_ForcedMask+"AdditionalMask_Final_mask.png"
                    text_to_write = "Forth mask: %s\nForced mask: %s\nCleaning: %s"%( in_msg.name_4Mask, in_msg.name_ForcedMask, cleaning_text )
                    make_figure(mask, area_def, outputFile,colorbar = True, text_to_write = text_to_write, vmin = 0, vmax = 1)
                
                labels, numobjects = ndimage.label(mask)
                
                metadata = {}
                metadata['sat_nr']       = in_msg.sat_nr
                metadata['seviri_level'] = in_msg.reader_level
                metadata['cleaning']     = chosen_settings['clean_mask']
                metadata['masks']        = [in_msg.name_4Mask, in_msg.name_ForcedMask]
                metadata['downscaling']  = chosen_settings['mode_downscaling']
                metadata['rapid_scan_mode'] = chosen_settings['rapid_scan_mode']
                metadata['cloud_depth']           = n_tests_cd
                metadata['glaciation_indicators'] = n_tests_gi
                metadata['updraft_strength']      = n_tests_us
                
                if in_msg.shelve_labels==True and properties_cells == False:
                      labels = labels.astype('uint32') 
                      filename = 'labels/Labels_%s.shelve'%(yearS+monthS+dayS+hourS+minS)
                      print ("*** writing variables ", filename)
                      myShelve = shelve.open(filename)
                      # write data as dictionary into the shelve
                      dict_labels = {'labels': labels, 'metadata': metadata}
                      myShelve.update(dict_labels)
                      # close the shelve
                      myShelve.close()
                elif in_msg.pickle_labels==True and properties_cells == False:
                      labels = labels.astype('uint32') 
                      pickle.dump( labels, open(create_dir(outputDir +"/cosmo/Channels/labels/labels_"+yearS+monthS+dayS+hourS+minS+".p"), "wb" ) )
                
                if 'labelled_objects' in in_msg.aux_results:
                      outputFile = outputDir +"/aux_results/labelled/"+yearS+monthS+dayS+"_"+hourS+minS+"_4th"+in_msg.name_4Mask+"_"+in_msg.name_ForcedMask+"AdditionalMask.png"
                      make_figure(labels, area_def, outputFile,colorbar = False, 
                                  text_to_write = "Forth mask: %s\nForcen mask: %s\nCleaning: %s"%(in_msg.name_4Mask,in_msg.name_ForcedMask,cleaning_text), 
                                  vmin = False, vmax = False)
      
                # set background_color for "no clouds" 
                rgbArray[sum_array<=0,0] = background_color[0] # see coalition2_settings.py
                rgbArray[sum_array<=0,1] = background_color[1] # see coalition2_settings.py
                rgbArray[sum_array<=0,2] = background_color[2] # see coalition2_settings.py
                # set transparency for "no clouds" 
                rgbArray[sum_array<=0,3] = background_alpha    # see coalition2_settings.py
                
                ############################################################################################################################################

                # create output file name (replace wildcards)
                if in_msg.parallax_correction:
                    rgb_name='C2rgbPC'
                else:
                    rgb_name='C2rgb'

                c2File = format_name(outputDir+'/'+in_msg.outputFile, data.time_slot, area=area, rgb=rgb_name, sat=data.satname, sat_nr=data.sat_nr())
                print ("************"+c2File, in_msg.parallax_correction)

                if 'C2rgb' in in_msg.results:

                    PIL_image = Image.fromarray( rgbArray, 'RGBA' )
                    #add_borders_and_rivers( PIL_image, cw, area_tuple,
                    #                        add_borders=in_msg.add_borders, border_color=in_msg.border_color,
                    #                        add_rivers=in_msg.add_rivers, river_color=in_msg.river_color, 
                    #                        resolution=in_msg.resolution, verbose=in_msg.verbose)

                    # use HRV to 'imprint' cloud top structure to image   # this actually never gave good results...
                    if in_msg.HRV_enhancement:
                        if in_msg.verbose:
                            print ("*** Enhance the image with the HRV channel")
                        # create luminance from HRV channel
                        from mpop.imageo.geo_image import GeoImage
                        luminance = GeoImage((data["HRV"].data), data.area, data.time_slot, crange=(0, 100), mode="L")
                        luminance.enhance(gamma=2.0)
                        # add luminance to image
                        img = pilimage2geoimage(PIL_image, data.area_def, data.time_slot)
                        img.replace_luminance(luminance.channels[0])
                        PIL_image = img.pil_image()

                    # sza indication
                    if in_msg.indicate_sza:
                        from pyorbital.astronomy import sun_zenith_angle
                        lonlats = data['IR_108'].area.get_lonlats()
                        sza = sun_zenith_angle(time_slot, lonlats[0], lonlats[1])
                        ind_sza = (sza > 72) & (sum_array<=0)
                        # modify background to bluesh with alpha = 100
                        rgbArray[ind_sza,2] = 130    # 255 intense blue 
                        rgbArray[ind_sza,3] =  60    # 255=opaque

                    # add title
                    if in_msg.add_title:
                        from pydecorate import DecoratorAGG
                        dc = DecoratorAGG(PIL_image)

                        # bad fix
                        if area=='ccs4':
                            title_y_line_nr = 2 
                        else:
                            title_y_line_nr = deepcopy(in_msg.title_y_line_nr)
                        print ("... in_msg.title_y_line_nr ", in_msg.title_y_line_nr)

                        add_title(PIL_image, in_msg.title, "COALITION-2", 
                                  in_msg.sat_str(), in_msg.sat_nr_str(), in_msg.datetime, area, dc, in_msg.verbose, title_y_line_nr=title_y_line_nr )

                    print ("... save image: display ", c2File, " &")
                    PIL_image.save( create_dir(c2File) )
                    
                    if 'ninjotif' in in_msg.outputFormats:
                        
                        if area == "ccs4":
                            area_ninjotif = 'nrEURO1km'
                            chan_id = 8800015
                        elif area == "EuropeCanaryS95":
                            area_ninjotif = 'nrEURO3km'
                            chan_id = 9600015
                        area_def_ninjotif = get_area_def(area_ninjotif)  

                        print ("... reproject COALITION2 result ("+area+") to "+area_ninjotif)
                        
                        # !!! FIX ME !!!
                        # there is a problem, that areas outside ccs4 are extrapolated with nearest neighbour
                        # here: delete the outermost lines of the result, so that nearest neighbour is NaN
                        if area_ninjotif == 'nrEURO1km':
                            rgbArray[ 0, :, :] = 0
                            rgbArray[-1, :, :] = 0
                            rgbArray[ :, 0, :] = 0
                            rgbArray[ :,-1, :] = 0

                        from mpop.channel import Channel
                        # add rgb array as channel to a GeostationaryFactory object
                        c2_data = GeostationaryFactory.create_scene(in_msg.sat_str(), in_msg.sat_nr_str(), "seviri", time_slot)
                        c2_data.channels.append(Channel(name='r', wavelength_range=[0.,0.,0.], resolution=1000., data=rgbArray[:,:,0], area=area))  
                        c2_data.channels.append(Channel(name='g', wavelength_range=[0.,0.,0.], resolution=1000., data=rgbArray[:,:,1], area=area))
                        c2_data.channels.append(Channel(name='b', wavelength_range=[0.,0.,0.], resolution=1000., data=rgbArray[:,:,2], area=area))
                        c2_data.channels.append(Channel(name='a', wavelength_range=[0.,0.,0.], resolution=1000., data=rgbArray[:,:,3], area=area))


                        c2_data = c2_data.project(area_ninjotif, precompute=True) # (default) mode='quick' || mode="bilinear", radius=50e3 || mode="ewa" || mode="nearest"

                        """
                        # !!! FIX ME !!!
                        # reproject all channels to the area needed by NINJO
                        if area_ninjotif == 'nrEURO3km':
                            # normal reprojection
                            c2_data = c2_data.project(area_ninjotif, precompute=True) 
                        elif area_ninjotif == 'nrEURO1km':
                            # take care of area outside of ccs4, which is filled with nearest neighbour...
                            c2_data = c2_data.project(area_ninjotif, mode='quick', precompute=True) # , mode='quick' || mode="bilinear", radius=50e3 || mode="ewa" || mode="nearest"

                            ##c2_data['a'].data = np.where(c2_data['r'].data==c2_data['r'].data[0,0], 255, c2_data['a'].data)
                            ##c2_data['a'].data = np.where(isinstance(c2_data['r'].data, np.ma.core.MaskedConstant), 0, c2_data['a'].data)
                            #outputFile = outputDir +"/aux_results/masks/"+yearS+monthS+dayS+"_"+hourS+minS+"_arg.png"
                            #make_figure(c2_data['a'].data.mask, area_def_ninjotif, outputFile, colorbar=True, text_to_write = "wiogbwpg", vmin = 0, vmax = 1)
                            # np.where(type(c2_data['r'].data)=='numpy.ma.core.MaskedConstant', c2_data['r'].data.max()
                            #print ("******************", c2_data['r'].data.max(), c2_data['g'].data.max(), c2_data['b'].data.max(), 
                            #       isinstance(c2_data['r'].data[0,0], np.ma.core.MaskedConstant), type(c2_data['r'].data[0,0]), np.isnan(c2_data['r'].data[0,0]))
                            #print ("******************", c2_data['r'].data.max(), c2_data['g'].data.max(), c2_data['b'].data.max(), type(c2_data['r'].data[0,0]), np.isnan(c2_data['r'].data[0,0]))
                            #print ("******************", c2_data['r'].data.max(), c2_data['g'].data.max(), c2_data['b'].data.max(), type(c2_data['r'].data[0,0]), np.isnan(c2_data['r'].data[0,0]))
                        else:
                            print ("... Warning, unknown projection in save ninjotiff")
                            c2_data = c2_data.project(area_ninjotif, precompute=True)
                        """

                        nx2,ny2 = c2_data['r'].data.shape
                        print ("    new shape (nx,ny)= (",nx2,",",ny2,")")

                        rgbArray2 = np.zeros( (nx2,ny2,4), 'uint8')
                        print (type(rgbArray2), rgbArray2.shape)
                        print (rgbArray2[:,:,0].shape, c2_data['r'].data.shape)
                        rgbArray2[:,:,0] = c2_data['r'].data
                        rgbArray2[:,:,1] = c2_data['g'].data
                        rgbArray2[:,:,2] = c2_data['b'].data
                        rgbArray2[:,:,3] = c2_data['a'].data
                        
                        c2ninjotif_file = format_name (outputDir+'/'+in_msg.ninjotifFilename, data.time_slot, sat_nr=data.sat_nr(), RSS=True, area=area_ninjotif )
                        print ("... save ninjotif image: display ", c2ninjotif_file, " &")
                        PIL_image = Image.fromarray(rgbArray2, 'RGBA')
                        GEO_image = pilimage2geoimage(PIL_image, c2_data['r'].area_def, data.time_slot)
                        if area_ninjotif == 'nrEURO1km':
                            GEO_image.save(c2ninjotif_file,
                                           fformat='mpop.imageo.formats.ninjotiff',
                                           ninjo_product_name='COALITION2', chan_id=chan_id,
                                           nbits=8, pixel_xres=0.00949833,  pixel_yres=0.00949833)   # meridian_west=0.0, meridian_east=0.0 -> no effect
                        else:
                            GEO_image.save(c2ninjotif_file,
                                           fformat='mpop.imageo.formats.ninjotiff',
                                           ninjo_product_name='COALITION2', chan_id=chan_id,
                                           nbits=8)   
                        os.chmod(c2ninjotif_file, 0777)
                        if in_msg.upload_ninjotif:
                            print ("... upload ninjotif: /tools/mch/datadisp/bin/jwscp_upload.zueub227.tcoalition2 &")
                            subprocess.call("/tools/mch/datadisp/bin/jwscp_upload.zueub227.tcoalition2 &", shell=True)

                    #pickle.dump( PIL_image, open("RGB"+yearS+monthS+dayS+hourS+minS+".p", "wb" ) )
                
                if area in in_msg.postprocessing_areas:                        
                    print ("... post-processing for area ", area)
                    in_msg.postprocessing_composite = deepcopy(in_msg.postprocessing_composite1)
                    postprocessing(in_msg, time_slot, int(data.sat_nr()), area)

                """
                if 'C2rgbHRV' in in_msg.results: # and in_msg.nrt == False:
                    if area == "ccs4":
                        type_image = "_HRV"
                    else:
                        type_image = "_overview"
                    #c2FileHRV = (outputDir+"/aux_results/RGB-HRV"+maskS+"/%s_%s_C2rgb"+maskS+"4th"+in_msg.name_4Mask+"_"+in_msg.name_ForcedMask+"AdditionalMask.png") % (yearS+monthS+dayS,hourS+minS)
                    #hrvFile = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/"+yearS+"-"+monthS+"-"+dayS+type_image+"_"+area+"/MSG"+type_image+"-"+area+"_"+yearS[2:]+monthS+dayS+hourS+minS+".png"
                     
                    #hrvFile = outputDir+"MSG_IR-108-"+area+"_"+"16"+monthS+dayS+hourS+minS+".png"
                    
                    #out_file1 = create_dir( outputDir +"/"+yearS+monthS+dayS+"_"+hourS+minS+"_C2rgb-HRV_"+"4th"+in_msg.name_4Mask+"_"+in_msg.name_ForcedMask+"AdditionalMask"+area+".png" )
 
                    dic_figure={}
                    dic_figure['rgb']='C2rgb-'+type_image[1:] #-IR-108'
                    dic_figure['area']=area
                    print (outputFile)
                    out_file1 = create_dir( outputDir+outputFile%dic_figure)
                    print ("!!! out_file1: ", out_file1)
                    #quit()

                    if in_msg.nrt == False:

                        hrvFile = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/"+yearS+"-"+monthS+"-"+dayS+type_image+"_"+area+"/MSG"+type_image+"-"+area+"_"+yearS[2:]+monthS+dayS+hourS+minS+".png"
                        print ("...creating composite", out_file1)
                        print ("... create composite "+c2File+" "+hrvFile+" "+out_file1)
                        subprocess.call("/usr/bin/composite "+c2File+" "+hrvFile+" "+out_file1, shell=True)
                        print ("... saved composite: display ", out_file1, " &")
                
                    ## start postprocessing
                    elif area in in_msg.postprocessing_areas:
                       print ("area in post processing")
                       in_msg.postprocessing_composite = deepcopy(in_msg.postprocessing_composite1)
                       postprocessing(in_msg, [], time_slot, int(data.sat_nr()), area)
                """
          
                if area == "ccs4" and in_msg.properties_cells == True:
                    print ("**** Computing properties of the cells")
                    outputDir_labels = outputDir+'/labels/'
                    """
                    if 'labels_tracked' in in_msg.aux_results:        !!!! UH this might give very hard to find bugs
                        outputDir_labels = outputDir+'/labels/'       !!!! switching on an additional output changes the directory where to read from ...
                    else:
                        outputDir_labels = None
                    """
                    labels_corrected, first_time_step = properties_cells(time_slot, time_slot, current_labels=labels, metadata=metadata,
                                                                         labels_dir=labelsDir, outputDir_labels=outputDir_labels, in_msg=in_msg, sat_data=data)
                    if first_time_step:
                        print ("no history to follow, first timestep")
                    if in_msg.plot_forecast == True and first_time_step == False:
                        print ("**** Forecasting Area")
                        if in_msg.nrt == False:
                            add_path = "" #"/new_forecasted_area/"
                        else:
                            add_path = ""
                        #plot_forecast_area(time_slot, in_msg.model_fit_area, outputFile=outputDir+add_path, current_labels=labels_corrected,
                        #                  t_stop=time_slot, BackgroundFile=out_file1, ForeGroundRGBFile=c2File, labels_dir=labelsDir, in_msg=in_msg)
                        plot_forecast_area(time_slot, in_msg.model_fit_area, outputDir=outputDir+add_path, current_labels=labels_corrected,
                                           t_stop=time_slot, BackgroundFile=c2File, ForeGroundRGBFile=c2File, labels_dir=labelsDir, in_msg=in_msg)
            


          # add 5min and do the next time step
          f4p = labelsDir+"/Labels*"
          import glob
          filenames_for_permission = glob.glob(f4p)
          for file_per in filenames_for_permission:
                #print("modified permission: ", file_per)
                os.chmod(file_per, 0664)  ## FOR PYTHON3: 0o664           
          time_slot = time_slot + timedelta(minutes=5)

    # return True, if result file exists
    if os.path.exists(c2File) and os.path.getsize(c2File) > 0:
        return True
    else:
        return False


#=================================================================================================
#=================================================================================================
def print_usage():
   
    inputFile="input_coalition2"
    print("***           ")
    print("*** Error, not enough command line arguments")
    print("***        please specify at least an input file")
    print("***        possible calls are:")
    print("*** python "+inspect.getfile(inspect.currentframe())+" "+inputFile+" ")
    print("*** python "+inspect.getfile(inspect.currentframe())+" "+inputFile+" 2014 07 23 16 10 ")
    print("                                 date and time must be completely given")
    print("*** python "+inspect.getfile(inspect.currentframe())+" "+inputFile+" 2014 07 23 16 10 2014 07 23 16 30")
    print("***           ")
    quit() # quit at this point
#----------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    from get_input_msg import get_date_and_inputfile_from_commandline
    in_msg = get_date_and_inputfile_from_commandline(print_usage=print_usage)    
    time_slot = in_msg.datetime

    from coalition2_settings import *    
    print ("... input imported")
             
    if len(sys.argv) > 7:
        yearSTOP   = int(sys.argv[7])
        monthSTOP  = int(sys.argv[8])
        daySTOP    = int(sys.argv[9])
        hourSTOP   = int(sys.argv[10])
        minuteSTOP = int(sys.argv[11])
        time_slotSTOP = datetime(yearSTOP, monthSTOP, daySTOP, hourSTOP, minuteSTOP)
        #nrt = False
        #in_msg.reader_level="seviri-level4"        
    else:
        time_slotSTOP = in_msg.datetime

    print ("*** start plot_coalition2 ")
    image_written = plot_coalition2(in_msg, in_msg.datetime, time_slotSTOP)

    if not image_written:
        print ("*** Error, COALITION2 image could not be produced!")
