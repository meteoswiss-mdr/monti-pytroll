from __future__ import division
from __future__ import print_function

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageEnhance

import nwcsaf
import numpy as np

from satpy import Scene, find_files_and_readers
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

#from satpy.utils import debug_on
#debug_on()

##import warnings
#warnings.filterwarnings("ignore")

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
    

###############################################################################################
###############################################################################################

if __name__ == '__main__':
    
    sat='MSG4'

    if len(sys.argv) == 1:
        start_time = get_last_SEVIRI_date(False, delay=6)
        base_dir_sat = "/data/cinesat/in/eumetcast1/"
        base_dir_nwc = "/data/cinesat/in/eumetcast1/"
        #base_dir_nwc = "/data/cinesat/in/safnwc_v2016/"
    elif len(sys.argv) == 6:
        year   = int(sys.argv[1])
        month  = int(sys.argv[2])
        day    = int(sys.argv[3])
        hour   = int(sys.argv[4])
        minute = int(sys.argv[5])
        start_time = datetime(year, month, day, hour, minute)
        base_dir_sat = start_time.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/%Y/%m/%d/")
        #base_dir_sat = start_time.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/%Y/%m/%d/")
        base_dir_nwc = start_time.strftime("/data/OWARNA/hau/database/meteosat/SAFNWC/%Y/%m/%d/CT/")
    else:        
        start_time = datetime(2020, 10, 7, 16, 0)
        base_dir_sat = start_time.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/%Y/%m/%d/")
        base_dir_nwc = start_time.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/CT/")
        
    print("... processing time ", start_time)

    show_interactively=False
    save_black_white_png=False

    print("")
    print("")
    print("*** Creating LSCL (low stratus confidence level) product")
    print("")


    # read MSG (full disk service) L2
    #################################
    print("... read "+sat+" L1.5 data")
    print("    search for HRIT files in "+base_dir_sat)

    files_sat = find_files_and_readers(sensor='seviri',
                                   start_time=start_time, end_time=start_time,
                                   base_dir=base_dir_sat,
                                   reader='seviri_l1b_hrit')

    files = deepcopy(files_sat['seviri_l1b_hrit'])
    #print("    found SEVIRI files: ", files_sat)
    for f in files:
        if not (sat in f):
            files_sat['seviri_l1b_hrit'].remove(f)
            continue
        if ("HRV" in f) or ("VIS006" in f) or ("VIS008" in f) or ("IR_016" in f) or ("IR_039" in f):
            files_sat['seviri_l1b_hrit'].remove(f)
            continue
        if  ("WV_062" in f) or ("WV_073" in f) or ("IR_097" in f) or ("IR_108" in f) or ("IR_134" in f):
            files_sat['seviri_l1b_hrit'].remove(f)
            continue

    global_scene = Scene(reader="seviri_l1b_hrit", filenames=files_sat)
    global_scene.load(['IR_087','IR_120'])


    # read NWCSAF files
    ########################
    print("... read "+sat+" NWCSAF CTTH")
    print("    search for NWCSAF files in "+base_dir_nwc)

    files_nwc = find_files_and_readers(sensor='seviri',
                                       start_time=start_time, end_time=start_time,
                                       base_dir=base_dir_nwc, reader='nwcsaf-geo')
    print("    found NWCSAF files: ", files_nwc)
    
    files = deepcopy(files_nwc['nwcsaf-geo'])
    for f in files:
        # remove files from other satellites 
        if not (sat in f):
            files_nwc['nwcsaf-geo'].remove(f)
            continue
        # remove CTTH files 
        if ("CTTH" in f):
            files_nwc['nwcsaf-geo'].remove(f)
            continue

    global_nwc = Scene(filenames=files_nwc)
    global_nwc.load(['ct'])  # "CT"


    # loop over areas, resample and create products
    # create netCDF file for area cosmo1
    # create png    file for area cosmo1_150 (50% more pixels)
    ############################################################
    #for area in ['SeviriDisk00Cosmo',"cosmo1x150"]:
    #for area in ['cosmo1', 'cosmo1eqc3km']:
    for area in ['cosmo1eqc3km']:
    #for area in ['cosmo1x150', 'cosmo1eqc3km']:

        # resample MSG L2
        ##################
        print("")
        print("=======================")
        print("resample to "+area)
        local_scene = global_scene.resample(area)

        # fake a new channel
        print("fake a new channel")
        local_scene['lscl'] = deepcopy(local_scene['IR_120'])
        #local_scene['lscl'].wavelength=""
        #local_scene['lscl'].standard_name="low_stratus_confidence_level"
        #local_scene['lscl'].calibration="brightness_temperature_difference"

        #print(local_scene['IR_120'])
        #print(dir(local_scene['IR_120']))
        #print(local_scene['IR_120'].standard_name)
        #print(type(local_scene['IR_120'].standard_name))
        #local_scene['lscl'].standard_name = "toa_brightness_temperature_difference"
        #print(local_scene['lscl']) 

        ##############################################
        # calculate lscl "low stratus confidence level
        # see MSc Thesis of Anna Ehrler (chapter 3.2.1 to 3.2.2) 
        ##############################################

        th_liquid_cloud = 1.8 # K 
        # cloud_confidence_range
        ccr  = 1.0 # K
        local_scene['lscl'].values = (th_liquid_cloud - (local_scene['IR_120']-local_scene['IR_087']) - ccr) / (-2. * ccr)

        #local_scene['lscl'].area_def = local_scene['IR_120'].area_def

        # print(global_nwc)
        local_nwc = global_nwc.resample(area)


        # delete values for high clouds
        ###########################################
        # !!! ONLY NWCSAF VERSION 2016 and 2018 !!!
        # !!! Numbers are different for v2013 
        # ct:comment = "1:  Cloud-free land; 2:  Cloud-free sea; 3:  Snow over land;  4:  Sea ice; 5:  Very low clouds;
        #               6:  Low clouds; 7:  Mid-level clouds;  8:  High opaque clouds; 9:  Very high opaque clouds;
        #              10:  Fractional clouds; 11:  High semitransparent thin clouds;  12:  High semitransparent meanly thick clouds;
        #              13:  High semitransparent thick clouds;  14:  High semitransparent above low or medium clouds;  15:  High semitransparent above snow/ice" ;
        for _ct_ in [7,8,9,10,11,12,13,14,15]:
            print("replace cloud type",_ct_)
            local_scene['lscl'].values = np.where(local_nwc['ct'].values==_ct_, np.nan, local_scene['lscl'].values)

        if show_interactively:
            fig, ax = plt.subplots(figsize=(13, 7))
            pos = plt.imshow(local_scene['lscl'].values, vmin=0, vmax=1)
            fig.colorbar(pos)
            plt.title(start_time.strftime('low stratus confidence level, %y-%m-%d %H:%MUTC'))
            plt.show()

        if save_black_white_png:
            local_scene.save_dataset('lscl', './lscl_'+area+'.png')
            print(dir(local_scene.save_dataset))
            print('display ./lscl_'+area+'.png &')    

        # save png file for SATLive
        ##############################
        if area=="cosmo1x150" or area=="cosmo1":
            png_file = start_time.strftime('/data/cinesat/out/MSG_lscl-'+area+'_%y%m%d%H%M.png')
            from trollimage.colormap import spectral, greys, ylorrd, rdgy 
            imgarr = np.array(local_scene['lscl'].data)
            from trollimage.image import Image as Timage
            img = Timage(imgarr, mode="L")
            img.colorize( rdgy.reverse() )
            img.save(png_file)

            # local_scene.save_dataset( 'lscl', png_file )
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

            if area=="cosmo1x150":
                scpID="-i ~/.ssh/id_rsa_las"
                scpOutputDir="las@zueub241:/srn/las/www/satellite/DATA/MSG_"+"lscl"+"-"+area+"_/"
                scp_command = "/usr/bin/scp "+scpID+" "+png_file+" "+scpOutputDir+" 2>&1 &"
                print(scp_command)
                subprocess.call(scp_command, shell=True)
            elif area=="cosmo1":
                scpID="-i ~/.ssh/id_rsa_tsa"
                scpOutputDir="hamann@tsa.cscs.ch:/scratch/hamann/DayNightFog/"
                print("... scp "+png_file+" to "+scpOutputDir)
                subprocess.call("/usr/bin/scp "+scpID+" "+png_file+" "+scpOutputDir+" 2>&1 &", shell=True)
            
        # save netCDF file for APN
        ##############################
        if area=='cosmo1eqc3km':
            netCDF_file = start_time.strftime('/data/cinesat/out/MSG_lscl-'+area+'_%y%m%d%H%M.nc')
            print("... save result in: "+ netCDF_file)
            print("include_lonlats=True")
            local_scene.save_dataset('lscl', netCDF_file, include_lonlats=True, writer='cf',
                                     exclude_attrs=['raw_metadata'], epoch='seconds since 1970-01-01 00:00:00')   #, writer='cf'

            #import netCDF4 as nc
            #file_input = nc.Dataset(netCDF_file, 'r+')
            #print(file_input.variables.keys())

            #lonlats = local_scene['lscl'].area.get_lonlats()

            #lons = file_input.createVariable('longitues', 'single', ('y', 'x'))
            #lats = file_input.createVariable('latitudes', 'single', ('y', 'x'))

            #lons[:] = lonlats[0][:,:]
            #lats[:] = lonlats[1][:,:]

            #local_scene.save_datasets(['lscl'], filename=netCDF_file, include_lonlats=True)   #, writer='cf'
            print("... ncview " + netCDF_file +" &")

            rewrite_xy_axis(netCDF_file)

            scpID="-i ~/.ssh/id_rsa_tsa"
            #scpOutputDir="hamann@tsa.cscs.ch:/scratch/hamann/DayNightFog/"
            scpOutputDir="hamann@tsa.cscs.ch:/scratch/hamann/DayNightFog_Filter-CT-7-15/"
            print("... scp "+netCDF_file+" to "+scpOutputDir)
            subprocess.call("/usr/bin/scp "+scpID+" "+netCDF_file+" "+scpOutputDir+" 2>&1 &", shell=True)

