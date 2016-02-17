
export VIS_IRSouthLine=3218    # lower
export VIS_IRNorthLine=3341    # upper 
export VIS_IREastColumn=1819   # right 
export VIS_IRWestColumn=2054   # left

# output of /home/lom/users/hau/TOOLS/C/MSG/calc_lat_lon.sh
#   0.9367538679257      48.4989661018926
#  11.0889286255534      48.3989381138650
#   1.8770844646736      42.6994291436896
#  10.9169793877153      42.6287114069792

export lat_min=42.6994291436896
export lat_max=48.3989381138650
export lon_min=1.8770844646736
export lon_max=10.9169793877153 
export sat_lon=9.5
export resolution=3.003

# change lon_0 by hand
# echo $lat_min $lat_max $lon_min $lon_max

# (-594837.0493598427, 4081678.327128149, 124481.885711465, 4461484.553510189)


echo ""
echo coord2area_def.py 
/usr/bin/python /data/OWARNA/hau/pytroll/test/coord2area_def.py area_name geos $lat_min $lat_max $lon_min $lon_max
# (-667487.5853936968, 4080362.2163360775, 124481.885711465, 4461484.553510189)

echo ""
echo coord2area_def_geos.py
/usr/bin/python /data/OWARNA/hau/pytroll/test/coord2area_def_geos.py area_name $sat_lon $lat_min $lat_max $lon_min $lon_max $resolution
# (-667487.5853936968, 4080362.2163360775, 124481.885711465, 4461484.553510189)

echo ""
echo msg_geocoord2area.py
/usr/bin/python /data/OWARNA/hau/pytroll/test/msg_geocoord2area.py $lat_min $lat_max $lon_min $lon_max vis $sat_lon
# (-667487.5853936968, 4080362.2163360775, 124481.885711465, 4461484.553510189)

echo ""
echo msg_pixcoord2area.py
#export VIS_IRSouthLine=3218    # lower
#export VIS_IRNorthLine=3341    # upper 
#export VIS_IREastColumn=1819   # right 
#export VIS_IRWestColumn=2054   # left                                  3341              2054             3218            1819
/usr/bin/python /data/OWARNA/hau/pytroll/test/msg_pixcoord2area.py $VIS_IRNorthLine $VIS_IRWestColumn $VIS_IRSouthLine $VIS_IREastColumn vis $sat_lon
