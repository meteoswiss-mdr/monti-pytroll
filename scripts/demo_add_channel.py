from __future__ import division
from __future__ import print_function

from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime
import numpy as np

# in this example we read parallax corrected data
# from an netCDF file, do some modifications to it.
# you could also use another data source,
# or another modification, e.g. Lagrangian movement.

# Afterwards, we create another geostationaryFactory object
# and demonstrate how to add an artificial channel

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
        timeslot = datetime.datetime(year, month, day, hour, minute)

print ("         ")    
print ('*** load data for time:', str(time_slot))

#global_data = GeostationaryFactory.create_scene("Meteosat-10", "", "seviri", time_slot)
global_data = GeostationaryFactory.create_scene("Meteosat-9", "", "seviri", time_slot)
#global_data = GeostationaryFactory.create_scene("Meteosat-8", "", "seviri", time_slot)

from my_composites import get_image
obj_image = get_image(global_data, 'HRoverview')
print ("... read following channels: ", obj_image.prerequisites)

# read parallax corrected data from netCDF
global_data.load(obj_image.prerequisites, reader_level="seviri-level9")
print ("         ")    
print ('*** some info about the loaded data')
print (global_data)

# data manipulation, we move by 100pixels to the East and 50 to the South
dx=50
dy=100
HRV    = np.roll(global_data['HRV'].data   , dx,axis=0)
HRV    = np.roll(HRV                       , dy,axis=1)
VIS006 = np.roll(global_data['VIS006'].data, dx,axis=0)
VIS006 = np.roll(VIS006                    , dy,axis=1)
VIS008 = np.roll(global_data['VIS008'].data, dx,axis=0)
VIS008 = np.roll(VIS008,                     dy,axis=1)
IR_108 = np.roll(global_data['IR_108'].data, dx,axis=0)
IR_108 = np.roll(IR_108,                     dy,axis=1)

# create another geostat object
data = GeostationaryFactory.create_scene("Meteosat-9", "", "seviri", time_slot)
from mpop.channel import Channel

# external definiton of the area
from mpop.projector import get_area_def
area = 'ccs4'
area_def = get_area_def(area)

print ("         ")    
print ('*** some info about the area definition')
print (area_def)
# print (area_def.proj_id)   # 'somerc'
# print (area_def.proj_dict) # {'ellps': 'bessel', 'k_0': '1', 'lat_0': '46.9524055555556', 'lon_0': '7.43958333333333', 'proj': 'somerc', 'x_0': '600000', 'y_0': '200000'}
# print (area_def.aex)       #      (255000.0, -21000.0, 965000.0, 330000.0)
# print (area_def.x_size)    # 710
# print (area_def.y_size)    # 640 -> this is changed later! 

create_subregion=False
if create_subregion:
    y1=150
    y2=500
    HRV    = HRV[y1:y2,:]
    VIS006 = VIS006[y1:y2,:]
    VIS008 = VIS008[y1:y2,:]
    IR_108 = IR_108[y1:y2,:]
    # print (HRV.shape) # (350, 710)

    # get_area_extent_for_subset(self, row_LR, col_LR, row_UL, col_UL):
    aex = area_def.get_area_extent_for_subset(y2,0,y1,area_def.x_size-1)

    from pyresample.geometry import AreaDefinition
    area = "on_the_fly"
    # redefine area_def (using still the original area_def on the right side)
    area_def = AreaDefinition(area, area, area_def.proj_id, area_def.proj_dict, area_def.x_size, y2-y1, aex)
    print ("         ")    
    print ('*** some info about the NEW area definition')
    print (area_def)
    
    
# defining a new channels named 'var', the wavenlegth range is not that critial (for radar data I usually use [0.,0.,0.])
data.channels.append(Channel(name='var', wavelength_range=[0.0,0.0,0.0], data=HRV ))
data['var'].area     = area
data['var'].area_def = area_def

# here we replace the already defined channels 
data['HRV'].data     = HRV
data['HRV'].area     = area
data['HRV'].area_def = area_def
data['VIS006'].data     = VIS006
data['VIS006'].area     = area
data['VIS006'].area_def = area_def
data['VIS008'].data     = VIS008
data['VIS008'].area     = area
data['VIS008'].area_def = area_def
data['IR_108'].data     = IR_108
data['IR_108'].area     = area
data['IR_108'].area_def = area_def

print ("         ")    
print ('*** some info about the manipulated data')
print (data)

print ("         ")    
print ('*** create the image')
img = data.image.hr_overview()

#if True:
#    img.show()
#else:
#    filename=time_slot.strftime('MSG_'+chn+'-'+area+'_%y%m%d%H%M.png')
#    img.save(filename)

PIL_image=img.pil_image()

add_map_overlay=True
if add_map_overlay:
    print ("         ")    
    print ('*** add the map overlap')
    from pycoast import ContourWriterAGG
    cw = ContourWriterAGG('/opt/users/common/shapes/')
    # define area
    proj4_string = area_def.proj4_string            
    # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
    area_extent = area_def.area_extent              
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
    print ("*** show image in x-Window ")
else:
    filename=time_slot.strftime('MSG_'+chn+'-'+area+'_%y%m%d%H%M_shifted.png')
    PIL_image.save(filename)
    print ("*** display "+filename)
