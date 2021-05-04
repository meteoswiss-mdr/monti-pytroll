from __future__ import print_function

from PIL import Image
from mpop.projector import Projector
from mpop.projector import get_area_def # python2 version
#from satpy.resample import get_area_def  # python3 version

#from mpop.utils import debug_on
import numpy as np
from pycoast import ContourWriterAGG

# Image.MAX_IMAGE_PIXELS = 500000000
#debug_on()

#Which projection do you need?
#=============================
area='ccs4'
#area='EuropeCanaryS'
#area='EuropeCanaryS95'
#area='SeviriDiskFull00'
#area='SeviriDiskFull95'
#area='nrEURO3km'

# specify input file
# ==================
#bkg_file = "/data/COALITION2/database/Land/blue_marble/world.topo.200408.3x21600x10800.png"
#area_bkg = get_area_def('world_plat_21600_10800')
#outfile = 'blue_marble_'+area+'.jpg'

# C2 tile (very high resolution) -> only to CCS4 possible
bkg_file = "/data/COALITION2/database/Land/blue_marble/high resolution tiles/world.topo.bathy.200408.3x21600x21600.C1.png"
area_bkg = get_area_def('world_plat_C1_21600_21600')
outfile = 'blue_marble_bathy_C1_'+area+'.png'

# C2 tile (very high resolution) -> only to CCS4 possible
#bkg_file = "/data/COALITION2/database/Land/blue_marble/BlackMarble_2012_C1.jpg"
#area_bkg = get_area_def('world_plat_C1_21600_21600')
#outfile = 'black_marble_C1_'+area+'.jpg'

#bkg_file = "/data/COALITION2/database/Land/blue_marble/BlackMarble_2016_3km_geo.13500x6750.tif"
#area_bkg = get_area_def('world_plat_13500_6750')
#outfile = 'black_marble_'+area+'.jpg'

#
#
#
#
#
#

area_target = get_area_def(area)

projector = Projector(area_bkg, area_target, mode = "nearest")

background = Image.open(bkg_file)

data = background.split()
r = projector.project_array(np.array(data[0]))
g = projector.project_array(np.array(data[1]))
b = projector.project_array(np.array(data[2]))
pil_r = Image.fromarray(r)
pil_g = Image.fromarray(g)
pil_b = Image.fromarray(b)
background = Image.merge("RGB", (pil_r, pil_g, pil_b))

background.save(outfile)
print("display "+outfile+" &")

cw = ContourWriterAGG('/data/OWARNA/hau/pytroll/shapes')
#cw.add_coastlines_to_file(outfile, area_target, resolution='i', level=3)
#cw.add_borders_to_file(outfile, area_target, outline="red", resolution='i',level=3)
