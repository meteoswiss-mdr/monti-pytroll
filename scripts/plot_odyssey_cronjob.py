#!/usr/bin/python
import datetime
import logging

from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from mpop.utils import debug_on

from pyresample import plot
import numpy as np
from pydecorate import DecoratorAGG
import aggdraw
from trollimage.colormap import rainbow, RainRate
from trollimage.image import Image as trollimage
from PIL import ImageFont, ImageDraw 
from pycoast import ContourWriterAGG
from datetime import timedelta
import sys

LOG = logging.getLogger(__name__)

delay=0

print "... number of arguments:", len(sys.argv)

if len(sys.argv) > 1:
    if len(sys.argv) < 6:
        print "***           "
        print "*** Warning, please specify date and time completely, e.g."
        print "***          python plot_hsaf.py 2014 07 23 16 10 "
        print "***           "
        quit() # quit at this point
    else:
        year   = int(sys.argv[1])
        month  = int(sys.argv[2])
        day    = int(sys.argv[3])
        hour   = int(sys.argv[4])
        minute = int(sys.argv[5])
else:
    if True:  # automatic choise of last 5min 
        from my_msg_module import get_last_SEVIRI_date
        datetime1 = get_last_SEVIRI_date(False)
        if delay != 0:
            datetime1 -= timedelta(minutes=delay)
        year  = datetime1.year
        month = datetime1.month
        day   = datetime1.day
        hour  = datetime1.hour
        minute = datetime1.minute
    else: # fixed date for text reasons
        year = 2015
        month = 12
        day = 16
        hour = 13
        minute = 30

#prop_str='DBZH'
prop_str='RATE'

#if len(sys.argv) > 1:
#   prop_str = sys.argv[1]

yearS = str(year)
#yearS = yearS[2:]
monthS = "%02d" % month
dayS   = "%02d" % day
hourS  = "%02d" % hour
minS   = "%02d" % minute
dateS=yearS+'-'+monthS+'-'+dayS
timeS=hourS+':'+minS+'UTC' 


#import sys, string, os
#sys.path.insert(0, "/opt/users/mbc/pytroll/install/lib/python2.6/site-packages")
debug_on()

time_slot = datetime.datetime(year, month, day, hour, minute)
print "... process date: ",  str(time_slot)

global_data = GeostationaryFactory.create_scene("odyssey", "", "radar", time_slot)

global_data.load([prop_str])

color_mode='RainRate'

outputDir = "/data/cinesat/out/"
#outputFile = "/tmp/test1."+prop_str+".png"

#print "global_data[prop_str].product_name=",global_data[prop_str].product_name

#area='odyssey'
area='odysseyS25'

reproject=True
if reproject:
   print '-------------------'
   print "start projection"
   # PROJECT data to new area 
   data = global_data.project(area)
   #data[prop_str].product_name = global_data[prop_str].product_name
   #data[prop_str].units = global_data[prop_str].units
   global_data = data

obj_area = get_area_def(area)

outputFile = outputDir+'ODY_'+prop_str+'-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS +'.png'


# define area
print '-------------------'
print 'obj_area ', obj_area
proj4_string = obj_area.proj4_string     
# e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
print 'proj4_string ',proj4_string
area_extent = obj_area.area_extent              
# e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
area_def = (proj4_string, area_extent)
print '-------------------'
print 'area_def ', area_def


prop=global_data[prop_str].data

fill_value=None # transparent background 
min_data = 0.0
max_data = 150
colormap = RainRate

if prop_str == 'RATE':
#   prop = np.log10(prop)
#   min_data = prop.min()
#   #max_data = prop.max()
#   #min_data = -0.25 
#   #max_data = 1.9
#   min_data = -0.2 # log(0.63)
#   max_data = 2.41  # log(260)
#   units='log(RR)'
#   tick_marks = 1           # default
#   minor_tick_marks = 0.1   # default
   lower_value=0.15

if prop_str == 'DBZH':
   min_data = -20
   max_data = 70
   colormap = rainbow
   lower_value=13

if prop_str == 'ACRR':
   min_data = 0
   max_data = 250
   lower_value=0.15


if lower_value > -1000:
   prop [prop < lower_value ] = np.ma.masked

LOG.debug("min_data/max_data: "+str(min_data)+" / "+str(max_data))
colormap.set_range(min_data, max_data)

img = trollimage(prop, mode="L", fill_value=fill_value)
img.colorize(colormap)
PIL_image=img.pil_image()
dc = DecoratorAGG(PIL_image)

resolution='l'

if False:
   cw = ContourWriterAGG('/data/OWARNA/hau/pytroll/shapes/')
   cw.add_coastlines(PIL_image, area_def, outline='white', resolution=resolution, outline_opacity=127, width=1, level=2)  #, outline_opacity=0

   outline = (255, 0, 0)
   outline = 'red'
   cw.add_coastlines(PIL_image, area_def, outline=outline, resolution=resolution, width=2)  #, outline_opacity=0
   cw.add_borders(PIL_image, area_def, outline=outline, resolution=resolution, width=2)       #, outline_opacity=0 

add_logos=1
add_colorscale=0
add_title=1
verbose=1
layer=' 2nd layer'

ticks=20
tick_marks=20        # default
minor_tick_marks=10  # default
title_color='white'
units=global_data[prop_str].info["units"]
#global_data[prop_str].units

if add_logos:
   if verbose:
      print '... add logos'
   dc.align_right()
   if add_colorscale:
      dc.write_vertically()
   #dc.add_logo("../logos/meteoSwiss3.jpg",height=60.0)
   #dc.add_logo("../logos/pytroll3.jpg",height=60.0)
   #dc.add_logo("/data/OWARNA/hau/pytroll/logos/meteoSwiss.png",height=40.0)
   dc.add_logo("../logos/meteoSwiss.png",height=40.0)
   
#font_scale = aggdraw.Font("black","/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif-Bold.ttf",size=16)
fontsize=18
font = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", fontsize)

if add_colorscale:
   print '... add colorscale ranging from min_data (',min_data,') to max_data (',max_data,')'
   dc.align_right()
   dc.write_vertically()
   #font_scale = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", fontsize)
   colormap_r = colormap.reverse()
   #rainbow_r.set_range(min_data, max_data)
   dc.add_scale(colormap_r, extend=True, ticks=ticks, tick_marks=tick_marks, minor_tick_marks=minor_tick_marks, font=font, line_opacity=100, unit=units) #

indicate_range=True
if indicate_range:
    mask = global_data[prop_str+'-MASK'].data
    img = trollimage(mask, mode="L", fill_value=None) #fill_value,[1,1,1], None
    from trollimage.colormap import greys
    img.colorize(greys.reverse())
    img.putalpha(mask*0+0.25)
    PIL_mask = img.pil_image()
    from PIL import Image as PILimage 
    PIL_image = PILimage.alpha_composite(PIL_mask, PIL_image)

if add_title:
   draw = ImageDraw.Draw(PIL_image)

   if layer.find('2nd') != -1:
      y_pos_title=20
   elif layer.find('3rd') != -1:
      y_pos_title=40
   else:
      y_pos_title=5
      layer = dateS+' '+timeS
   if len(layer) > 0:
      layer=layer+':'

   #title = layer+' radar, '+prop_str+' ['+global_data[prop_str].units+']'
   title = layer+' ODYSSEY, '+'precipitation rate'+' ['+global_data[prop_str].info["units"]+']'
   draw.text((0, y_pos_title),title, title_color, font=font)


PIL_image.save(outputFile)
print '... save image as ', outputFile

# make composite and scp composite
if True:
    from get_input_msg import get_input_msg
    in_msg = get_input_msg('input_template')
    from postprocessing import postprocessing
    in_msg.postprocessing_areas=[area]
    in_msg.scpOutput = False
    in_msg.datetime = global_data.time_slot
    in_msg.outputDir = outputDir
    in_msg.postprocessing_composite=["RATE-HRV", "RATE-ir108", "RATE-VIS006ir108"]   
    postprocessing(in_msg, global_data.time_slot, global_data.number, area)
