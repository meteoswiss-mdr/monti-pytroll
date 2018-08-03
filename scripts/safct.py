# -*- coding: utf-8 -*-
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from mpop.imageo import palettes
from mpop.imageo import geo_image
import datetime
from pyresample import image, geometry
from PIL import Image
from pycoast import ContourWriterAGG
import aggdraw
from mpop.projector import get_area_def 

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

from mpop.utils import debug_on
debug_on() 

from trollimage.colormap import rdbu, greys, rainbow, spectral
from trollimage.image import Image as trollimage

import datetime

debug_on()

time_slot = datetime.datetime(2015, 7, 8, 12, 00)

global_data = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot)

global_data.load(["CloudType"], calibrate=False)

print global_data

prod = "CloudType"

global_data = global_data.project("ccs4", precompute=True)

img = trollimage(global_data[prod].cloudtype, mode="P",palette=global_data[prod].cloudtype_palette)

img.save('./CTtest.png')


img = trollimage(global_data[prod].cloudphase, mode="P",palette=global_data[prod].cloudphase_palette)

img.save('./CT_PHASEtest.png')


