# Copyright (c) 2012
#
# code from
# http://nullege.com/codes/show/src@p@y@pytroll-HEAD@tools@coord2area_def.py
  
# Author(s):
#   Martin Raspaud <martin.raspaud@smhi.se>
  
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
  
"""
Convert human coordinates to an area definition.
  
Here is a usage example:

python coord2area_def_geos.py met09globeFull 0.0 -60  60 -60 60  3.003
(the arguments are "name lon_0 min_lat max_lat min_lon max_lon resolution(km)")
  
  
and the result is:
REGION: met09globeFull {
        NAME:   met09globeFull
        PCS_ID: geos_0.0_0.0
        PCS_DEF:        proj=geos, lon_0=0.0, a=6378169.00, b=6356583.80, h=35785831.0
        XSIZE:  1624
        YSIZE:  3204
        AREA_EXTENT:    (-2438833.400548724, -4811749.901981245, 2438833.400548724, 4811749.901981245)
};
  
"""
  

# import pyproj
# prj = pyproj.Proj('+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0 +units=m')
#prj(-24.155, 25.323)
##(-2286247.2851917786, 2619381.7495930935)
#prj([38.927],  [25.981])
## ([3411452.747249025], [2619322.000216889])
## AREA_EXTENT:    (-2297235.7282523895, 2619322.000216889, 3411452.747249025, 5322582.755436438)

# https://pyresample.readthedocs.org/en/latest/geo_def.html#areadefinition


import sys
from pyproj import Proj
  
if len(sys.argv) != 8:
    print "Usage: ", sys.argv[0], "name lon_0 min_lat max_lat min_lon max_lon resolution"
    exit(1)
  
name = sys.argv[1]
proj = 'geos'

lon_0 = float(sys.argv[2])

up    = float(sys.argv[3])
down  = float(sys.argv[4])
left  = float(sys.argv[5])
right = float(sys.argv[6])

res = float(sys.argv[7]) * 1000
 
lat_0 = 0.0
#lat_0 = (up + down) / 2
#lon_0 = (right + left) / 2
  
#p = Proj(proj=proj, lat_0=lat_0, lon_0=lon_0, ellps="WGS84")
p = Proj(proj="geos", lon_0=lon_0, a=6378169.0, b=6356583.8, h=35785831.0, lat_0=0)

left_ex1,  up_ex1   = p(left, up)    # 3, 1
right_ex1, up_ex2   = p(right, up)   # 4, 1
left_ex2,  down_ex1 = p(left, down)  # 3, 2 
right_ex2, down_ex2 = p(right, down) # 4, 2

area_extent = (min(left_ex1,  left_ex2),
               min(up_ex1,    up_ex2),
               max(right_ex1, right_ex2),
               max(down_ex1,  down_ex2))
  
xsize = int((area_extent[2] - area_extent[0]) / res)
ysize = int((area_extent[3] - area_extent[1]) / res)
  
print "REGION:", name, "{"
print "\tNAME:\t", name
print "\tPCS_ID:\t", proj + "_" + str(lon_0) + "_" + str(lat_0)
#print ("\tPCS_DEF:\tproj=" + proj + ",lat_0=" + str(lat_0) + ",lon_0=" + str(lon_0) + ",ellps=WGS84")
print ("\tPCS_DEF:\tproj=geos, lon_0=" + str(lon_0) + ", a=6378169.00, b=6356583.80, h=35785831.0")
print "\tXSIZE:\t", xsize
print "\tYSIZE:\t", ysize
print "\tAREA_EXTENT:\t", area_extent
print "};"
