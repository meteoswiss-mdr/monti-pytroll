#!/bin/sh

ImgPath=$1

echo ""
echo "1: Input file: `basename $1` CS image with projection or .prj file"

PrjFile="Tmp.prj"
rm -f $PrjFile



# Input parameters
cinesat show prj ${ImgPath} > $PrjFile

echo "INPUT prj file:"
echo "----------------------------------------------"
cat $PrjFile
echo "----------------------------------------------"


height_y=`grep Prj.Height $PrjFile | cut -d ' ' -f 2-`
width_x=`grep Prj.Width $PrjFile| cut -d ' ' -f 2-`

prj_type=`grep Prj.Type $PrjFile| cut -d ' ' -f 2-`
equator_rad=`grep Prj.EquatorRadius $PrjFile| cut -d ' ' -f 2-`
polar_rad=`grep Prj.PolarRadius $PrjFile| cut -d ' ' -f 2-`
#ref_lat=`grep Prj.RefLat1 $PrjFile| cut -d ' ' -f 2-`
ref_lon=`grep Prj.RefLong $PrjFile| cut -d ' ' -f 2-`
#img_width=`grep Prj.Width $PrjFile| cut -d ' ' -f 2-`
#img_height=`grep Prj.Height $PrjFile| cut -d ' ' -f 2-`
description=`grep Prj.Description $PrjFile| cut -d ' ' -f 2-`
lat_true_scale=`grep Prj.RefLat1 $PrjFile| cut -d ' ' -f 2-`
prj_sat_height=`grep Prj.SatelliteHeight $PrjFile| cut -d ' ' -f 2-`

# Read corners

#PROJECT  <X>    <Y>  <PrjFile> /INV

x0y0=`cinesat project 0 0 $PrjFile /INV`
x1y0=`cinesat project $width_x 0 $PrjFile /INV`
x0y1=`cinesat project 0 $height_y $PrjFile /INV`
x1y1=`cinesat project $width_x $height_y $PrjFile /INV`

echo "x0,y0--------------x1,y0"
echo "  |                  |"
echo "  |                  |"
echo "  |                  |"
echo "x0,y1---------------x1,y1"

echo "         lon       lat"
echo "x0,y0: $x0y0"
echo "x1,y0: $x1y0"
echo "x0,y1: $x0y1"
echo "x1,y1: $x1y1"

echo "------------------------------"
echo "Calculating area extent:"
echo "------------------------------"
echo "(x-lowerleft,y-lowerleft,x-upperright,y-upperright)"
echo "lower left  lon-lat is x0,y1: $x0y1"
echo "upper right lon-lat is x1,y0: $x1y0"

#from_proj_string="+proj=longlat +lon_0=0.0 +a=6378169.00  +b=6356583.80 +h=42164000.0"

from_proj_string="+proj=longlat +lon_0=${ref_lon//[[:blank:]]/} +a=${equator_rad//[[:blank:]]/}  +b=${polar_rad//[[:blank:]]/} +h=${prj_sat_height//[[:blank:]]/}"



to_proj_string="+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0 +units=m"
area_extent_string="proj=geos, lon_0=0.0, a=6378169.00, b=6356583.80, h=35785831.0"

cs2cs_lower_string=`echo $x0y1 |cs2cs -v -f %.6f $from_proj_string +to $to_proj_string|tail -1`
cs2cs_upper_string=`echo $x1y0 |cs2cs -v -f %.6f $from_proj_string +to $to_proj_string|tail -1`

echo " "
echo "Proj conversion string used:"
echo "From:"
echo $from_proj_string
echo "To:"
echo $to_proj_string

cmd_string_l="echo $x0y1 |cs2cs -v -f %.6f $from_proj_string +to $to_proj_string|tail -1"
cmd_string_u="echo $x1y0 |cs2cs -v -f %.6f $from_proj_string +to $to_proj_string|tail -1"

echo "lower: $cmd_string_l"
echo "upper: $cmd_string_u"

echo "Output:"
echo "Lower left  x,y: $cs2cs_lower_string"
echo "Upper right x,y: $cs2cs_upper_string"
echo "---------------------------------------------------"

lower_left_x=`echo $cs2cs_lower_string|cut -d ' ' -f 1`
lower_left_y=`echo $cs2cs_lower_string|cut -d ' ' -f 2`

upper_right_x=`echo $cs2cs_upper_string|cut -d ' ' -f 1`
upper_right_y=`echo $cs2cs_upper_string|cut -d ' ' -f 2`

echo "REGION: ${description//[[:blank:]]/} {"
echo "        NAME:          ${description//[[:blank:]]/}"
echo "        PCS_ID:        geos0"
echo "        PCS_DEF:       $area_extent_string"
echo "        XSIZE:         ${width_x//[[:blank:]]/}"
echo "        YSIZE:         ${height_y//[[:blank:]]/}" 
echo "        AREA_EXTENT:   ($lower_left_x,$lower_left_y,$upper_right_x,$upper_right_y)" 
echo "};"

