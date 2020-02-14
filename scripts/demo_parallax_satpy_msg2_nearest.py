from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime
import numpy as np
from trollimage.colormap import rainbow, greys
from trollimage.image import Image as trollimage
from copy import deepcopy
from pydecorate import DecoratorAGG
import nwcsaf
import sys

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

def show_image(data, dataname, save_png, colors="rainbow", min_data=None, max_data=None, title=None, add_colorscale=True):
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

    if add_colorscale:
        dc = DecoratorAGG(PIL_image)
        colormap_r = colormap.reverse()
        dc.align_right()
        dc.write_vertically()
        dc.add_scale(colormap_r, extend=True, tick_marks=5, minor_tick_marks=1, line_opacity=100) #, tick_marks=tick_marks, minor_tick_marks=minor_tick_marks, unit=units
        
    show_or_save_image(PIL_image, save_png, dataname)


#################################################################################################################
#################################################################################################################
    
if __name__ == '__main__':


    verbose=False
    replace=True   # replace the channel with parallax corrected data
    #replace=False  # add a second channel CHN_PC
    
    if verbose:
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
    fill="nearest"          # fill options: "False", "nearest" or "bilinear"
    #fill="bilinear"         # fill options: "False", "nearest" or "bilinear"
    estimate_CTH = False # if False use CTH from NWC-SAF (recommended), if True estimate CTH from IR_108
    save_data=True
    
    #chn='IR_108'
    chn='HRV'
    channels=[chn, 'IR_108']
    if not verbose:
        channels=['VIS006','VIS008','IR_016','IR_039','WV_062','WV_073','IR_087','IR_097','IR_108','IR_120','IR_134','HRV']
    
    colors="rainbow"
    #colors="greys"

    if near_real_time:
        from my_msg_module import get_last_SEVIRI_date
        time_slot = get_last_SEVIRI_date(False, delay=3)
    else:
        if len(sys.argv) == 6:
            yyyy  = int(sys.argv[1])
            month = int(sys.argv[2])
            dd    = int(sys.argv[3])
            hh    = int(sys.argv[4])
            mm    = int(sys.argv[5])
        else:
            yyyy  = int(sys.argv[1])
            month = int(sys.argv[2])
            dd    = int(sys.argv[3])
            hh    = int(sys.argv[4])
            mm    = int(sys.argv[5])            
            
        time_slot = datetime.datetime(yyyy, month, dd, hh, mm)
        print "*** CHECK THAT YOU ACTIVATED OFFLINE ENVIRONMENT "
        import subprocess
        #subprocess.call(". ../setup/bashrc_offline ", shell=True)
        import os
        os.environ['PPP_CONFIG_DIR']=os.environ['PYTROLLHOME']+"/cfg_offline/"
        print "... set PPP_CONFIG_DIR to: " + os.environ['PPP_CONFIG_DIR']

    if verbose:
        print str(time_slot)

    ## define the geostationary factory 
    ## --------------------------------
    #global_data = GeostationaryFactory.create_scene("Meteosat-9", "", "seviri", time_slot)
    global_data = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot)
    #global_data = GeostationaryFactory.create_scene("meteosat", "10", "seviri", time_slot)

    # read data that you like to correct for parallax and the Cloud Top Height product of the NWC-SAF
    ## ----------------------------------------------------------------------------------------------
    global_data.load(channels)
    if verbose:
        loaded_channels = [c.name for c in global_data.loaded_channels()]
        print loaded_channels

    
    # read CTH with satpy 
    from satpy import Scene, find_files_and_readers
    files_nwc = find_files_and_readers(sensor='seviri',
                                       start_time=time_slot,
                                       end_time=time_slot,
                                       #base_dir=time_slot.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2013/%Y/%m/%d/"),
                                       base_dir=time_slot.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/CTTH/"),
                                       reader='nc_nwcsaf_msg')
    #print files_nwc
    #files = dict(files_sat.items() + files_nwc.items())
    files = dict(files_nwc.items())
    global_nwc = Scene(filenames=files)
    #global_nwc.load(nwcsaf.product['cloud_top_height']) # this will load a RGB representation
    global_nwc.load(['ctth_alti'])
    if verbose:
        print type(global_nwc['ctth_alti'].values)

    
    # reproject data to your desired projection
    ## ----------------------------------------
    #area="EuropeCanaryS95"
    area="ccs4"
    #area="germ"
    data = global_data.project(area, precompute=True)
    #nwc  = global_nwc.project(area, precompute=True)

    # reproject cloud top height 
    local_scene = global_nwc.resample("ccs4")

    # copy cloud top height (replace Not a Numbers with 0)
    cth = np.nan_to_num(local_scene['ctth_alti'].values)
    if verbose:
        print type(cth)
        print cth.shape
        print global_data['IR_108'].data.shape
        print "min cth:", np.nanmin(cth)
        print "max cth:",np.nanmax(cth)
    
    if show_CTH and verbose:
        show_image(cth, 'CTH', save_png, colors=colors, title='cloud top height', add_colorscale=False)
    
    if True:
        # do parallax correction for all channels
        #data = data.parallax_corr(fill="bilinear", replace=replace)
        data = data.parallax_corr(cth=cth, fill=fill, replace=replace)
        show_azimuth       = False
        show_elevation     = False

    else:

        # parallax correction for one channel only

        # get the orbital of the satellite
        ## -----------------------------------------
        print "... data.get_orbital(use_NEAR_for_DEEP_space=True)"
        orbital = data.get_orbital(use_NEAR_for_DEEP_space=True)

        # calculate the viewing geometry of the SEVIRI sensor
        ## --------------------------------------------------
        print "... calculate the viewing geometry of the SEVIRI sensor"
        (azi, ele) = data['IR_108'].get_viewing_geometry(orbital, data.time_slot)
        print "azi.min(), azi.max()", azi.min(), azi.max()
        print "ele.min(), ele.max()", ele.min(), ele.max()

        if not estimate_CTH:
            # possible call of the parallax correction 
            # ========================================
            data[chn+"_PC"] = data[chn].parallax_corr(cth=cth, azi=azi, ele=ele, fill=fill, replace=replace)      
            #data[chn+"_PC"] = data[chn].parallax_corr(cth=cth, orbital=orbital, time_slot=data.time_slot, fill="False", replace=replace)
        else:
            # parallax correction using a simple CTH estimation 
            # =================================================
            cth = data.estimate_cth(cth_atm='best')   # cth_atm options: "best" (choose temperature profile according to lon/lat/time)
            #data.estimate_cth(cth_atm='standard')    # cth_atm options: "standard", "tropics", "midlatitude summer", "midlatitude winter", "subarctic summer", "subarctic winter"
            ##data.estimate_cth(cth_atm='tropopause') # fixed tropopause height and temperature gradient, assumes coldest pixel is tropopause temperature

            data[chn+"_PC"] = data[chn].parallax_corr(cth=data["CTH"].data, time_slot=data.time_slot,  azi=azi, ele=ele, fill=fill, replace=replace) 


    loaded_channels = [c.name for c in data.loaded_channels()]
    print loaded_channels

    if show_azimuth and verbose:
        show_image(azi, "azi", save_png, colors=colors, min_data=None, max_data=None, title='azimuth')

    if show_elevation and verbose:
        show_image(ele, "ele", save_png, colors=colors, min_data=None, max_data=None, title='elevation')

    if chn=='HRV' or chn=='VIS006' or chn=='VIS008':
        min_data=0
        max_data=70
    else:
        min_data=250
        max_data=305
        
    if show_chn and verbose:
        show_image(data[chn].data, chn, save_png, colors=colors, min_data=min_data, max_data=max_data, title=chn)

    if show_chn_cloudy and verbose:
        prop = np.ma.masked_where( data["CTTH"].height.mask == True, data[chn].data)
        show_image(prop, chn+'_cloudy', save_png, colors=colors, min_data=min_data, max_data=max_data, title=chn+'_cloudy')

    if show_chn_PC and verbose:
        show_image(data[chn+"_PC"].data, chn+'_PC', save_png, colors=colors, min_data=min_data, max_data=max_data, title=chn+'_PC')

    if save_data:
        from my_msg_module import format_name
        ncOutputFile = data.time_slot.strftime("./test_rad_PLAX.nc")
        ncOutputFile = format_name('%(msg)s_%(area)s_%Y%m%d%H%M_rad_PLAX.nc', time_slot, area=area, sat_nr=data.sat_nr())
        ncOutputFile = "/data/COALITION2/tmp/nc_PLAX/"+ncOutputFile.replace("-","")
        print "... save reprojected data: ncview "+ ncOutputFile+ " &" 
        #data.save(ncOutputFile, to_format="netcdf4", compression=False)
        data.save(ncOutputFile, band_axis=2, concatenate_bands=False) # netCDF4 is default 
