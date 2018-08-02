from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime

## uncomment these two lines for more debugging information
#from mpop.utils import debug_on
#debug_on()

from my_msg_module import get_last_SEVIRI_date
time_slot = get_last_SEVIRI_date(False, delay=5)
#time_slot = datetime.datetime(2018, 3, 8, 17, 35)
print str(time_slot)

global_data = GeostationaryFactory.create_scene("Meteosat-11", "", "seviri", time_slot)
#europe = get_area_def("EuropeCanaryS95")
global_data.load([0.6, 0.8, 10.8])  # , area_extent=europe.area_extent
print global_data

area="EuropeCanaryS95"
#area="ccs4"
data = global_data.project(area, precompute=True)

from trollimage.colormap import rainbow
colormap = rainbow
#chn = 'VIS006'
chn = 'IR_108'
#print dir(data)
min_data = data[chn].data.min()
max_data = data[chn].data.max()
print " "
min_data=220
print "min_data, max_data: ", min_data, max_data
colormap.set_range(min_data, max_data)
from trollimage.image import Image as trollimage
img = trollimage(data[chn].data, mode="L", fill_value=[0,0,0])
img.colorize(colormap)
img.show()
#img.save("tmp.png")
