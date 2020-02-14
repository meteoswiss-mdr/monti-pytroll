from __future__ import print_function

from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime

time_slot = datetime.datetime(2014, 07, 16, 13, 30)
global_data = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot)
europe = get_area_def("EuropeCanary")

# load data
global_data.load(["vaa"], reader_level="seviri-level6")



prop = global_data["vaa"].data
plot_type='trollimage'
min_data = prop.min()
max_data = prop.max()
print (prop.shape, min_data, max_data)

from trollimage.colormap import rainbow
colormap = rainbow
colormap.set_range(min_data, max_data)

from trollimage.image import Image as trollimage
img = trollimage(prop, mode="L", fill_value=None)
img.colorize(colormap)
img.save("test_vaa.png")
