from mpop.projector import get_area_def

# list created with awk '/^#/ {next}  /REGION/ {printf "\"%s\", ", $2}' areas.def
# removed "{" manually 

areas=["alps95", "alps95L", "ccs4", "ccs4c2", "swissXXL", "cosmo1", "cosmo7", "ticino", "nrCOALtwo1km", "nrCOALtwo750m", "swiss02", "SwitzerlandStereo500m", "nrEURO1km", "nrEURO3km", "nrEuro4km", "nrMET3km", "nrIODC8km", "baltrad_lambert", "baws", "bsea250", "bsea1000", "bsea250_new", "EastEurope", "eport", "eport1", "eport10", "eport2", "eport4", "Etna", "euro", "euro1", "euro4", "euron1", "euron0250", "EuroMercator", "europe_center", "euro_north", "EuropeCanary35", "EuropeCanary95", "EuropeOdyssey00", "EuropeOdyssey95", "EuropeOdyssey95a", "EuropeCanary", "EuropeCanaryS", "EuropeCanaryS95", "eurotv", "eurotv4n", "euroHDready", "euroHDfull", "eurol", "eurol1", "FranceSouthHyMex", "germ", "germ2", "hsaf", "hsaf_merc", "iber", "iceland", "italy", "mesanX", "mesanE", "nq0001km", "nq0003km", "nq0008km", "nqceur1km", "nqceur3km", "nqeuro1km", "nrEuro4kmEqc", "nsea", "nsea250", "nsper_swe", "nswe", "odyssey", "odysseyS2", "odysseyS25", "odysseyS3", "odysseyS4", "pifh", "pifn", "romania", "rome", "scan", "scanl", "scan1", "scan2", "scan500m", "scanice", "spain", "ssea", "ssea250", "sswe", "sve",  "met07globe", "MSGHRVN", "SeviriDisk00", "SeviriDiskFull00", "SeviriDiskFull00S2", "SeviriDiskFull00S3", "SeviriDiskFull00S4", "SeviriDiskFull00S5", "SeviriDisk35", "SeviriDiskFull35", "SeviriDisk95", "SeviriDiskFull95", "SeviriDiskFull95S", "SeviriDiskFull95S3", "SeviriDiskFull95S4", "SeviriDiskFull95S5", "moll", "robinson", "worldeqc30km", "worldeqc3km70", "worldeqc30km70", "worldeqc3km73", "worldeqc3km", "worldeqc30km", "world_plat_21600_10800", "world_plat_21600_10927", "world_plat_8192_4096", "AfHorn", "afhorn", "africa", "africa_10km", "kuwait", "kuwait_phil", "kuwait_phil_small", "libya", "mali", "mali_eqc", "maspalomas", "SouthArabia", "antarctica", "arctica", "arctic_europe_1km", "arctic_europe_9km", "barents_sea", "ease_nh", "ease_sh", "sval", "afghanistan", "euroasia", "euroasia_10km", "euroasia_asia", "euroasia_asia_10km", "japan", "pacific", "stere_asia_test", "australia", "australia_pacific", "australia_pacific_10km", "brazil", "brazil2", "southamerica", "SouthAmerica", "southamerica_10km", "SouthAmerica_flat", "south_america", "northamerica", "northamerica_10km", "npp_sample_m", "npp_sample_i", "baws250", "bocheng_test", "sudeste"]
#areas= ["fullearth"]
#areas=["ccs4"]

for area in areas:

    print area+":"
    area_def=get_area_def(area)
    print "  description: "+ area_def.name
    print "  projection:"
    for key in ["proj","lat_0","lon_0","lat_1","lon_1","lat_2","lon_2","lat_ts","ellps","x_0","y_0","k_0","a","b","h"]:
        if key in area_def.proj_dict:
            print "    "+key+': ', area_def.proj_dict[key]
            area_def.proj_dict.pop(key, None)
        
    for key in area_def.proj_dict:
        print "    "+key+': ', area_def.proj_dict[key]

    print "  shape:"
    print "    height: "+str(area_def.y_size)
    print "    width:  "+str(area_def.x_size)
    
    print "  area_extent:"
    print "    lower_left_xy: ["+str(area_def.area_extent[0])+", "+str(area_def.area_extent[1])+"]" 
    print "    upper_right_xy: ["+str(area_def.area_extent[2])+", "+str(area_def.area_extent[3])+"]" 
    print ""
