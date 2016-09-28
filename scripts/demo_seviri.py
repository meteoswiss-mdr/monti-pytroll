from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime

from my_msg_module import get_last_SEVIRI_date

time_slot = get_last_SEVIRI_date(True)
from datetime import timedelta
time_slot -= timedelta(minutes=5) #?????
#time_slot = datetime.datetime(2015, 11, 26, 19, 30)
print str(time_slot)

global_data = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot)
europe = get_area_def("EuropeCanaryS95")
global_data.load([0.6, 0.8, 10.8])  # , area_extent=europe.area_extent
print global_data

area="EuropeCanaryS95"
data = global_data.project(area)

from trollimage.colormap import rainbow
colormap = rainbow
#chn = 'VIS006'
chn = 'IR_108'
min_data = data[chn].data.min()
max_data = data[chn].data.max()
colormap.set_range(min_data, max_data)
from trollimage.image import Image as trollimage
img = trollimage(data[chn].data, mode="L", fill_value=[0,0,0])
img.colorize(colormap)
img.show()
