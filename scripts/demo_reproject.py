from PIL import Image
#from pyresample.utils import load_area
from pyresample import load_area
import numpy as np
import pkg_resources
pkg_resources.require("scipy==0.19.0")
import scipy.misc
import os, pyresample
from pyresample import image, geometry
from mpop import CONFIG_PATH

path = os.path.dirname(pyresample.__file__)
print(path)


#REGION: regionB {
#        NAME:          regionB
#        PCS_ID:        regionB
#        PCS_DEF:       proj=merc, lon_0=-34, k=1, x_0=0, y_0=0, a=6378137, b=6378137
#        XSIZE:         800
#        YSIZE:         548
#        ROTATION:      -45
#        AREA_EXTENT:   (-7761424.714818418, -4861746.639279127, 11136477.43264252, 8236799.845095873)
#};

#REGION: world_plat_5400_2700 {
#        NAME:           world_plat_5400_2700
#        PCS_ID:         world_plat_5400_2700
#        PCS_DEF:        proj=eqc,ellps=WGS84
#        XSIZE:          5400
#        YSIZE:          2700
#        AREA_EXTENT:    (-20037508.342789244, -10018754.171394622, 20037508.342789244, 10018754.171394622)
#};



bkg_file = "world.topo.small.png"
outfile = 'regionB.jpg'
background = Image.open(bkg_file)
#area_bkg = load_area('/opt/users/cll/PyTroll/etc/areas.def', 'world_plat_5400_2700')
#area_target = load_area('/opt/users/cll/PyTroll/etc/areas.def', 'regionB')
area_bkg = load_area('/opt/users/cll/official/PyTroll/bluemarble-pyresample/areas.yaml', 'world_plat_5400_2700')
area_target = load_area(os.path.join(CONFIG_PATH, "areas.def"), 'EuropeCanaryS95')

data = background.split()
data = np.dstack((np.array(data[0]), np.array(data[1]), np.array(data[2])))
nn = image.ImageContainerNearest(data, area_bkg, radius_of_influence=50000)
area_con_quick = nn.resample(area_target)
scipy.misc.imsave(outfile,area_con_quick.image_data)
