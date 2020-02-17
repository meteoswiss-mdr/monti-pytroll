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
sat="MSG2"

files_sat = find_files_and_readers(sensor='seviri',
                               #start_time=datetime(2015, 7, 7, 12, 0), end_time=datetime(2015, 7, 7, 12, 0),
                               #base_dir="/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/2015/07/07/",
                               start_time=datetime(2015, 8, 7, 12, 0), end_time=datetime(2015, 8, 7, 12, 0),
                               base_dir="/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/2015/08/07/",
                               reader='seviri_l1b_hrit')                                   
#                               reader='hrit_msg')

#print files_sat
#files = dict(files_sat.items() + files_nwc.items())
files = dict(list(files_sat.items()))

if sat=="MSG3":
    #remove MSG2 files
    for f in files['seviri_l1b_hrit']:
        if "MSG2" in f: files['seviri_l1b_hrit'].remove(f)
else:
    #remove MSG3 files
    for f in files['seviri_l1b_hrit']:
        if "MSG3" in f: files['seviri_l1b_hrit'].remove(f)

#global_scene = Scene(reader="hrit_msg", filenames=files)
global_scene = Scene(reader="seviri_l1b_hrit", filenames=files)

print("")
print("=======================")
print(dir(global_scene))
print("=======================")

global_scene.load([0.6])
print(global_scene[0.6])
print(global_scene[0.6].orbital_parameters)
print(global_scene[0.6].area)
print("=======================")
print("")

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
#area="ccs4"

print("")
print("=======================")
print("resample to "+area)
local_scene = global_scene.resample(area)

print("=======================")
print("")

print(global_scene.available_composite_names())

pngfile='./'+sat+'_overview_global.png'
global_scene.save_dataset('overview', pngfile)
print('display '+pngfile+' &')

#local_scene.show('overview')
pngfile='./'+sat+'_overview_'+area+'.png'
local_scene.save_dataset('overview', pngfile)
print('display '+pngfile+' &')

new=False
if new==False:
    local_scene["ndvi"] = (local_scene[0.8] - local_scene[0.6]) / (local_scene[0.8] + local_scene[0.6])
    #from satpy.enhancements import colorize
    #colorize(img, **kwargs)
    #'ylgn'
    #https://satpy.readthedocs.io/en/latest/writers.html
    #nice NDVI colourbar here:
    #https://www.researchgate.net/figure/NDVI-maps-Vegetation-maps-created-by-measuring-the-Normalized-Vegetation-Difference_fig7_323885082
else:
    from satpy.dataset import combine_attrs  # does not work!!!
    ndvi = (local_scene[0.8] - local_scene[0.6]) / (local_scene[0.8] + local_scene[0.6])
    ndvi.attrs = combine_attrs(local_scene[0.8], local_scene[0.6])
    local_scene['ndvi'] = ndvi

#local_scene.show('ndvi')

local_scene.save_dataset('ndvi', './ndvi_'+area+'.png')
print(dir(local_scene.save_dataset))
print('display ./ndvi_'+area+'.png &')



