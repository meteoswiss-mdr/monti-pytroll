from __future__ import division
from __future__ import print_function

from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime
import numpy as np
from trollimage.colormap import rainbow, greys
from trollimage.image import Image as trollimage
from copy import deepcopy
from pydecorate import DecoratorAGG

def show_or_save_image(img, save_png, name):
    if save_png:
        pngfile = 'parallax_demo_'+name+'.png'
        print("saved file: "+pngfile)
        img.save(pngfile)  
    else:
        img.show() 

def get_colormap(colors, min_data, max_data):
    if colors=="rainbow":
        colormap = deepcopy(rainbow)
    else:
        colormap = deepcopy(greys)
    colormap.set_range(min_data, max_data)
    return colormap

def show_image(data, dataname, save_png, colors="rainbow", min_data=None, max_data=None, title=None, add_colorscale=True):
    if min_data is None:
        min_data=data.min()
    if max_data is None:
        max_data=data.max()
    img = trollimage(data, mode="L", fill_value=[0,0,0])
    print(min_data, max_data)
    colormap = get_colormap(colors, min_data, max_data)
    img.colorize(colormap)
    if title is not None:
        title_color=(255,255,255)
        from PIL import ImageFont
        from PIL import ImageDraw 
        PIL_image=img.pil_image()
        draw = ImageDraw.Draw(PIL_image)
        fontsize=18
        font = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", fontsize)
        draw.text( (10, 10), title, title_color, font=font)

    if add_colorscale:
        dc = DecoratorAGG(PIL_image)
        print(colormap)
        colormap_r = colormap.reverse()
        dc.align_right()
        dc.write_vertically()
        print(colors)
        print(colormap_r)
        dc.add_scale(colormap_r, extend=True, tick_marks=5, minor_tick_marks=1, line_opacity=100) #, tick_marks=tick_marks, minor_tick_marks=minor_tick_marks, unit=units
        
    show_or_save_image(PIL_image, save_png, dataname)


#################################################################################################################
#################################################################################################################
    
if __name__ == '__main__':

    from mpop.utils import debug_on
    debug_on()
    
    # some options to choose
    save_png = False
    show_azimuth    = False
    show_elevation  = False
    show_chn        = True
    show_chn_cloudy = False
    show_CTH        = True
    show_chn_PC     = True
    near_real_time  = False
    #fill="False"            # fill options: "False" (default)
    #fill="nearest"          # fill options: "False", "nearest" or "bilinear"
    fill="bilinear"         # fill options: "False", "nearest" or "bilinear"
    estimate_CTH = False # if False use CTH from NWC-SAF (recommended), if True estimate CTH from IR_108
    save_data=True
    
    #chn='IR_108'
    chn='HRV'
    
    colors="rainbow"
    #colors="greys"

    if near_real_time:
        from my_msg_module import get_last_SEVIRI_date
        time_slot = get_last_SEVIRI_date(False, delay=3)
    else:
        time_slot = datetime.datetime(2015, 7, 7, 14, 35)
        print("*** CHECK THAT YOU ACTIVATED OFFLINE ENVIRONMENT ")
        import subprocess
        #subprocess.call(". ../setup/bashrc_offline ", shell=True)
        import os
        os.environ['PPP_CONFIG_DIR']=os.environ['PYTROLLHOME']+"/cfg_offline/"
        print("... set PPP_CONFIG_DIR to: " + os.environ['PPP_CONFIG_DIR'])
        
    print(str(time_slot))

    ## define the geostationary factory 
    ## --------------------------------
    #global_data = GeostationaryFactory.create_scene("Meteosat-9", "", "seviri", time_slot)
    global_data = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot)
    global_nwc  = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot)

    # read data that you like to correct for parallax and the Cloud Top Height product of the NWC-SAF
    ## ----------------------------------------------------------------------------------------------
    global_data.load([chn, 'IR_108'])
    global_data.load(['CTTH'], reader_level="seviri-level3")
    #global_data.load([chn])
    #global_nwc.load(['CTTH'], reader_level="seviri-level3")
    loaded_channels = [c.name for c in global_data.loaded_channels()]
    print(loaded_channels)
    
    # reproject data to your desired projection
    ## ----------------------------------------
    #area="EuropeCanaryS95"
    area="ccs4"
    #area="germ"
    data = global_data.project(area, precompute=True)
    #nwc  = global_nwc.project(area, precompute=True)

    if True:

        # do parallax correction for all channels
        #data = data.parallax_corr(fill="bilinear")
        data = data.parallax_corr(fill=fill)
        cth = data["CTTH"].height
        #cth = nwc["CTTH"].height
        show_azimuth       = False
        show_elevation     = False

    else:

        # parallax correction for one channel only

        # get the orbital of the satellite
        ## -----------------------------------------
        print("... data.get_orbital(use_NEAR_for_DEEP_space=True)")
        orbital = data.get_orbital(use_NEAR_for_DEEP_space=True)

        # calculate the viewing geometry of the SEVIRI sensor
        ## --------------------------------------------------
        print("... calculate the viewing geometry of the SEVIRI sensor")
        (azi, ele) = data['IR_108'].get_viewing_geometry(orbital, data.time_slot)
        print("azi.min(), azi.max()", azi.min(), azi.max())
        print("ele.min(), ele.max()", ele.min(), ele.max())

        if not estimate_CTH:
            # possible call of the parallax correction 
            # ========================================
            #cth = nwc["CTTH"].height
            cth = data["CTTH"].height
            data[chn+"_PC"] = data[chn].parallax_corr(cth=cth, azi=azi, ele=ele, fill=fill)      
            #data[chn+"_PC"] = data[chn].parallax_corr(cth=cth, orbital=orbital, time_slot=data.time_slot, fill="False")
        else:
            # parallax correction using a simple CTH estimation 
            # =================================================
            cth = data.estimate_cth(cth_atm='best')   # cth_atm options: "best" (choose temperature profile according to lon/lat/time)
            #data.estimate_cth(cth_atm='standard')    # cth_atm options: "standard", "tropics", "midlatitude summer", "midlatitude winter", "subarctic summer", "subarctic winter"
            ##data.estimate_cth(cth_atm='tropopause') # fixed tropopause height and temperature gradient, assumes coldest pixel is tropopause temperature

            data[chn+"_PC"] = data[chn].parallax_corr(cth=data["CTH"].data, time_slot=data.time_slot,  azi=azi, ele=ele, fill=fill) 


    loaded_channels = [c.name for c in data.loaded_channels()]
    print(loaded_channels)

    if show_azimuth:
        show_image(azi, "azi", save_png, colors=colors, min_data=None, max_data=None, title='azimuth')

    if show_elevation:
        show_image(ele, "ele", save_png, colors=colors, min_data=None, max_data=None, title='elevation')

    if chn=='HRV' or chn=='VIS006' or chn=='VIS008':
        min_data=0
        max_data=70
    else:
        min_data=250
        max_data=305
        
    if show_chn:
        show_image(data[chn].data, chn, save_png, colors=colors, min_data=min_data, max_data=max_data, title=chn)

    if show_chn_cloudy:
        prop = np.ma.masked_where( data["CTTH"].height.mask == True, data[chn].data)
        show_image(prop, chn+'_cloudy', save_png, colors=colors, min_data=min_data, max_data=max_data, title=chn+'_cloudy')

    if show_CTH:
        show_image(cth, 'CTH', save_png, colors=colors, min_data=0, max_data=12000, title='cloud top height')

    if show_chn_PC:
        show_image(data[chn+"_PC"].data, chn+'_PC', save_png, colors=colors, min_data=min_data, max_data=max_data, title=chn+'_PC')

    if save_data:
        ncOutputFile = data.time_slot.strftime("./test_rad_PLAX.nc")
        print("... save reprojected data: ncview "+ ncOutputFile+ " &") 
        #data.save(ncOutputFile, to_format="netcdf4", compression=False)
        data.save(ncOutputFile, band_axis=2, concatenate_bands=False) # netCDF4 is default 
