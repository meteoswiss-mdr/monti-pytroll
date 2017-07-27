from datetime import datetime
import sys, string, os
import logging
sys.path.insert(0, "/home/lom/users/cll/pytroll/install/lib/python2.6/site-packages")
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from mpop.utils import debug_on
from pyresample import plot
from trollimage.colormap import TRT, black # rainbow
#from TRTimage import TRTimage
from mpop.imageo.TRTimage import TRTimage
from trollimage.image import Image as trollimage
import numpy as np
from pydecorate import DecoratorAGG
import aggdraw
from PIL import ImageFont, ImageDraw
from os.path import exists
from os import makedirs

import scp_settings
scpOutputDir = scp_settings.scpOutputDir
scpID = scp_settings.scpID 

debug_on()

save_statistics=True

title_color=(255,255,255)
#layer=''
#layer=' 2nd layer'
layer=' 3rd layer'
add_rivers=False
add_borders=False

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
        if len(sys.argv) >6:
            cell = int(sys.argv[6])
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
        minute=00

time_slot = datetime(year, month, day, hour, minute)
global_data = GeostationaryFactory.create_scene("swisstrt", "04", "radar", time_slot)

#cell='2014072316550030'
#cell='2014072313000006' # max_rank
if 'cell' in locals():
    cell_ID='_'+cell[8:]
    cell_dir='/ID'+cell[8:]+'/'
    print "search cell id", cell_ID
    global_data.load(['TRTcells'], cell=cell)
else:
    cell_ID=''
    cell_dir=''
    global_data.load(['TRTcells']) # ,min_rank=8

#if hasattr(global_data, 'traj_IDs'):
#    print ""
#    print "Trajectory IDs: ", global_data.traj_IDs
#    print ""
#    if len(global_data.traj_IDs) > 0:
#           traj = global_data.traj_IDs[0]
#           print traj, global_data.TRTcells[traj].date, global_data.TRTcells[traj].lon, global_data.TRTcells[traj].lat

#print "global_data ", global_data
area="ccs4"
#area="EuropeCanaryS95"
#area="EuropeCanary95"
#area="ticino"
obj_area = get_area_def(area)

#print "area_def.pixel_size_x", obj_area.pixel_size_x
#print "area_def.pixel_size_y", obj_area.pixel_size_y

#plot.show_quicklook(obj_area, global_data['precip'].data )
#print "global_data['precip'].data", global_data['precip'].data
#print "global_data['precip'].data", global_data['precip'].data[355,:]
#print "shape: ", global_data['TRTcells'].data.shape

prop = np.ma.asarray(global_data['TRTcells'].data)
prop.mask = (prop == 9999.9) | (prop <= 0.0001) 

#print "prop.shape ", prop.shape

yearS = str(year)
#yearS = yearS[2:]
monthS = "%02d" % month
dayS   = "%02d" % day
hourS  = "%02d" % hour
minS   = "%02d" % minute
dateS = yearS+'-'+monthS+'-'+dayS
timeS = hourS+':'+minS+" UTC"

#output_dir='./pics/'+yearS+'-'+monthS+'-'+dayS+'/'+yearS+'-'+monthS+'-'+dayS+'_TRT/'
#output_dir='./pics/TRT/'
#output_dir='./pics/'
output_dir='/data/COALITION2/PicturesSatellite/'+yearS+'-'+monthS+'-'+dayS+'/'+yearS+'-'+monthS+'-'+dayS+'_TRT_'+area+'/'
#output_dir='/data/cinesat/out/'

if not exists(output_dir+cell_dir):
    print '... create output directory: ' + output_dir+cell_dir
    makedirs(output_dir+cell_dir)

# calculate statistics (number of cells, area with precipitation)
save_statistics = False
if save_statistics:
    statisticFile = output_dir + 'TRT_'+'cells'+'-'+area+'_'+yearS[2:]+monthS+dayS+cell_ID+'.txt'
    f1 = open(statisticFile,'a')   # mode append 
    ind = (prop > 0.0001) &  (prop < 500.0)
    print "prop.data[ind]"
    #for pp in prop.data[ind]:
    #    print pp
    n_cells = len(global_data.traj_IDs)
    area_km2 = prop.data[ind].size

    str2write = yearS+' '+monthS+' '+dayS+' '+hourS+' '+minS+'      '
    str2write = str2write+' '+ "%7.4f" % n_cells
    str2write = str2write+' '+ "%8.0f" % area_km2
    str2write = str2write+"\n"
    print  "date       HH : MM UTC    n_cells   area"
    #      "2014-07-23 18 : 00 UTC    2.1661    54868"
    print str2write
    f1.write(str2write) 
    f1.close()
    print "wrote statistics file: emacs "+ statisticFile +" &"


#outputFile = "./pics/radar.png"
outputFile = output_dir+cell_dir+'RAD_TRT-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS + cell_ID
image_type ='.png'

#min_data=prop.min()
#max_data=prop.max()
min_data=0
max_data=3

method='linear'
units='cells'
tick_marks=1        # default
minor_tick_marks=1   # default

old_style=False

if old_style: 
    print '... use trollimage to ', method,' plot data (min,max)=',min_data, max_data
    img = trollimage(prop, mode="L") # , fill_value=(0,0,0)  add black background color 
    #colormap   = rainbow
    #colormap_r = rainbow.reverse()
    if True:
        colormap   = TRT
        colormap_r = TRT.reverse()
        colorscale=True
        black_vel=False
    else:
        colormap   = black
        colormap_r = black
        colorscale=False
        black_vel=True
    colormap.set_range(min_data, max_data)
    img.colorize(colormap)
        
    PIL_image=img.pil_image()

else:

    colorscale=False
    black_vel=True

    PIL_image = TRTimage( global_data.traj_IDs, global_data.TRTcells, obj_area) # minRank=8, alpha_max=1.0, plot_vel=True

# create decorator 
dc = DecoratorAGG(PIL_image)
draw = ImageDraw.Draw(PIL_image)


if colorscale:
    print '... add colorscale ranging from min_data (',min_data,') to max_data (',max_data,')'
    dc.align_right()
    dc.write_vertically()
    font_scale = aggdraw.Font("black","/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif-Bold.ttf",size=16)
    colormap_r.set_range(min_data, max_data)
    dc.add_scale(colormap_r, extend=True, tick_marks=tick_marks, minor_tick_marks=minor_tick_marks, font=font_scale, line_opacity=100, unit=units) #

if add_borders:
    from pycoast import ContourWriterAGG
    # define contour write for coasts, borders, rivers
    cw = ContourWriterAGG('/data/OWARNA/hau/maps_pytroll/')
    # define area
    from mpop.projector import get_area_def
    # obj_area = get_area_def('ccs4')
    proj4_string = obj_area.proj4_string            
    # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
    area_extent = obj_area.area_extent              
    # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
    area_def = (proj4_string, area_extent)
    resolution='h'
    cw.add_borders(PIL_image, area_def, outline=(255, 0, 0), resolution=resolution, width=1)       #, outline_opacity=0
    
if False:
    print '... add cell velocities'
    from math import isnan

    print "traj_ID             Rank    x0     y0     vx      vy"

    for traj in global_data.traj_IDs:
        
        if global_data.TRTcells[traj].RANKr > min_rank:

            x0=global_data.TRTcells[traj].jCH
            y0=global_data.TRTcells[traj].iCH
            vx=global_data.TRTcells[traj].vel_x
            vy=global_data.TRTcells[traj].vel_y
            RANKr=global_data.TRTcells[traj].RANKr
            print traj, ("%6.0f,%6.0f,%6.0f,%6.0f,%6.0f  " % (RANKr, x0, y0, vx, vy))

            if isnan(x0) or isnan(y0) or isnan(vx) or isnan(vy) or isnan(RANKr):
                pass
            else:
                if RANKr < 5:
                    acolor='green'
                elif RANKr < 15:
                    acolor='orange'
                elif RANKr < 25:
                    acolor='red'
                else:
                    acolor='purple'
                if black_vel:
                    acolor='black'
                draw.line((x0, y0, x0+vx,y0+vy), width=2, fill=acolor) ## 

    # try later http://svn.effbot.org/public/stuff/sandbox/agglib/aggarrow.py

add_title=True
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

    title = layer+' TRT cells ' # [white v. weak, green weak, yellow med., red strong]
    draw.text((0, y_pos_title),title, title_color, font=font)


#if add_title:
#    title_color=(255,255,255)
#    title = ' TRT cell mask, '+dateS+" "+timeS
#    fontsize=18
#    font = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", fontsize)
#    #draw.text((0, 20), title, title_color, font=font)
#    draw.text((0, 40), title, title_color, font=font)

print '... save image as ', outputFile+image_type
PIL_image.save(outputFile+image_type)

# copy to another place
if False:
    import subprocess
#    if in_msg.verbose:
#        print "... secure copy "+outputFile+ " to "+in_msg.scpOutputDir
    print "scp "+scpID+" "+outputFile+image_type +" "+" "+scpOutputDir+" 2>&1 &"
    subprocess.call("scp "+scpID+" "+outputFile+image_type +" "+" "+scpOutputDir+" 2>&1 &", shell=True)
#    if in_msg.compress_to_8bit:
#        if in_msg.verbose:
#            print "... secure copy "+outputFile.replace(".png","-fs8.png")+ " to "+in_msg.scpOutputDir
#        subprocess.call("scp "+in_msg.scpID+" "+outputFile.replace(".png","-fs8.png")+" "+in_msg.scpOutputDir+" 2>&1 &", shell=True)
