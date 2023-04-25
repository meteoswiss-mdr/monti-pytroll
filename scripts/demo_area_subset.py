from __future__ import division
from __future__ import print_function

#from pyresample import utils

#area_id = 'ease_sh'
#area_name = 'Antarctic EASE grid'
#proj_id = 'ease_sh'
#proj4_args = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
#x_size = 425
#y_size = 425
#area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
#area_def = utils.get_area_def(area_id, area_name, proj_id, proj4_args,
#                                      x_size, y_size, area_extent)

# old mpop verion
## from mpop.projector import get_area_def
##area_def = get_area_def("SeviriDiskFull")
#area_def = get_area_def("SeviriDiskFull00")

# new version
from pyresample import load_area
get_area_def = load_area 
area_def = load_area("/opt/users/hau/monti-pytroll/etc/areas.def", "SeviriDiskFull00")

import numpy as np

print("dir(area_def)", dir(area_def))
#dir(area_def) ['__class__', '__contains__', '__delattr__', '__dict__', '__doc__', '__eq__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'area_extent', 'area_extent_ll', 'area_id', 'cartesian_coords', 'corners', 'dtype', 'get_area', 'get_boundary_lonlats', 'get_cartesian_coords', 'get_lonlat', 'get_lonlats', 'get_proj_coords', 'get_xy_from_lonlat', 'intersection', 'lats', 'lons', 'name', 'ndim', 'nprocs', 'overlap_rate', 'overlaps', 'pixel_offset_x', 'pixel_offset_y', 'pixel_size_x', 'pixel_size_y', 'pixel_upper_left', 'proj4_string', 'proj_dict', 'proj_id', 'proj_x_coords', 'proj_y_coords', 'projection_x_coords', 'projection_y_coords', 'shape', 'size', 'x_size', 'y_size']

print("area_def.area_id         ", area_def.area_id)              #SeviriDiskFull                                                                             
print("area_def.proj_id         ", area_def.proj_id)              #geos0                                                                                      
print("area_def.proj_dict       ", area_def.proj_dict)            #{'a': '6378169.00', 'h': '35785831.0', 'lon_0': '0.0', 'b': '6356583.80', 'proj': 'geos'}  
                                                                                                                                                            
print("area_def.area_extent     ", area_def.area_extent)          #(-5570248.477339261, -5567248.074173444, 5567248.074173444, 5570248.477339261)             
print("area_def.shape           ", area_def.shape)                #(3712, 3712)                                                                               
print("area_def.x_size          ", area_def.x_size)               #3712                                                                                       
print("area_def.y_size          ", area_def.y_size)               #3712                                                                                       
print("area_def.pixel_size_x    ", area_def.pixel_size_x)         #3000.40316582                                                                              
print("area_def.pixel_size_y    ", area_def.pixel_size_y)         #3000.40316582                                                                              
print("area_def.pixel_offset_x  ", area_def.pixel_offset_x)       #1856.5                                                                                     
print("area_def.pixel_offset_y  ", area_def.pixel_offset_y)       #1856.5                                                                                     
print("area_def.pixel_upper_left", area_def.pixel_upper_left)     #(-5568748.275756353, 5568748.275756353)                                                    
print("area_def.area_extent_ll  ", area_def.area_extent_ll)       #(1e+30, 1e+30, 1e+30, 1e+30)                                                               
                                                                    
             
print("area_def.get_proj_coords()",area_def.get_proj_coords())  # (array([[-5568748.27575635, -5565747.87259054, -5562747.46942472, ...,    works only with mpop (cache=True)
print("area_def.projection_x_coords", area_def.projection_x_coords)       # [[-5568748.27575635 -5565747.87259054 -5562747.46942472 ..., 
print("area_def.projection_y_coords", area_def.projection_y_coords)       # [[ 5568748.27575635  5568748.27575635  5568748.27575635 ...,
              
#print "area_def.get_lonlats()    ",area_def.get_lonlats(cache=True)    
#print "area_def.lats             ", area_def.lats                                        
#print "area_def.lons             ", area_def.lons                                        

print("area_def.get_xy_from_lonlat(42, 1.2) ", area_def.get_xy_from_lonlat(42, 1.2))   # (3210, 1814)
print("area_def.get_lonlat(3210,1814)       ", area_def.get_lonlat(3210,1814))  # (array(-1.598585517586475), array(-42.282596990951376))

print("area_def.get_proj_coords(data_slice=(0,0))", np.array(area_def.get_proj_coords(data_slice=(0,0))))   # +0.5*area_def.pixel_size_x
print("area_def.get_proj_coords(data_slice=(1,1))",area_def.get_proj_coords(data_slice=(1,1)))              # (-5565747.8725905353,  5565747.8725905353)
print("area_def.get_proj_coords(data_slice=(3711,3711))",area_def.get_proj_coords(data_slice=(3711,3711)))  # ( 5565747.8725905353, -5565747.8725905353)


#REGION: SeviriDiskFull {
#        NAME:          Full globe MSG image 0 degrees
#        PCS_ID:        geos0
#        PCS_DEF:       proj=geos, lon_0=0.0, a=6378169.00, b=6356583.80, h=35785831.0
#        #PCS_DEF:       proj=geos, lon_0=0.0, a=6378144.0, b=6356759.0, h=35785831.0, rf=295.49
#        XSIZE:         3712
#        YSIZE:         3712
#        AREA_EXTENT:   (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
#};      #    area_extent: (x_ll,                y_ll,                 x_ur,               y_ur)
#area_def.get_proj_coords(data_slice=(   0,   0)) 
#                         (-5568748.2757563526,                                      5568748.2757563526)     <- right lower
#                              -x/2 = x_ll                                               +y/2=y_ur           <- right lower
#area_def.get_proj_coords(data_slice=(3711,3711))               
#                                             ( 5565747.8725905353, -5565747.8725905353)   
#                                                  +x/2 = x_ur    <->   -y/2=y_ll

# np.array(area_def.get_proj_coords(data_slice=(3711,      0))) -  3000.40316582/2.                      # lower left 
#                 array([-5570248.47733926, -5567248.07417344])                                          # lower left 
# np.array(area_def.get_proj_coords(data_slice=(   0,   3711))) +  3000.40316582/2.                      # upper right 
#                                                         array([ 5567248.07417344,  5570248.47733926])  # upper right

#np.array(area_def.get_proj_coords(data_slice=(2617,  2727))) -  3000.40316582/2.
#         array([ 2611850.9558437 , -2284807.01076965])
#>>> np.array(area_def.get_proj_coords(data_slice=( 717, 3627))) +  3000.40316582/2.
#                                              array([ 5315214.20824482,  3418959.40744847])
#AREA_EXTENT:    (-2284807.01076965, 2611850.9558437,  3418959.40744847,  5315214.20824482)


# in get_area_extent_for_subset in pyresample/pyresample/geometry.py
# e.g. used in
# mpop/mpop/satin/hsaf_h03.py:        # aex = full_disk.get_area_extent_for_subsets(985,1095,85,2995)
# mpop/mpop/satin/msg_seviri_hdf.py:  aex = full_disk_def.get_area_extent_for_subset(3712-VIS_IRSouthLine,3712-VIS_IRWestColumn,3712-VIS_IRNorthLine,3712-VIS_IREastColumn)
# def get_area_extent_for_subset(self, row_LR, col_LR, row_UL, col_UL):
print(area_def.get_area_extent_for_subset(985,1095,85,2995))  # (-2284807.0107696461, 2611850.9558436987, 3418959.4074484715, 5315214.2082448164)


#proj_x_range = area_def.proj_x_coord
#print proj_x_range
#print type(proj_x_range)

#print type(area_def.cartesian_coords)
#cartesian_coords = area_def.get_cartesian_coords(cache=True)
#print type(cartesian_coords)
#print dir(cartesian_coords)
#print cartesian_coords.shape
#cart_subset = area_def.cartesian_coords[100:200, 350:]
#print cart_subset

