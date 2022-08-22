from __future__ import division
from __future__ import print_function

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2011, 2014 SMHI

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Minimal script for geostationary production.

NUCAPS stands for NOAA Unique Combined Atmospheric Processing System
We take the case of NUCAPS data, as downloaded from  

https://www.ospo.noaa.gov/Products/atmosphere/soundings/nucaps/

- Install mipp, satpy, and pyresample
- Don't forget to set up the PPP_CONFIG_DIR variable to point to your
  configuration files. (e.g. satpy/satpy/etc)
- Edit the nucaps.yaml configuration file (a template is provided in case
  you don't have one) with your HRIT directory:

  .. code-block:: ini

file_types:
  nucaps:
    file_reader: !!python/name:satpy.readers.nucaps.NUCAPSFileHandler
    file_patterns:
    - 'NUCAPS-EDR_{nucaps_version}_{platform_shortname}_s{start_time:%Y%m%d%H%M%S%f}_e{end_time:%Y%m%d%H%M%S%f}_c{creation_time:%Y%m%d%H%M%S%f}.nc'
    - 'NUCAPS-sciEDR_{am_pm:2s}_{platform_shortname:3s}_s{start_time:%Y%m%d%H%M%S}_e{end_time:%Y%m%d%H%M%S}_STC_fsr.nc'

"""

#from satpy.utils import debug_on
#debug_on()
from satpy import Scene, find_files_and_readers
import numpy as np
from datetime import datetime


start_time    = datetime.strptime("202003020000070", "%Y%m%d%H%M%S%f")
end_time      = datetime.strptime("202003020000370", "%Y%m%d%H%M%S%f")

files_sat = find_files_and_readers(start_time=start_time, end_time=end_time, # creation_time=creation_time,
                           base_dir="/data/COALITION2/database/NUCAPS/2020/03/02",
                           reader='nucaps')  
print(files_sat)

global_scene = Scene(reader="nucaps", filenames=files_sat)

var="H2O_MR"
global_scene.load([var], pressure_levels=True)

#print(global_scene)
#print("============")
print(global_scene[var])
print(type(global_scene[var].data))

var_np = global_scene[var].data.compute()
print(np.nanmin(var_np))
print(np.nanmax(var_np))

print(global_scene[var].coords)
#print(global_scene[var].coords["Time"])
print(global_scene[var].coords["Time"].values[0])
#print(datetime.fromtimestamp(global_scene[var].coords["Time"].values[0]/1000.) )
Time_= [datetime.fromtimestamp(tt/1000.) for tt in global_scene[var].coords["Time"].values]
[print(tt) for tt in Time_]
print(global_scene[var].coords["Pressure"].values[0,:])

import matplotlib.pyplot as plt
global_scene[var].plot()
plt.show()

# some websites for understanding and plotting xarray
# https://examples.dask.org/xarray.html
# http://xarray.pydata.org/en/stable/plotting.html
# http://xarray.pydata.org/en/stable/examples/multidimensional-coords.html



if False:
    import pylab
    pylab.imshow(global_scene[var].data.compute().transpose())
    pylab.xlabel("satellite path")
    pylab.ylabel("pressure levels")
    pylab.show()
    
