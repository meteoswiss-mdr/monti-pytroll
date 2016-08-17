#!/usr/bin/python

# program to plot SEVIRI observations   
# usage from command line  
# $ python plot_msg.py
# 
# pass arguments to overwrite time, rgb, area given in the script 
# $ python plot_msg.py year month day hour min rgb area
# year month day hour min 
#        -> integers specifying the date of observation 
# rgb    -> string,      e.g. RGBs='HRoverview' or
#           string list, e.g. RGBs=['IR_108','IR_120-IR_108','HRoverview']
#           for possible options have a look at __main__
# area   -> string or string array, e.g. 'EuropeCanary' or 'ccs4' (default)
#           for possible options have a look at the file area.def
# RSS    -> logical (True or False) rapid scan service
#           True  ->  5min service for europe (default)
#           False -> 15min service for whole disk 
# verbose-> logical (True or False) activates verbose output
#           True -> more messages for debugging (default)
#           False -> quiet
#
# Author  Ulrich Hamann
# History 2014-10-01 U. Hamann, first version
#         2014-10-28 U. Hamann, area can also be used as array
#         2014-02-10 U. Hamann, introduced input file 
#         2015-02-25 U. Hamann, added the ability to plot 
#                               NWC-SAF cloud mask and SPhR products
#

from mpop.satellites import GeostationaryFactory
from mpop.imageo.geo_image import GeoImage
#from mpop.imageo.palettes import cms_modified, convert_palette, convert_palette2colormap
from datetime import datetime, timedelta
from pyresample import image, geometry
from pycoast import ContourWriterAGG
from pydecorate import DecoratorAGG
from mpop.channel import Channel, GenericChannel
import aggdraw
from numpy import where, zeros
import numpy.ma as ma
from os.path import dirname, exists, join
from os import makedirs, chmod, stat
import subprocess
from mpop.projector import get_area_def
from copy import deepcopy

from PIL import Image
from trollimage.image import Image as trollimage
from PIL import ImageFont
from PIL import ImageDraw 
from trollimage.colormap import rdbu, greys, rainbow, spectral

from my_composites import mask_clouddepth, get_image

from my_msg_module import get_last_SEVIRI_date, check_input, channel_str2ind
from my_msg_module import choose_msg, convert_NWCSAF_to_radiance_format, get_NWC_pge_name, format_name
from my_msg_module import check_loaded_channels
from postprocessing import postprocessing

import products 

#from mpop.utils import debug_on
#debug_on() 

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------


def plot_msg(in_msg):


   # get date of the last SEVIRI observation
   if in_msg.datetime == None:
      in_msg.get_last_SEVIRI_date()

   yearS = str(in_msg.datetime.year)
   #yearS = yearS[2:]
   monthS = "%02d" % in_msg.datetime.month
   dayS   = "%02d" % in_msg.datetime.day
   hourS  = "%02d" % in_msg.datetime.hour
   minS   = "%02d" % in_msg.datetime.minute

   dateS=yearS+'-'+monthS+'-'+dayS
   timeS=hourS+'-'+minS

   if in_msg.sat_nr==None:
      in_msg.sat_nr=choose_msg(in_msg.datetime,in_msg.RSS)

   if in_msg.datetime.year > 2012:
      if in_msg.sat_nr == 8:
         area_loaded = get_area_def("EuropeCanary35")
      elif in_msg.sat_nr ==  9: # rapid scan service satellite
         area_loaded = get_area_def("EuropeCanary95")  
      elif in_msg.sat_nr == 10: # default satellite
         area_loaded = get_area_def("SeviriDiskFull00")  # full disk service, like EUMETSATs NWC-SAF products
      elif in_msg.sat_nr == 0: # fake satellite for reprojected ccs4 data in netCDF
         area_loaded = get_area_def("ccs4")  # 
         #area_loaded = get_area_def("EuropeCanary")
         #area_loaded = get_area_def("alps")  # new projection of SAM
      else:
         print "*** Error, unknown satellite number ", in_msg.sat_nr
         area_loaded = get_area_def("hsaf")  # 
   else:
      if in_msg.sat_nr == 8:
         area_loaded = get_area_def("EuropeCanary95") 
      elif in_msg.sat_nr ==  9: # default satellite
         area_loaded = get_area_def("EuropeCanary")

   # define contour write for coasts, borders, rivers
   cw = ContourWriterAGG(in_msg.mapDir)

   # check if input data is complete 
   if in_msg.verbose:
      print "*** check input data for ", in_msg.sat_str()
   RGBs = check_input(in_msg, in_msg.sat_str(layout="%(sat)s")+in_msg.sat_nr_str(), in_msg.datetime)  
   # in_msg.sat_nr might be changed to backup satellite

   if len(RGBs) != len(in_msg.RGBs):
      print "*** Warning, input not complete."
      print "*** Warning, process only: ", RGBs
   #else:
   #   print "... produce plots for ", RGBs

   if in_msg.verbose:
      print '*** Create plots for '
      print '    Satellite/Sensor: ' + in_msg.sat_str() 
      print '    Satellite number: ' + in_msg.sat_nr_str()
      print '    Date/Time:        '+dateS +' '+hourS+':'+minS+'UTC'
      print '    RGBs:            ', in_msg.RGBs
      print '    Area:            ', in_msg.areas


   # define satellite data object
   #global_data = GeostationaryFactory.create_scene(in_msg.sat, in_msg.sat_nr_str(), "seviri", in_msg.datetime)
   global_data = GeostationaryFactory.create_scene(in_msg.sat_str(), in_msg.sat_nr_str(), "seviri", in_msg.datetime)

   # print "type(global_data) ", type(global_data)   # <class 'mpop.scene.SatelliteInstrumentScene'>
   # print "dir(global_data)", dir(global_data)  [..., '__init__', ... 'area', 'area_def', 'area_id', 'channel_list', 'channels', 
   #      'channels_to_load', 'check_channels', 'fullname', 'get_area', 'image', 'info', 'instrument_name', 'lat', 'load', 'loaded_channels', 
   #      'lon', 'number', 'orbit', 'project', 'remove_attribute', 'satname', 'save', 'set_area', 'time_slot', 'unload', 'variant']
   
   ## define satellite data object one scan before
   #if in_msg.RSS:
   #   scan_time =  5 # min
   #else:
   #   scan_time = 15 # min
   #datetime_m1 -= timedelta(scan_time)
   #global_data_m1 = GeostationaryFactory.create_scene(in_msg.sat, in_msg.sat_nr_str(), "seviri", datetime_m1)

   if len(RGBs) == 0 and len(in_msg.postprocessing_areas) == 0:
      return RGBs

   if in_msg.verbose:
      print "*** load satellite channels for " + in_msg.sat_str()+in_msg.sat_nr_str()+" ", global_data.fullname

   # initialize processed RGBs
   RGBs_done=[]

   # -------------------------------------------------------------------
   # load reflectivities, brightness temperatures, NWC-SAF products ...
   # -------------------------------------------------------------------
   area_loaded = load_products(global_data, RGBs, in_msg, area_loaded)
   # ----------------------------------------------------------------------
   # load reflectivities, brightness temperatures, NWC-SAF products for t-1
   # ----------------------------------------------------------------------
   #load_products(global_data_m1, RGBs, in_msg, area_loaded)

   # check if all prerequisites are loaded
   #rgb_complete = []
   #for rgb in RGBs:
   #   all_loaded = True
   #   if rgb in products.RGBs_buildin or rgb in products.RGB_user:
   #      obj_image = get_image(global_data, rgb)
   #      for pre in obj_image.prerequisites:
   #         if pre not in loaded_channels:
   #            all_loaded = False
   #   elif rgb in products.MSG_color:
   #      if rgb.replace("c","") not in loaded_channels:
   #         all_loaded = False
   #   else:
   #      if rgb not in loaded_channels:
   #         all_loaded = False
   #   if all_loaded:
   #      rgb_complete.append(rgb)
   #print "rgb_complete", rgb_complete

   # preprojecting the data to another area 
   # --------------------------------------
   for area in in_msg.areas:
      print ""
      obj_area = get_area_def(area)

      # reproject data to new area 
      if obj_area == area_loaded: 
         if in_msg.verbose:
            print "*** Use data for the area loaded: ", area
         #obj_area = area_loaded
         data = global_data
         resolution='l'
      else:
         if in_msg.verbose:    
            print "*** Reproject data to area: ", area, "(org projection: ",  area_loaded.name, ")"     
         obj_area = get_area_def(area)
         # PROJECT data to new area 
         data = global_data.project(area)
         resolution='i'

      if in_msg.parallax_correction:
         if in_msg.verbose:
            loaded_products = [chn.name for chn in data.loaded_channels()]
            print "    perform parallax correction for loaded channels: ", loaded_products
         if area == 'ccs4':
            estimate_cth=False
         else:
            estimate_cth=True
         data = data.parallax_corr(fill=in_msg.parallax_gapfilling, estimate_cth=estimate_cth, replace=True)

      #import matplotlib.pyplot as plt
      #plt.imshow(data['lat'].data)
      #plt.colorbar()
      #plt.show()
      #quit()

      # save reprojected data
      if area in in_msg.save_reprojected_data:
         save_reprojected_data(data, area, in_msg)

      # apply a mask to the data (switched off at the moment)
      if False:
         mask_data(data, area)

      # save average values 
      if in_msg.save_statistics:

         mean_array = zeros(len(RGBs))
         #statisticFile = '/data/COALITION2/database/meteosat/ccs4/'+yearS+'/'+monthS+'/'+dayS+'/MSG_'+area+'_'+yearS[2:]+monthS+dayS+'.txt'
         statisticFile = './'+yearS+'-'+monthS+'-'+dayS+'/MSG_'+area+'_'+yearS[2:]+monthS+dayS+'.txt'
         if in_msg.verbose:
            print "*** write statistics (average values) to "+statisticFile
         f1 = open(statisticFile,'a')   # mode append
         i_rgb=0
         for rgb in RGBs:
            if rgb in products.MSG_color:
               mean_array[i_rgb]=data[rgb.replace("c","")].data.mean()
               i_rgb=i_rgb+1

         # create string to write
         str2write = dateS +' '+hourS+' : '+minS+' UTC  '
         for mm in mean_array:
            str2write = str2write+' '+ "%7.2f" % mm
         str2write = str2write+"\n"
         f1.write(str2write)
         f1.close()

      # creating plots/images 
      if in_msg.make_plots:
      
         # choose map resolution 
         in_msg.resolution = choose_map_resolution(area, resolution, in_msg.mapResolution)

         # define area
         proj4_string = obj_area.proj4_string            
         # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
         area_extent = obj_area.area_extent              
         # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
         area_tuple = (proj4_string, area_extent)
         
         for rgb in RGBs:

            # do automatic chose if no input
            if in_msg.HRV_enhancement is None:
                                     # UTC is shifted by 1hour to local winter time ( more or less solar time)
               if area == 'ccs4' and (5 < in_msg.datetime.hour) and (in_msg.datetime.hour < 19) and rgb in ['VIS006', 'VIS008','VIS006c','VIS008c','overview','overview_sun', 'natural','green_snow','red_snow','convection']:  
                  HRV_enhancement=True
                  print "*** switch on HRV enhancement"
               else:
                  HRV_enhancement=False
            else:
               HRV_enhancement=in_msg.HRV_enhancement

            if HRV_enhancement:
               HRV_enhance_str='hr_'
            else:
               HRV_enhance_str=''

            if not check_loaded_channels(rgb, data):
               continue 

            PIL_image = create_PIL_image(rgb, data, in_msg, HRV_enhancement=HRV_enhancement)   # !!! in_msg.colorbar[rgb] is initialized inside (give attention to rgbs) !!!

            add_border_and_rivers(PIL_image, cw, area_tuple, in_msg)
   
            # indicate mask
            if in_msg.indicate_mask:
               PIL_image = indicate_mask(rgb, PIL_image, data, in_msg.verbose)

            #if area.find("EuropeCanary") != -1 or area.find("ccs4") != -1:
            dc = DecoratorAGG(PIL_image)

            # add title to image
            if in_msg.add_title:
               add_title(PIL_image, HRV_enhance_str+rgb, data.sat_nr(), dateS, hourS, minS, area, dc, in_msg.verbose )

            # add MeteoSwiss and Pytroll logo
            if in_msg.add_logos:
               if in_msg.verbose:
                  print '... add logos'
               dc.align_right()
               if in_msg.add_colorscale:
                  dc.write_vertically()
               if PIL_image.mode != 'L':
                  height = 60  # height=60.0 normal resolution 
                  dc.add_logo("../logos/pytroll3.jpg",height=height)                          # height=60.0
                  dc.add_logo("../logos/meteoSwiss3.jpg",height=height)                       
                  dc.add_logo("../logos/EUMETSAT_logo2_tiny_white_square.png",height=height)  # height=60.0
   
            # add colorscale
            if in_msg.add_colorscale and in_msg.colormap[rgb] != None:
               if rgb in products.MSG_color:
                  unit = data[rgb.replace("c","")].info['units']
               #elif rgb in products.MSG or rgb in products.NWCSAF or rgb in products.HSAF:
               #   unit = data[rgb].info['units']
               else:
                  unit = None
                  if hasattr(data[rgb], 'info'):
                     print "hasattr(data[rgb], 'info')", data[rgb].info.keys()
                     if 'units' in data[rgb].info.keys():
                        print "'units' in data[rgb].info.keys()"
                        unit = data[rgb].info['units']
               print "... units = ", unit
               add_colorscale(dc, rgb, in_msg, unit=unit)

            # create output filename
            outputDir =              format_name(in_msg.outputDir,  data.time_slot, area=area, rgb=rgb, sat=data.satname, sat_nr=data.sat_nr()) # !!! needs change
            outputFile = outputDir + format_name(in_msg.outputFile, data.time_slot, area=area, rgb=rgb, sat=data.satname, sat_nr=data.sat_nr()) # !!! needs change
   
            # check if output directory exists, if not create it
            path= dirname(outputFile)
            if not exists(path):
               if in_msg.verbose:
                  print '... create output directory: ' + path
               makedirs(path)
   
            # save file
            if stat(outputFile).st_size > 0:
               print '... outputFile '+outputFile+' already exists'
            else:
               if in_msg.verbose:
                  print '... save final file: ' + outputFile
               PIL_image.save(outputFile, optimize=True)  # optimize -> minimize file size
               chmod(outputFile, 0664)  ## FOR PYTHON3: 0o664  # give access read/write access to group members
   
            if in_msg.compress_to_8bit:
               if in_msg.verbose:
                  print '... compress to 8 bit image: display '+outputFile.replace(".png","-fs8.png")+' &'
               subprocess.call("/usr/bin/pngquant -force 256 "+outputFile+" 2>&1 &", shell=True) # 256 == "number of colors"
   
            #if in_msg.verbose:
            #   print "    add coastlines to "+outputFile   
            ## alternative: reopen image and modify it (takes longer due to additional reading and saving)
            #cw.add_rivers_to_file(img, area_tuple, level=5, outline='blue', width=0.5, outline_opacity=127)
            #cw.add_coastlines_to_file(outputFile, obj_area, resolution=resolution, level=4)
            #cw.add_borders_to_file(outputFile, obj_area, outline=outline, resolution=resolution)
    
            # copy to another place
            if in_msg.scpOutput:
               if in_msg.verbose:
                  print "... secure copy "+outputFile+ " to "+in_msg.scpOutputDir
               subprocess.call("scp "+in_msg.scpID+" "+outputFile+" "+in_msg.scpOutputDir+" 2>&1 &", shell=True)
               if in_msg.compress_to_8bit:
                  if in_msg.verbose:
                     print "... secure copy "+outputFile.replace(".png","-fs8.png")+ " to "+in_msg.scpOutputDir
                     subprocess.call("scp "+in_msg.scpID+" "+outputFile.replace(".png","-fs8.png")+" "+in_msg.scpOutputDir+" 2>&1 &", shell=True)
   
            if rgb not in RGBs_done:
               RGBs_done.append(rgb)
   
      ## start postprocessing
      if area in in_msg.postprocessing_areas:
         postprocessing(in_msg, global_data.time_slot, int(data.sat_nr()), area)

   if in_msg.verbose:
      print " "

   return RGBs_done


#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def load_products(data_object, RGBs, in_msg, area_loaded):

   if in_msg.verbose:
      print "*** load products ", RGBs
 
   # check if PyResample is loaded
   try:
      # Work around for on demand import of pyresample. pyresample depends
      # on scipy.spatial which memory leaks on multiple imports
      IS_PYRESAMPLE_LOADED = False
      from pyresample import geometry
      IS_PYRESAMPLE_LOADED = True
   except ImportError:
      LOGGER.warning("pyresample missing. Can only work in satellite projection")

   if in_msg.parallax_correction:
      if 'CTH' not in RGBs:
         RGBs.append('CTH')
      if in_msg.nwcsaf_calibrate == False:
         print "*** Error in plot_msg (plot_msg.py) "
         print "    in_msg.nwcsaf_calibrate = ", in_msg.nwcsaf_calibrate
         print "    parallax correction needs physical (calibrated) CTH values"
         quit()

   # load all channels / information 
   for rgb in RGBs:
      if rgb in products.MSG or rgb in products.MSG_color: 
         for channel in products.MSG:
            if rgb.find(channel) != -1:                   # if a channel name (IR_108) is in the rgb name (IR_108c)
               if in_msg.verbose: 
                  print "    load prerequisites by name: ", channel, in_msg.reader_level
               if in_msg.reader_level == None:
                  data_object.load([channel], area_extent=area_loaded.area_extent)   # try all reader levels  load the corresponding data
               else:
                  data_object.load([channel], area_extent=area_loaded.area_extent, reader_level=in_msg.reader_level)  # load the corresponding data

      if rgb in products.RGBs_buildin or rgb in products.RGBs_user:
         obj_image = get_image(data_object, rgb)          # find corresponding RGB image object
         if in_msg.verbose:
            print "    load prerequisites by function: ", obj_image.prerequisites
         if in_msg.reader_level == None:
            data_object.load(obj_image.prerequisites, area_extent=area_loaded.area_extent)   # load prerequisites
         else:
            data_object.load(obj_image.prerequisites, area_extent=area_loaded.area_extent, reader_level=in_msg.reader_level)  # load prerequisites

      if rgb in products.NWCSAF:

         pge = get_NWC_pge_name(rgb)

         if in_msg.verbose:
            print "    load NWC-SAF product: "+pge.replace('_', '') 

         data_object.load([pge.replace('_', '')], calibrate=in_msg.nwcsaf_calibrate, reader_level="seviri-level3") 

         # False, area_extent=area_loaded.area_extent (difficulties to find correct h5 input file)
         #print data_object.loaded_channels()
         #loaded_channels = [chn.name for chn in data_object.loaded_channels()]
         #if pge not in loaded_channels:
         #   return []
         if area_loaded != data_object[pge].area:
            print "*** Warning: NWC-SAF input file on a differnt grid ("+data_object[pge].area.name+") than suggested input area ("+area_loaded.name+")"
            print "    use "+data_object[pge].area.name+" as standard grid"
            area_loaded = data_object[pge].area
         convert_NWCSAF_to_radiance_format(data_object, area_loaded, rgb, in_msg.nwcsaf_calibrate, IS_PYRESAMPLE_LOADED)

      if rgb in products.HSAF: 
         if in_msg.verbose:
            print "    load hsaf product by name: ", rgb
         data_object.load([rgb])   # , area_extent=area_loaded.area_extent load the corresponding data

      if rgb in products.CPP:
         if in_msg.verbose:
            print "    load CPP product by name: ", rgb
         data_object.load([rgb])   # , area_extent=area_loaded.area_extent load the corresponding data

      if rgb in products.SEVIRI_viewing_geometry: 
         data_object.load([rgb], reader_level=in_msg.reader_level)
         #print data_object[rgb].data.shape, data_object[rgb].data.min(), data_object[rgb].data.max()

      if in_msg.HRV_enhancement==True or in_msg.HRV_enhancement==None:
         # load also the HRV channel (there is a check inside in the load function, if the channel is already loaded)
         if in_msg.verbose:
            print "    load additionally the HRV channel for HR enhancement"
         data_object.load(["HRV"], area_extent=area_loaded.area_extent)

   # loaded_channels = [chn.name for chn in data_object.loaded_channels()]
   # print loaded_channels

   return area_loaded

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def choose_map_resolution(area, resolution, MapResolutionInputfile):

   ## add coasts, borders, and rivers, database is heree 
   ## http://www.soest.hawaii.edu/pwessel/gshhs/index.html
   ## possible resolutions                                          
   ## f  full resolution: Original (full) data resolution.          
   ## h  high resolution: About 80 % reduction in size and quality. 
   ## i  intermediate resolution: Another ~80 % reduction.          
   ## l  low resolution: Another ~80 % reduction.                   
   ## c  crude resolution: Another ~80 % reduction.   

   if MapResolutionInputfile == None:         # if the user did not specify the resolution 
      if area.find("EuropeCanary") != -1: # make a somewhat clever choise  
         resolution='l'
      if area.find("ccs4") != -1:
         resolution='i' 
      if area.find("ticino") != -1:
         resolution='h'
   else:
      resolution = MapResolutionInputfile     # otherwise take specification of user 

   return resolution 

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def save_reprojected_data(data, area, in_msg, concatenate_bands=False):
   
   _sat_nr = int(data.number)-7 if int(data.number)-7 > 0 else 0
   # directory / path 
   nc_dir  = (data.time_slot.strftime(in_msg.reprojected_data_dir)
              % {"area": area,
                 "msg": "MSG"+str(_sat_nr)})
   # check if output directory exists, if not create it
   if not exists(nc_dir):
      if in_msg.verbose:
         print '... create output directory: ' + nc_dir
      makedirs(nc_dir)
   # filename
   nc_file = (data.time_slot.strftime(in_msg.reprojected_data_filename)
              % {"area": area,
                 "msg": "MSG"+str(_sat_nr)})
   ncOutputFile = join(nc_dir, nc_file)
   if in_msg.verbose:
      print "... save reprojected data: ncview "+ ncOutputFile+ " &" 
   #data.save(ncOutputFile, to_format="netcdf4", compression=False)
   data.save(ncOutputFile, band_axis=2, concatenate_bands=concatenate_bands) # netCDF4 is default 
           # mpop/satout/cfscene.py -> mpop/satout/netcdf4.py

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

# !!! this is a very preliminary version !!!
# !!! this is a very preliminary version !!!
# !!! this is a very preliminary version !!!

def mask_data(data, area):

   # extract loaded channels
   loaded_products = [chn.name for chn in data.loaded_channels()]

   # mask for the cloud depths tests (masked data)
   #if area == 'ccs4':
   if area == False:     # !!! at the moment switched off !!! 
      print '... apply convective mask'
      mask_depth = data.image.mask_clouddepth()
      #print type(mask_depth.max)
      #print dir(mask_depth.max)
      index = where( mask_depth < 5 )  # less than 5 (of 6) tests successfull -> mask out
      for prod in loaded_products:
         ## ??? ## ??? data[prod].data[index] = fill_value or data[prod].data.data[index] = fill_value
         data[prod].data.mask[index] = True
         ## ??? ## ??? fill_value = data[prod].data.fill_value

   #      if rgb in products.MSG_color:
   #         rgb2=rgb.replace("c","")
   #         data[rgb2].data.mask[index]=True
   #         fill_value = data[rgb2].data.fill_value
   #         #data["IR_108"].data[index] = fill_value

   #print "data[IR_108].data.min/max ", data["IR_108"].data.min(), data["IR_108"].data.max()
   #if rgb == "IR_108c":
   #   print type(data["IR_108"].data)
   #   print dir(data["IR_108"].data)
   #print data["IR_108"].data.mask


#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def create_PIL_image(rgb, data, in_msg, colormap='rainbow', HRV_enhancement=False):

   from mpop.imageo.palettes import convert_palette2colormap
   from trollimage.colormap import rainbow   # reload in order to be save not to use a scaled colormap

   if in_msg.verbose:
      print ""
      print "*** make image for: ", rgb

   # default colormap 
   if colormap=='rainbow':
      colormap = deepcopy(rainbow)
   elif colormap=='greys':
      from trollimage.colormap import greys
      colormap = deepcopy(greys)
   else:
      print "Error, unknown colormap ", colormap ," in plot_msg.py"
      quit()

   # get the data array that you want to plot 
   if rgb in products.MSG:
      prop = data[rgb].data
      plot_type='channel_image'
   elif rgb in products.MSG_color:
      prop = data[rgb.replace("c","")].data
      plot_type='trollimage'
   elif rgb in products.SEVIRI_viewing_geometry:
      prop = data[rgb].data
      plot_type='trollimage'
   elif rgb in (products.CTTH + products.PC + products.CRR + products.PPh) :
      prop = data[rgb].data
      prop.mask = (prop <= 0)
      if in_msg.nwcsaf_calibrate==True:
         if rgb == 'CTH':
            prop /= 1000. # 1000. == m -> km
            data[rgb].info['units'] = 'km'
         plot_type='trollimage'
         if rgb == 'CRR' or rgb == 'CRPh' :
            from trollimage.colormap import RainRate
            colormap=RainRate
      else:
         plot_type='palette'
   elif rgb in products.CT:
      prop = data[rgb].data
      plot_type='palette'
      if rgb ==  'CT_QUALITY':
         plot_type='trollimage'
   elif rgb in products.CMa or rgb in products.SPhR:
      prop = data[rgb].data
      if hasattr(data[rgb], 'palette') and in_msg.nwcsaf_calibrate==False:
         plot_type='palette'
      else:
         plot_type='trollimage'
   elif rgb in products.HSAF:
      prop = data[rgb].data
      plot_type='trollimage'
      from trollimage.colormap import RainRate
      colormap=RainRate
   elif rgb in products.CPP:
      prop = data[rgb].data
      plot_type='trollimage'
      if rgb == 'precip' or rgb == 'precip_ir' or rgb == 'cot' or rgb == 'cwp':
         from trollimage.colormap import RainRate
         colormap=RainRate
   else:
      # includes products.RGBs_buildin
      prop = ma.asarray([-999.,-999.])
      plot_type='user_defined'

   #from numpy import log10    
   #prop=log10(prop)

   # search minimum and maximum
   # (default)
   min_data = prop.min()
   max_data = prop.max()
   # replace default with fixed min/max if specified 

   if in_msg.fixed_minmax:
      if rgb in in_msg.rad_min.keys():
         min_data = in_msg.rad_min[rgb]
      else:
         if rgb not in products.RGBs_buildin:
            print "*** Warning, no specified minimum for plotting in get_input_msg.py or input file"
      if rgb in in_msg.rad_max.keys():
         max_data = in_msg.rad_max[rgb]
      else:
         if rgb not in products.RGBs_buildin:
            print "*** Warning, no specified maximum for plotting in get_input_msg.py or input file"
   if in_msg.verbose and rgb not in products.RGBs_buildin:
      print '... set value range from min_data (',min_data,') to max_data (',max_data,')'
      print '    min/max value of colormap', colormap.values[0], colormap.values[-1]

   # specifies if a colorbar does make sense at all
   in_msg.colormap={}

   # make the image
   if plot_type == 'channel_image':
      if in_msg.verbose:
         print "    use data.image.channel_image for black and white pictures"
      img = data.image.channel_image(rgb)
      in_msg.colormap[rgb] = None 
   elif plot_type == 'trollimage':
      if in_msg.verbose:
         print "    use trollimage.image.image for colorized pictures (min="+str(min_data)+", max="+str(max_data)+")"
      img = trollimage(prop, mode="L", fill_value=in_msg.fill_value)
      if colormap.values[0] == 0.0 and colormap.values[-1]==1.0:  # scale normalized colormap to range of data 
         colormap.set_range(min_data, max_data)
      img.colorize(colormap)
      in_msg.colormap[rgb] = colormap.reverse()
      # print "in_msg.colormap[rgb]", rgb, in_msg.colormap[rgb]
   elif plot_type == 'palette':
      min_data = 0.
      max_data = float(len(data[rgb].palette)-1)
      if in_msg.verbose:
         print "    use GeoImage and colorize with a palette (min="+str(min_data)+", max="+str(max_data)+")"
      img = GeoImage( prop, data.area, data.time_slot, mode="P", palette = data[rgb].palette, fill_value=in_msg.fill_value )
      colormap = convert_palette2colormap(data[rgb].palette)
      colormap.set_range(min_data, max_data)  # no return value!
      in_msg.colormap[rgb] = colormap
   elif plot_type == 'user_defined':
      obj_image = get_image(data, rgb)
      if in_msg.verbose:
         print "    use image function defined by my_msg_module.py"
      img = obj_image()
      in_msg.colormap[rgb] = None
      #if rgb == 'ndvi':
      #   in_msg.colormap[rgb] = rdylgn_r
   else:
      print "*** Error in create_PIL_image (plot_msg.py)"
      print "    unknown plot_type ", plot_type
      quit()


   if HRV_enhancement:
      if in_msg.verbose:
         print "enhance the image with the HRV channel"
      luminance = GeoImage((data["HRV"].data), data.area, data.time_slot,
                           crange=(0, 100), mode="L")
      luminance.enhance(gamma=2.0)
      img.replace_luminance(luminance.channels[0])

   ## alternative: for geoimages is possible to add coasts and borders, but not for trollimage
   #if hasattr(img, 'add_overlay'):
   #   if in_msg.verbose:
   #      print "    add coastlines to image by add_averlay"
   #   img.add_overlay(color=(0, 0, 0), width=0.5, resolution=None)

   # convert image to PIL image 
   if hasattr(img, 'pil_image'):
      if in_msg.verbose:
         print "    convert to PIL_image by pil_image function"
      PIL_image=img.pil_image()  
   else:
      if in_msg.verbose:
         print "    convert to PIL_image by saving and reading"
      tmp_file = outputDir +satS+'_'+dateS+'_'+timeS+'__'+area+'_'+rgb.replace("_","-")+'_tmp.png'  # in_msg.
      img.save(tmp_file)
      PIL_image = Image.open(tmp_file)
      subprocess.call("rm "+tmp_file, shell=True)

   return PIL_image


#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def add_border_and_rivers(PIL_image, cw, area_tuple, in_msg):

   if PIL_image.mode == 'RGB' or PIL_image.mode == 'RGBA': 
      border_color = in_msg.border_color
      river_color  = in_msg.river_color
   elif PIL_image.mode == 'L':
      border_color = 'white'
      river_color  = 'white'
   else:
      print "*** Error in add_border_and_rivers (plot_msg.py)"
      print "    Unknown image mode"

   if in_msg.add_rivers:
      if in_msg.verbose:
         print "    add rivers to image (resolution="+in_msg.resolution+")"
      cw.add_rivers(PIL_image, area_tuple, outline=river_color, resolution=in_msg.resolution, outline_opacity=127, width=0.5, level=5) # 
      if in_msg.verbose:
         print "    add lakes to image (resolution="+in_msg.resolution+")"
      cw.add_coastlines(PIL_image, area_tuple, outline=river_color, resolution=in_msg.resolution, outline_opacity=127, width=0.5, level=2)  #, outline_opacity=0
   if in_msg.add_borders:
      if in_msg.verbose:
         print "    add coastlines to image (resolution="+in_msg.resolution+")"
      cw.add_coastlines(PIL_image, area_tuple, outline=border_color, resolution=in_msg.resolution, width=1)  #, outline_opacity=0
      if in_msg.verbose:
         print "    add borders to image (resolution="+in_msg.resolution+")"
      cw.add_borders(PIL_image, area_tuple, outline=border_color, resolution=in_msg.resolution, width=1)     #, outline_opacity=0 

   return PIL_image

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def indicate_mask(rgb, PIL_image, data, verbose):

   mask = None
   if rgb in products.CPP:
      if rgb in ['cth','cldmask','cot','cph','ctt','cwp','dcld','dcot','dcwp','dndv','dreff',\
                    'precip','qa','reff','sds','sds_cs','sds_diff','sds_diff_cs']:

         mask = data['MASK'].data

   if mask != None:
      if verbose:
         print "    indicate measurement mask "

      img = trollimage(mask, mode="L", fill_value=None) #fill_value,[1,1,1], None
      from trollimage.colormap import greys
      img.colorize(greys)
      img.putalpha(mask*0 + 0.5)
      PIL_mask = img.pil_image()
      from PIL import Image as PILimage 
      PIL_image = PILimage.alpha_composite(PIL_mask, PIL_image)
   
   return PIL_image

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------


def add_title(PIL_image, rgb, sat_nr, dateS, hourS, minS, area, dc, verbose ):

   if verbose:
      print "    add title to image "

   if True: # new version of adding title 

      if PIL_image.mode == 'RGB' or PIL_image.mode == 'RGBA':    # color 
         title_color=(255,255,255)
         #title_color=(0,0,0)
         outline=(255, 0, 0)
      elif PIL_image.mode == 'L':    # black white 
         title_color=(255)
         outline=(255)

      # determine font size
      if area == "EuropeCanary":
         fontsize=36
      elif area.find("ticino") != -1:
         fontsize=12
      else:
         fontsize=18

      #fontsize=50
      font = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", fontsize)

      title = ' '+ "MSG-"+str(sat_nr-7) +', '+ dateS+' '+hourS+':'+minS+'UTC, '+area+', '+rgb
      draw = ImageDraw.Draw(PIL_image)

      # if area is not Europe 
      if area.find("EuropeCanary") == -1:
         y_pos_title=0
         if rgb=="CRR" or rgb=="CRPh" or rgb in products.CPP or rgb in products.HSAF:
            y_pos_title=20
            if rgb=="CRR":
               title= ' 2nd layer: '+rgb+", precip rate [mm/h]"
            if rgb=="CRPh":
               title= ' 2nd layer: '+rgb+" (day only), precip rate [mm/h]"
            if rgb in products.CPP:
               day_str=''
               if rgb in ['cth','cldmask','cot','cph','ctt','cwp','dcld','dcot','dcwp','dndv','dreff',\
                             'precip','qa','reff','sds','sds_cs','sds_diff','sds_diff_cs']:
                  day_str=" (day only)"
               title= ' 2nd layer: CPP ' + rgb + day_str
            if rgb in products.HSAF:
               title= " 2nd layer: HSAF "+ rgb + " [mm/h]"
         draw.text((0, y_pos_title),title, title_color,font=font)
      else:
         y1 =  5 # y1 = 10
         dy = 20 # dy = 50
         x1 =  0 # x1 = 10
         if not (rgb in products.CPP or rgb in products.HSAF) : # normal case  
            draw.text((x1, y1     ),' '+dateS+' '+hourS+':'+minS+'UTC', title_color, font=font)
            draw.text((x1, y1+  dy),' '+rgb.replace("_","-")+" (MSG-"+str(sat_nr-7) +' SEVIRI)',                title_color, font=font)
            #draw.text((x1, y1+2*dy),' '+rgb.replace("_","-"),           title_color, font=font)
         else:         
            draw.text((x1, y1+2*dy),' '+rgb.replace("_","-")+" (MSG-"+str(sat_nr-7) +' SEVIRI)',                title_color, font=font)
      if verbose:
         print "    added title: "+title

   else: # old version of adding title 
      font=aggdraw.Font("blue","/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf",size=16)
      dc.add_text(dateS+"\n"+"MSG-"+str(sat_nr-7)+" SEVIRI\n"+rgb.replace("_"," ")+"\n")

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def add_colorscale(dc, rgb, in_msg, unit=None):

   dc.align_right()
   dc.write_vertically()
   font_scale = aggdraw.Font("black","/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif-Bold.ttf",size=16)

   # choose tick marks for colorbar  
   tick_marks=20        # general default
   minor_tick_marks=5   # general default

   # look if there are default tick marks for the rgb product specified in get_input.py 
   if rgb in in_msg.tick_marks.keys():
      tick_marks=in_msg.tick_marks[rgb]
   if rgb in in_msg.minor_tick_marks.keys():
      minor_tick_marks=in_msg.minor_tick_marks[rgb]
   if rgb.find("-") != -1: # for channel differences use tickmarks of 1 
      tick_marks=1
      minor_tick_marks=1

   if in_msg.verbose:
      print '... add colorscale '
   dc.add_scale(in_msg.colormap[rgb], extend=True, tick_marks=tick_marks, minor_tick_marks=minor_tick_marks, font=font_scale, line_opacity=100, unit=unit) #

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
# the main function get the command line arguments and start the function plot_msg
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------

def print_usage():
         print "***           "
         print "*** Error, not enough command line arguments"
         print "***        please specify at least an input file"
         print "***        possible calls are:"
         print "*** python plot_msg.py input_MSG "
         print "*** python plot_msg.py input_MSG 2014 07 23 16 10 "
         print "                                 date and time must be completely given"
         print "*** python plot_msg.py input_MSG 2014 07 23 16 10 'IR_108'"
         print "*** python plot_msg.py input_MSG 2014 07 23 16 10 'IR_108' 'ccs4'"
         print "*** python plot_msg.py input_MSG 2014 07 23 16 10 ['HRoverview','fog'] ['ccs4','euro4']"
         print "***           "
         quit() # quit at this point

if __name__ == '__main__':

   import sys
   from get_input_msg import get_input_msg

   # get command line arguments, e.g. 
   # $: python plot_msg.py input_MSG or
   # $: python plot_msg.py input_MSG 2014 07 23 16 10 or
   # $: python plot_msg.py input_MSG 2014 07 23 16 10 'IR_108' 'ccs4' or
   # $: python plot_msg.py input_MSG 2014 07 23 16 10 ['HRoverview','fog'] ['ccs4','euro4']
   # and overwrite arguments given in the initialization in get_input_msg
   if len(sys.argv) < 2:
      print_usage()
   else:
      # read input file 
      input_file=sys.argv[1]
      if input_file[-3:] == '.py': 
         input_file=input_file[:-3]
      in_msg = get_input_msg(input_file)

      # check for more arguments 
      if len(sys.argv) > 2:
         if len(sys.argv) < 7:
            print_usage()
         else:
            year   = int(sys.argv[2])
            month  = int(sys.argv[3])
            day    = int(sys.argv[4])
            hour   = int(sys.argv[5])
            minute = int(sys.argv[6])
            # update time slot in in_msg class
            in_msg.update_datetime(year, month, day, hour, minute)
         if len(sys.argv) > 7:
            if type(sys.argv[7]) is str:
               in_msg.RGBs = [sys.argv[7]]
            else:
               in_msg.RGBs = sys.argv[7]
            if len(sys.argv) > 8:
               if type(sys.argv[8]) is str:
                  in_msg.area = [sys.argv[8]]
               else:
                  in_msg.area = sys.argv[8]

   RGBs_done = plot_msg(in_msg)
   print "*** Satellite pictures produced for ", RGBs_done 
   print " "
