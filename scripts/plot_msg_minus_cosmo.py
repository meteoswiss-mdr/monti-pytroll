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
from my_msg_module import choose_msg, choose_area_loaded_msg, convert_NWCSAF_to_radiance_format, get_NWC_pge_name, format_name
from my_msg_module import check_loaded_channels
from postprocessing import postprocessing

import products
from datetime import datetime

from plot_msg import load_products, create_PIL_image, choose_map_resolution, save_reprojected_data, mask_data
from plot_msg import add_colorscale, add_title, indicate_mask, add_borders_and_rivers
from get_input_msg import parse_commandline_and_read_inputfile

import inspect

from mpop.utils import debug_on
debug_on() 

try:
  basestring
except NameError:
  basestring = str

#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------


def plot_msg_minus_cosmo(in_msg):


   # do statistics for the last full hour (minutes=0, seconds=0) 
   in_msg.datetime = datetime(in_msg.datetime.year, in_msg.datetime.month, in_msg.datetime.day, in_msg.datetime.hour, 0, 0) 
  
   area_loaded = choose_area_loaded_msg(in_msg.sat, in_msg.sat_nr, in_msg.datetime)  
   
   # define contour write for coasts, borders, rivers
   cw = ContourWriterAGG(in_msg.mapDir)

   # check if input data is complete 
   if in_msg.verbose:
      print "*** check input data for ", in_msg.sat_str()
   RGBs = check_input(in_msg, in_msg.sat_str(layout="%(sat)s")+in_msg.sat_nr_str(), in_msg.datetime)  
   # in_msg.sat_nr might be changed to backup satellite

   if in_msg.verbose:
      print '*** Create plots for '
      print '    Satellite/Sensor: ' + in_msg.sat_str() 
      print '    Satellite number: ' + in_msg.sat_nr_str() +' // ' +str(in_msg.sat_nr)
      print '    Satellite instrument: ' + in_msg.instrument
      print '    Date/Time:        '+ str(in_msg.datetime)
      print '    RGBs:            ', in_msg.RGBs
      print '    Area:            ', in_msg.areas
      print '    reader level:    ', in_msg.reader_level

   # define satellite data object
   #global_data = GeostationaryFactory.create_scene(in_msg.sat, in_msg.sat_nr_str(), "seviri", in_msg.datetime)
   global_data = GeostationaryFactory.create_scene(in_msg.sat_str(), in_msg.sat_nr_str(), in_msg.instrument, in_msg.datetime)
   # global_data = GeostationaryFactory.create_scene("msg-ot", "", "Overshooting_Tops", in_msg.datetime)
   
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

   cosmo_input_file="input_cosmo_cronjob.py"
   print "... read COSMO input file: ", cosmo_input_file
   in_cosmo = parse_commandline_and_read_inputfile(input_file=cosmo_input_file)

   # add composite
   in_msg.scpOutput = True
   in_msg.resize_montage = 70
   in_msg.postprocessing_montage = [["MSG_IR-108cpc","COSMO_SYNMSG-BT-CL-IR10.8","MSG_IR-108-COSMO-minus-MSGpc"]]
   in_msg.scpProducts = [["MSG_IR-108cpc","COSMO_SYNMSG-BT-CL-IR10.8","MSG_IR-108-COSMO-minus-MSGpc"]]
   #in_msg.scpProducts = ["all"]

   # define satellite data object
   cosmo_data = GeostationaryFactory.create_scene(in_cosmo.sat_str(), in_cosmo.sat_nr_str(), in_cosmo.instrument, in_cosmo.datetime)

   area_loaded_cosmo = load_products(cosmo_data, ['SYNMSG_BT_CL_IR10.8'], in_cosmo, area_loaded)
   
   # preprojecting the data to another area 
   # --------------------------------------
   if len(RGBs) > 0:
      for area in in_msg.areas:
         print ""
         obj_area = get_area_def(area) 

         if area != 'ccs4':
           print "*** WARNING, diff MSG-COSMO only implemented for ccs4"
           continue 
         
         # reproject data to new area
         print  area_loaded
 
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
            data = global_data.project(area, precompute=True)
            resolution='i'

         if in_msg.parallax_correction:
            loaded_products = [chn.name for chn in data.loaded_channels()]

            if 'CTH' not in loaded_products:
               print "*** Error in plot_msg ("+inspect.getfile(inspect.currentframe())+")"
               print "    Cloud Top Height is needed for parallax correction "
               print "    either load CTH or specify the estimation of the CTH in the input file (load 10.8 in this case)"
               quit()

            if in_msg.verbose:
               print "    perform parallax correction for loaded channels: ", loaded_products

            data = data.parallax_corr(fill=in_msg.parallax_gapfilling, estimate_cth=in_msg.estimate_cth, replace=True)
 
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
            in_msg.resolution = choose_map_resolution(area, in_msg.mapResolution) 

            # define area
            proj4_string = obj_area.proj4_string            
            # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
            area_extent = obj_area.area_extent              
            # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
            area_tuple = (proj4_string, area_extent)

            RGBs=['IR_108-COSMO-minus-MSG']

            print data['IR_108'].data.shape
            print cosmo_data['SYNMSG_BT_CL_IR10.8'].data.shape
            diff_MSG_COSMO = cosmo_data['SYNMSG_BT_CL_IR10.8'].data - data['IR_108'].data
            HRV_enhance_str=''
            
            # add IR difference as "channel object" to satellite regional "data" object
            data.channels.append(Channel(name=RGBs[0],
                                         wavelength_range=[0.,0.,0.],
                                         resolution=data['IR_108'].resolution, 
                                         data = diff_MSG_COSMO) )
            
            for rgb in RGBs:

               if not check_loaded_channels(rgb, data):
                  continue 

               PIL_image = create_PIL_image(rgb, data, in_msg, obj_area=obj_area)  
                                          # !!! in_msg.colorbar[rgb] is initialized inside (give attention to rgbs) !!!

               add_borders_and_rivers(PIL_image, cw, area_tuple,
                                      add_borders=in_msg.add_borders, border_color=in_msg.border_color,
                                      add_rivers=in_msg.add_rivers, river_color=in_msg.river_color, 
                                      resolution=in_msg.resolution, verbose=in_msg.verbose)

               # indicate mask
               if in_msg.indicate_mask:
                  PIL_image = indicate_mask(rgb, PIL_image, data, in_msg.verbose)

               #if area.find("EuropeCanary") != -1 or area.find("ccs4") != -1: 
               dc = DecoratorAGG(PIL_image)

               # add title to image
               if in_msg.add_title:
                  add_title(PIL_image, in_msg.title, HRV_enhance_str+rgb, in_msg.sat_str(), data.sat_nr(), in_msg.datetime, area, dc, in_msg.verbose,
                            title_color=in_msg.title_color, title_y_line_nr=in_msg.title_y_line_nr ) # !!! needs change

               # add MeteoSwiss and Pytroll logo
               if in_msg.add_logos:
                  if in_msg.verbose:
                     print '... add logos'
                  dc.align_right()
                  if in_msg.add_colorscale:
                     dc.write_vertically()
                  if PIL_image.mode != 'L':
                     height = 60  # height=60.0 normal resolution 
                     dc.add_logo(in_msg.logos_dir+"/pytroll3.jpg",height=height)                          # height=60.0
                     dc.add_logo(in_msg.logos_dir+"/meteoSwiss3.jpg",height=height)                       
                     dc.add_logo(in_msg.logos_dir+"/EUMETSAT_logo2_tiny_white_square.png",height=height)  # height=60.0

               # add colorscale
               if in_msg.add_colorscale and in_msg.colormap[rgb] != None:
                  if rgb in products.MSG_color:
                     unit = data[rgb.replace("c","")].info['units']
                  #elif rgb in products.MSG or rgb in products.NWCSAF or rgb in products.HSAF:
                  #   unit = data[rgb].info['units']
                  else:
                     unit = None
                     loaded_channels = [chn.name for chn in data.loaded_channels()]
                     if rgb in loaded_channels:
                       if hasattr(data[rgb], 'info'):
                         print "    hasattr(data[rgb], 'info')", data[rgb].info.keys()
                         if 'units' in data[rgb].info.keys():
                           print "'units' in data[rgb].info.keys()"
                           unit = data[rgb].info['units']
                  print "... units = ", unit
                  add_colorscale(dc, rgb, in_msg, unit=unit)

               if in_msg.parallax_correction:
                  parallax_correction_str='pc'
               else:
                  parallax_correction_str=''
               rgb+=parallax_correction_str

               # create output filename
               outputDir =              format_name(in_msg.outputDir,  data.time_slot, area=area, rgb=rgb, sat=data.satname, sat_nr=data.sat_nr()) # !!! needs change
               outputFile = outputDir +"/"+ format_name(in_msg.outputFile, data.time_slot, area=area, rgb=rgb, sat=data.satname, sat_nr=data.sat_nr()) # !!! needs change

               # check if output directory exists, if not create it
               path= dirname(outputFile)
               if not exists(path):
                  if in_msg.verbose:
                     print '... create output directory: ' + path
                  makedirs(path)

               # save file
               if exists(outputFile) and not in_msg.overwrite:
                  if stat(outputFile).st_size > 0:
                     print '... outputFile '+outputFile+' already exists (keep old file)'
                  else: 
                     print '*** Warning, outputFile'+outputFile+' already exists, but is empty (overwrite file)'
                     PIL_image.save(outputFile, optimize=True)  # optimize -> minimize file size
                     chmod(outputFile, 0777)  ## FOR PYTHON3: 0o664  # give access read/write access to group members
               else:
                  if in_msg.verbose:
                     print '... save final file: ' + outputFile
                  PIL_image.save(outputFile, optimize=True)  # optimize -> minimize file size
                  chmod(outputFile, 0777)  ## FOR PYTHON3: 0o664  # give access read/write access to group members

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

               # secure copy file to another place
               if in_msg.scpOutput:
                  if (rgb in in_msg.scpProducts) or ('all' in [x.lower() for x in in_msg.scpProducts if type(x)==str]):
                     scpOutputDir = format_name (in_msg.scpOutputDir, data.time_slot, area=area, rgb=rgb, sat=data.satname, sat_nr=data.sat_nr() )
                     if in_msg.compress_to_8bit:
                        if in_msg.verbose:
                           print "... secure copy "+outputFile.replace(".png","-fs8.png")+ " to "+scpOutputDir
                        subprocess.call("scp "+in_msg.scpID+" "+outputFile.replace(".png","-fs8.png")+" "+scpOutputDir+" 2>&1 &", shell=True)
                     else:
                        if in_msg.verbose:
                           print "... secure copy "+outputFile+ " to "+scpOutputDir
                        subprocess.call("scp "+in_msg.scpID+" "+outputFile+" "+scpOutputDir+" 2>&1 &", shell=True)

               if in_msg.scpOutput and in_msg.scpID2 != None and in_msg.scpOutputDir2 != None:
                  if (rgb in in_msg.scpProducts2) or ('all' in [x.lower() for x in in_msg.scpProducts2 if type(x)==str]):
                     scpOutputDir2 = format_name (in_msg.scpOutputDir2, data.time_slot, area=area, rgb=rgb, sat=data.satname, sat_nr=data.sat_nr() )
                     if in_msg.compress_to_8bit:
                        if in_msg.verbose:
                           print "... secure copy "+outputFile.replace(".png","-fs8.png")+ " to "+scpOutputDir2
                        subprocess.call("scp "+in_msg.scpID2+" "+outputFile.replace(".png","-fs8.png")+" "+scpOutputDir2+" 2>&1 &", shell=True)
                     else:
                        if in_msg.verbose:
                           print "... secure copy "+outputFile+ " to "+scpOutputDir2
                        subprocess.call("scp "+in_msg.scpID2+" "+outputFile+" "+scpOutputDir2+" 2>&1 &", shell=True)

                           
               if 'ninjotif' in in_msg.outputFormats:
                  ninjotif_file = format_name (outputDir+'/'+in_msg.ninjotifFilename, data.time_slot, sat_nr=data.sat_nr(), RSS=in_msg.RSS, area=area, rgb=rgb )
                  from plot_coalition2 import pilimage2geoimage
                  GEO_image = pilimage2geoimage(PIL_image, obj_area, data.time_slot)
                  GEO_image.save(ninjotif_file,
                                fformat='mpop.imageo.formats.ninjotiff',
                                ninjo_product_name=rgb, chan_id = products.ninjo_chan_id[rgb.replace("_","-")+"_"+area],
                                nbits=8)
                  chmod(ninjotif_file, 0777)
                  print ("... save ninjotif image: display ", ninjotif_file, " &")

               if rgb not in RGBs_done:
                  RGBs_done.append(rgb)
   
      ## start postprocessing
      for area in in_msg.postprocessing_areas:
         postprocessing(in_msg, global_data.time_slot, int(data.sat_nr()), area)

   if in_msg.verbose:
      print " "

   return RGBs_done

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
   print "*** python "+inspect.getfile(inspect.currentframe())+" input_MSG "
   print "*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 "
   print "                                 date and time must be completely given"
   print "*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 'IR_108'"
   print "*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 'IR_108' 'ccs4'"
   print "*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 ['HRoverview','fog'] ['ccs4','euro4']"
   print "***           "
   quit() # quit at this point
#----------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

   in_msg = parse_commandline_and_read_inputfile(input_file="input_msg_cosmo_cronjob.py")

   RGBs_done = plot_msg_minus_cosmo(in_msg)
   print "*** Satellite pictures produced for ", RGBs_done 
   print " "
