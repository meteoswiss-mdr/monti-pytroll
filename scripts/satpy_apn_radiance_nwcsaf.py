from __future__ import division
from __future__ import print_function

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageEnhance

import nwcsaf
import numpy as np

from satpy import Scene, find_files_and_readers
from satpy.resample import get_area_def
from parallax import ParallaxCorrection

from datetime import datetime, timedelta
from copy import deepcopy 

import netCDF4
import subprocess
import sys

import inspect
import logging
LOG = logging.getLogger(__name__)
LOG.setLevel(50)
#CRITICAL 50 #ERROR 40 #WARNING 30 #INFO 20 #DEBUG 10 #NOTSET 0

import matplotlib.pyplot as plt
scpID="-i ~/.ssh/id_rsa_tsa"

#from satpy.utils import debug_on
#debug_on()

##import warnings
#warnings.filterwarnings("ignore")

def show_result(local_scene, product, start_time, area, show_interactively=False, save_black_white_png=False, save_png=False):
    
    if show_interactively:
        fig, ax = plt.subplots(figsize=(13, 7))
        pos = plt.imshow(local_scene[product].values, vmin=0, vmax=1)
        fig.colorbar(pos)
        plt.title(start_time.strftime(product+', %y-%m-%d %H:%MUTC'))
        plt.show()

    if save_black_white_png:
        local_scene.save_dataset(product, product+'_'+area+'.png')
        print(dir(local_scene.save_dataset))
        print('display ./+product+_'+area+'.png &')    

    # save png file for SATLive%
    ##############################
    if save_png:

        png_file = start_time.strftime('/data/cinesat/out/MSG_'+product+'-'+area+'_%y%m%d%H%M.png')
        from trollimage.colormap import  rdgy # spectral, greys, ylorrd
        imgarr = np.array(local_scene[product].data)
        from trollimage.image import Image as Timage
        img = Timage(imgarr, mode="L")
        img.colorize( rdgy.reverse() )
        img.save(png_file)

        # local_scene.save_dataset( 'IR_108', png_file )
        from pyresample.utils import load_area
        swiss = load_area("/opt/users/hau/monti-pytroll/etc/areas.def", area)

        from pycoast import ContourWriterAGG
        cw = ContourWriterAGG('/opt/users/common/shapes')
        cw.add_borders_to_file(png_file, swiss, outline="green", resolution='i', level=3, width=2)

        img = Image.open(png_file)
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (img.size[0]*0.7, 25)], fill=(0,0,0,200))
        font = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", 18)
        title = start_time.strftime(" "+sat[0:3]+"-"+sat[3]+', %y-%m-%d %H:%MUTC, low stratus confidence level')
        draw.text( (1, 1), title, "green" , font=font)  # (255,255,255)
        img.save(png_file)

        print("display " + png_file +" &")

def get_last_SEVIRI_date(RSS, delay=0, time_slot=None):

    '''
    input: RSS 
    logical variable True or False 
    specifies if you like get 
    (RSS=True)  the last rapid scan observation date (every 5  min) 
    (RSS=False) the last full disk  observation date (every 15 min)
    (delay=INT) number of minutes to substract before finding the date (good if data needs a few min before arriving)
    (time_slot) If not given, take last time
    otherwise search scanning time of SEVIRI before given time_slot
    output:
    date structure with the date of the last SEVIRI observation
    '''
    
    from time import gmtime
    
    LOG.info("*** start get_last_SEVIRI_date ("+inspect.getfile(inspect.currentframe())+")")
    
    # if rapid scan service than 5min otherwise 15
    if RSS:
        nmin = 5 
    else:
        nmin = 15
    
    if (time_slot is None):
        # get the current time
        gmt = gmtime()
        #print ("GMT time: "+ str(gmt))
        # or alternatively 
        # utc = datetime.utcnow()
        # convert to datetime format
        t0 = datetime(gmt.tm_year, gmt.tm_mon, gmt.tm_mday, gmt.tm_hour, gmt.tm_min, 0) 
        LOG.debug("    current time = "+str(t0))
    else:
        t0 = time_slot + timedelta(seconds=nmin*60)  # we substract one scanning time later, so we can add it here
        LOG.debug("    reference time = "+str(t0))
    
    # apply delay (if it usually takes 5 min for the data to arrive, use delay 5min)
    if delay != 0:
       t0 -= timedelta(minutes=delay)
    LOG.debug("    applying delay "+str(delay)+" min delay, time = "+ str(t0))
    
    LOG.debug("    round by scanning time "+str(nmin)+" min, RSS = "+str(RSS))
    #tm_min2 = gmt.tm_min - (gmt.tm_min % nmin)
    minute1 = t0.minute - (t0.minute % nmin)
    
    # define current date rounded by one scan time 
    #date1 = datetime(gmt.tm_year, gmt.tm_mon, gmt.tm_mday, gmt.tm_hour, tm_min2 , 0) 
    t1 = datetime(t0.year, t0.month, t0.day, t0.hour, minute1, 0) 
    LOG.debug("    end time of last scan: "+str(t1))
    
    # substracting one scan time (as the start time of scan is returned) 
    t1 -= timedelta(seconds=nmin*60)
    LOG.info("    start time of last scan: "+str(t1))
    
    return t1

def rewrite_xy_axis(netCDF_file):
    print("... re-place values on the x and y axis with lon/lat values in "+netCDF_file)
    ds = netCDF4.Dataset(netCDF_file, 'r+')
    lat = ds["latitude"][:,0]
    ds["y"][:] = lat.data
    ds["y"].units = 'Degrees North'
    lon = ds["longitude"][0,:]
    ds["x"][:] = lon.data
    ds["x"].units = 'Degrees East'
    ds.close()

def save_netCDF_file(data_name, local_scene, products, start_time, scp_product_to_CSCS=False):    

    netCDF_file = start_time.strftime('/data/cinesat/out/MSG_'+data_name+'_'+area+'_%y%m%d%H%M.nc')
        
    print("... save result in: "+ netCDF_file)
    print("include_lonlats=True")
    #local_scene.save_dataset("IR_108", netCDF_file, include_lonlats=True, writer='cf',
    #                         exclude_attrs=['raw_metadata'], epoch='seconds since 1970-01-01 00:00:00')   #, writer='cf'
    local_scene.save_datasets(datasets=products, filename=netCDF_file, include_lonlats=True, writer='cf',
                                     exclude_attrs=['raw_metadata'], epoch='seconds since 1970-01-01 00:00:00')   #, writer='cf'

    #local_scene.save_datasets(['lscl'], filename=netCDF_file, include_lonlats=True)   #, writer='cf'
    print("... ncview " + netCDF_file +" &")

    #if data_name=="radiance" or data_name=="nwcsaf":
    rewrite_xy_axis(netCDF_file)

    if scp_product_to_CSCS:
        scpOutputDir="hamann@tsa.cscs.ch:/scratch/hamann/APN_MSG4_"+data_name+"/"
        print("... scp "+scpID+" "+netCDF_file+" "+scpOutputDir)
        subprocess.call("/usr/bin/scp "+scpID+" "+netCDF_file+" "+scpOutputDir+" 2>&1 &", shell=True)

    
    
###############################################################################################
###############################################################################################

if __name__ == '__main__':
    
    sat='MSG4'
    scp_product_to_CSCS=False
    
    if len(sys.argv) == 1:
        start_time = get_last_SEVIRI_date(False, delay=6)
        base_dir = "/data/cinesat/in/eumetcast1/"
        base_dir_nwc = "/data/cinesat/in/eumetcast1/"    # eumetsat product
        #base_dir_nwc = "/data/cinesat/in/safnwc_v2016/" # our own NWCSAF products
    elif len(sys.argv) == 6:
        year    = int(sys.argv[1])
        month   = int(sys.argv[2])
        day     = int(sys.argv[3])
        hour    = int(sys.argv[4])
        minute  = int(sys.argv[5])
        start_time = datetime(year, month, day, hour, minute)
        base_dir = start_time.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/%Y/%m/%d/")
        #base_dir = start_time.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/%Y/%m/%d/")
        base_dir_nwc = start_time.strftime("/data/OWARNA/hau/database/meteosat/SAFNWC/%Y/%m/%d/*/")

        
    print("... processing time ", start_time)


    show_interactively=False
    save_black_white_png=False
    save_png=True
    save_netCDF=True
    scp_product_to_CSCS=True

    print("")
    process_radiance=True
    process_nwc=True
    process_parallax_radiance=True
    process_parallax_nwcsaf=False
    
    
    # read MSG (full disk service) L2
    #################################
    if process_radiance or process_parallax_radiance:
        print("... read "+sat+" L1.5 data")
        print("    search for HRIT files in "+base_dir)

        reader="seviri_l1b_hrit"
        products = ['VIS006', 'VIS008', 'IR_016', 'IR_039', 'WV_062', 'WV_073',\
                    'IR_087', 'IR_097', 'IR_108', 'IR_120', 'IR_134', 'HRV']

        files_sat = find_files_and_readers(sensor='seviri',
                                           start_time=start_time, end_time=start_time,
                                           base_dir=base_dir,
                                           reader=reader)

        files = deepcopy(files_sat[reader])
        #print("    found SEVIRI files: ", files_sat)
        for f in files:
            if not (sat in f):
                files_sat[reader].remove(f)
            continue

        global_scene = Scene(reader=reader, filenames=files_sat)
        global_scene.load(products)
        
    if process_nwc or process_parallax_radiance or process_parallax_nwcsaf:
        # read NWCSAF files
        ########################
        print("... read "+sat+" NWCSAF products")
        print("    search for NWCSAF files in "+base_dir_nwc)
        products_nwc = ['cma', 'ct', 'ctth_tempe', 'ctth_alti', 'ctth_pres', 'ctth_quality', 'ctth_status_flag', 'ctth_conditions', 'ctth_method' ]
        reader_nwc='nwcsaf-geo'

        files_nwc = find_files_and_readers(sensor='seviri',
                                           start_time=start_time, end_time=start_time,
                                           base_dir=base_dir_nwc,
                                           reader=reader_nwc)
        
        files = deepcopy(files_nwc[reader_nwc])
        #print("    found SEVIRI files: ", files_sat)
        for f in files:
            if not (sat in f):
                files_nwc[reader_nwc].remove(f)
            continue

        global_nwc = Scene(reader=reader_nwc, filenames=files_nwc)
        global_nwc.load(products_nwc)

        if process_parallax_radiance or process_parallax_nwcsaf:
            global_nwc["ctth_alti"].attrs['satellite_latitude']  = global_scene[products[0]].attrs['satellite_latitude']
            global_nwc["ctth_alti"].attrs['satellite_altitude']  = global_scene[products[0]].attrs['satellite_altitude']
            global_nwc["ctth_alti"].attrs['satellite_longitude'] = global_scene[products[0]].attrs['satellite_longitude']

    # loop over areas, resample and create products
    ############################################################
    for area in ['cosmo1eqc3km']:

        # resample to another area
        ##################
        print("")
        print("=======================")
        print("resample to "+area)
        if process_radiance:
            local_scene = global_scene.resample(area)
            show_result(local_scene, products[0], start_time, area, show_interactively=show_interactively, save_black_white_png=save_black_white_png, save_png=save_png)
            if save_netCDF:
                save_netCDF_file("radiance", local_scene, products, start_time, scp_product_to_CSCS=scp_product_to_CSCS)
            
        if process_nwc:
            local_nwc = global_nwc.resample(area)
            show_result(local_nwc, products_nwc[0], start_time, area, show_interactively=show_interactively, save_black_white_png=save_black_white_png, save_png=save_png)
            if save_netCDF:
                save_netCDF_file("nwcsaf", local_nwc, products_nwc, start_time, scp_product_to_CSCS=scp_product_to_CSCS)               

        if process_parallax_radiance or process_parallax_nwcsaf:
            area_def = get_area_def(area)
            parallax_correction = ParallaxCorrection(area_def)
            plax_corr_area = parallax_correction(global_nwc["ctth_alti"])
                            
        if process_parallax_radiance:
            print("==========================================")
            print("resample parallax correction")
            print("==========================================")
            local_scene_plax = global_scene.resample(plax_corr_area)
            print("==========================================")
            print("back to regular grid")
            print("==========================================")
            local_scene_plax_reg = local_scene_plax.resample(area)
            print("==========================================")
            print("resampling done")
            print("==========================================")
            if save_netCDF:
                save_netCDF_file("radiance-plax", local_scene_plax_reg, products, start_time, scp_product_to_CSCS=scp_product_to_CSCS)
            
        if process_parallax_nwcsaf:
            local_nwc_plax = global_nwc.resample(plax_corr_area)
            if save_netCDF:
                save_netCDF_file("nwcsaf-plax", local_nwc_plax, products_nwc, start_time, scp_product_to_CSCS=scp_product_to_CSCS)
            
