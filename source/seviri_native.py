from __future__ import print_function
from satpy.utils import debug_on
debug_on()
from satpy import Scene

#area="ccs4"
area="EuropeCanaryS95"
#area="SeviriDisk00"

#### https://satpy.readthedocs.io/en/latest/quickstart.html
testfile="MSG3-SEVI-MSG15-0100-NA-20170326102740.340000000Z-20170326102757-1213498.nat"
data_dir = "/data/COALITION2/database/meteosat/radiance_nat/native_test/"
    
filenames=[data_dir+testfile]

global_scene = Scene(sensor="seviri", reader="native_msg", filenames=[data_dir+testfile])

print (global_scene.available_dataset_names())
#['HRV', 'IR_016', 'IR_039', 'IR_087', 'IR_097', 'IR_108', 'IR_120', 'IR_134', 'VIS006', 'VIS008', 'WV_062', 'WV_073']
#global_scene.load([0.6, 0.8, 10.8])
#global_scene.load(["VIS006", "VIS008", "IR_108"])

available_composite_names = global_scene.available_composite_names()
print (available_composite_names)
available_composite_names = ['airmass', 'ash', 'cloudtop', 'convection', 'day_microphysics', 'day_microphysics_winter', 'dust', 'fog', 'green_snow', 'ir108_3d', 'ir_cloud_day', 'ir_overview', 'natural', 'natural_color', 'natural_color_sun', 'natural_sun', 'night_fog', 'night_microphysics', 'overview', 'overview_sun', 'snow']
global_scene.load(available_composite_names)
local_scene = global_scene.resample(area)

for composite in available_composite_names:

    print ("================================")
    print (composite)
    if composite=="airmass_corr" or composite=="cloudtop_daytime" or composite=="realistic_colors":
        continue
    print ("================================")
    local_scene.save_dataset(composite, data_dir+'/'+composite+'_'+area+'.png')

