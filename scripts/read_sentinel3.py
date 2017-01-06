from datetime import datetime
from satpy import Scene
from satpy.utils import debug_on

debug_on()

scn = Scene(
    sensor='olci',
    start_time=datetime(2016, 10, 20, 8, 12),
    end_time=datetime(2016, 10, 20, 8, 16),
    base_dir="/var/tmp/data/sentinel3")
composite = 'true_color'
scn.load([composite]) 
newscn = scn.resample('euron1')
newscn.show(composite)
