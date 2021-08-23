from __future__ import division
from __future__ import print_function



#from satpy import Scene
#from satpy.utils import debug_on
#debug_on()

import inspect
import logging
LOG = logging.getLogger(__name__)
LOG.setLevel(50)

from satpy import Scene, find_files_and_readers
from datetime import datetime, timedelta
from copy import deepcopy


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


sat="MSG3"

start_time = get_last_SEVIRI_date(True, delay=5)
print(start_time)

files_sat = find_files_and_readers(sensor='seviri',
                               start_time=start_time, end_time=start_time,
                               base_dir="/data/cinesat/in/eumetcast1/",
                               reader='seviri_l1b_hrit')                                   

files = deepcopy(files_sat['seviri_l1b_hrit'])
for f in files:
    if not (sat in f):
        files_sat['seviri_l1b_hrit'].remove(f)
        continue

global_scene = Scene(reader="seviri_l1b_hrit", filenames=files_sat)

print("")
print("=======================")
print(dir(global_scene))
print("=======================")

all_channels=['VIS006','VIS008','IR_016','IR_039','WV_062','WV_073','IR_087','IR_097','IR_108','IR_120', 'IR_134','HRV']

global_scene.load(all_channels)

#area="eurol"
#area="EuropeCanaryS95"
area="ccs4"

local_scene = global_scene.resample(area)

ncfile=start_time.strftime('/data/cinesat/out/MSG_'+area+'_%y%m%d%H%M_rad.nc')
# see https://satpy.readthedocs.io/en/latest/api/satpy.writers.html
local_scene.save_datasets(writer='cf', datasets=all_channels, filename=ncfile)
print('ncview '+ncfile+' &')



