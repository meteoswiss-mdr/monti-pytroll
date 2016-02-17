from numpy import cos
from numpy import sin
from numpy import pi as PI
from numpy import arctan as atan
from numpy import sqrt


SAT_HEIGHT = 42164.0       # distance from Earth centre to satellite     */
R_EQ       =  6378.169     # radius from Earth centre to equator         */
R_POL      =  6356.5838    # radius from Earth centre to pol             */


def get_lfac_cfac_coff_loff(HRVis):

    CFAC_NONHRV  =  -781648343      # scaling coefficients (see note above)  */
    LFAC_NONHRV  =  -781648343      # scaling coefficients (see note above)  */
    
    CFAC_HRV     =   -2344945030.   # scaling coefficients (see note above)  */
    LFAC_HRV     =   -2344945030.   # scaling coefficients (see note above)  */
    
    COFF_NONHRV  =        1856      # scaling coefficients (see note above)  */
    LOFF_NONHRV  =        1856      # scaling coefficients (see note above)  */
    
    COFF_HRV     =        5566      # scaling coefficients (see note above)  */
    LOFF_HRV     =        5566      # scaling coefficients (see note above)  */
    
    if HRVis == "hrv" :
        lfac=LFAC_HRV
        cfac=CFAC_HRV
        coff=COFF_HRV
        loff=LOFF_HRV
    else:
        lfac=LFAC_NONHRV
        cfac=CFAC_NONHRV
        coff=COFF_NONHRV
        loff=LOFF_NONHRV

    return lfac, cfac, coff, loff

# ---------------------------------------------------------------------

def msg_pixcoord2geocoord(column, row, HRVis, SUB_LON_DEG):

  s1=0.0; s2=0.0; s3=0.0; sn=0.0; sd=0.0; sxy=0.0; sa=0.0
  x=0.0; y=0.0
  longi=0.0; lati=0.0

  c=0; l=0

  c=column
  l=row

  lfac, cfac, coff, loff = get_lfac_cfac_coff_loff(HRVis)

  SUB_LON = SUB_LON_DEG * PI / 180.0

  #  calculate viewing angle of the satellite by use of the equation  */
  #  on page 28, Ref [1]. */

  x = 2 ** 16  * ( float(c) - float(coff)) / float(cfac)
  y = 2 ** 16  * ( float(l) - float(loff)) / float(lfac)

  #  now calculate the inverse projection */

  # first check for visibility, whether the pixel is located on the Earth   */
  # surface or in space. 						     */
  # To do this calculate the argument to sqrt of "sd", which is named "sa". */
  # If it is negative then the sqrt will return NaN and the pixel will be   */
  # located in space, otherwise all is fine and the pixel is located on the */
  # Earth surface.                                                          */

  sa =  (SAT_HEIGHT * cos(x) * cos(y))**2   - (cos(y)*cos(y) + 1.006803 * sin(y)*sin(y)) * 1737121856. 

  # produce error values */
  if ( sa <= 0.0 ) :
      latitude = -999.999
      longitude = -999.999
      print "*** ERROR: pixel is located in space (sa <= 0.0)"
      print "    conversion to lon,lat not possible"
      exit()
      return longitude, latitude
  

  # now calculate the rest of the formulas using equations on */
  # page 25, Ref. [1]  */

  sd = sqrt( (SAT_HEIGHT * cos(x) * cos(y))**2 
	     - (cos(y)*cos(y) + 1.006803 * sin(y)*sin(y)) * 1737121856. )
  sn = (SAT_HEIGHT * cos(x) * cos(y) - sd) / ( cos(y)*cos(y) + 1.006803 * sin(y)*sin(y) ) 
  
  s1 = SAT_HEIGHT - sn * cos(x) * cos(y)
  s2 = sn * sin(x) * cos(y)
  s3 = -sn * sin(y)

  sxy = sqrt( s1*s1 + s2*s2 )

  # using the previous calculations the inverse projection can be  */
  # calculated now, which means calculating the lat./long. from    */
  # the pixel row and column by equations on page 25, Ref [1].     */

  longi = atan(s2/s1) + SUB_LON
  lati  = atan((1.006803*s3)/sxy)

  # convert from radians into degrees */
  latitude = lati*180./PI
  longitude = longi*180./PI
  
  return longitude, latitude

# ------------------------------------------------------------------------------

def print_usage():
         print "***           "
         print "*** Error, not enough command line arguments"
         print "***        please specify at least "
         print "***        possible calls are:"
         print "*** python msg_pixcoord2geocoord.py  <COLUMN> <LINE> [<HRVis>] [<SUB_LON_DEG>] [<qiet>] "
         print "           e.g."
         print "    python msg_pixcoord2geocoord.py    1234    2343    "
         print "    python msg_pixcoord2geocoord.py    1234    2343    vis               # (default) "
         print "    python msg_pixcoord2geocoord.py    3800    5300                      # hrv resolution"
         print "    python msg_pixcoord2geocoord.py    1234    2343    vis        9.5    # subsatellite longitude 9.5 deg East == MSG2"
         print "    python msg_pixcoord2geocoord.py    1234    2343    vis        9.5 q  # quiet" 
         quit() # quit at this point

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

if __name__ == '__main__':

    import sys

    if len(sys.argv) < 3 or len(sys.argv) > 6 :
        print_usage()
    else:
        # read input file 
        COLUMN = sys.argv[1]
        LINE   = sys.argv[2]
        
        # default: VIS/IR == non-HRV resolution
        hrv="vis"
        # default, subsatellite longitude 0.0
        SUB_LON_DEG = 0.0
        # default: not quiet
        quiet = 0

        # check for more arguments 
        if len(sys.argv) > 3:
          # check for HRVis */
            if sys.argv[3]=="1" or sys.argv[3]=="hrv" or sys.argv[3]=="HRV":
                HRVis="hrv"
            elif sys.argv[3]=="0" or sys.argv[3]=="vis" or sys.argv[3]=="VIS" or sys.argv[3]=="ir" or sys.argv[3]=="IR":
                HRVis="vis"
            else: 
                print "\n*** Error, unkown 3rd command line argument: ", sys.argv[3], "\n"
                exit ()

            if len(sys.argv) > 4:
                SUB_LON_DEG  = float(sys.argv[4])

                if len(sys.argv) > 5:
                    quiet=1

    if quiet != 1:

        print " "
        print "... search longitude latitude for MSG SEVIRI column: ", COLUMN, ", and line: ", LINE
        if HRVis=="hrv":
            print "... use HRV coordinates!"
        else:
            print "... use VIS-IR (non-HRV) coordinates!"
        print "... use subsatellite longitude:", SUB_LON_DEG
        print "  longitude     latitude "

    longitude, latitude = msg_pixcoord2geocoord(COLUMN, LINE, HRVis, SUB_LON_DEG)
    print " ", longitude, latitude
    if quiet != 1:
        print ""
