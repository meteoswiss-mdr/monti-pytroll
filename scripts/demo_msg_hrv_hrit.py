from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime

## uncomment these two lines for more debugging information
from mpop.utils import debug_on
debug_on()

if False:
    from my_msg_module import get_last_SEVIRI_date
    time_slot = get_last_SEVIRI_date(True, delay=5)
else:
    import sys
    if len(sys.argv) <= 2:
        time_slot = datetime.datetime(2016, 9, 1, 12, 00)
    else:
        # python 
        year   = int(sys.argv[1])
        month  = int(sys.argv[2])
        day    = int(sys.argv[3])
        hour   = int(sys.argv[4])
        minute = int(sys.argv[5])
        timeslot = datetime.datetime(year, month, day, hour, minute)

print str(time_slot)

global_data = GeostationaryFactory.create_scene("Meteosat-10", "", "seviri", time_slot)
#global_data = GeostationaryFactory.create_scene("Meteosat-8", "", "seviri", time_slot)
#europe = get_area_def("EuropeCanaryS95")
global_data.load(['HRV'], reader_level="seviri-level2")  # , area_extent=europe.area_extent
print global_data

area="EuropeCanaryS95"
#area="ccs4"
data = global_data.project(area)

chn = 'HRV'

if True:
    from trollimage.colormap import rainbow
    colormap = rainbow
    min_data = data[chn].data.min()
    max_data = data[chn].data.max()
    colormap.set_range(min_data, max_data)
    from trollimage.image import Image as trollimage
    img = trollimage(data[chn].data, mode="L", fill_value=[0,0,0])
    img.colorize(colormap)
else:
    img = data.image.channel_image('HRV')

if True:
    img.show()
else:
    filename=time_slot.strftime('MSG_'+chn+'-'+area+'_%y%m%d%H%M.png')
    img.save(filename)
