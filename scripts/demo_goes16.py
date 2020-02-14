from __future__ import print_function

from satpy import Scene
from glob import glob
import socket

if 'zueub' in socket.gethostname():
    #MeteoSwiss
    filenames = glob("/data/COALITION2/database/goes-16/2017/04/05/*s20170952100319_e20170952100377*")
else:
    #kesch/CSCS
    filenames = glob("/store/msrad/sat/goes-16/2017/04/05/*s20170952100319_e20170952100377*")

print (filenames)

global_scene = Scene(reader="abi_l1b", filenames=filenames)
print (global_scene.available_composite_names())

#['airmass', 'ash', 'dust', 'fog', 'green', 'green_crefl', 'green_raw', 'green_snow', 'ir108_3d', 'ir_cloud_day', 'natural', 'natural_color', 'natural_color_raw', 'natural_color_sun', 'natural_sun', 'night_microphysics', 'overview', 'overview_raw', 'true_color', 'true_color_crefl', 'true_color_raw']

# the following does not work ???
##################################

#rgb='true_color' # needs /u/37482654/rayleigh_only/rayleigh_luts_rayleigh_only.tgz which fails to download automatically
#rgb='overview' # does not exist
rgb='airmass'
### rgb='VIS006' ... unknown dataset ...
global_scene.load([rgb])
global_scene[rgb].show()
local_scene = global_scene.resample("eurol")
local_scene.show(rgb)
