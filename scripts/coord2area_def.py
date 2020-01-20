from __future__ import division
from __future__ import print_function

# Copyright (c) 2012
#

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

import sys
from pyproj import Proj

if len(sys.argv) != 7:
    print("Usage: ", sys.argv[0], "name proj min_lat max_lat min_lon max_lon")
    exit(1)
    
name = sys.argv[1]
proj = sys.argv[2]

up = float(sys.argv[3])     # !!! lat_min
down = float(sys.argv[4])   # !!! lat_max
left = float(sys.argv[5])
right = float(sys.argv[6])

lat_0 = 0 # (up + down) / 2
lon_0 = (right + left) / 2

#p = Proj(proj="stere", lat_0=lat_0, lon_0=lon_0, ellps="WGS84")
#p = Proj(proj="geos", lon_0=10.0, a=6378169.00, b=6356583.80, h=35785831.0)
p = Proj(proj="geos", lon_0=9.5, a=6378169.00, b=6356583.80, h=35785831.0)
#p = Proj(proj="geos", lon_0=0.0, a=6378169.00, b=6356583.80, h=35785831.0)

left_ex1, up_ex1    = p(left, up)   # 3, 1
right_ex1, up_ex2   = p(right, up)  # 4, 1
left_ex2, down_ex1  = p(left, down)
right_ex2, down_ex2 = p(right, down)

area_extent = (min(left_ex1, left_ex2),
               min(up_ex1, up_ex2),
               max(right_ex1, right_ex2),
               max(down_ex1, down_ex2))

print("REGION:", name, "{")
print("\tNAME:\t", name)
print("\tPCS_ID:\t", proj + "_" + str(lon_0) + "_" + str(lat_0))
print(("\tPCS_DEF:\tproj=" + proj +
       ",lat_0=" + str(lat_0) +
       ",lon_0=" + str(lon_0) +
       ",ellps=WGS84"))
print("\tXSIZE:\t")
print("\tYSIZE:\t")
print("\tAREA_EXTENT:\t", area_extent)
print("};")


