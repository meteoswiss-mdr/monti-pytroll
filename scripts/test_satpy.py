#import os
#os.chdir("/data/cinesat/in/eumetcast1/")
#from satpy import Scene
#from satpy.scene import Scene
from datetime import datetime
from my_msg_module import get_last_SEVIRI_date

RSS=False

from satpy.utils import debug_on
debug_on()

#time_slot = datetime(lastdate.year, lastdate.month, lastdate.day, lastdate.hour, lastdate.minute)
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=datetime(2015, 4, 20, 10, 0))
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=datetime(2015, 4, 20, 10, 0), base_dir="/home/a001673/data/satellite/Meteosat-10/seviri/lvl1.5/2015/04/20/HRIT") 
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=lastdate, base_dir="/data/cinesat/in/eumetcast1")
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=lastdate, reader="hrit_msg", basedir="/data/cinesat/in/eumetcast1/")  
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=datetime(2017, 1, 27, 13, 45))
#print "hallo world", dir(global_scene), global_scene.info
#print global_scene.available_composites()

from satpy import Scene

#my_dir="/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/singletime/"
#from datetime import datetime
#time_slot = datetime(2017, 3, 29, 10, 15)

#lastdate = get_last_SEVIRI_date(RSS, delay=10)
#my_dir="/data/cinesat/in/eumetcast1/"
#reader="hrit_msg"

#global_scene = Scene(platform_name="Meteosat-9", sensor="seviri", reader="hrit_msg", start_time=lastdate)


my_dir="/data/COALITION2/database/meteosat/native_test/"
reader="native_msg"

import os
os.chdir(my_dir)

global_scene = Scene(platform_name="Meteosat-9", sensor="seviri", reader=reader, filenames=["/data/COALITION2/database/meteosat/native_test/MSG3-SEVI-MSG15-0100-NA-20170326102740.340000000Z-20170326102757-1213498.nat"])

#global_scene.load([0.6, 0.8, 10.8])
global_scene.load(['overview'])
#global_scene.load(["VIS006", "VIS008", "IR_108"])
#global_scene.save_dataset('overview', '/data/COALITION2/database/meteosat/native_test/local_overview.png')

local_scene = global_scene.resample("ccs4")
local_scene.save_dataset('overview', '/data/COALITION2/database/meteosat/native_test/local_overview.png')


#print global_scene
#print global_scene[0.6]

#local_scene = global_scene.project("ccs4")

# print global_scene.available_datasets()  ## does not work

#global_scene.show(0.6)
#global_scene.show('VIS006')
#global_scene.show('overview')

#Traceback (most recent call last):
#  File "test_satpy.py", line 18, in <module>
#    global_scene.load([0.6, 0.8, 10.8])
#  File "/opt/users/hau/PyTroll/packages/satpy/satpy/scene.py", line 611, in load
#    **kwargs)
#  File "/opt/users/hau/PyTroll/packages/satpy/satpy/scene.py", line 496, in read
#    return self.read_from_deptree(dataset_keys, **kwargs)
#  File "/opt/users/hau/PyTroll/packages/satpy/satpy/scene.py", line 491, in read_from_deptree
#    resolution=kwargs.get('resolution'))
#  File "/opt/users/hau/PyTroll/packages/satpy/satpy/scene.py", line 360, in create_deptree
#    resolution=resolution))
#  File "/opt/users/hau/PyTroll/packages/satpy/satpy/scene.py", line 325, in _find_dependencies
#    (str(dataset_key), str(err)))
