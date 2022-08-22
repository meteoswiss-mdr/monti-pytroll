# read Metop and MSG and collocate them 
#######################################

from satpy import Scene, find_files_and_readers
from datetime import datetime

metop_files = find_files_and_readers(base_dir='/tcenas/scratch/pytroll/ex6',
                                     reader='avhrr_l1b_eps',
                                     start_time=datetime(2018, 10, 7 ,9, 25),
                                     end_time=datetime(2018, 10, 7 ,9, 30))
scn_metop = Scene(filenames=metop_files)
scn_metop.load([10.8])
msg_files = find_files_and_readers(base_dir='/tcenas/scratch/pytroll/ex6',
                                   reader='seviri_l1b_native')

scn = Scene(filenames=msg_files)
scn_msg = Scene(filenames=msg_files)
scn_msg.load(['day_microphysics','IR_108'])
newscn_metop = scn_metop.resample('eurol')
newscn_metop.show(10.8)
newscn_msg = scn_msg.resample('eurol')
newscn_msg.show('IR_108')

# COMBINE LEO DATA WITH GEO DATA
##########################################

from satpy.writers import get_enhanced_image
import xarray as xr
from trollimage.xrimage import XRImage

# Lets compare MSG and METOP channel 10.8 data
msg_image = get_enhanced_image(newscn_msg['IR_108'])
metop_image = get_enhanced_image(newscn_metop[10.8])

array1 = msg_image.data.where(metop_image.data.isnull(), metop_image.data)
img=XRImage(array1)
img.show()

# Now Using MSG composite
msg_image = get_enhanced_image(newscn_msg['day_microphysics'])
color_array = xr.concat((metop_image.data, metop_image.data, metop_image.data), 'bands')
color_array['bands'] = ['R', 'G', 'B']
final_array = msg_image.data.where(color_array.isnull(), color_array.data)
img=XRImage(final_array)
img.show()

# using MultiScenes
###########################################

from satpy import MultiScene
mscn = MultiScene([scn_msg, scn_metop])
mscn.load(['overview'])
new_mscn = mscn.resample('eurol')
blended_scene = new_mscn.blend()
blended_scene.show('overview', overlay={'coast_dir': '/tcenas/scratch/pytroll/shapes/', 'color': (255, 0, 0), 'resolution': 'i'})

