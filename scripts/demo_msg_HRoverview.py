from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime

## uncomment these two lines for more debugging information
from mpop.utils import debug_on
debug_on()

if False:
    from my_msg_module import get_last_SEVIRI_date
    time_slot = get_last_SEVIRI_date(True, delay=10)
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
from my_composites import get_image
obj_image = get_image(global_data, 'HRoverview')
global_data.load(obj_image.prerequisites, reader_level="seviri-level9")
print global_data

#area="EuropeCanaryS95"
area="ccs4"
data = global_data.project(area, precompute=True)

img = data.image.hr_overview()

#if True:
#    img.show()
#else:
#    filename=time_slot.strftime('MSG_'+chn+'-'+area+'_%y%m%d%H%M.png')
#    img.save(filename)

PIL_image=img.pil_image()

if True:
    from pycoast import ContourWriterAGG
    cw = ContourWriterAGG('/opt/users/common/shapes/')
    from mpop.projector import get_area_def
    obj_area = get_area_def(area)
    # define area
    proj4_string = obj_area.proj4_string            
    # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
    area_extent = obj_area.area_extent              
    # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
    area_tuple = (proj4_string, area_extent)
    from plot_msg import add_borders_and_rivers
    ## possible resolutions                                          
    ## f  full resolution: Original (full) data resolution.          
    ## h  high resolution: About 80 % reduction in size and quality. 
    ## i  intermediate resolution: Another ~80 % reduction.          
    ## l  low resolution: Another ~80 % reduction.                   
    ## c  crude resolution: Another ~80 % reduction.  
    add_borders_and_rivers(PIL_image, cw, area_tuple,
                           add_borders=True, border_color='red',
                           add_rivers=False, river_color='blue', 
                           resolution='i', verbose=False)

if True:
    PIL_image.show()
else:
    filename=time_slot.strftime('MSG_'+chn+'-'+area+'_%y%m%d%H%M.png')
    PIL_image.save(filename)

