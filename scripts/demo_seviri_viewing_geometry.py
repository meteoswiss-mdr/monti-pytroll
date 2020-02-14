from __future__ import print_function

from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime

## uncomment these two lines for more debugging information
#from mpop.utils import debug_on
#debug_on()

from my_msg_module import get_last_SEVIRI_date
time_slot = get_last_SEVIRI_date(True, delay=5)
#time_slot = datetime.datetime(2015, 11, 26, 19, 30)
print (str(time_slot))

global_data = GeostationaryFactory.create_scene("Meteosat-9", "", "seviri", time_slot)
europe = get_area_def("EuropeCanaryS95")
#global_data.load(['vza','vaa','lat','lon'])  # , area_extent=europe.area_extent
global_data.load(['vza'])  # , area_extent=europe.area_extent
print (global_data)

area="EuropeCanaryS95"
data = global_data.project(area, precompute=True)

from trollimage.colormap import rainbow
colormap = rainbow
#chn = 'vaa'
chn = 'vza'
min_data = data[chn].data.min()
max_data = data[chn].data.max()
colormap.set_range(min_data, max_data)
from trollimage.image import Image as trollimage
img = trollimage(data[chn].data, mode="L", fill_value=[0,0,0])
img.colorize(colormap)
#img.show()

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
   from pydecorate import DecoratorAGG
   dc = DecoratorAGG(PIL_image)
   
   print('... add colorscale ranging from min (',min_data,') to max (',max_data,')')
   dc.align_right()
   dc.write_vertically()
   ticks=30
   tick_marks=10        # default
   minor_tick_marks=1  # default
   fontsize=16
   units=data[chn].info["units"]
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
