from glob import glob
import numpy as np
from satpy import Scene, find_files_and_readers
from datetime import datetime

#start_time=datetime(2020, 2, 12, 12, 15)
#end_time=datetime(2020, 2, 12, 12, 15)

file_land = find_files_and_readers(base_dir="/data/COALITION2/database/LandSeaMask/LandCover",  
                                   reader='generic_image')

print(file_land)
