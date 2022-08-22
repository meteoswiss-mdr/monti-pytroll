from __future__ import division
from __future__ import print_function

#from satpy.utils import debug_on
#debug_on()

from satpy import Scene, find_files_and_readers

files_sat = find_files_and_readers(base_dir="/data/COALITION2/database/Land/LandSeaMask/MODIS/",reader='landsea_nc')
print(files_sat)
global_scene = Scene(reader="landsea_nc", filenames=files_sat)
print("load the data")
global_scene.load(["lsmask"])

#area="eurol"
area="EuropeCanaryS95"
#area="ccs4"

#print(global_scene["lsmask"].attrs)

global_scene.save_dataset('lsmask', "lsmask.png", overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 255, 255), 'resolution': 'i'})

print("")
print("=======================")
print("resample to "+area)
local_scene = global_scene.resample(area)   #, datasets='lsmask'


print("")
print("=======================")
print("local_scene",local_scene)

print("plot the data")
import matplotlib.pyplot as plt
local_scene["lsmask"].plot()
plt.show()
