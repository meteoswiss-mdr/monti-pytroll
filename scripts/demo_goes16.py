from satpy import Scene
from glob import glob
filenames = glob("/store/msrad/sat/goes-16/2017/04/05/*s20170952100319_e20170952100377*")
global_scene = Scene(reader="abi_l1b", filenames=filenames)
