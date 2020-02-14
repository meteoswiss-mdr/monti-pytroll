from __future__ import division
from __future__ import print_function


#from satpy import Scene
from satpy.utils import debug_on
debug_on()

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

files_sat = find_files_and_readers(sensor='seviri',
                               start_time=datetime(2015, 7, 7, 12, 0),
                               end_time=datetime(2015, 7, 7, 12, 0),
                               base_dir="/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/2015/07/07/",
                               reader='hrit_msg')

#print files_sat
#files = dict(files_sat.items() + files_nwc.items())
files = dict(list(files_sat.items()))

global_scene = Scene(reader="hrit_msg", filenames=files)

print(dir(global_scene))

#global_scene.load([0.6, 0.8, 10.8])
#global_scene.load(['IR_120', 'IR_134'])
global_scene.load(['overview',0.6,0.8])
#print(global_scene[0.6])            # works only if you load also the 0.6 channel, but not an RGB that contains the 0.6
#!!# print(global_scene['overview']) ### this one does only work in the develop version

global_scene.available_dataset_names()

global_scene["ndvi"] = (global_scene[0.8] - global_scene[0.6]) / (global_scene[0.8] + global_scene[0.6])
# !!! BUG: will not be resampled in global_scene.resample(area)

#from satpy import DatasetID
#my_channel_id = DatasetID(name='IR_016', calibration='radiance')
#global_scene.load([my_channel_id])
#print(scn['IR_016'])

#area="eurol"
area="EuropeCanaryS95"
local_scene = global_scene.resample(area)

print(global_scene.available_composite_names())

#local_scene.show('overview')
local_scene.save_dataset('overview', './overview_'+area+'.png')
print('display ./overview_'+area+'.png &')

local_scene["ndvi"] = (local_scene[0.8] - local_scene[0.6]) / (local_scene[0.8] + local_scene[0.6])
local_scene.save_dataset('ndvi', './ndvi_'+area+'.png')
print(dir(local_scene.save_dataset))
#from satpy.enhancements import colorize
#colorize(img, **kwargs)
#'ylgn'
#https://satpy.readthedocs.io/en/latest/writers.html
#nice NDVI colourbar here:
#https://www.researchgate.net/figure/NDVI-maps-Vegetation-maps-created-by-measuring-the-Normalized-Vegetation-Difference_fig7_323885082

print('display ./ndvi_'+area+'.png &')



