from __future__ import division
from __future__ import print_function

# Marco Sassi's program
# zueub428:/opt/pytroll/nwcsaf/nwcsaf-processing/bin/NWCSAF_processing.py
# old version: zueub428:/opt/safnwc/bin/NWCSAF_processing.py
# see also https://github.com/pytroll/pytroll-examples/blob/master/satpy/ears-nwc.ipynb

#from satpy.utils import debug_on
#debug_on()

import nwcsaf
import numpy as np

from satpy import Scene, find_files_and_readers
from datetime import datetime, timedelta
from copy import deepcopy 

import inspect
import logging
LOG = logging.getLogger(__name__)
LOG.setLevel(50)
#CRITICAL 50 #ERROR 40 #WARNING 30 #INFO 20 #DEBUG 10 #NOTSET 0

import matplotlib.pyplot as plt

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

def get_last_SEVIRI_date(RSS, delay=0, time_slot=None):
    
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




sat='MSG4'
start_time = get_last_SEVIRI_date(False, delay=10)

#area="EuropeCanaryS95"
#area="ccs4"
area="cosmo1"


if True:
    files_sat = find_files_and_readers(sensor='seviri',
                                   start_time=start_time, end_time=start_time,
                                   base_dir="/data/cinesat/in/eumetcast1/",
                                   reader='seviri_l1b_hrit')   

    files = deepcopy(files_sat['seviri_l1b_hrit'])
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
    #for f in files_sat['seviri_l1b_hrit']:
    #    print(f)

    #global_scene = Scene(reader="hrit_msg", filenames=files)
    global_scene = Scene(reader="seviri_l1b_hrit", filenames=files_sat)

    global_scene.load(['IR_087','IR_120'])

    print("")
    print("=======================")
    print("resample to "+area)
    local_scene = global_scene.resample(area)


    th_liquid_cloud = 1.8 # K 
    # cloud_confidence_range
    ccr  = 1.0 # K
    local_scene['lscl'] = (th_liquid_cloud - (local_scene['IR_120']-local_scene['IR_087']) - ccr) / (-2. * ccr) 

if False:
    local_scene.save_dataset('lscl', './lscl_'+area+'.png')
    print(dir(local_scene.save_dataset))
    print('display ./lscl_'+area+'.png &')

#base_dir=start_time.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/"+p_+"/")
#base_dir=start_time.strftime("/data/cinesat/in/safnwc_v2016/")
base_dir=start_time.strftime("/data/cinesat/in/eumetcast1/")

files_nwc = find_files_and_readers(sensor='seviri',
                                   start_time=start_time, end_time=start_time,
                                   base_dir=base_dir, reader='nwcsaf-geo')

global_nwc = Scene(filenames=files_nwc)

global_nwc.load(['ct'])  # "CT"

# print(global_nwc)
local_nwc = global_nwc.resample(area)

# ct:comment = "1:  Cloud-free land; 2:  Cloud-free sea; 3:  Snow over land;  4:  Sea ice; 5:  Very low clouds; 6:  Low clouds; 7:  Mid-level clouds;  8:  High opaque clouds; 9:  Very high opaque clouds;  10:  Fractional clouds; 11:  High semitransparent thin clouds;  12:  High semitransparent meanly thick clouds;  13:  High semitransparent thick clouds;  14:  High semitransparent above low or medium clouds;  15:  High semitransparent above snow/ice" ;


if False:
    # delete values for high clouds
    for _ct_ in [8,9,11,12,13,14,15]:
        print("replace cloud type",_ct_)
        local_nwc["ct"].values = np.where(local_nwc['ct'].values==_ct_, 255, local_nwc['ct'].values)

    plt.imshow(local_nwc["ct"].values, vmin=-1, vmax=16)
    plt.show()

# delete values for high clouds
for _ct_ in [8,9,11,12,13,14,15]:
    print("replace cloud type",_ct_)
    local_scene['lscl'].values = np.where(local_nwc['ct'].values==_ct_, np.nan, local_scene['lscl'].values)

fig, ax = plt.subplots(figsize=(13, 7))
pos = plt.imshow(local_scene['lscl'].values, vmin=0, vmax=1)
fig.colorbar(pos)
plt.title(start_time.strftime('low stratus confidence level, %y-%m-%d %H:%MUTC'))
plt.show()

local_scene.save_dataset('lscl', start_time.strftime('/data/cinesat/out/MSG_lscl-'+area+'_%y%m%d%H%M.nc'))
