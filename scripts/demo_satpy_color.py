
from satpy.utils import debug_on
debug_on()


from satpy import find_files_and_readers, Scene
from datetime import datetime

files_sat = find_files_and_readers(sensor='seviri',
                               start_time=datetime(2017, 6, 6, 12, 0),
                               end_time=datetime(2017, 6, 6, 12, 0),
                               base_dir="/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/2017/06/06/",
                               reader="seviri_l1b_hrit")

files = dict(files_sat.items())
global_scene = Scene(filenames=files) # not allowed any more: reader="hrit_msg", 
global_scene.load([10.8])

area="EuropeCanaryS95"
local_scene = global_scene.resample(area)

import numpy as np
# from satpy.composites import BWCompositor     does not exist any more
from satpy.composites import GenericCompositor
from satpy.enhancements import colorize
from satpy.writers import to_image

arr = np.array([[0, 0, 0], [255, 0, 0]])
np.save("/tmp/binary_colormap.npy", arr)

# compositor = BWCompositor("test", standard_name="colorized_ir_clouds")
compositor = GenericCompositor("test", standard_name="colorized_ir_clouds")
composite = compositor((local_scene[10.8], ))
img = to_image(composite)

kwargs = {"palettes": [{"filename": "/tmp/binary_colormap.npy",
          "min_value": 223.15, "max_value": 303.15}]}

kwargs = {"palettes": [{"colors": "spectral",
          "min_value": 223.15, "max_value": 303.15}]}

colorize(img, **kwargs)

img.show()
