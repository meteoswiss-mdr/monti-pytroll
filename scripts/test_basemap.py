# https://pyresample.readthedocs.org/en/latest/plot.html#displaying-data-quickly

import numpy as np
import matplotlib.pyplot as plt
import pyresample as pr

lons = np.zeros(1000)
tb37v = np.arange(1000)
#lats = np.arange(-80, -90, -0.01)                                   # orginal example  -> shows north pole 
#area_def = pr.utils.load_area('../cfg_test/areas.def', 'ease_sh')   # orginal example  -> shows north pole 
lats = np.arange(80, 90, 0.01)                                       # ??? need to use positive lats for south pole ??? 
area_def = pr.utils.load_area('/data/OWARNA/hau/pytroll/cfg_test/areas.def', 'ease_nh')    # ??? need to use nh to show south pole ??? 

swath_def = pr.geometry.SwathDefinition(lons, lats)
result = pr.kd_tree.resample_nearest(swath_def, tb37v, area_def, radius_of_influence=20000, fill_value=None)

bmap = pr.plot.area_def2basemap(area_def)
bmng = bmap.bluemarble()
col = bmap.imshow(result, origin='upper') 

filename='test_basemap.png'
plt.savefig('./'+filename, bbox_inches='tight')
print "display "+filename+" &"
