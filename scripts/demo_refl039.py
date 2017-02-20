#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c14526.ad.smhi.se>

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

"""Test deriving the 3.9 relfectance of real data and make some imagery
"""


from mpop.satellites import GeostationaryFactory
from datetime import datetime
from mpop.projector import get_area_def
import sys

europe = get_area_def("EuropeCanary")

if len(sys.argv) == 1:
    from my_msg_module import get_last_SEVIRI_date
    tslot = get_last_SEVIRI_date(True, delay=5)
    #tslot = datetime(2013, 10, 11, 11, 30)
    #tslot = datetime(2015, 7, 7, 15, 10)
    #tslot = datetime(2015, 10, 15, 11, 00)
elif len(sys.argv) == 6:
    year   = int(sys.argv[1])
    month  = int(sys.argv[2])
    day    = int(sys.argv[3])
    hour   = int(sys.argv[4])
    minute = int(sys.argv[5])
    tslot = datetime(year, month, day, hour, minute)
else:
    print "\n*** Error, wrong number of input arguments"
    print "    usage:"
    print "    python demo_refl039.py"
    print "    or"
    print "    python demo_refl039.py 2017 2 17 14 35\n"
    quit()

print "*** plot day microphysics RGB for ", str(tslot)

#glbd = GeostationaryFactory.create_scene("meteosat", "09", "seviri", tslot)
glbd = GeostationaryFactory.create_scene("Meteosat-9", "", "seviri", tslot)

print "... load sat data"
glbd.load(['VIS006','VIS008','IR_016','IR_039','IR_108','IR_134'], area_extent=europe.area_extent)
#area="EuropeCanaryS95"
area="EuroMercator" # blitzortung projection
local_data = glbd.project(area)

print "... read responce functions"
from pyspectral.near_infrared_reflectance import Calculator
from pyspectral.solar import (SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)

solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.0005)

#from pyspectral.seviri_rsr import load
#seviri = load()
#rsr = {'wavelength': seviri['IR3.9']['wavelength'], 
#       'response': seviri['IR3.9']['met10']['95']}
#sflux = solar_irr.solar_flux_over_band(rsr)

solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.0005)
from pyspectral.rsr_reader import RelativeSpectralResponse
seviri = RelativeSpectralResponse('Meteosat-10', 'seviri')
sflux = solar_irr.inband_solarflux(seviri.rsr['IR3.9'])

ch39 = local_data['IR_039']
ch11 = local_data['IR_108']
ch13 = local_data['IR_134']
lonlats = ch39.area.get_lonlats()

from pyorbital.astronomy import sun_zenith_angle
sunz = sun_zenith_angle(tslot, lonlats[0], lonlats[1])

print "... create look-up-table"
#refl37 = Calculator(rsr)
refl37 = Calculator('Meteosat-9', 'seviri', 'IR3.9', solar_flux=sflux)
#refl37.make_tb2rad_lut('/tmp/seviri_37_tb2rad_lut.npz')
# new syntax -> 
#refl37.make_tb2rad_lut('IR3.9','/data/COALITION2/database/meteosat/SEVIRI/seviri_tb2rad_lut/')

print "... calculate reflectance"
r39 = refl37.reflectance_from_tbs(sunz, ch39.data, ch11.data, ch13.data) # , lookuptable='/tmp/seviri_37_tb2rad_lut.npz'

import numpy as np
r39 = np.ma.masked_array(r39, mask = np.logical_or(np.less(r39, -0.1), 
                                                   np.greater(r39, 3.0)))
print "... show new RGB image"
from mpop.imageo.geo_image import GeoImage
img = GeoImage((local_data[0.8].data, local_data[1.6].data, r39 * 100), area, 
               tslot, crange=((0, 100), (0, 70), (0, 30)), 
               fill_value=(0, 0, 0), mode="RGB")
img.enhance(gamma=1.7)
img.show()
