from __future__ import division
from __future__ import print_function

from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime
from my_msg_module import get_last_SEVIRI_date
from pycoast import ContourWriterAGG
from mpop.projector import get_area_def

time_slot = get_last_SEVIRI_date(False, delay=15)
#time_slot = datetime.datetime(2015, 12, 18, 12, 30)
print(str(time_slot))

global_data = GeostationaryFactory.create_scene("cpp", "10", "seviri", time_slot)
#europe = get_area_def("EuropeCanaryS95")
#channels = ['cth']
#channels = ['cot']
channels = ['precip']
#channels = ['reff']
#channels = ['cth', 'cot','precip']
chn=channels[0]
global_data.load(channels)  # , area_extent=europe.area_extent
print(global_data)

area="EuropeCanaryS95"
area="ccs4"
data = global_data.project(area, precompute=True)

from trollimage.colormap import rainbow
colormap = rainbow
min_data = data[chn].data.min()
max_data = data[chn].data.max()
if chn=='cth':
    min_data=0
    max_data=12000

colormap.set_range(min_data, max_data)
from trollimage.image import Image as trollimage
img = trollimage(data[chn].data, mode="L", fill_value=[1,1,1]) # fill_value=[0,0,0]
img.colorize(colormap)
PIL_image=img.pil_image()

obj_area = get_area_def(area)
print('obj_area ', obj_area)
proj4_string = obj_area.proj4_string     
# e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
print('proj4_string ',proj4_string)
area_extent = obj_area.area_extent              
# e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
area_def = (proj4_string, area_extent)

if True:
   #cw = ContourWriterAGG('/data/OWARNA/hau/pytroll/shapes/')
   cw = ContourWriterAGG('/opt/users/common/shapes/')
   resolution='l'
   if area=='ccs4':
       resolution='h'
   #outline = (255, 0, 0)
   #outline = 'white'
   outline = 'red'
   cw.add_coastlines(PIL_image, area_def, outline='blue', resolution=resolution, level=2, width=1)  #, outline_opacity=127, outline_opacity=0
   #cw.add_coastlines(PIL_image, area_def, outline=outline, resolution=resolution, width=2)  #, outline_opacity=0
   cw.add_borders(PIL_image, area_def, outline=outline, resolution=resolution, width=2)       #, outline_opacity=0 


if True:
    from plot_msg import add_title
    from pydecorate import DecoratorAGG

    if socket.gethostname()[0:5] == 'zueub':
        font_file = "/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf"
    elif socket.gethostname()[0:7] == 'keschln' or socket.gethostname()[0:7]=="eschaln":
        font_file = "/usr/share/fonts/dejavu/DejaVuSansMono.ttf"
    else:
        print("*** ERROR, unknown computer, unknown location of the ttf-file")
        quit()

    dc = DecoratorAGG(PIL_image)
    title="Cloud Physical Properties (Roebeling, 2009), %Y-%m-%d %H:%MUTC, %(area)s\n%(rgb)s"
    add_title(PIL_image, title, chn, "cpp", "10", time_slot, area, dc, font_file, True, title_color='red' )

#img.show()
PIL_image.show()
