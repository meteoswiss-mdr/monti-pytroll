from datetime import datetime
from satpy import Scene
from satpy.utils import debug_on

debug_on()

# https://sentinel.esa.int/web/sentinel/user-guides/sentinel-3-olci/naming-convention
# MMM_OL_L_TTTTTT_yyyymmddThhmmss_YYYYMMDDTHHMMSS_YYYYMMDDTHHMMSS_[instance ID]_GGG_[class ID].SEN3
# S3A_OL_1_EFR____20151102T094537_20151102T094837_20151103T075458_0180_090_022______LN2_D_NT_001.SEN3
# https://sentinel.esa.int/web/sentinel/sentinel-data-access
# https://www.onda-dias.eu/cms/services/catalogues/download/  use firefox !!!!
# https://catalogue.onda-dias.eu/catalogue/
# https://sobloo.eu/data/satellites/sentinel-2


scn = Scene(
    sensor='olci',
    start_time=datetime(2016, 10, 20, 8, 12),
    end_time=datetime(2016, 10, 20, 8, 16),
    base_dir="/var/tmp/data/sentinel3")
composite = 'true_color'
scn.load([composite]) 
newscn = scn.resample('euron1')
newscn.show(composite)
