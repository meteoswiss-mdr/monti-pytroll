from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime

from my_msg_module import get_last_SEVIRI_date

from mpop.utils import debug_on
debug_on()

#sat_nr="09"   # for data from the MeteoSwiss processing (alps region)
#sat_nr="10"   # for data from the Eumetcast processing (FES == full earth service)
sat_nr="11"   # for data from the Eumetcast processing (FES == full earth service)

if sat_nr=="09":
    Rapid_Scan=True
    delay=10
    area="ccs4"
    #area="cosmo1"
    #area="cosmo7"
    #area="EuropeCanaryS"
elif sat_nr=="10":
    Rapid_Scan=False
    delay=10
    area="EuropeCanaryS"
elif sat_nr=="11":
    Rapid_Scan=False
    delay=10
    area="EuropeCanaryS"
else:
    print "Unknown satellite"
    quit()

print "... Meteosat ", sat_nr,", Rapid Scan mode: ", Rapid_Scan
time_slot = get_last_SEVIRI_date(Rapid_Scan, delay=delay)
#time_slot = datetime.datetime(2015, 11, 26, 15, 30)
print str(time_slot)

global_data = GeostationaryFactory.create_scene("meteosat", sat_nr, "seviri", time_slot)

#prop="CMa"
#prop='CT'
prop="CTH"

# e.g. return "CTTH" for prop "CTH"
from my_msg_module import get_NWC_pge_name
pge = get_NWC_pge_name(prop)

print "read pge: ", pge
nwcsaf_calibrate=True   # converts data into physical units
global_data.load([pge], calibrate=nwcsaf_calibrate, reader_level="seviri-level3")  # , area_extent=europe.area_extent
print global_data

# get lon/lat coordinates of the original "alps" projection
if False:
    lonlats = global_data[pge].area.get_lonlats()
    #print type(lonlats)   # tuple
    import numpy as np
    lonlatsnp = np.asarray(lonlats)
    print lonlatsnp.shape
    print lonlatsnp[:,0,0]
    print lonlatsnp[:,0,-1]
    print lonlatsnp[:,-1,0]
    print lonlatsnp[:,-1,-1]

# convert structure from data["CTTH"].height.data etc to data["CTH"].data
from my_msg_module import convert_NWCSAF_to_radiance_format
IS_PYRESAMPLE_LOADED = True
convert_NWCSAF_to_radiance_format(global_data, None, prop, nwcsaf_calibrate, IS_PYRESAMPLE_LOADED)

# project data to anther projection defined in etc/area.def
#area = get_area_def("euro")
data = global_data.project(area, precompute=True)

from trollimage.colormap import rainbow
colormap = rainbow

## normal convection is something like data[pge].height
## but after convert_NWCSAF_to_radiance_format we can use 
#min_data = data[pge].height.data.min()
#max_data = data[pge].height.data.max()
#colormap.set_range(min_data, max_data)
#from trollimage.image import Image as trollimage
#img = trollimage(data[prop].height.data, mode="L", fill_value=[0,0,0])

min_data = data[prop].data.min()
max_data = data[prop].data.max()
colormap.set_range(min_data, max_data)
from trollimage.image import Image as trollimage
img = trollimage(data[prop].data, mode="L", fill_value=[0,0,0])

img.colorize(colormap)
img.show()
#img.save("nwcsaf_demo.png")
