from datetime import datetime
import sys, string, os
import logging
#sys.path.insert(0, "/home/lom/users/cll/pytroll/install/lib/python2.6/site-packages")
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from mpop.utils import debug_on
from pyresample import plot
#from trollimage.colormap import rainbow, purples, prgn, pubugn, brbg, piyg, spectral, greens, greens2
from trollimage.colormap import greens2
from trollimage.image import Image as trollimage
import numpy as np
from pydecorate import DecoratorAGG
import aggdraw
from PIL import ImageFont, ImageDraw 
from os.path import exists
from os import makedirs
from pycoast import ContourWriterAGG
import subprocess

import scp_settings
scpOutputDir = scp_settings.scpOutputDir
scpID = scp_settings.scpID 

#debug_on()

prop_str = 'dens'
#prop_str = 'densIC'
#prop_str = 'densCG'
#prop_str = 'curr_abs'
#prop_str = 'curr_neg'
#prop_str = 'curr_per_lightning'

save_statistics=False
plot_diagram=True
verbose=True

add_colorscale=False
add_title=True
#fill_value=(0,0,0) # black background  # usually not used   
title_color=(255,255,255) # white       # for multi layer overlay 
#fill_value=(1,1,1) # white background  # for single layer 
#title_color=(0,0,0) # black            # for single layer 
#layer=''
#layer=' 2nd layer'
layer=' 3rd layer'
add_rivers=True
add_borders=True
if len(layer) > 0:
    print "*** No borders and rivers for an overlay"
    add_rivers  = False # no rivers if an overlay is needed
    add_borders = False # no map    if an overlay is needed
scpOutput = False


if len(sys.argv) > 1:
    if len(sys.argv) < 6:
        print "***           "
        print "*** Warning, please specify date and time completely, e.g."
        print "***          python plot_lightning.py 2014 07 23 16 10 "
        print "***          arguments given by you:"
        for i in range(len(sys.argv)):
            print sys.argv[i]
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

print "... read lightning data"
global_data = GeostationaryFactory.create_scene("lightning", "", "thx", time_slot)
global_data.load([prop_str])
print "... global_data "
print global_data
area='ccs4'
obj_area = get_area_def(area)
#plot.show_quicklook(ccs4, global_data['precip'].data )
#print "global_data[prop_str].data", global_data[prop_str].data
print "... shape: ", global_data[prop_str].data.shape
print "... min/max: ", global_data[prop_str].data.min(), global_data[prop_str].data.max()
print "... dt: ", global_data.dt, " min"
print "... dx: ", global_data.dx, " km"
print "... form: ", global_data.form

dt_str = ("%04d" % global_data.dt) + "min"
dx_str = ("%03d" % global_data.dx) + "km"

prop = np.ma.asarray(global_data[prop_str].data)
prop.mask = (prop == 0) 

yearS = str(year)
#yearS = yearS[2:]
monthS = "%02d" % month
dayS   = "%02d" % day
hourS  = "%02d" % hour
minS   = "%02d" % minute

dateS=yearS+'-'+monthS+'-'+dayS
timeS = hourS+':'+minS+' UTC'

#outputDir='./pics/'+yearS+'-'+monthS+'-'+dayS+'_lightnings/'
#outputDir='/data/cinesat/out/'
#outputDir='./'+yearS+'-'+monthS+'-'+dayS+'/THX/'
outputDir='./pics/'
#outputDir='./'+yearS+'-'+monthS+'-'+dayS+'/'+yearS+'-'+monthS+'-'+dayS+'_'+prop_str+'-'+area+'/'
#outputDir='/data/COALITION2/PicturesSatellite/'+yearS+'-'+monthS+'-'+dayS+'/'+yearS+'-'+monthS+'-'+dayS+'_THX-'+area+'/'

if not exists(outputDir):
    print '... create output directory: ' + outputDir
    makedirs(outputDir)

file_basename = 'THX_'+prop_str+'-'+'ccs4'+'_'+yearS[2:]+monthS+dayS+hourS+minS+'_'+dt_str+'_'+dx_str
file_basename2 = 'THX_'+prop_str+'-'+'ccs4'+'_'+yearS[2:]+monthS+dayS+'_'+dt_str+'_'+dx_str


# calculate statistics (area with precipitation, mean precipitation, total precipitation)
if save_statistics:
    statisticFile = outputDir + file_basename2 + '.txt'
    f1 = open(statisticFile,'a')   # mode append 

    ind = (prop != 0.0) 
    prop_sum = np.sum(prop.data[ind])
    if prop_sum==0:
        prop_mean= 0.
        prop_p50 = 0.
        prop_p75 = 0.
        prop_p90 = 0.
        prop_max = 0.
        prop_sum = 0.
        prop_km2 = 0.
    else:
        #for pp in prop.data[ind]:
        #    print pp
        prop_mean= prop.data[ind].mean()
        prop_p50 = np.percentile(prop.data[ind],50)
        prop_p75 = np.percentile(prop.data[ind],75)
        prop_p90 = np.percentile(prop.data[ind],90)
        prop_max = prop.data[ind].max()
        prop_sum = np.sum(prop.data[ind])
        prop_km2 = prop.data[ind].size

    str2write = yearS+' '+monthS+' '+dayS+' '+hourS+' '+minS+'      '
    str2write = str2write+' '+ "%7.4f" % prop_mean
    str2write = str2write+' '+ "%7.3f" % prop_p50
    str2write = str2write+' '+ "%7.3f" % prop_p75
    str2write = str2write+' '+ "%7.3f" % prop_p90
    str2write = str2write+' '+ "%7.3f" % prop_max
    str2write = str2write+' '+ "%8.0f" % prop_sum
    str2write = str2write+' '+ "%8.0f" % prop_km2
    str2write = str2write+"\n"
    print  "date       HH : MM UTC    mean     p50     p75     p90    max       sum     area"
    #      "2014 07 23 18 35        1.6162   1.000   2.000   3.000    5.00      160       99"
    print str2write
    f1.write(str2write)
    f1.close()
    print "wrote statistics file: emacs "+ statisticFile +" &"

if plot_diagram:
    #outputFile = "./pics/radar.png"
    outputFile = outputDir + file_basename + '.png'

    min_data=prop.min()
    max_data=prop.max()
    #ind = (prop != 0.0) 
    #max_data = np.percentile(prop.data[ind],99.5)
    min_data=0
    #max_data=35
    max_data=80
    
    method='linear'

    fontsize=18
    font = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", fontsize)

    units='flashs / (' +("%d" % global_data.dA)+'km^2 '+ ("%d" % global_data.dt) +'min)'
    if len(layer) > 0:
        layer=layer+':'
    tick_marks=5        # default
    minor_tick_marks=1   # default

    if prop_str == 'dens':
        prop_str2 = 'lightning density'
        title = layer+' lightning density ['+units+']'
    elif prop_str == 'densIC':
        prop_str2 = 'intra-cloud lightning density'
    elif prop_str == 'densCG':
        prop_str2 = 'cloud-groud lightning density'
    elif prop_str == 'curr_abs':
        units='I/kA'
        prop_str2 = 'lightning abs(current)'
        tick_marks=100        
        minor_tick_marks=50  
        max_data=500
    elif prop_str == 'curr_neg':
        units='I/kA'
        prop_str2 = 'lightning current<0'
        tick_marks=100        
        minor_tick_marks=50  
    elif prop_str == 'curr_per_lightning':
        units='I/kA'
        prop_str2 = 'current per lightning'
        tick_marks=5
        minor_tick_marks=1  
    else:
        print "*** Error, unknown property", prop_str

    log_str=''
    if True:
        prop=np.log10(prop)
        min_data=prop.min()
        #max_data=prop.max()
        if prop_str=='dens' or prop_str=='densIC' or prop_str=='densCG':
            max_data=2.0
        else:
            max_data=3.0
        method='logarithmic'
        #units='log(RR)'
        log_str='log_10 '
        # units='log(I)'
        tick_marks=1        # default
        minor_tick_marks=0.1   # default

    print '... use trollimage to ', method,' plot data (min,max)=',min_data, max_data
    if 'fill_value' in locals():
        img = trollimage(prop, mode="L", fill_value=fill_value)  # fillvalue    -> opaque background 
    else:
        img = trollimage(prop, mode="L")                         # no fillvalue -> transparent backgroud

    #colorbar=prgn        # colorbars in trollimage-v0.3.0-py2.7.egg/trollimage/colormap.py
    #colorbar=rainbow
    #colorbar=pubugn
    #colorbar=brbg
    #colorbar=piyg   # too purple at the beginning
    #colorbar=spectral
    colorbar=greens2.reverse()
    colorbar.set_range(min_data, max_data)
    img.colorize(colorbar)

    PIL_image=img.pil_image()
    dc = DecoratorAGG(PIL_image)

    draw = ImageDraw.Draw(PIL_image)

    if add_colorscale:
        print '... add colorscale ranging from min_data (',min_data,') to max_data (',max_data,')'
        dc.align_right()
        dc.write_vertically()
        font_scale = aggdraw.Font("black","/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif-Bold.ttf",size=16)
        greens2.set_range(min_data, max_data)
        dc.add_scale(greens2, extend=True, tick_marks=tick_marks, minor_tick_marks=minor_tick_marks, font=font_scale, line_opacity=100, unit=units) #
    
    # define contour write for coasts, borders, rivers
    cw = ContourWriterAGG('/data/OWARNA/hau/maps_pytroll/')

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

    if add_title:
        title = layer+' '+log_str+prop_str2 +' ['+units+']'
        if layer.find('2nd') != -1:
            y_pos_title=20
        elif layer.find('3rd') != -1:
            y_pos_title=40
        else:
            y_pos_title=5
        draw.text((0, y_pos_title), title, title_color, font=font)
        if len(layer)==0:
            draw.text((0, 30), ' '+dateS+' '+timeS, title_color, font=font)

    print '... save image as ', outputFile
    PIL_image.save(outputFile)

    if scpOutput:
        print "... secure copy "+outputFile+ " to "+scpOutputDir
        subprocess.call("scp "+scpID+" "+outputFile+" "+scpOutputDir+" 2>&1 &", shell=True)
