
#from satpy.utils import debug_on
#debug_on()


# new version of satpy after 0.8
#################################
from satpy import Scene, find_files_and_readers
from datetime import datetime

#def find_files_and_readers(start_time=None, end_time=None, base_dir=None,
#                           reader=None, sensor=None, ppp_config_dir=get_environ_config_dir(),
#                           filter_parameters=None, reader_kwargs=None):

files = find_files_and_readers(sensor='radar',  
                               start_time=datetime(2018, 4, 27, 12, 0),  
                               end_time=datetime(2018, 4, 27, 12, 15),  
                               base_dir="/data/COALITION2/database/radar/odyssey/2018/04/27",  
                               reader='h5_odyssey')


#print files
global_scene = Scene(filenames=files)

global_scene.load(['rr'])

global_scene.available_dataset_names()
#print(global_scene[0.6])            # works only if you load also the 0.6 channel, but not an RGB that contains the 0.6
#!!# print(global_scene['overview']) ### this one does only work in the develop version

#from satpy import DatasetID
#my_channel_id = DatasetID(name='IR_016', calibration='radiance')
#global_scene.load([my_channel_id])
#print(scn['IR_016'])

#local_scene = global_scene.resample("eurol")
local_scene = global_scene.resample("EuropeCanaryS95")

#print global_scene.available_composite_names()

local_scene.show('rr')
local_scene.save_dataset('rr', './local_rainrate.png')

