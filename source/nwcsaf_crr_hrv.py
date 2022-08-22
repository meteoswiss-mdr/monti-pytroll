from __future__ import division
from __future__ import print_function

#from satpy.utils import debug_on
#debug_on()

map_dir="/opt/users/common/shapes/"

import nwcsaf
import numpy as np
import sys

from satpy import Scene, find_files_and_readers
from datetime import datetime

print(len(sys.argv))
if len(sys.argv) == 6:
    fixed_date=True
    print(sys.argv[1],sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    start_time = datetime(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]))
    end_time   = start_time
    base_dir=start_time.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/"+p_+"/")
else:
    fixed_date=False
    from my_msg_module_py3 import get_last_SEVIRI_date
    start_time = get_last_SEVIRI_date(False, delay=10)
    end_time   = start_time
    #base_dir="/data/cinesat/in/eumetcast1/"
    base_dir=start_time.strftime("//data/cinesat/in/safnwc/")

    print("======================")
    print("======================")
    print ("... search files in "+ base_dir)
    files_nwc = find_files_and_readers(sensor='seviri',
                                       start_time=start_time,
                                       end_time=end_time,
                                       base_dir=base_dir,
                                       reader='nwcsaf-geo')
    print (files_nwc)

    print ("... define global scene ")
    global_scene = Scene(filenames=files_nwc)

    
