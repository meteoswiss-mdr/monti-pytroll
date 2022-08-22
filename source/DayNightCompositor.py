# see also https://satpy.readthedocs.io/en/stable/composites.html

from glob import glob

from satpy.scene import Scene
from satpy import find_files_and_readers
from datetime import datetime
from glob import glob
import sys

#%matplotlib notebook
import matplotlib.pyplot as plt
#import cartopy
#import cartopy.crs as ccrs
#from cartopy._crs import (CRS, Geodetic, Globe, PROJ4_VERSION, WGS84_SEMIMAJOR_AXIS, WGS84_SEMIMINOR_AXIS)
from satpy.writers import get_enhanced_image
from satpy import Scene

from satpy.resample import get_area_def

from satpy.composites import DayNightCompositor
from satpy.composites import GenericCompositor
from satpy.writers import to_image

from my_msg_module_py3 import get_input_dir
from produce_forecasts_nrt_py3 import create_seviri_scene

import warnings

reader = 'seviri_l1b_hrit'
composite_day   = 'hrv_fog'
composite_night = 'night_microphysics'
#composite_day   = 'HRV'
#composite_night = 'IR_108'

if len(sys.argv) == 1:
    from my_msg_module_py3 import get_last_SEVIRI_date
    start_time = get_last_SEVIRI_date(False, delay=10)
    base_dir = start_time.strftime(get_input_dir("MSG-HRIT-RSS", nrt=True))
elif len(sys.argv) == 6:
    fixed_date=True
    start_time = datetime(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]))
    end_time   = start_time
    base_dir = start_time.strftime(get_input_dir("MSG-HRIT-RSS", nrt=False)+"/%Y/%m/%d/")

print ("... search files in "+ base_dir + " for "+ str(start_time))

scn = create_seviri_scene(start_time, base_dir, sat="MSG3")

#global_scene = Scene(reader="hrit_msg", start_time=time_slot)

#filenames = glob('C:/Users/binis/OneDrive/Desktop/To_Binish/ftp_h8_hsd_2pm/16_bands/*20210417_0200*.DAT')
#len(filenames)

#scn = Scene(reader=reader, filenames=files_sat)
#scn.load(['true_color'])
#scn.load(['true_color_with_night_ir'])

print("... load channels and create RGB in original projection")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    scn.load([composite_day, composite_night])

#area_def = create_area_def('Singapore',
#                           {'proj': 'longlat', 'datum': 'WGS84'},
#                            area_extent=[103, 1, 104, 2],
#                            shape=(800, 800),
#                            units='degrees',
#                            description='Global 1x1 degree lat-lon grid')

from pyresample import create_area_def
area="EuropeCanaryS95"
area_def = get_area_def(area)

#new_scn = scn.resample(area_def, reduce_data=False)
#new_scn.load(['true_color'])
#new_scn.load(['true_color_with_night_ir'])

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    print("... resample channels to area: "+area)
    new_scn = scn.resample(area_def, reduce_data=False)
    print("... reload composites: "+composite_day+" (day) and "+composite_night+" (night)")
    new_scn.load([composite_day, composite_night])

print("... create day-night-composite")
#            DayNightCompositor("dnc", lim_low=85., lim_high=88., day_night="day_night")
compositor = DayNightCompositor("day_night_test")
#composite = compositor([new_scn["true_color"], new_scn["true_color_with_night_ir"]])
composite = compositor([new_scn[composite_day], new_scn[composite_night]])
img = to_image(composite)

print("... produce png image")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    result_filename="demo_satpy_DayNightCompositor.png"
    img.save(writer="simple_image",
             filename=result_filename,
             base_dir="./")
    print("display "+result_filename+" &")
    print("")
