from __future__ import division
from __future__ import print_function




from datetime import datetime
import sys, string, os
import logging
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
from mpop.imageo.HRWimage import HRW_2dfield # , HRWstreamplot, HRWimage
from datetime import timedelta
from plot_msg import create_PIL_image, add_borders_and_rivers, add_title
from pycoast import ContourWriterAGG
from my_msg_module import format_name, fill_with_closest_pixel
from copy import deepcopy 
from my_msg_module import convert_NWCSAF_to_radiance_format, get_NWC_pge_name
from mpop.imageo.palettes import convert_palette2colormap
from plot_msg import load_products

import scp_settings
scpOutputDir = scp_settings.scpOutputDir
scpID = scp_settings.scpID 

# debug_on()


def read_HRW(sat, sat_nr, instrument, time_slot, ntimes, dt=5, read_basic_or_detailed='detailed', 
             min_correlation=85, min_conf_nwp=80, min_conf_no_nwp=80, cloud_type=None, level=None):

    #print time_slot
    data = GeostationaryFactory.create_scene(sat, sat_nr, instrument, time_slot)
    data.load(['HRW'], reader_level="seviri-level5", read_basic_or_detailed=read_basic_or_detailed)

    # read data for previous time steps if needed
    for it in range(1,ntimes):
        time_slot_i = time_slot - timedelta( minutes = it*5 )
        data_i = GeostationaryFactory.create_scene(sat, sat_nr, instrument, time_slot_i)
        data_i.load(['HRW'], reader_level="seviri-level5", read_basic_or_detailed=read_basic_or_detailed)
        # merge all datasets
        data['HRW'].HRW_detailed = data['HRW'].HRW_detailed + data_i['HRW'].HRW_detailed
        data['HRW'].HRW_basic    = data['HRW'].HRW_basic    + data_i['HRW'].HRW_basic

    # apply quality filter
    data['HRW'].HRW_detailed = data['HRW'].HRW_detailed.filter(min_correlation=min_correlation, \
                    min_conf_nwp=min_conf_nwp, min_conf_no_nwp=min_conf_no_nwp, cloud_type=cloud_type, level=level)

    return data

# ------------------------------------------

def wind_shift(data, u, v, dt, area):

    print(type(u), u.shape)
    print(type(dt), dt)
    print(type(area.pixel_size_x), area.pixel_size_x)

    dx = (np.round ( u * (dt*60.) / area.pixel_size_x ) ) # u in m/s, t in min -> s, pixel_size in m
    dy = (np.round ( v * (dt*60.) / area.pixel_size_y ) )
    dx = dx.astype(int)
    dy = dy.astype(int)
    #dy = np.flipud(dy)

    print('dx.min() ', dx.min())
    print('dx.max() ', dx.max())

    (nx,ny) = data.shape

    # coordinates for verbose messages
    ii=100
    jj=600

    if 1==0:
        dd = dy
        #dd = data_s
        #dd = u
        vmin=-10
        vmax=10
        import matplotlib.pyplot as plt
        fig = plt.figure()
        plt.imshow(dd, vmin=vmin, vmax=vmax)
        plt.colorbar()
        fig.savefig("ws_dy.png")
        print("... display ws_dy.png &")
        print("dx[ii,jj]", dx[ii,jj])
        #plt.show()
        #quit()

    return dx, dy

def wind_nowcast (data, dx, dy):

    # create new 
    (nx,ny) = data.shape
    data_s = np.empty(data.shape)
    data_s[:,:] = np.nan
    print(data_s.shape)

    for i in range(0,nx):       # starting upper right going down
        for j in range(0,ny):   # starting lower right going right
            i2 = i-dy[i,j]   # moving north-south 
            j2 = j+dx[i,j]   # moving east-west
            if i2<nx-1 and j2<ny-1 and i2 >= 0 and j2 >=0:
                #if i==ii and j==jj: 
                #    print i,j, i2, j2, data[j2,i2], data[j,i]
                data_s[i2,j2] = data[i,j]

    data_s = fill_with_closest_pixel(data_s)

    if 1==0:
        #dd = dx
        dd = data_s
        #dd = u
        vmin=-10
        vmax=10
        import matplotlib.pyplot as plt
        fig = plt.figure()
        plt.imshow(dd)
        plt.colorbar()
        fig.savefig("ws_data_s.png")
        print("... display ws_data_s.png &")
        #plt.show()
        quit()

    if 1==0:
        #dd = dx
        dd = data
        #dd = u
        vmin=-10
        vmax=10
        import matplotlib.pyplot as plt
        fig = plt.figure()
        plt.imshow(dd)
        plt.colorbar()
        fig.savefig("ws_data.png")
        print("... display ws_data.png &")
        #plt.show()
        quit()

    import numpy.ma as ma
    data_s = ma.masked_invalid(data_s)

    return data_s

# ------------------------------------------

if __name__ == '__main__':

    # input 

    detailed = True 

    delay=5

    title_color=(255,255,255)
    #layer=''
    layer=' 2nd layer'
    #layer='3rd layer'
    add_rivers=False
    add_borders=False
    legend=True

    ntimes = 4
    print("... aggregate winddata for ", ntimes, " timesteps") 
    min_correlation = 85
    min_conf_nwp    = 80
    min_conf_no_nwp = 80
    cloud_type = [5,6,7,8,9,10,11,12,13,14]

    delta_t = 5

    # satellite for HRW winds
    sat_nr = "09"


    area="ccs4"
    #area="alps95"
    #area="EuropeCanaryS95"
    #area="EuropeCanary95"
    #area="ticino"

    #rgb='HRVc'
    #rgb='CT'
    rgb='CTT'
    channel = rgb.replace("c","")

    # load a few standard things 
    from get_input_msg import get_input_msg
    in_msg = get_input_msg('input_template')
    in_msg.resolution = 'i'
    in_msg.sat_nr = 9
    in_msg.add_title=False
    in_msg.outputDir='./pics/'
    in_msg.outputFile='WS_%(rgb)s-%(area)s_%y%m%d%H%M'
    in_msg.fill_value = [0,0,0] # black
    #in_msg.fill_value = None    # transparent
    #colormap='rainbow'
    colormap='greys'

    # ------------------------------------------

    # possible High Resolution wind images
    HRWimages = ['channel','pressure','correlation','conf_nwp','conf_no_nwp']
    # alternatively also possible is the plot of 'stream' lines 

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


    yearS = str(year)
    #yearS = yearS[2:]
    monthS = "%02d" % month
    dayS   = "%02d" % day
    hourS  = "%02d" % hour
    minS   = "%02d" % minute
    dateS = yearS+'-'+monthS+'-'+dayS
    timeS = hourS+':'+minS+" UTC"


    # read data for the current time
    time_slot = datetime(year, month, day, hour, minute)

    # define area object 
    obj_area = get_area_def(area)

    # define area
    proj4_string = obj_area.proj4_string            
    # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
    area_extent = obj_area.area_extent              
    # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
    area_tuple = (proj4_string, area_extent)

    # read HRW wind vectors 
    hrw_data = read_HRW("meteosat", sat_nr, "seviri", time_slot, ntimes, \
                               min_correlation=min_correlation, min_conf_nwp=min_conf_nwp, \
                               min_conf_no_nwp=min_conf_no_nwp, cloud_type=cloud_type)


    # now read the data we would like to forecast
    global_data = GeostationaryFactory.create_scene(in_msg.sat, str(in_msg.sat_nr).zfill(2), "seviri", time_slot)

    # area we would like to read
    area_loaded = get_area_def("EuropeCanary95")  

    # load product 
    area_loaded = load_products(global_data, [rgb], in_msg, area_loaded)

    #pge = get_NWC_pge_name(rgb)
    #print '...load satellite channel ', pge
    #global_data.load([pge], reader_level="seviri-level3")
    #if rgb=='CTT':
    #    nwcsaf_calibrate=False
    #else:
    #    nwcsaf_calibrate=False
    #convert_NWCSAF_to_radiance_format(global_data, area, rgb, nwcsaf_calibrate, True)

    #from trollimage.image import Image as trollimage

    #min_data = 0.
    #max_data = float(len(global_data[rgb].palette)-1)
    #if in_msg.verbose:
    #    print "    use GeoImage to plot ", rgb
    #from mpop.imageo.geo_image import GeoImage
    #prop = global_data[rgb].data
    #img = GeoImage( prop, global_data.area, global_data.time_slot, mode="P", palette = global_data[rgb].palette, fill_value=[0,0,0] )
    #if colorsize_image:
    #    if in_msg.verbose:
    #        print "    colorize image with a palette (min="+str(min_data)+", max="+str(max_data)+")"
    #    colormap = convert_palette2colormap(global_data[rgb].palette)
    #    colormap.set_range(min_data, max_data)  # no return value!

    #in_msg.colormap[rgb] = colormap
    #img = trollimage(global_data[channel].data, mode="L", fill_value=[0,0,0])
    #from trollimage.colormap import rainbow
    #colormap = rainbow
    #img.colorize(colormap)
    #img.show()
    #quit()

    #img = trollimage(prop, mode="L", fill_value=in_msg.fill_value)

    area='ccs4'

    print('... project data to desired area ', area)
    data = global_data.project(area, precompute=True)
    data2 = deepcopy(data)

    print('... calculate gridded 2d wind field') 
    u2d, v2d = HRW_2dfield( hrw_data['HRW'].HRW_detailed, obj_area )

    ##print "u2d.shape B", u2d.shape
    #vmin=-10
    #vmax=10
    #import matplotlib.pyplot as plt
    #fig = plt.figure()
    #plt.imshow(u2d, vmin=vmin, vmax=vmax)
    ##plt.imshow(data[channel].data)
    #plt.colorbar()
    #fig.savefig("ws_u2d_tmp.png")
    ##plt.show()
    #quit()

    # define contour write for coasts, borders, rivers
    cw = ContourWriterAGG(in_msg.mapDir)

    for it in range(12):

        print('... shift sat observation with wind field, it = ',it)
        data2[channel].data[:,:] = np.nan

        dx, dy = wind_shift(data[channel].data, u2d, v2d, it*delta_t, obj_area)

        data2[channel].data = wind_nowcast (data[channel].data, dx, dy)

        # print '... create PIL image'
        PIL_image = create_PIL_image(rgb, data2, in_msg, colormap=colormap) 
        #if in_msg.verbose:
        #    print "    use GeoImage to plot ", rgb
        #prop = data2[rgb].data
        #img = GeoImage( prop, global_data.area, global_data.time_slot, mode="P", palette = global_data[rgb].palette, fill_value=[0,0,0] )
        #if colorsize_image:
        #    if in_msg.verbose:
        #        print "    colorize image with a palette (min="+str(min_data)+", max="+str(max_data)+")"
        #    colormap = convert_palette2colormap(global_data[rgb].palette)
        #    colormap.set_range(min_data, max_data)  # no return value!
        #PIL_image=img.pil_image() 

        if add_borders:
            add_borders_and_rivers( PIL_image, cw, area_tuple,
                                    add_borders=in_msg.add_borders, border_color=in_msg.border_color,
                                    add_rivers=in_msg.add_rivers, river_color=in_msg.river_color, 
                                    resolution=in_msg.resolution, verbose=in_msg.verbose)

        #if area.find("EuropeCanary") != -1 or area.find("ccs4") != -1:
        dc = DecoratorAGG(PIL_image)

        # add title to image
        if in_msg.add_title:
            add_title(PIL_image, rgb, int(data.number), dateS, hourS, minS, area, dc, in_msg.font_file, in_msg.verbose )

        # create output filename
        outputDir =              format_name(in_msg.outputDir,  data.time_slot, area=area, rgb=rgb, sat_nr=data.number)
        outputFile = outputDir + format_name(in_msg.outputFile+'p'+str(it*delta_t).zfill(2)+'.png', data.time_slot, area=area, rgb=rgb, sat_nr=data.number)

        if not exists(outputDir):
            print('... create output directory: ' + outputDir)
            makedirs(outputDir)

        # save file
        if in_msg.verbose:
            print('... save final file :' + outputFile)
        PIL_image.save(outputFile, optimize=True)  # optimize -> minimize file size

    quit()

    PIL_image = create_PIL_image(rgb, data, in_msg) 

    # ------------------------------------------
    # output 


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
            print("*** plot detailed winds")
            detailed_str = 'detailed'      # hrw_channels=None, min_correlation=None, cloud_type=None, style='barbs'
            detailed_char = 'd'                    
        else:
            print("*** plot basic winds")
            detailed_str = 'basic'
            detailed_char = 'b'


    for plot_mode in plot_modes:

        print("    create HRW plot, plot mode = ", plot_mode)

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
            PIL_image = HRWstreamplot( u2d, v2d, obj_area, color_mode='speed') # , legend=True, legend_loc=3

            outputFile = output_dir+'/MSG_stream'+detailed_char+'-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS 
            title = layer+' '+detailed_str+' High Resolution Winds streamplot' # [white v. weak, green weak, yellow med., red strong]


        else:
            print("*** Error in plot_hrw.py")
            print("    unknown plot_mode")
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

        print('... save image as ', outputFile+image_type)
        PIL_image.save(outputFile+image_type)

        # copy to another place
        if False:
            import subprocess
        #    if in_msg.verbose:
        #        print "... secure copy "+outputFile+ " to "+in_msg.scpOutputDir
            print("scp "+scpID+" "+outputFile+image_type +" "+" "+scpOutputDir+" 2>&1 &")
            subprocess.call("scp "+scpID+" "+outputFile+image_type +" "+" "+scpOutputDir+" 2>&1 &", shell=True)
        #    if in_msg.compress_to_8bit:
        #        if in_msg.verbose:
        #            print "... secure copy "+outputFile.replace(".png","-fs8.png")+ " to "+in_msg.scpOutputDir
        #        subprocess.call("scp "+in_msg.scpID+" "+outputFile.replace(".png","-fs8.png")+" "+in_msg.scpOutputDir+" 2>&1 &", shell=True)

        # make composite and scp composite
        if False:
            import subprocess
            if plot_mode in ['channel','pressure']:
                product = 'hrw'+detailed_char+color_char
            elif plot_mode == 'stream':
                product = 'stream'+detailed_char

            ir_file    = output_dir+'/MSG_ir108-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS+".png"
            hrv_file   = output_dir+'/MSG_HRV-'  +area+'_'+yearS[2:]+monthS+dayS+hourS+minS+".png"
            ir_outfile  = output_dir+'/MSG_'+product+'-ir108-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS+".png"
            hrv_outfile = output_dir+'/MSG_'+product+'-HRV-'  +area+'_'+yearS[2:]+monthS+dayS+hourS+minS+".png"
            print("/usr/bin/composite "+outputFile+image_type+" "+ir_file+" "+" "+ir_outfile+" && sleep 1")
            subprocess.call("/usr/bin/composite "+outputFile+image_type+" "+ir_file +" "+" "+ir_outfile +" 2>&1 && sleep 1 ", shell=True)
            print("/usr/bin/composite "+outputFile+image_type+" "+hrv_file+" "+" "+hrv_outfile+" && sleep 1")
            subprocess.call("/usr/bin/composite "+outputFile+image_type+" "+hrv_file+" "+" "+hrv_outfile+" 2>&1 && sleep 1 ", shell=True)

            if True:
                print("scp "+scpID+" "+ir_outfile  +" "+" "+scpOutputDir+" 2>&1 &")
                subprocess.call("scp "+scpID+" "+ir_outfile  +" "+" "+scpOutputDir+" 2>&1 && sleep 1", shell=True)
                print("scp "+scpID+" "+hrv_outfile +" "+" "+scpOutputDir+" 2>&1 &")
                subprocess.call("scp "+scpID+" "+hrv_outfile +" "+" "+scpOutputDir+" 2>&1 && sleep 1", shell=True)
