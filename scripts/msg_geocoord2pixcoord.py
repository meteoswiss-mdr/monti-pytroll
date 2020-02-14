from __future__ import division
from __future__ import print_function

from numpy import cos
from numpy import sin
from numpy import pi as PI
from numpy import arctan as atan
from numpy import arcsin as asin
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

# ------------------------------------------------------------------------------

def msg_geocoord2pixcoord( longitude, latitude, HRVis,  SUB_LON_DEG):

  ccc=0; lll=0

  lati=0.0; longi=0.0
  c_lat=0.0
  lat=0.0
  lon=0.0
  r1=0.0; r2=0.0; r3=0.0; rn=0.0; re=0.0; rl=0.0
  xx=0.0; yy=0.0
  cc=0.0; ll=0.0 
  dotprod=0.0
  
  lati = latitude
  longi = longitude

  lfac, cfac, coff, loff = get_lfac_cfac_coff_loff(HRVis)

  SUB_LON = SUB_LON_DEG * PI / 180.0

  # check if the values are sane, otherwise return error values */
  if (lati < -90.0 or lati > 90.0 or longi < -180.0 or longi > 180.0 ): 
      row = -999
      column = -999
      print("*** ERROR latitude ", lati , "or longitude", longi, "outside range")
      return column, row

  # convert them to radiants */
  lat = lati*PI / 180.
  lon = longi *PI / 180.
    
  # calculate the geocentric latitude from the          */
  # geograhpic one using equations on page 24, Ref. [1] */

  c_lat = atan ( ( 0.993243*(sin(lat)/cos(lat)) ))

  # using c_lat calculate the length form the Earth */
  # centre to the surface of the Earth ellipsoid    */
  # equations on page 23, Ref. [1]                  */
  
  re = R_POL / sqrt( ( 1.0 - 0.00675701 * cos(c_lat) * cos(c_lat) ) )

  # calculate the forward projection using equations on */
  # page 24, Ref. [1]                                        */

  rl = re 
  r1 = SAT_HEIGHT - rl * cos(c_lat) * cos(lon - SUB_LON)
  r2 = - rl *  cos(c_lat) * sin(lon - SUB_LON)
  r3 = rl * sin(c_lat)
  rn = sqrt( r1*r1 + r2*r2 +r3*r3 )
  
  
  # check for visibility, whether the point on the Earth given by the */
  # latitude/longitude pair is visible from the satellte or not. This */ 
  # is given by the dot product between the vectors of:               */
  # 1) the point to the spacecraft,			               */
  # 2) the point to the centre of the Earth.			       */
  # If the dot product is positive the point is visible otherwise it  */
  # is invisible.						       */
     
  dotprod = r1*(rl * cos(c_lat) * cos(lon - SUB_LON)) - r2*r2 - r3*r3*( (R_EQ/R_POL)**2 )
     
  if (dotprod <= 0 ):
      column = -999
      row = -999
      print("*** ERROR dotproduct <= 0")
      return column, row
  

  # the forward projection is x and y */

  xx = atan( (-r2/r1) )
  yy = asin( (-r3/rn) )


  # convert to pixel column and row using the scaling functions on */
  # page 28, Ref. [1]. And finding nearest integer value for them. */


  cc = coff + xx *  2**(-16) * cfac 
  ll = loff + yy *  2**(-16) * lfac 

  ccc = int(round(cc))
  lll = int(round(ll))

  return ccc, lll

# ------------------------------------------------------------------------------

def print_usage():
         print("***           ")
         print("*** Error, not enough command line arguments")
         print("***        please specify at least ")
         print("***        possible calls are:")
         print("*** python msg_pixcoord2geocoord.py  <LON> <LAT> [<HRVis>] [<SUB_LON_DEG>] [<qiet>] ")
         print("           e.g.")
         print("    python msg_pixcoord2geocoord.py   1.2  46.3                             ")
         print("    python msg_pixcoord2geocoord.py   1.2  46.3     vis                     # default ")
         print("    python msg_pixcoord2geocoord.py   1.2  46.3     hrv                     # hrv resolution")
         print("    python msg_pixcoord2geocoord.py   1.2  46.3     vis         9.5         # subsatellite longitude 9.5 deg East == MSG2")
         print("    python msg_pixcoord2geocoord.py   1.2  46.3     vis         9.5   q     # quiet") 
         quit() # quit at this point

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

if __name__ == '__main__':

    import sys

    if len(sys.argv) < 3 or len(sys.argv) > 6 :
        print_usage()
    else:
        # read input file 
        LONGITUDE = float(sys.argv[1])
        LATITUDE  = float(sys.argv[2])
        
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
                print("\n*** Error, unkown 3rd command line argument: ", sys.argv[3], "\n")
                exit ()

            if len(sys.argv) > 4:
                SUB_LON_DEG  = float(sys.argv[4])

                if len(sys.argv) > 5:
                    quiet=1

    if quiet != 1:

        print(" ")
        print("... search longitude latitude for MSG SEVIRI longitude: ", LONGITUDE, ", and latitude: ", LATITUDE) 
        if HRVis=="hrv":
            print("... use HRV coordinates!")
        else:
            print("... use VIS-IR (non-HRV) coordinates!")
        print("... use subsatellite longitude:", SUB_LON_DEG)
        print("  column     row ")

    COLUMN, LINE = msg_geocoord2pixcoord(LONGITUDE, LATITUDE, HRVis, SUB_LON_DEG)
    print(" ", COLUMN, "      ", LINE)
    if quiet != 1:
        print("")
