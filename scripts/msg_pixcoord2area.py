

def msg_pixcoord2area(Y_UL, X_UL, Y_LR, X_LR, HRVis, SUB_LON_DEG):

    from msg_pixcoord2geocoord import msg_pixcoord2geocoord
    from msg_geocoord2area     import msg_geocoord2area

    # X_UL = PIX_EAST
    # X_LR = PIX_WEST
    # Y_UL = PIX_NORTH
    # Y_LR = PIX_SOUTH

    # we must shift the upper left   pixel number by +0.5 as we need lon, lat from the boundary of the pixel (not the center)
    X_UL = X_UL+0.5
    Y_UL = Y_UL+0.5
    # we must shift the lower rright pixel number by -0.5 as we need lon, lat from the boundary of the pixel (not the center)
    X_LR = X_LR-0.5
    Y_LR = Y_LR-0.5

    # calculate longitude and latitude for all corners 
    #print "calculate upper left"
    lon_UL,lat_UL = msg_pixcoord2geocoord( X_UL, Y_UL, HRVis, SUB_LON_DEG) # Upper Left
    #print "calculate upper right"
    lon_UR,lat_UR = msg_pixcoord2geocoord( X_LR, Y_UL, HRVis, SUB_LON_DEG) # Upper Right
    #print "calculate lower left"
    lon_LL,lat_LL = msg_pixcoord2geocoord( X_UL, Y_LR, HRVis, SUB_LON_DEG) # Lower Left
    #print "calculate lower left"
    lon_LR,lat_LR = msg_pixcoord2geocoord( X_LR, Y_LR, HRVis, SUB_LON_DEG) # Lower Right

    #print "(msg_pixcoord2area) lon_UL,lat_UL ",  lon_UL,lat_UL 
    #print "(msg_pixcoord2area) lon_UR,lat_UR ",  lon_UR,lat_UR 
    #print "(msg_pixcoord2area) lon_LL,lat_LL ",  lon_LL,lat_LL 
    #print "(msg_pixcoord2area) lon_LR,lat_LR ",  lon_LR,lat_LR 

    lon_min = max(lon_UL,lon_LL)
    lon_max = min(lon_UR,lon_LR)
    lat_min = max(lat_LL,lat_LR)
    lat_max = min(lat_UL,lat_UR)
    #print "(msg_pixcoord2area) lon_min, lon_max, lat_min, lat_max ", lon_min, lon_max, lat_min, lat_max
    xsize=X_UL-X_LR
    ysize=Y_UL-Y_LR
    #print "(msg_pixcoord2area) xsize=", xsize," ysize=", ysize

    area_def = msg_geocoord2area(lat_min, lat_max, lon_min, lon_max, HRVis, SUB_LON_DEG, xsize=xsize, ysize=ysize)

    return area_def

# ------------------------------------------------------------------------------

def print_usage(nargv):
         print "***           "
         print "*** Error, wrong number of command line arguments", nargv
         print "***        please specify at least "
         print "***        possible calls are:"
         print "*** python msg_pixcoord2area.py  <Y_UL> <X_UL> <Y_LR> <X_LR> [<HRVis>] [<SUB_LON_DEG>] [<qiet>] "
         print "    python msg_pixcoord2area.py   3341   2054   3218   1819                                        "
         print "    python msg_pixcoord2area.py   3341   2054   3218   1819     vis                       # default "
         print "    python msg_pixcoord2area.py   3341   2054   3218   1819     hrv                       # hrv resolution"
         print "    python msg_pixcoord2area.py   3341   2054   3218   1819     vis         9.5           # subsatellite longitude 9.5 deg East == MSG2"
         print "    python msg_pixcoord2area.py   3341   2054   3218   1819     vis         9.5     q     # quiet" 
         quit() # quit at this point

         print "    where, X_UL is the column nr of the upper left pixel"
         print "    where, Y_UL is the line   nr of the upper left pixel"
         print "    where, X_LR is the column nr of the upper left pixel"
         print "    where, Y_LR is the line   nr of the upper left pixel"
         print "    e.g."

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

if __name__ == '__main__':

    import sys

    if len(sys.argv) < 5 or len(sys.argv) > 8 :
        print_usage(len(sys.argv))
    else:
        # read input file 
        Y_UL = float(sys.argv[1])
        X_UL = float(sys.argv[2])
        Y_LR = float(sys.argv[3])
        X_LR = float(sys.argv[4])
        
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
                print "\n*** Error, unkown 5th command line argument: ", sys.argv[5], "\n"
                exit ()

            if len(sys.argv) > 6:
                SUB_LON_DEG  = float(sys.argv[6])

                if len(sys.argv) > 7:
                    quiet=1

    if quiet != 1:

        print " "
        print "... search area for"
        print "    MSG SEVIRI pixel upper left  = [",Y_UL,",",X_UL,"]" 
        print "    MSG SEVIRI pixel lower right = [",Y_LR,",",X_LR,"]"
        if HRVis=="hrv":
            print "... use HRV coordinates!"
        else:
            print "... use VIS-IR (non-HRV) coordinates!"
        print "... use subsatellite longitude:", SUB_LON_DEG


    area_def = msg_pixcoord2area(Y_UL, X_UL, Y_LR, X_LR, HRVis, SUB_LON_DEG)

    if quiet != 1:
        print ""
    print "REGION:", area_def.area_id, "{"
    print "\tNAME:\t", area_def.name
    print "\tPCS_ID:\t", area_def.proj_id
    print ("\tPCS_DEF:\tproj="+area_def.proj_dict['proj']+", lon_0=" + area_def.proj_dict['lon_0'] + ", a="+area_def.proj_dict['a']+", b="+area_def.proj_dict['b']+", h="+area_def.proj_dict['h'])
    print "\tXSIZE:\t", area_def.x_size 
    print "\tYSIZE:\t", area_def.y_size
    print "\tAREA_EXTENT:\t", area_def.area_extent
    print "};"
    if quiet != 1:
        print ""
