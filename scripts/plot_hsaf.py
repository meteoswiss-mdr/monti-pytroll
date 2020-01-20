from __future__ import division
from __future__ import print_function

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
from trollimage.colormap import rainbow, hsaf
from trollimage.image import Image as trollimage
import numpy as np
from pydecorate import DecoratorAGG
import aggdraw
from PIL import ImageFont, ImageDraw 
from os.path import exists
from os import makedirs
from pycoast import ContourWriterAGG
from datetime import timedelta

import scp_settings
scpOutputDir = scp_settings.scpOutputDir
scpID = scp_settings.scpID 

# debug_on()

save_statistics=False
verbose=True
layer=''
#layer=' 2nd layer'
#layer=' 3rd layer'
#add_rivers=True
add_rivers=False
add_borders=True
if len(layer) > 0:
    print("*** No borders and rivers for an overlay")
    add_rivers  = False # no rivers if an overlay is needed
    add_borders = False # no map    if an overlay is needed

add_title=True
add_logos=True

add_colorscale=True
#add_colorscale=False

#color_mode=''
color_mode='hsaf'
#color_mode='radar'

areas=['ccs4']
#areas=['EuropeCanaryS95']
#areas=['ccs4','EuropeCanaryS95']

parallax_correction=True
estimate_cth=False

#fill_value=(1,1,1) # fill_value=(1,1,1)  # white background
#fill_value=(0,0,0) # fill_value=(0,0,0)  # black background 
fill_value=None
title_color=(0,0,0)
#title_color=(255,255,255)
delay=10    # usually 8min, between 0->8 and 15->23 

if len(sys.argv) > 1:
    if len(sys.argv) < 6:
        print("***           ")
        print("*** Warning, please specify date and time completely, e.g.")
        print("***          python plot_hsaf.py 2014 07 23 16 10 ")
        print("***           ")
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
        datetime1 = get_last_SEVIRI_date(False, delay=delay)
        year  = datetime1.year
        month = datetime1.month
        day   = datetime1.day
        hour  = datetime1.hour
        minute = datetime1.minute
    else: # fixed date for text reasons
        year=2015
        month= 7
        day= 21
        hour= 12
        minute=45

time_slot = datetime(year, month, day, hour, minute)
print("*** ")
print("*** read hsaf data (plot_hsaf.py)")
#global_data = GeostationaryFactory.create_scene("dem", "", "dem", time_slot)
#prop_str = 'dem'


global_data = GeostationaryFactory.create_scene("meteosat", "10", "seviri", time_slot)
#prop_str = ['h03']
prop_str = ['h03']
# load data
global_data.load(prop_str)
#plot.show_quicklook(global_data[prop_str].area_def, global_data[prop_str].data )

## mask array if necessary
#prop = np.ma.asarray(global_data[prop_str].data)
#prop.mask = (prop == 9999.9) | (prop <= 0.0001) 

yearS = str(year)
#yearS = yearS[2:]
monthS = "%02d" % month
dayS   = "%02d" % day
hourS  = "%02d" % hour
minS   = "%02d" % minute
dateS=yearS+'-'+monthS+'-'+dayS
timeS=hourS+':'+minS+'UTC' 

#outputDir='./'+yearS+'-'+monthS+'-'+dayS+'/'+yearS+'-'+monthS+'-'+dayS+'_'+prop_str+'-'+area+'/'
outputDir='./pics/'
#outputDir='/data/cinesat/out/'

# parallax correction
parallax_str=''
if parallax_correction:
    if estimate_cth:
        print("*** estimate cth")
        print("... read IR_108")
        IR_data = GeostationaryFactory.create_scene("Meteosat-9", "", "seviri", time_slot)
        IR_data.load(['IR_108'], reader_level="seviri-level2")
        print("    reproject IR_108 to projection of hsaf")  
        IR_data = IR_data.project('hsaf', precompute=True)  # return statement is necessary
        global_data.parallax_corr(fill="nearest", estimate_cth=True, IR_108=IR_data['IR_108'], cth_atm="best", time_slot=time_slot, replace=True)
        parallax_str='-PC-ECTH'
        #plot.show_quicklook(global_data['CTH'].area_def, global_data['CTH'].data)
    else:
        print("... take cth from NWC-SAF")
        print("*** read CTH")
        global_data.load(['CTTH'], reader_level="seviri-level3")
        from my_msg_module import convert_NWCSAF_to_radiance_format
        convert_NWCSAF_to_radiance_format(global_data, global_data['CTTH'].area, 'CTH', True, True)
        global_data.channels.remove('CTTH')
        print("reproject CTH to projection of hsaf")  
        global_data = global_data.project('hsaf', precompute=True)  # return statement is necessary
        global_data.parallax_corr(fill="nearest", estimate_cth=False, replace=True)  # fill="False", "nearest" or "bilinear"
        parallax_str='-PC-CTH'

if not exists(outputDir):
    print('... create output directory: ' + outputDir)
    makedirs(outputDir)

for area in areas:

    # PROJECT data to new area 
    if area.find("EuropeCanary") != -1:
        resolution='l'
    if area.find("ccs4") != -1:
        resolution='i' 
    if area.find("ticino") != -1:
        resolution='h'
    if area.find('hsaf_merc') != -1:
        resolution='c'

    data = global_data.project(area, precompute=True)
    #data[prop_str].product_name = global_data[prop_str].product_name
    #data[prop_str].units = global_data[prop_str].units

    obj_area = get_area_def(area)
    
    # calculate statistics (area with precipitation, mean precipitation, total precipitation)
    if save_statistics:
        statisticFile = outputDir + 'RAD_'+data[prop_str].product_name+'-'+area+'_'+yearS[2:]+monthS+dayS+'.txt'
        f1 = open(statisticFile,'a')   # mode append 
        ind = (prop > 0.0001) &  (prop < 500.0)
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
        print("date       HH : MM UTC    mean      p50     p75     p90   max      area")
        #      "2014-07-23 18 : 00 UTC    2.1661    1.00    2.00    5.05  118.05  54868"
        print(str2write)
        f1.write(str2write) 
        f1.close()
        print("wrote statistics file: emacs "+ statisticFile +" &")


    #outputFile = "./pics/radar.png"
    #outputFile = outputDir+'MSG_'+data[prop_str].product_name+'-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS +'.png'
    outputFile = outputDir+'/MSG_'+'h03'+parallax_str+'-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS +'.png'

    prop=data[prop_str].data
    
    #min_data=prop.min()
    min_data =  0.
    if color_mode=='hsaf':
        max_data = 30.
        colormap   = hsaf
        colormap_r = hsaf.reverse()
        data[prop_str].units = 'mm/h'
    else:
        colormap   = rainbow
        colormap_r = rainbow.reverse()
        max_data = prop.max()
        print('max_data: ', max_data)
        if prop.max() < 10:
            max_data = max_data-(max_data%1)
            print('round(max_data): ', max_data)
        else:
            max_data=max_data-(max_data%10)
            print('round(max_data): ', max_data)

    colormap.set_range(min_data, max_data)

    if max_data >= 20:
        tick_marks=10        # default
        minor_tick_marks=5  # default
    else:
        tick_marks=2        # default
        minor_tick_marks=1  # default    

    print("*** min(set) / min(data) / max: ", min_data, prop.min(), max_data)

    method='linear'
    #method='logarithmic'
    units = '['+data[prop_str].units+']'

    if method == 'logarithmic':
        prop=np.log10(prop)
        min_data=prop.min()
        #max_data=prop.max()
        min_data = -0.25
        max_data=2.0
        units='log(RR)'
        tick_marks=1        # default
        minor_tick_marks=0.1   # default

    print('... use trollimage to ', method,' plot data (min,max)=',min_data, max_data)
    if 'fill_value' in locals():
        img = trollimage(prop, mode="L", fill_value=fill_value) 
    else:
        img = trollimage(prop, mode="L")

    img.colorize(colormap)

    PIL_image=img.pil_image()
    dc = DecoratorAGG(PIL_image)

    # define contour write for coasts, borders, rivers
    #cw = ContourWriterAGG('/data/OWARNA/hau/maps_pytroll/')
    cw = ContourWriterAGG('/opt/users/common/shapes/')


    resolution='l'
    if area.find("EuropeCanary") != -1:
        resolution='l'
    if area.find("ccs4") != -1:
        resolution='i' 
    if area.find("ticino") != -1:
        resolution='h'

    # define area
    proj4_string = obj_area.proj4_string     
    # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
    area_extent = obj_area.area_extent              
    # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
    area_def = (proj4_string, area_extent)

    if add_rivers:
       if verbose:
          print("    add rivers to image (resolution="+resolution+")")
       cw.add_rivers(PIL_image, area_def, outline='blue', resolution=resolution, outline_opacity=127, width=1, level=5) # 
       if verbose:
          print("    add lakes to image (resolution="+resolution+")")
       cw.add_coastlines(PIL_image, area_def, outline='blue', resolution=resolution, outline_opacity=127, width=1, level=2)  #, outline_opacity=0
    if add_borders:
       outline = (255, 0, 0)
       outline = 'black'
       if verbose:
          print("    add coastlines to image (resolution="+resolution+")")
       cw.add_coastlines(PIL_image, area_def, outline=outline, resolution=resolution, width=2)  #, outline_opacity=0
       if verbose:
          print("    add borders to image (resolution="+resolution+")")
       cw.add_borders(PIL_image, area_def, outline=outline, resolution=resolution, width=2)       #, outline_opacity=0 

    # add MeteoSwiss and Pytroll logo
    if add_logos:
        if verbose:
            print('... add logos')
        dc.align_right()
        if add_colorscale:
            dc.write_vertically()
        dc.add_logo("/opt/users/common/logos/meteoSwiss3.jpg",height=60.0)
        dc.add_logo("/opt/users/common/logos/pytroll3.jpg",height=60.0)
        #dc.add_logo("/opt/users/common/logos/EUMETSAT_logo2_tiny_white.png",height=60.0)

    if add_colorscale:
        print('... add colorscale ranging from min_data (',min_data,') to max_data (',max_data,')')
        dc.align_right()
        dc.write_vertically()
        font_scale = aggdraw.Font("black","/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif-Bold.ttf",size=16)

        colormap_r.set_range(min_data, max_data)
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

        title = layer+' HSAF, '+'h03'+' ['+data['h03'].units+']'
        draw.text((0, y_pos_title),title, title_color, font=font)

    print('... save image as ', outputFile)
    PIL_image.save(outputFile)
