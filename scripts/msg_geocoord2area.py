from __future__ import division
from __future__ import print_function

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
  

def msg_geocoord2area(LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, HRVis, SUB_LON_DEG, xsize=-999, ysize=-999):

    from msg_geocoord2pixcoord import msg_geocoord2pixcoord
    from pyresample.geometry import AreaDefinition
    from pyproj import Proj
  
    area_name ="area_"+'{:+06.1f}'.format(LON_MIN)+"_"+'{:+06.1f}'.format(LON_MAX)+"_"+'{:+06.1f}'.format(LAT_MIN)+"_"+'{:+06.1f}'.format(LAT_MAX)

    lon_0 = SUB_LON_DEG

    p = Proj(proj="geos", a=6378169.0, b=6356583.8, h=35785831.0, lon_0=lon_0, lat_0=0)
    proj = {'proj':'geos', 'a':'6378169.0', 'b':'6356583.8', 'h':'35785831.0', 'lon_0':str(lon_0)}  # , ellps=WGS84"

    left_ex1,  up_ex1   = p(LON_MIN, LAT_MIN)
    right_ex1, up_ex2   = p(LON_MAX, LAT_MIN)
    left_ex2,  down_ex1 = p(LON_MIN, LAT_MAX)
    right_ex2, down_ex2 = p(LON_MAX, LAT_MAX)

    area_extent = (min(left_ex1,  left_ex2, right_ex1, right_ex2 ),
                   min(down_ex1,  down_ex2, up_ex1,    up_ex2    ),
                   max(left_ex1,  left_ex2, right_ex1, right_ex2 ),
                   max(down_ex1,  down_ex2, up_ex1,    up_ex2    ))
  
    #COLUMN1, LINE1 = msg_geocoord2pixcoord(LON_MIN, LAT_MIN, HRVis, SUB_LON_DEG)
    #COLUMN2, LINE2 = msg_geocoord2pixcoord(LON_MAX, LAT_MIN, HRVis, SUB_LON_DEG)
    #COLUMN3, LINE3 = msg_geocoord2pixcoord(LON_MIN, LAT_MAX, HRVis, SUB_LON_DEG)
    #COLUMN4, LINE4 = msg_geocoord2pixcoord(LON_MAX, LAT_MAX, HRVis, SUB_LON_DEG)

    #print "msg_geocoord2area: LON_MIN, LAT_MIN // COLUMN1, LINE1 = ", COLUMN1, LINE1
    #print "msg_geocoord2area: LON_MAX, LAT_MIN // COLUMN2, LINE2 = ", COLUMN2, LINE2
    #print "msg_geocoord2area: LON_MIN, LAT_MAX // COLUMN3, LINE3 = ", COLUMN3, LINE3
    #print "msg_geocoord2area: LON_MAX, LAT_MAX // COLUMN4, LINE4 = ", COLUMN4, LINE4


    #print "xsize = ", (COLUMN1-COLUM-COLUMN4)
    #xsize = max( (COLUMN1-COLUMN4) )     # min or max !?
    #print "msg_geocoord2area: xsize=", max( (COLUMN1-COLUMN2), (COLUMN3-COLUMN4) )     # min or max !?
    ##print "ysize = ", (LINE3  -LINE1  ), (LINE4  -LINE2)
    #ysize = max( (LINE3  -LINE1  ), (LINE4  -LINE2)   )     # min or max !?
    #print "msg_geocoord2area: ysize=", max( (LINE3  -LINE1  ), (LINE4  -LINE2)   )     # min or max !?

    area_def = AreaDefinition(area_name,
                              area_name,
                              'GEOS<'+'{:+06.1f}'.format(lon_0)+'>' ,
                              proj,
                              xsize,
                              ysize,
                              area_extent)

    return area_def

# ------------------------------------------------------------------------------

def print_usage():
         print("***           ")
         print("*** Error, not enough command line arguments")
         print("***        please specify at least ")
         print("***        possible calls are:")
         print("*** python msg_geocoord2area.py  <LAT_MIN> <LAT_MAX> <LON_MIN> <LON_MAX> [<HRVis>] [<SUB_LON_DEG>] [<qiet>] ")
         print("           e.g.")                                    
         print("    python msg_geocoord2area.py    45.3      47.1     1.2        4.5                               ")
         print("    python msg_geocoord2area.py    45.3      47.1     1.2        4.5        vis                     # default ")
         print("    python msg_geocoord2area.py    45.3      47.1     1.2        4.5        hrv                     # hrv resolution")
         print("    python msg_geocoord2area.py    45.3      47.1     1.2        4.5        vis         9.5         # subsatellite longitude 9.5 deg East == MSG2")
         print("    python msg_geocoord2area.py    45.3      47.1     1.2        4.5        vis         9.5   q     # quiet") 
         quit() # quit at this point

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

if __name__ == '__main__':

    import sys

    if len(sys.argv) < 5 or len(sys.argv) > 8 :
        print_usage()
    else:
        # read input file 
        LAT_MIN = float(sys.argv[1])
        LAT_MAX = float(sys.argv[2])
        LON_MIN = float(sys.argv[3])
        LON_MAX = float(sys.argv[4])
        
        # default: VIS/IR == non-HRV resolution
        HRVis="vis"
        # default, subsatellite longitude 0.0
        SUB_LON_DEG = 0.0
        # default: not quiet
        quiet = 0

        # check for more arguments 
        if len(sys.argv) > 5:
          # check for HRVis */
            if sys.argv[5]=="1" or sys.argv[5]=="hrv" or sys.argv[5]=="HRV":
                HRVis="hrv"
            elif sys.argv[5]=="0" or sys.argv[5]=="vis" or sys.argv[5]=="VIS" or sys.argv[5]=="ir" or sys.argv[5]=="IR":
                HRVis="vis"
            else: 
                print("\n*** Error, unkown 3rd command line argument: ", sys.argv[3], "\n")
                exit ()

            if len(sys.argv) > 6:
                SUB_LON_DEG  = float(sys.argv[6])

                if len(sys.argv) > 7:
                    quiet=1

    if quiet != 1:

        print(" ")
        print("... search area for MSG SEVIRI LATITUDES = [",LAT_MIN,"...",LAT_MAX,"], LONGITUDES=[",LON_MIN,"...",LON_MAX,"]") 
        if HRVis=="hrv":
            print("... use HRV coordinates!")
        else:
            print("... use VIS-IR (non-HRV) coordinates!")
        print("... use subsatellite longitude:", SUB_LON_DEG)


    area_def = msg_geocoord2area(LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, HRVis, SUB_LON_DEG)

    #print type(area_def)
    #print dir(area_def)

    if quiet != 1:
        print("")
    print("REGION:", area_def.area_id, "{")
    print("\tNAME:\t", area_def.name)
    print("\tPCS_ID:\t", area_def.proj_id)
    print(("\tPCS_DEF:\tproj="+area_def.proj_dict['proj']+", lon_0=" + area_def.proj_dict['lon_0'] + ", a="+area_def.proj_dict['a']+", b="+area_def.proj_dict['b']+", h="+area_def.proj_dict['h']))
    print("\tXSIZE:\t", area_def.x_size)
    print("\tYSIZE:\t", area_def.y_size)
    print("\tAREA_EXTENT:\t", area_def.area_extent)
    print("};")
    if quiet != 1:
        print("")
