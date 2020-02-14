from datetime import datetime
from satpy.resample import get_area_def
from satpy.scene import Scene
from satpy.utils import debug_on
from my_msg_module import get_last_SEVIRI_date

debug_on()

if __name__ == '__main__':

    scn = Scene(
        sensor='ahi',
        start_time=datetime(2016, 11, 25, 8, 0),
        end_time=datetime(2016, 11, 25, 8, 10),
        base_dir="/data/cinesat/in/eumetcast1/"
    )

    print scn
    print scn.available_composites()

    composite = 'B09'

    areadef = get_area_def("australia")
    scn.load(['true_color'])
    scn['true_color'].mask[scn['true_color'] < 0] = True
    scn['true_color'][scn['true_color'] < 0] = 0
    scn['true_color'][scn['true_color'] > 110] = 110

    import numpy as np
    info = scn['true_color'].info
    scn['true_color'] = np.ma.log10(scn['true_color'] / 100.0)
    scn['true_color'] = (scn['true_color'] - np.log10(0.0223)
                         ) / (1.0 - np.log10(0.0223)) * 100
    scn['true_color'].info = info
    scn.show('true_color')
