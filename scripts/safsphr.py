# -*- coding: utf-8 -*-
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from mpop.imageo import palettes
from mpop.imageo import geo_image
from pyresample import image, geometry
from PIL import Image
from pycoast import ContourWriterAGG
from mpop.projector import get_area_def 

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

import datetime
import aggdraw

from mpop.utils import debug_on
debug_on() 

from trollimage.colormap import rdbu, greys, rainbow, spectral
from trollimage.image import Image as trollimage

import datetime

#SAFNWC_MSG2_CT___201412021350_alps________.h5

debug_on()

time_slot = datetime.datetime(2015, 7, 9, 13, 00)

#area = get_area_def("alps") 

global_data = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot)

prod = "SPhR"

global_data.load([prod], calibrate=False)

global_data = global_data.project("ccs4")


img = trollimage(global_data[prod].sphr_bl, mode="P",palette=global_data[prod].sphr_bl_palette)

img.save('./SPHR_BL_test.png')


img = trollimage(global_data[prod].sphr_hl, mode="P",palette=global_data[prod].sphr_hl_palette)

img.save('./SPHR_HL_test.png')


img = trollimage(global_data[prod].sphr_ki, mode="P",palette=global_data[prod].sphr_ki_palette)

img.save('./SPHR_KI_test.png')


img = trollimage(global_data[prod].sphr_li, mode="P",palette=global_data[prod].sphr_li_palette)

img.save('./SPHR_LI_test.png')


img = trollimage(global_data[prod].sphr_ml, mode="P",palette=global_data[prod].sphr_ml_palette)

img.save('./SPHR_ML_test.png')


img = trollimage(global_data[prod].sphr_shw, mode="P",palette=global_data[prod].sphr_shw_palette)

img.save('./SPHR_SHW_test.png')

print type(global_data[prod].sphr_tpw)

img = trollimage(global_data[prod].sphr_tpw, mode="P",palette=global_data[prod].sphr_tpw_palette)

img.save('./SPHR_TPW_test.png')

print type(global_data[prod].sphr_cape)

# no palette 
img = trollimage(global_data[prod].sphr_cape, mode="L") 
from trollimage.colormap import rainbow
rainbow.set_range(0, 250)
img.colorize(rainbow)

img.save('./SPHR_CAPE_test.png')


del global_data

global_data = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot)
global_data.load(["SPhR"]) #, calibrate=False
global_data = global_data.project("ccs4")

# no palette 
img = trollimage(global_data[prod].sphr_tpw, mode="L") 
min_data=global_data[prod].sphr_tpw.min()
max_data=global_data[prod].sphr_tpw.max()
from trollimage.colormap import rainbow
rainbow.set_range(min_data, max_data)
img.colorize(rainbow)
img.save('./SPHR_TPW_test2.png')
