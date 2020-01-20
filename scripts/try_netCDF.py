from __future__ import division
from __future__ import print_function

from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime
time_slot = datetime.datetime(2014, 0o7, 16, 13, 30)
time_slot = datetime.datetime(2014, 0o7, 23, 00, 0o5)
global_data = GeostationaryFactory.create_scene("meteosat", "00", "seviri", time_slot)
europe = get_area_def("ccs4")
global_data.load([0.6, 0.8, 1.6, 3.9, 6.2, 7.3, 8.7, 9.7, 10.8, 12.0, 13.4, 'HRV']) #, area_extent=europe.area_extent
print(global_data)
rgb='IR_108'
min_data=global_data[rgb].data.min()
max_data=global_data[rgb].data.max()
img = global_data.image.channel_image(rgb)
#img = global_data.image.hr_overview()
print(type(img))
print(dir(img))
print("min/max", min_data, max_data)
#img.show()
PIL_image=img.pil_image() 
outputFile='test_IR_108.png'
img.save(outputFile, optimize=True)
print("save file as ", outputFile)
