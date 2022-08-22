# see also https://satpy.readthedocs.io/en/stable/composites.html

from glob import glob

from satpy.scene import Scene
from satpy import find_files_and_readers
from datetime import datetime
from glob import glob

%matplotlib notebook
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
from cartopy._crs import (CRS, Geodetic, Globe, PROJ4_VERSION, WGS84_SEMIMAJOR_AXIS, WGS84_SEMIMINOR_AXIS)
from satpy.writers import get_enhanced_image
from satpy import Scene

from satpy.composites import DayNightCompositor, satpy

filenames = glob('C:/Users/binis/OneDrive/Desktop/To_Binish/ftp_h8_hsd_2pm/16_bands/*20210417_0200*.DAT')
len(filenames)

scn = Scene(reader='ahi_hsd', filenames=filenames)
scn.load(['true_color'])
scn.load(['true_color_with_night_ir'])


from pyresample import create_area_def

area_def = create_area_def('Singapore',
                           {'proj': 'longlat', 'datum': 'WGS84'},
                            area_extent=[103, 1, 104, 2],
                            shape=(800, 800),
                            units='degrees',
                            description='Global 1x1 degree lat-lon grid')

new_scn = scn.resample(area_def, reduce_data=False)
new_scn.load(['true_color'])
new_scn.load(['true_color_with_night_ir'])

compositor = satpy.composites.DayNightCompositor("day_night_true_color")
composite = compositor([new_scn["true_color"], new_scn["true_color_with_night_ir"]])
img = satpy.writers.to_image(composite)

img.save(writer="simple_image",            
                       filename="Singapore on 17-4-21 0200 Time-dayNight composite using area definition latest 2.png",
                       base_dir="C:/Users/binis/OneDrive/Desktop/To_Binish/")
