from satpy import Scene
from glob import glob
import socket

if 'zueub' in socket.gethostname():
    #MeteoSwiss
    filenames = glob("/data/COALITION2/database/goes-16/2017/04/05/*s20170952100319_e20170952100377*")
else:
    #kesch/CSCS
    filenames = glob("/store/msrad/sat/goes-16/2017/04/05/*s20170952100319_e20170952100377*")

print filenames
global_scene = Scene(reader="abi_l1b", filenames=filenames)
