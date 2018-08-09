## does not work!!!
#import subprocess
#print "... set python path and config path" 
#subprocess.call("export PYTHONPATH=/home/cinesat/python/lib/python2.7/site-packages:${PWD}", shell=True)
#subprocess.call("export PPP_CONFIG_DIR=${PWD}", shell=True)
#subprocess.call("export XRIT_DECOMPRESS_PATH=/data/OWARNA/hau/pytroll/bin/xRITDecompress", shell=True)

from datetime import datetime
import sys, string, os
import logging
sys.path.insert(0, "/home/lom/users/cll/pytroll/install/lib/python2.6/site-packages")
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from mpop.utils import debug_on
from pyresample import plot
from trollimage.colormap import rainbow, RainRate
from trollimage.image import Image as trollimage
import numpy as np
from pydecorate import DecoratorAGG
import aggdraw
from PIL import ImageFont, ImageDraw 
from os.path import exists
from os import makedirs
from pycoast import ContourWriterAGG
from datetime import timedelta

# debug_on()

save_statistics=False
delay = 5
verbose=True
#layer=''
layer=' 2nd layer'
#layer=' 3rd layer'

#color_mode='rainbow'
color_mode='RainRate'
#color_mode='datalevels256'

add_rivers=True
add_borders=True 
if len(layer) > 0:
    print "*** No borders and rivers for an overlay"
    add_rivers  = False # no rivers if an overlay is needed
    add_borders = False # no map    if an overlay is needed
add_title=True
add_logos=False
add_colorscale=True
fill_value=None # transparent background 
#fill_value=(1,1,1)  # white background
#title_color=(0,0,0)
title_color='white'
#fill_value=(0,0,0)  # black background 
#title_color=(255,255,255)



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
        minute=35

time_slot = datetime(year, month, day, hour, minute)
print "*** "
print "*** read radar data (plot_radar.py)"
global_data = GeostationaryFactory.create_scene("swissradar", "", "radar", time_slot)
prop_str='PRECIP'                     # RZC
#prop_str='POH'    # does not work!!!  # BZC
#prop_str='MESHS' # does not work!!!  # MZC
#prop_str='VIL'                       # LZC
#prop_str='MaxEcho'                   # CZC
#prop_str='EchoTOP15'                 # EZC
#prop_str='EchoTOP20'                 # EZC                 
#prop_str='EchoTOP45'                 # EZC
#prop_str='EchoTOP50'                 # EZC
#global_data = GeostationaryFactory.create_scene("dem", "", "dem", time_slot)
#prop_str = 'dem'

#global_data.load(['precip', 'maxecho'])
#print "global_data ", global_data
area="ccs4"

#global_data = GeostationaryFactory.create_scene("hsaf", "", "seviri", time_slot)
#prop_str = 'h03'
#area="hsaf"

obj_area = get_area_def(area)
global_data.load([prop_str])

#plot.show_quicklook(obj_area, global_data[prop_str].data )
#print "global_data[prop_str].data", global_data[prop_str].data
#print "global_data[prop_str].data", global_data[prop_str].data[355,:]
#print "shape: ", global_data[prop_str].data.shape
#print "radar product name: ", global_data[prop_str].product_name

#prop = np.ma.asarray(global_data[prop_str].data)
#prop.mask = (prop == 9999.9) | (prop <= 0.0001) 

# print "prop.shape (plot_radar.py)", prop.shape


yearS = str(year)
#yearS = yearS[2:]
monthS = "%02d" % month
dayS   = "%02d" % day
hourS  = "%02d" % hour
minS   = "%02d" % minute
dateS=yearS+'-'+monthS+'-'+dayS
timeS=hourS+':'+minS+'UTC' 

top_str=''
if hasattr(global_data[prop_str], 'product_name'):
    if global_data[prop_str].product_name == 'EZC':
        top_str=global_data[prop_str].name[-2:]


#output_dir='./'+yearS+'-'+monthS+'-'+dayS+'/'+yearS+'-'+monthS+'-'+dayS+'_'+prop_str+'-'+area+'/'
#output_dir='./pics/'
output_dir='/data/COALITION2/PicturesSatellite/'+yearS+'-'+monthS+'-'+dayS+'/'+yearS+'-'+monthS+'-'+dayS+'_radar_'+area+'/'
#output_dir = '/data/COALITION2/PicturesSatellite/%Y-%m-%d/%Y-%m-%d_RZC_%(area)s/'

if not exists(output_dir):
    print '... create output directory: ' + output_dir
    makedirs(output_dir)

# calculate statistics (area with precipitation, mean precipitation, total precipitation)
if save_statistics:
    statisticFile = output_dir + 'RAD_'+global_data[prop_str].product_name+'-'+area+'_'+yearS[2:]+monthS+dayS+'.txt'
    f1 = open(statisticFile,'a')   # mode append 
    ind = (prop > 0.0001) &  (prop < 500.0)
    print "prop.data[ind]"
    #for pp in prop.data[ind]:
    #    print pp
    prop_mean=prop.data[ind].mean()
    prop_p50 =np.percentile(prop.data[ind],50)
    prop_p75 =np.percentile(prop.data[ind],75)
    prop_p90 =np.percentile(prop.data[ind],90)
    prop_max =prop.data[ind].max()
    area_km2 =prop.data[ind].size

    str2write = yearS+' '+monthS+' '+dayS+' '+hourS+' '+minS+'      '
    str2write = str2write+' '+ "%7.4f" % prop_mean
    str2write = str2write+' '+ "%7.3f" % prop_p50
    str2write = str2write+' '+ "%7.3f" % prop_p75
    str2write = str2write+' '+ "%7.3f" % prop_p90
    str2write = str2write+' '+ "%7.2f" % prop_max
    str2write = str2write+' '+ "%8.0f" % area_km2
    str2write = str2write+"\n"
    print  "date       HH : MM UTC    mean      p50     p75     p90   max      area"
    #      "2014-07-23 18 : 00 UTC    2.1661    1.00    2.00    5.05  118.05  54868"
    print str2write
    f1.write(str2write) 
    f1.close()
    print "wrote statistics file: emacs "+ statisticFile +" &"


#outputFile = "./pics/radar.png"
outputFile = output_dir+'RAD_'+global_data[prop_str].product_name+top_str+'-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS +'.png'

prop=global_data[prop_str].data

#min_data=prop.min()
min_data=0
max_data = prop.max()
print 'max_data: ', max_data
if prop.max() < 10:
    max_data=max_data-(max_data%1)
    print 'round(max_data): ', max_data
else:
    max_data=max_data-(max_data%10)
    print 'round(max_data): ', max_data

if max_data >= 20:
    tick_marks=10        # default
    minor_tick_marks=5  # default
else:
    tick_marks=2        # default
    minor_tick_marks=1  # default    

if global_data[prop_str].units=='km':
    max_data=12
    tick_marks=2
    minor_tick_marks=1
elif prop_str=='vil':
    max_data=15
    tick_marks=5
    minor_tick_marks=1  # default
elif prop_str=='POH':
    min_data=0
    max_data=100
#    tick_marks=5
#    minor_tick_marks=1  # default
#elif prop_str.find('echotop') != -1:
#    max_data=12
#    tick_marks=5
#    minor_tick_marks=1  # default
#elif prop_str=='maxecho':
#    max_data=60

print "*** min/max: ", min_data, max_data

method='linear'
method='logarithmic'
units = '['+global_data[prop_str].units+']'

print color_mode
if color_mode == 'rainbow':

    colormap = rainbow

    if method == 'logarithmic':
        prop = np.log10(prop)
        min_data = prop.min()
        #max_data = prop.max()
        #min_data = -0.25 
        #max_data = 1.9
        min_data = -0.2 # log(0.63)
        max_data = 2.41  # log(260)
        units='log(RR)'
        tick_marks = 1           # default
        minor_tick_marks = 0.1   # default

    colormap.set_range(min_data, max_data)

elif color_mode == 'RainRate':
    min_data = 0.08
    max_data = 250
    colormap = RainRate
    units='mm/h'
elif color_mode == 'datalevels256':

    if prop_str == 'PRECIP':
        from trollimage.colormap import RainRate
        colormap = RainRate        
    elif prop_str == 'POH':
        from trollimage.colormap import ProbabilityOfHail
        colormap = ProbabilityOfHail
        #from trollimage.colormap import rainbow
        #colormap = rainbow
    elif prop_str == 'MESHS':
        from trollimage.colormap import MESHS
        colormap = MESHS
    elif prop_str == 'VIL':
        from trollimage.colormap import VerticalIntegratedLiquid
        colormap = VerticalIntegratedLiquid
    elif prop_str == 'MaxEcho':
        from trollimage.colormap import Reflectivity
        colormap = Reflectivity
    elif prop_str[0:7] == 'EchoTOP':
        from trollimage.colormap import EchoTop
        colormap = EchoTop

    #from ConfigParser import ConfigParser
    #from mpop import CONFIG_PATH
    #conf = ConfigParser()
    #conf.read(os.path.join(CONFIG_PATH, global_data.fullname + ".cfg"))
    #for i in xrange(9):
    #    radar_product='radar-{0:1d}'.format(i+1)
    #    prod_name = conf.get(radar_product, "name")
    #    if prod_name.replace("'", "").replace('"', '') == prop_str.replace("'", "").replace('"', ''):
    #        if verbose:
    #            print "... radar product to read:", prop_str
    #        scale = conf.get(radar_product, "scale")
    #        print '... read color scale from ', scale
    #        break
    ##scale = conf.get(prop_str, "scale")
    #colorscale = np.loadtxt(scale, skiprows=1)
    #print colorscale
    #print colorscale.shape, type(colorscale)
    #print colorscale[1:,4], type(colorscale[0,:])
    #print colorscale[1:,1:4]    
    
else:
    print "*** ERROR, unknown color mode"

print '... use trollimage to ', method,' plot data (min,max)=',min_data, max_data
if 'fill_value' in locals():
    img = trollimage(prop, mode="L", fill_value=fill_value) 
else:
    img = trollimage(prop, mode="L")
 
img.colorize(colormap)

PIL_image=img.pil_image()
dc = DecoratorAGG(PIL_image)

# define contour write for coasts, borders, rivers
cw = ContourWriterAGG('/data/OWARNA/hau/maps_pytroll/')

resolution='l'
if area.find("EuropeCanary") != -1:
    resolution='l'
if area.find("ccs4") != -1:
    resolution='i' 
if area.find("ticino") != -1:
    resolution='h'

# define area
print 'obj_area ', obj_area
proj4_string = obj_area.proj4_string     
# e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
area_extent = obj_area.area_extent              
# e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
area_def = (proj4_string, area_extent)
print 'area_def ', area_def

if add_rivers:
   if verbose:
      print "    add rivers to image (resolution="+resolution+")"
   cw.add_rivers(PIL_image, area_def, outline='blue', resolution=resolution, outline_opacity=127, width=1, level=5) # 
   if verbose:
      print "    add lakes to image (resolution="+resolution+")"
   cw.add_coastlines(PIL_image, area_def, outline='blue', resolution=resolution, outline_opacity=127, width=1, level=2)  #, outline_opacity=0
if add_borders:
   outline = (255, 0, 0)
   outline = 'black'
   if verbose:
      print "    add coastlines to image (resolution="+resolution+")"
   cw.add_coastlines(PIL_image, area_def, outline=outline, resolution=resolution, width=2)  #, outline_opacity=0
   if verbose:
      print "    add borders to image (resolution="+resolution+")"
   cw.add_borders(PIL_image, area_def, outline=outline, resolution=resolution, width=2)       #, outline_opacity=0 

# add MeteoSwiss and Pytroll logo
if add_logos:
    if verbose:
        print '... add logos'
    dc.align_right()
    if add_colorscale:
        dc.write_vertically()
    dc.add_logo("/opt/users/common/logos/meteoSwiss3.jpg",height=60.0)
    dc.add_logo("/opt/users/common/logos/pytroll3.jpg",height=60.0)
    dc.add_logo("/opt/users/common/logos/EUMETSAT_logo2_tiny_white.png",height=60.0)

if add_colorscale:
    print '... add colorscale ranging from min_data (',min_data,') to max_data (',max_data,')'
    dc.align_right()
    dc.write_vertically()
    font_scale = aggdraw.Font("black","/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif-Bold.ttf",size=16)
    colormap_r = colormap.reverse()
    #rainbow_r.set_range(min_data, max_data)
    dc.add_scale(colormap_r, extend=True, tick_marks=tick_marks, minor_tick_marks=minor_tick_marks, font=font_scale, line_opacity=100, unit=units) #

if add_title:
    draw = ImageDraw.Draw(PIL_image)
    fontsize=18
    font = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", fontsize)

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
    title = layer+' radar, '+'precipitation rate'+' ['+global_data[prop_str].units+']'
    draw.text((0, y_pos_title),title, title_color, font=font)

print '... save image as ', outputFile
PIL_image.save(outputFile)
