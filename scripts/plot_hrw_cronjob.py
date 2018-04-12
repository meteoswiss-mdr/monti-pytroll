from datetime import datetime
import sys, string, os
import logging
sys.path.insert(0, "/home/lom/users/cll/pytroll/install/lib/python2.6/site-packages")
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from mpop.utils import debug_on
from pyresample import plot
import numpy as np
from pydecorate import DecoratorAGG
import aggdraw
from PIL import ImageFont, ImageDraw
from os.path import exists
from os import makedirs
from mpop.imageo.HRWimage import HRWimage, HRW_2dfield, HRWstreamplot
from datetime import timedelta

import scp_settings
scpOutputDir = scp_settings.scpOutputDir
scpID = scp_settings.scpID 

# debug_on()

#plot_modes = ['channel','pressure','correlation','conf_nwp','conf_no_nwp', 'stream']
#plot_modes = ['pressure']
#plot_modes = ['channel']
#plot_modes = ['stream']
plot_modes = ['channel', 'pressure'] # , 'stream'
detailed = True 

delay=5

add_title=True
title_color=(255,255,255)
#layer=''
layer=' 2nd layer'
#layer='3rd layer'
add_rivers=False
add_borders=False
legend=True

timesteps=1
min_correlation = 85
min_conf_nwp    = 80
min_conf_no_nwp = 80

HRWimages = ['channel','pressure','correlation','conf_nwp','conf_no_nwp']

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
        minute=00

# read data for the current time
time_slot = datetime(year, month, day, hour, minute)
#print time_slot
global_data = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot)
global_data.load(['HRW'], reader_level="seviri-level5", read_basic_or_detailed='detailed', \
                     min_correlation=min_correlation, min_conf_nwp=min_conf_nwp, min_conf_no_nwp=min_conf_no_nwp )

# read data for previous time steps if needed
for it in range(1,timesteps):
    time_slot_i = time_slot - timedelta(minutes=it*5)
    global_data_i = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot_i)
    global_data_i.load(['HRW'], reader_level="seviri-level5", read_basic_or_detailed='detailed', \
                     min_correlation=min_correlation, min_conf_nwp=min_conf_nwp, min_conf_no_nwp=min_conf_no_nwp )
    global_data['HRW'].HRW_detailed = global_data['HRW'].HRW_detailed + global_data_i['HRW'].HRW_detailed

    #print "global_data ", global_data

#m_per_s_to_knots = 1.944
#for wid in range(len(global_data['HRW'].HRW_detailed.wind_id)):
#    print '%6s %3d %10.7f %10.7f %7.2f %7.1f %8.1f' % (global_data['HRW'].HRW_detailed.channel[wid], global_data['HRW'].HRW_detailed.wind_id[wid], \
#                                                       global_data['HRW'].HRW_detailed.lon[wid], global_data['HRW'].HRW_detailed.lat[wid], \
#                                                       global_data['HRW'].HRW_detailed.wind_speed[wid]*m_per_s_to_knots, \
#                                                       global_data['HRW'].HRW_detailed.wind_direction[wid], global_data['HRW'].HRW_detailed.pressure[wid])

area="ccs4"
#area="alps95"
#area="EuropeCanaryS95"
#area="EuropeCanary95"
#area="ticino"
obj_area = get_area_def(area)

yearS = str(year)
#yearS = yearS[2:]
monthS = "%02d" % month
dayS   = "%02d" % day
hourS  = "%02d" % hour
minS   = "%02d" % minute
dateS = yearS+'-'+monthS+'-'+dayS
timeS = hourS+':'+minS+" UTC"

#output_dir='/data/COALITION2/PicturesSatellite/'+yearS+'-'+monthS+'-'+dayS+'/'+yearS+'-'+monthS+'-'+dayS+'_HRW_'+area+'/'
output_dir='/data/cinesat/out/'
#output_dir='./pics/'

if not exists(output_dir):
    print '... create output directory: ' + output_dir
    makedirs(output_dir)

image_type ='.png'

# global_data['HRW'].HRW_detailed = HRW_all

if add_title:
    # get font for title 
    fontsize=18
    font = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", fontsize)

    # get y position and layer string for the title 
    if layer.find('2nd') != -1:
        y_pos_title=20
    elif layer.find('3rd') != -1:
        y_pos_title=40
    else:
        y_pos_title=5
        layer = dateS+' '+timeS
    if len(layer) > 0:
        layer=layer+':'

    if detailed:
        print "*** plot detailed winds"
        detailed_str = 'detailed'      # hrw_channels=None, min_correlation=None, cloud_type=None, style='barbs'
        detailed_char = 'd'                    
    else:
        print "*** plot basic winds"
        detailed_str = 'basic'
        detailed_char = 'b'


for plot_mode in plot_modes:

    print "    create HRW plot, plot mode = ", plot_mode

    if plot_mode in HRWimages:
        if detailed:
            PIL_image = HRWimage( global_data['HRW'].HRW_detailed, obj_area, color_mode=plot_mode, legend=legend)  
            # possible options: color_mode='pressure', legend=False, hrw_channels=None, min_correlation=None, cloud_type=None, style='barbs'                   
        else:
            PIL_image = HRWimage( global_data['HRW'].HRW_basic,    obj_area, color_mode=plot_mode, legend=legend) 

        if plot_mode=='pressure':
            color_char='p'
        elif plot_mode=='channel':
            color_char='c'
        elif plot_mode=='correlation':
            color_char='r'
        elif plot_mode=='conf_nwp':
            color_char='cnwp'
        elif plot_mode=='conf_no_nwp':
            color_char='cnnwp'

        outputFile = output_dir+'/MSG_hrw'+detailed_char+color_char+'-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS 
        title = layer+' '+detailed_str+' High Resolution Winds' # [white v. weak, green weak, yellow med., red strong]

    elif plot_mode == 'stream':
        # get gridded wind field 
        u2d, v2d = HRW_2dfield( global_data['HRW'].HRW_detailed, obj_area )

        # create PIL image
        PIL_image = HRWstreamplot( u2d, v2d, obj_area, HRW_data.interpol_method, color_mode='speed') # , legend=True, legend_loc=3

        outputFile = output_dir+'/MSG_stream'+detailed_char+'-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS 
        title = layer+' '+detailed_str+' High Resolution Winds streamplot' # [white v. weak, green weak, yellow med., red strong]


    else:
        print "*** Error in plot_hrw.py"
        print "    unknown plot_mode"
        quit()


    # create decorator 
    dc = DecoratorAGG(PIL_image)
    draw = ImageDraw.Draw(PIL_image)

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

    if add_title:
        draw = ImageDraw.Draw(PIL_image)
        draw.text((0, y_pos_title),title, title_color, font=font)

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

    # make composite and scp composite
    if True:
        import subprocess
        if plot_mode in ['channel','pressure']:
            product = 'hrw'+detailed_char+color_char
        elif plot_mode == 'stream':
            product = 'stream'+detailed_char

        ir_file    = output_dir+'/MSG_ir108-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS+".png"
        hrv_file   = output_dir+'/MSG_HRV-'  +area+'_'+yearS[2:]+monthS+dayS+hourS+minS+".png"
        ir_outfile  = output_dir+'/MSG_'+product+'-ir108-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS+".png"
        hrv_outfile = output_dir+'/MSG_'+product+'-HRV-'  +area+'_'+yearS[2:]+monthS+dayS+hourS+minS+".png"
        print "/usr/bin/composite "+outputFile+image_type+" "+ir_file+" "+" "+ir_outfile+" && sleep 1"
        subprocess.call("/usr/bin/composite "+outputFile+image_type+" "+ir_file +" "+" "+ir_outfile +" 2>&1 && sleep 1 ", shell=True)
        print "/usr/bin/composite "+outputFile+image_type+" "+hrv_file+" "+" "+hrv_outfile+" && sleep 1"
        subprocess.call("/usr/bin/composite "+outputFile+image_type+" "+hrv_file+" "+" "+hrv_outfile+" 2>&1 && sleep 1 ", shell=True)

        if True:
            print "scp "+scpID+" "+ir_outfile  +" "+" "+scpOutputDir+" 2>&1 &"
            subprocess.call("scp "+scpID+" "+ir_outfile  +" "+" "+scpOutputDir+" 2>&1 && sleep 1", shell=True)
            print "scp "+scpID+" "+hrv_outfile +" "+" "+scpOutputDir+" 2>&1 &"
            subprocess.call("scp "+scpID+" "+hrv_outfile +" "+" "+scpOutputDir+" 2>&1 && sleep 1", shell=True)
