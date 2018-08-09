from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime
import numpy as np
from trollimage.colormap import rainbow, greys
from trollimage.image import Image as trollimage
from copy import deepcopy 

def show_or_save_image(img, save_png, name):
    if save_png:
        pngfile = 'parallax_demo_'+name+'.png'
        print "saved file: "+pngfile
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

def show_image(data, dataname, save_png, colors="rainbow", min_data=None, max_data=None, title=None):
    if min_data is None:
        min_data=data.min()
    if max_data is None:
        max_data=data.max()
    img = trollimage(data, mode="L", fill_value=[0,0,0])
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

    show_or_save_image(PIL_image, save_png, dataname)


#################################################################################################################
#################################################################################################################
    
if __name__ == '__main__':

    # some options to choose
    save_png = False
    show_azimuth       = False
    show_elevation     = False
    show_IR_108        = True
    show_IR_108_cloudy = False
    show_CTH           = True
    show_IR_108_PC     = True
    near_real_time = False
    estimate_CTH = False # if False use CTH from NWC-SAF (recommended), if True estimate CTH from IR_108
    
    colors="rainbow"
    #colors="greys"

    if near_real_time:
        from my_msg_module import get_last_SEVIRI_date
        time_slot = get_last_SEVIRI_date(False, delay=3)
    else:
        time_slot = datetime.datetime(2015, 7, 7, 13, 30)
    print str(time_slot)

    ## define the geostationary factory 
    ## --------------------------------
    #global_data = GeostationaryFactory.create_scene("Meteosat-9", "", "seviri", time_slot)
    global_data = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot)

    # read data that you like to correct for parallax and the Cloud Top Height product of the NWC-SAF
    ## ----------------------------------------------------------------------------------------------
    global_data.load(['IR_108','CTTH'])
    #loaded_channels = [chn.name for chn in global_data.loaded_channels()]
    #print loaded_channels

    # reproject data to your desired projection
    ## ----------------------------------------
    #area="EuropeCanaryS95"
    area="ccs4"
    #area="germ"
    data = global_data.project(area, precompute=True)

    if True:

        # do parallax correction for all channels
        data = data.parallax_corr(fill="bilinear")
        cth = data["CTTH"].height

    else:

        # parallax correction for one channel only

        # get the orbital of the satellite
        ## -----------------------------------------
        orbital = data.get_orbital()

        # calculate the viewing geometry of the SEVIRI sensor
        ## --------------------------------------------------
        (azi, ele) = data['IR_108'].get_viewing_geometry(orbital, data.time_slot)

        if not estimate_CTH:
            # possible call of the parallax correction 
            # ========================================
            cth = data["CTTH"].height
            data["IR_108_PC"] = data['IR_108'].parallax_corr(cth=cth, azi=azi, ele=ele, fill="False")      # fill options: "False" (default)
            #data["IR_108_PC"] = data['IR_108'].parallax_corr(cth=cth, azi=azi, ele=ele, fill="nearest")   # fill options: "False", "nearest" or "bilinear"
            #data["IR_108_PC"] = data['IR_108'].parallax_corr(cth=cth, azi=azi, ele=ele, fill="bilinear")   # fill options: "False", "nearest" or "bilinear"
            #data["IR_108_PC"] = data['IR_108'].parallax_corr(cth=cth, orbital=orbital, time_slot=data.time_slot, fill="False")
        else:
            # parallax correction using a simple CTH estimation 
            # =================================================
            cth = data.estimate_cth(cth_atm='best')   # cth_atm options: "best" (choose temperature profile according to lon/lat/time)
            #data.estimate_cth(cth_atm='standard')    # cth_atm options: "standard", "tropics", "midlatitude summer", "midlatitude winter", "subarctic summer", "subarctic winter"
            ##data.estimate_cth(cth_atm='tropopause') # fixed tropopause height and temperature gradient, assumes coldest pixel is tropopause temperature

            data["IR_108_PC"] = data['IR_108'].parallax_corr(cth=data["CTH"].data, time_slot=data.time_slot,  azi=azi, ele=ele, fill="False") 


    loaded_channels = [chn.name for chn in data.loaded_channels()]
    print loaded_channels

    if show_azimuth:
        show_image(azi, "azi", save_png, colors=colors, min_data=None, max_data=None, title='azimuth')

    if show_elevation:
        show_image(ele, "ele", save_png, colors=colors, min_data=None, max_data=None, title='elevation')

    if show_IR_108:
        show_image(data["IR_108"].data, 'IR_108', save_png, colors=colors, min_data=250, max_data=305, title='IR_108')

    if show_IR_108_cloudy:
        prop = np.ma.masked_where( data["CTTH"].height.mask == True, data["IR_108"].data)
        show_image(prop, 'IR_108_cloudy', save_png, colors=colors, min_data=250, max_data=305, title='IR_108_cloudy')

    if show_CTH:
        show_image(cth, 'CTH', save_png, colors=colors, min_data=0, max_data=12000, title='cloud top height')

    if show_IR_108_PC:
        show_image(data["IR_108_PC"].data, 'IR_108_PC', save_png, colors=colors, min_data=250, max_data=305, title='IR_108_PC')

