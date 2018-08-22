from __future__ import division
from __future__ import print_function

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
        time_slot = datetime.datetime(2015, 7, 7, 12, 00)
    else:
        # python 
        year   = int(sys.argv[1])
        month  = int(sys.argv[2])
        day    = int(sys.argv[3])
        hour   = int(sys.argv[4])
        minute = int(sys.argv[5])
        time_slot = datetime.datetime(year, month, day, hour, minute)

print ("         ")    
print ('*** load data for time:', str(time_slot))

#global_data = GeostationaryFactory.create_scene("Meteosat-10", "", "seviri", time_slot)
global_data = GeostationaryFactory.create_scene("Meteosat-9", "", "seviri", time_slot)
#global_data = GeostationaryFactory.create_scene("Meteosat-8", "", "seviri", time_slot)
from my_composites import get_image
obj_image = get_image(global_data, 'HRoverview')
print (obj_image.prerequisites)

parallax_correction=True
if parallax_correction:
    global_data.load(obj_image.prerequisites, reader_level="seviri-level9")
else:
    global_data.load(obj_image.prerequisites, reader_level="seviri-level8")   
print ("         ")    
print ('*** some info about the loaded data')
print (global_data)

# data is already in ccs4 projection, so we can skip this step
area="ccs4"
#data = global_data.project(area, precompute=True)
data = global_data

print ("         ")    
print ('*** some info about the projection')
print (global_data['HRV'].area)
#print (dir(global_data['HRV'].area))
print (global_data['HRV'].area.name)
print ("x_size area (south to north!): ", global_data['HRV'].area.x_size)
print ("y_size area (west to east!):   ", global_data['HRV'].area.y_size)

print ("         ")    
print ('*** create the image')
img = data.image.hr_overview()

#if True:
#    img.show()
#else:
#    filename=time_slot.strftime('MSG_'+chn+'-'+area+'_%y%m%d%H%M.png')
#    img.save(filename)

PIL_image=img.pil_image()

if True:
    print ("         ")    
    print ('*** add the map overlap')
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

if False: #True:
    PIL_image.show()
    print ("*** show image in x-Window ")
else:
    filename=time_slot.strftime('MSG_'+area+'_%y%m%d%H%M.png')
    PIL_image.save(filename)
    print ("*** display "+filename)

