from __future__ import print_function
#import os
#os.chdir("/data/cinesat/in/eumetcast1/")
#from satpy import Scene
#from satpy.scene import Scene
from datetime import datetime
from my_msg_module import get_last_SEVIRI_date
import os

RSS=False

from satpy.utils import debug_on
debug_on()

#### https://satpy.readthedocs.io/en/latest/quickstart.html
#### https://satpy.readthedocs.io/en/latest/quickstart.html


#time_slot = datetime(lastdate.year, lastdate.month, lastdate.day, lastdate.hour, lastdate.minute)
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=datetime(2015, 4, 20, 10, 0))
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=datetime(2015, 4, 20, 10, 0), base_dir="/home/a001673/data/satellite/Meteosat-10/seviri/lvl1.5/2015/04/20/HRIT") 
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=lastdate, base_dir="/data/cinesat/in/eumetcast1")
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=lastdate, reader="hrit_msg", basedir="/data/cinesat/in/eumetcast1/")  
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=datetime(2017, 1, 27, 13, 45))
#print ("hallo world", dir(global_scene), global_scene.info)
#print (global_scene.available_composites())
print (global_scene.available_dataset_names())
print (global_scene.available_composite_names())

from satpy import Scene

#my_dir="/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/singletime/"
#from datetime import datetime
#time_slot = datetime(2017, 3, 29, 10, 15)

#lastdate = get_last_SEVIRI_date(RSS, delay=10)
#my_dir="/data/cinesat/in/eumetcast1/"
#reader="hrit_msg"

#global_scene = Scene(platform_name="Meteosat-9", sensor="seviri", reader="hrit_msg", start_time=lastdate)

import socket
hostname=socket.gethostname()

reader="native_msg"
test_data=True
test_data=False
import datetime
time_start = datetime.datetime(2015, 05, 29, 12, 00, 0)
time_end = time_start + datetime.timedelta(minutes=12)

#testfile="MSG3-SEVI-MSG15-0100-NA-20170326101240.438000000Z-20170326101257-1213498.nat"
testfile="MSG3-SEVI-MSG15-0100-NA-20170326102740.340000000Z-20170326102757-1213498.nat"
#testfile="MSG2-SEVI-MSG15-0100-NA-20150531235918.139000000Z-20150531235936-1178986.nat"   # does not work, as number of column cant be devided by 4 

if "zueub" in hostname:
    data_dir = "/data/COALITION2/database/meteosat/radiance_nat/native_test/"
elif "kesch" in hostname:
    if test_data:
        data_dir = "/scratch/hamann/"
    else: 
        archive_dir = time_end.strftime("/store/mch/msclim/cmsaf/msg/native-fulldisk/%Y/%m/%d/")  # replace %Y%m%d%H%M
        # search file
        import glob
        bz2files = glob.glob(archive_dir + time_end.strftime('/MSG[1-4]-SEVI-MSG15-0100-NA-%Y%m%d%H%M??.*.nat.bz2'))
        print("...copy file from archive: "+bz2files[0])
        from subprocess import call
        data_dir="/scratch/hamann/"
        call(["cp", bz2files[0], data_dir])
        os.chdir(data_dir)
        print("...bunzip2 file: "+bz2files[0])
        bz2file=os.path.basename(bz2files[0])
        call(["bunzip2","/scratch/hamann/"+bz2file])
        testfile=bz2file[:-4]
else:
    raise ValueError("Unknown computer"+hostname+": no example file is provided")

filenames=[data_dir+testfile]

print(filenames)

#global_scene = Scene(platform_name="Meteosat-9", sensor="seviri", reader=reader, filenames=filenames)
global_scene = Scene(sensor="seviri", reader=reader, filenames=filenames)

#global_scene.load([0.6, 0.8, 10.8])
global_scene.load(['overview'])
#global_scene.load(["VIS006", "VIS008", "IR_108"])
global_scene.save_dataset('overview', data_dir+'/overview_global.png')

area="ccs4"
#area="SeviriDisk00"
local_scene = global_scene.resample("ccs4")
local_scene.save_dataset('overview', data_dir+'/overview_'+area+'.png')


#print (global_scene)
#print (global_scene[0.6])

#local_scene = global_scene.project("ccs4", precompute=True)

# print (global_scene.available_datasets())  ## does not work

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
