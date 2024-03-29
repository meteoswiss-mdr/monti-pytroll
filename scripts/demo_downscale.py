from __future__ import print_function
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime

## uncomment these two lines for more debugging information
#from mpop.utils import debug_on
#debug_on()

from my_msg_module import get_last_SEVIRI_date
time_slot = get_last_SEVIRI_date(True, delay=5)
#time_slot = datetime.datetime(2015, 11, 26, 19, 30)
print (str(time_slot))

global_data = GeostationaryFactory.create_scene("Meteosat-9", "", "seviri", time_slot)
#europe = get_area_def("EuropeCanaryS95")
#global_data.load([0.6, 0.8, 10.8])  # , area_extent=europe.area_extent
global_data.load([10.8])  # , area_extent=europe.area_extent
print (global_data)

#area="EuropeCanaryS95"
area="ccs4"
data = global_data.project(area, precompute=True)

from trollimage.colormap import rainbow
colormap = rainbow
#chn = 'VIS006'
chn = 'IR_108'
from trollimage.image import Image as trollimage

min_data = data[chn].data.min()
max_data = data[chn].data.max()
colormap.set_range(min_data, max_data)

img = trollimage(data[chn].data, mode="L", fill_value=[0,0,0])
img.colorize(colormap)
img.show()

from plot_coalition2 import downscale_array

data[chn].data = downscale_array(data[chn].data, mode='gaussian_225_125', mask=data[chn].data.mask)
img2 = trollimage(data[chn].data, mode="L", fill_value=[0,0,0])
img2.colorize(colormap)
img2.show()

#img.save("tmp.png")
