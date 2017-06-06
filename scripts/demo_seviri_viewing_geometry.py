from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime

## uncomment these two lines for more debugging information
#from mpop.utils import debug_on
#debug_on()

from my_msg_module import get_last_SEVIRI_date
time_slot = get_last_SEVIRI_date(True, delay=5)
#time_slot = datetime.datetime(2015, 11, 26, 19, 30)
print str(time_slot)

global_data = GeostationaryFactory.create_scene("Meteosat-9", "", "seviri", time_slot)
europe = get_area_def("EuropeCanaryS95")
global_data.load(['vza','vaa','lat','lon'])  # , area_extent=europe.area_extent
print global_data

area="EuropeCanaryS95"
data = global_data.project(area)

from trollimage.colormap import rainbow
colormap = rainbow
#chn = 'vaa'
chn = 'vza'
min_data = data[chn].data.min()
max_data = data[chn].data.max()
colormap.set_range(min_data, max_data)
from trollimage.image import Image as trollimage
img = trollimage(data[chn].data, mode="L", fill_value=[0,0,0])
img.colorize(colormap)
img.show()
