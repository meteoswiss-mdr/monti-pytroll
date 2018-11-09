
# old version of satpy before 0.8 
#from satpy import Scene
#from satpy.utils import debug_on
#debug_on()

#from glob import glob
#base_dir="/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/2015/07/07/"
#import os
#os.chdir(base_dir)
#filenames = glob("*201507071200*__")
#print base_dir
#print filenames
##global_scene = Scene(reader="hrit_msg", filenames=filenames, base_dir=base_dir, ppp_config_dir="/opt/users/hau/PyTroll//cfg_offline/")
#global_scene = Scene(reader="hrit_msg", filenames=filenames, base_dir=base_dir, ppp_config_dir="/opt/users/hau/PyTroll/packages/satpy/satpy/etc")


# new version of satpy after 0.8
#################################
from satpy import Scene, find_files_and_readers
from datetime import datetime
#files = find_files_and_readers(sensor='olci',  
#                               start_time=datetime(2017, 10, 11, 12, 0),  
#                               end_time=datetime(2017, 10, 11, 12, 59),  
#                               base_dir="/home/a001673/data/satellite/Sentinel-3",  
#                               reader='nc_olci_l1b')  
#scn = Scene(filenames=files)"  

#def find_files_and_readers(start_time=None, end_time=None, base_dir=None,
#                           reader=None, sensor=None, ppp_config_dir=get_environ_config_dir(),
#                           filter_parameters=None, reader_kwargs=None):


files_sat = find_files_and_readers(sensor='seviri',  
                               start_time=datetime(2015, 7, 7, 12, 0),  
                               end_time=datetime(2015, 7, 7, 12, 15),  
                               base_dir="/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/2015/07/07/",  
                               reader='hrit_msg')


files_new = find_files_and_readers(sensor='seviri',
                               start_time=datetime(2015, 7, 7, 12, 0),
                               end_time=datetime(2015, 7, 7, 12, 15),
                               base_dir="/data/COALITION2/database/meteosat/SAFNWC_v2013/2015/07/07/",
                               reader='hrit_msg')


#print files
global_scene = Scene(filenames=files)

#global_scene.load([0.6, 0.8, 10.8])
#global_scene.load(['IR_120', 'IR_134'])
global_scene.load(['overview',0.6,0.8])

global_scene.available_dataset_names()
#print(global_scene[0.6])            # works only if you load also the 0.6 channel, but not an RGB that contains the 0.6
#!!# print(global_scene['overview']) ### this one does only work in the develop version


global_scene["ndvi"] = (global_scene[0.8] - global_scene[0.6]) / (global_scene[0.8] + global_scene[0.6])

#from satpy import DatasetID
#my_channel_id = DatasetID(name='IR_016', calibration='radiance')
#global_scene.load([my_channel_id])
#print(scn['IR_016'])

#local_scene = global_scene.resample("eurol")
local_scene = global_scene.resample("EuropeCanaryS95")

print global_scene.available_composite_names()

#local_scene.show('overview')
local_scene.save_dataset('overview', './local_overview.png')
local_scene.save_dataset('ndvi', './local_ndvi.png')


