from __future__ import print_function
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime

from my_msg_module import get_last_SEVIRI_date
import logging

LOG = logging.getLogger(__name__)

time_slot = get_last_SEVIRI_date(False, delay=10)
LOG.debug("*** read radar data for "+str(time_slot))

global_radar = GeostationaryFactory.create_scene("odyssey", "", "radar", time_slot)

#prop_str='DBZH'
prop_str='RATE'
global_radar.load([prop_str])
print(global_radar)

#area="EuropeCanaryS95"
area='EuropeOdyssey95'
#europe = get_area_def(area)
local_radar = global_radar.project(area)

fill_value=None # transparent background 
#fill_value=(1,1,1) # white background 
min_radar = 0.0
max_radar = 150
from trollimage.colormap import RainRate
colormap = RainRate

LOG.debug("... min_radar/max_radar: "+str(min_radar)+" / "+str(max_radar))
colormap.set_range(min_radar, max_radar)

from trollimage.image import Image as trollimage
img = trollimage(local_radar[prop_str].data, mode="L", fill_value=fill_value)
img.colorize(colormap)
# img.show()


PIL_image=img.pil_image()
from pycoast import ContourWriterAGG
cw = ContourWriterAGG('/opt/users/common/shapes/')
obj_area = get_area_def(area)
area_def = (obj_area.proj4_string, obj_area.area_extent)
resolution='l'
cw.add_coastlines(PIL_image, area_def, outline='white', resolution=resolution, outline_opacity=127, width=1, level=2)
cw.add_borders(PIL_image, area_def, outline='white', resolution=resolution, width=1)       #, outline_opacity=0 

add_colorscale=True
if add_colorscale:
    print('... add colorscale ranging from min_radar (',min_radar,') to max_radar (',max_radar,')')
    from pydecorate import DecoratorAGG
    dc = DecoratorAGG(PIL_image)
    dc.align_right()
    dc.write_vertically()
    ticks=20
    tick_marks=20        # default
    minor_tick_marks=10  # default
    fontsize=18
    units=global_radar[prop_str].info["units"]
    import aggdraw
    font = aggdraw.Font("black","/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif-Bold.ttf",size=16)
    colormap_r = colormap.reverse()
    dc.add_scale(colormap_r, extend=True, ticks=ticks, tick_marks=tick_marks, minor_tick_marks=minor_tick_marks, font=font, line_opacity=100, unit=units) #


show_image=True
if show_image:
    PIL_image.show()
else:
    outputDir="./"
    outputFile = time_slot.strftime(outputDir+'/ODY_'+prop_str+'-'+area+'_%Y%m%d%H%M.png')
    print('... save image as '+outputFile)
    PIL_image.save(outputFile)
