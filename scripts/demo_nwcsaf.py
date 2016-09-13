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

global_data.load(["CTTH"])  # , area_extent=europe.area_extent
print global_data

# project data to anther projection defined in etc/area.def
area="ccs4"
#area = get_area_def("euro")
data = global_data.project(area)

from trollimage.colormap import rainbow
colormap = rainbow

min_data = data["CTTH"].height.data.min()
max_data = data["CTTH"].height.data.max()
colormap.set_range(min_data, max_data)
from trollimage.image import Image as trollimage
img = trollimage(data["CTTH"].height.data, mode="L", fill_value=[0,0,0])
img.colorize(colormap)
#img.show()
img.save("nwcsaf_demo.png")
