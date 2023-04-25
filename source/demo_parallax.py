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
from datetime import datetime, timedelta
from copy import deepcopy 

import netCDF4
import subprocess
import sys
import warnings
from time import perf_counter

from get_input_msg_py3 import parse_commandline_and_read_inputfile
from my_msg_module_py3 import format_name

from parallax import ParallaxCorrection

import inspect
import logging
LOG = logging.getLogger(__name__)
LOG.setLevel(50)
#CRITICAL 50 #ERROR 40 #WARNING 30 #INFO 20 #DEBUG 10 #NOTSET 0

import matplotlib.pyplot as plt

#from satpy.utils import debug_on
#debug_on()

##import warnings
#warnings.filterwarnings("ignore")

def get_last_SEVIRI_date(RSS, delay=0, time_slot=None):

    '''
    input: RSS 
    logical variable True or False 
    specifies if you like get 
    (RSS=True)  the last rapid scan observation date (every  5 min) 
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

def read_satellite_data(in_msg, base_dir, products, reader='seviri_l1b_hrit', filters=[]):

    # read MSG (full disk service) L2
    #################################
    
    print("... read "+in_msg.msg_str()+", "+reader+" data ")
    print("    search for files in "+base_dir)
    files_sat = find_files_and_readers(sensor='seviri',
                                   start_time=in_msg.datetime, end_time=in_msg.datetime,
                                   base_dir=base_dir,
                                   reader=reader)

    # remove unnecessary file from file list
    print("    use only "+in_msg.msg_str(layout="%(msg)s%(msg_nr)s"))
    if len(filters)>0:
        print("    remove also following files: ")
        for filt in filters:
            print("     ", filt)
    
    files = deepcopy(files_sat[reader])
    for f in files:
        # remove files from other MSG satellites
        if not (in_msg.msg_str(layout="%(msg)s%(msg_nr)s") in f):
            files_sat[reader].remove(f)
            continue
        # remove files according to the filters
        for filt in filters:
            if (filt in f):
                files_sat[reader].remove(f)
                continue
    #print("... found input files (filtered): ", files_sat['seviri_l1b_hrit'])

    global_scene = Scene(reader=reader, filenames=files_sat)
    print("    load products")
    [print("      "+str(p)) for p in products]
    global_scene.load(products)
    return global_scene
    
def save_image(local_scene, area, chn, title="", filename="/tmp/tmp.png", rivers=False, coasts=False, show_interactively=False):
    
    from trollimage.colormap import rdbu
    from trollimage.image import Image as Timage

    #img = Timage(local_scene[chn].data, mode="L")
    img = Timage(local_scene[chn].data.compute(), mode="L")
    if ("VIS" in chn):
        rdbu.set_range(0, 100)
    else:
        rdbu.set_range(225, 295)        
    img.colorize(rdbu)
    
    from pyresample import load_area
    area_borders = load_area("/opt/users/hau/monti-pytroll/etc/areas.def", area)
    
    PIL_image=img.pil_image()
    
    from pycoast import ContourWriterAGG
    cw = ContourWriterAGG('/opt/users/common/shapes')
    if coasts:
        cw.add_coastlines(PIL_image, area_borders, resolution='i', level=2)
    if rivers:
        cw.add_rivers(PIL_image, area_borders, resolution='i', level=5, outline='blue')
    cw.add_borders(PIL_image, area_borders, resolution='i', outline=(255, 0, 0))
    
    draw = ImageDraw.Draw(PIL_image)
    draw.rectangle([(0, 0), (PIL_image.size[0]*0.76, 25)], fill=(0,0,0,200))
    font = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", 18)
    draw.text( (1, 1), title, "green" , font=font)  # (255,255,255)
    
    from pydecorate import DecoratorAGG
    dc = DecoratorAGG(PIL_image)
    dc.align_right()
    dc.write_vertically()
    tick_marks=20        # general default
    minor_tick_marks=5   # general default
    import aggdraw
    font = aggdraw.Font("black","/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif-Bold.ttf",size=16)
    dc.add_scale(rdbu.reverse(), extend=True, tick_marks=tick_marks, minor_tick_marks=minor_tick_marks, font=font, line_opacity=100, unit='T/K') #
    
    if show_interactively:
        PIL_image.show()
    else:
        PIL_image.save(filename)
        print("display " + filename +" &")
        

###############################################################################################
###############################################################################################

if __name__ == '__main__':


    time_0 = perf_counter()
    
    # interpret command line arguments (first argument is configuration file) and read configuration file 
    in_msg = parse_commandline_and_read_inputfile()
    print(in_msg.msg_str(layout="%(msg)s%(msg_nr)s"))
    
    print("... produce satellite image for: "+in_msg.datetime.strftime("%Y-%m-%d, %H:%M:%S"))
    time_string = in_msg.datetime.strftime("%Y%m%d%H%M")
    
    time_read_input = perf_counter()

    base_dir_sat  = in_msg.datetime.strftime(in_msg.base_dir_sat)
    base_dir_nwc  = in_msg.datetime.strftime(in_msg.base_dir_ct)
    base_dir_ctth = in_msg.datetime.strftime(in_msg.base_dir_ctth)
                    
    print("... processing time ", in_msg.datetime)

    show_interactively=False
    save_black_white_png=False
    save_png=False
    #resampler='gradient_search'
    #resampler="bilinear"
    resampler="nearest"

    print("")
    
    # DIRTY FIX: need at least one channel to get satellite position, which is not in NWCSAF scene
    # properly done: fix NWCSAF reader to get satellite position in NWCSAF scene
    save_msg_plax = len(in_msg.msg_pc) > 0
    msg_dummy_channel='IR_108'
    in_msg.msg_pc = list(np.unique(in_msg.msg_pc+[msg_dummy_channel]))

    # read satellite data
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        global_scene = read_satellite_data(in_msg, base_dir_sat, in_msg.msg_pc)  # default reader='seviri_l1b_hrit'

    # read NWCSAF files (at least CTH is needed for parallax correction)
    save_nwc_plax = len(in_msg.nwcsaf_pc) > 0
    in_msg.nwcsaf_pc = list(np.unique(in_msg.nwcsaf_pc+['ctth_alti']))
    print(base_dir_nwc, "======")
    global_nwc = read_satellite_data(in_msg, base_dir_nwc, in_msg.nwcsaf_pc, reader='nwcsaf-geo', filters=["PLAX","RDT"])
    
    #!!! dirty fix for missing information in NWCSAF object, maybe fixed in the meantime 
    # NWCSAF products are missing the orbital parameter metadata 
    global_nwc["ctth_alti"].attrs['orbital_parameters']=global_scene[msg_dummy_channel].attrs['orbital_parameters']
    #print(global_scene[msg_dummy_channel].attrs.keys())
    #print(global_scene[msg_dummy_channel].attrs['orbital_parameters'])
    #print(global_nwc["ctth_alti"].attrs.keys())


    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        warnings.filterwarnings("ignore", category=FutureWarning)
    
        # loop over areas, resample and create products
        # create netCDF file for area cosmo1
        # create png    file for area cosmo1_150 (50% more pixels)
        ############################################################
        for area in in_msg.areas:

            area_def = get_area_def(area)

            print("resample to "+area+" (not parallax corrected)")
            local_scene = global_scene.resample(area_def)
    
            if save_black_white_png:
                png_file='/data/cinesat/out/parallax/MSG_'+msg_dummy_channel+'_'+area+'_org.png'
                local_scene.save_dataset(msg_dummy_channel, png_file)
                print('display '+png_file+' &')

            if show_interactively or save_png:
                filename = in_msg.datetime.strftime('/data/COALITION2/tmp/MSG_'+msg_dummy_channel+'-'+area+'_%y%m%d%H%M_org.png')
                title    = in_msg.datetime.strftime(" "+in_msg.msg_str()+', %y-%m-%d %H:%MUTC, no parallax correction')
                save_image(local_scene, area, msg_dummy_channel, title=title, filename=filename, show_interactively=show_interactively)

            # resample MSG L2
            ##################
            print("")
            print("=======================")
            print("resample to "+area+" (parallax corrected)")
            
            # define method to do parallax correction for specific area
            parallax_correction = ParallaxCorrection(area_def)
            # calculate parallax corrected position, using cloud top height 
            plax_corr_area = parallax_correction(global_nwc["ctth_alti"])
            
            # actual projection to parallax corrected positions (MSG channel)
            if save_msg_plax:
                local_scene = global_scene.resample(plax_corr_area, resampler=resampler, precompute=True, cache_dir='/tmp/resample/')
            
            # actual projection to parallax corrected positions (NWCSAF product)
            
            local_nwc = global_nwc.resample(plax_corr_area)

            if show_interactively or save_png:
                filename = in_msg.datetime.strftime('/data/COALITION2/tmp/MSG_'+msg_dummy_channel+'-'+area+'_%y%m%d%H%M_pc.png')
                print("... save image: "+filename)
                title    = in_msg.datetime.strftime(" "+in_msg.msg_str()+', %y-%m-%d %H:%MUTC, parallax correction')
                save_image(local_scene, area, msg_dummy_channel, title=title, filename=filename, show_interactively=show_interactively)
                print("=======================")

            if save_black_white_png:
                png_file='/data/cinesat/out/parallax/MSG_'+msg_dummy_channel+'_'+area+'_pc.png'
                print("... save black white image: "+png_file)
                local_scene.save_dataset(msg_dummy_channel, png_file)
                print('display '+png_file+' &')    
                print("=======================")
                
            if save_msg_plax:
                nc_file = format_name( in_msg.msg_pc_data_dir+in_msg.msg_pc_filename, in_msg.datetime,
                                       sat=in_msg.msg_str(layout="%(msg)s%(msg_nr)s"), sat_nr=in_msg.sat_nr, area=area )
                print("... save parallax corrected MSG SEVIRI Level 1.5 data in netCDF file:"+nc_file)
                local_scene.save_datasets(writer='cf', datasets=in_msg.msg_pc, filename=nc_file)
                print('ncview '+nc_file+' &')
                print("=======================")

            if save_nwc_plax:
                nc_file = format_name( in_msg.nwc_pc_data_dir+in_msg.nwc_pc_filename, in_msg.datetime,
                                       sat=in_msg.msg_str(layout="%(msg)s%(msg_nr)s"), sat_nr=in_msg.sat_nr, area=area )
                print("... save parallax corrected NWCSAF data in netCDF file:"+nc_file)
                local_nwc.save_datasets(writer='cf', datasets=in_msg.nwcsaf_pc, filename=nc_file)
                print('ncview '+nc_file+' &')
                print("=======================")
