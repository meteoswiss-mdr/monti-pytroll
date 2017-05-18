#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

"""Test the mpop reader for overshooting top detection by Kris Bedka
"""

from mpop.satellites import GeostationaryFactory
from datetime import datetime
from mpop.projector import get_area_def
import sys
import inspect

from satpy.utils import debug_on
debug_on()

area = get_area_def("ccs4")

if len(sys.argv) == 1:
    #from my_msg_module import get_last_SEVIRI_date
    #tslot = get_last_SEVIRI_date(True, delay=5)
    #tslot = datetime(2013, 10, 11, 11, 30)
    tslot = datetime(2015, 7, 7, 15, 10)
    #tslot = datetime(2015, 10, 15, 11, 00)
elif len(sys.argv) == 6:
    year   = int(sys.argv[1])
    month  = int(sys.argv[2])
    day    = int(sys.argv[3])
    hour   = int(sys.argv[4])
    minute = int(sys.argv[5])
    tslot = datetime(year, month, day, hour, minute)
else:
    print("\n*** Error, wrong number of input arguments")
    print("    usage:")
    print("    python "+inspect.getfile(inspect.currentframe()))
    print("    or")
    print("    python "+inspect.getfile(inspect.currentframe())+" 2017 2 17 14 35\n")
    quit()

print ("*** plot overshooting top detection for ", str(tslot))

glbd = GeostationaryFactory.create_scene("msg-ot", "", "Overshooting_Tops", tslot)

print ("... load sat data")

#    vars_1d = ['latitude','longitude','time']
#    vars_3d = ['ir_brightness_temperature',
#               'ot_rating_ir',
#               'ot_id_number',
#               'ot_anvilmean_brightness_temperature_difference',
#               'ir_anvil_detection',
#               'visible_reflectance',
#               'ot_rating_visible',
#               'ot_rating_shadow',
#               'ot_probability',
#               'surface_based_cape',
#               'most_unstable_cape',
#               'most_unstable_equilibrium_level_temperature',
#               'tropopause_temperature',
#               'surface_1km_wind_shear',
#               'surface_3km_wind_shear',
#               'surface_6km_wind_shear',
#               'ot_potential_temperature',
#               'ot_height',
#               'ot_pressure',
#               'parallax_correction_latitude',
#               'parallax_correction_longitude']

#varnames=['ir_brightness_temperature']
#varnames=['visible_reflectance']
varnames=['ir_anvil_detection']
#varnames=['ot_rating_ir']
#varnames=['ot_anvilmean_brightness_temperature_difference']
#varnames=['latitude','longitude']

glbd.load(varnames)  #, area_extent=area.area_extent

varname=varnames[0]
print (glbd[varname].data.shape)
print (glbd[varname].data)
max_data = glbd[varname].data.max()
min_data = glbd[varname].data.min()


from trollimage.image import Image as trollimage
from trollimage.colormap import rainbow
colormap=rainbow

if False:
    img = trollimage(glbd[varname].data, mode="L")  # , fill_value=0
    if colormap.values[0] == 0.0 and colormap.values[-1]==1.0:  # scale normalized colormap to range of data 
        colormap.set_range(min_data, max_data)
    img.colorize(colormap)
    img.show()

area="ccs4" #
local_data = glbd.project(area)

print(local_data[varname].data.shape)

if True:
    for varname in varnames:
      img = trollimage(local_data[varname].data, mode="L")  # , fill_value=0
      if  colormap.values[0] == 0.0 and colormap.values[-1]==1.0:  # scale normalized colormap to range of data 
          colormap.set_range(min_data, max_data)
      img.colorize(colormap)
      #img.show()
      PIL_image=img.pil_image()
      outputFile = "MSG_OT-"+varname.replace("_", "-")+"-ccs4_"+tslot.strftime("%Y%m%d%H%M")+".png"
      print("... display "+outputFile" &")
      PIL_image.save(outputFile, optimize=True)
    
#print "... show new RGB image"
#from mpop.imageo.geo_image import GeoImage
#img = GeoImage((local_data[0.8].data, local_data[1.6].data, r39 * 100), area, 
#               tslot, crange=((0, 100), (0, 70), (0, 30)), 
#               fill_value=(0, 0, 0), mode="RGB")
#img.enhance(gamma=1.7)
#img.show()
