from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy

# old version of satpy before 0.8 
#from satpy import Scene
#from satpy.utils import debug_on
#debug_on()

#from glob import glob
#base_dir="/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/2015/07/07/"
#import os
#os.chdir(base_dir)
#filenames = glob("*201507071200*__")
#print (base_dir)
#print (filenames)
##global_scene = Scene(reader="hrit_msg", filenames=filenames, base_dir=base_dir, ppp_config_dir="/opt/users/hau/PyTroll//cfg_offline/")
#global_scene = Scene(reader="hrit_msg", filenames=filenames, base_dir=base_dir, ppp_config_dir="/opt/users/hau/PyTroll/packages/satpy/satpy/etc")


# new version of satpy after 0.8
#################################

from satpy import Scene, find_files_and_readers
from datetime import datetime

#NWC SAF product to be read 
#p_ = "CTTH"
#rgb="cloud_top_temperature"
#product="ctth_tempe"
#p_ = "CT"
#rgb = "cloudtype"
#product="ct"
p_ = "CMA"
rgb = "cloudmask"
product="cma"

#start_time=datetime(2017, 7, 7, 12, 15)
#end_time=datetime(2017, 7, 7, 12, 15)
#base_dir_sat = start_time.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/%Y/%m/%d/")
#base_dir_nwc = start_time.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/"+p_+"/")

from my_msg_module import get_last_SEVIRI_date
start_time = get_last_SEVIRI_date(False, delay=5)
#start_time = datetime(2020, 3, 22, 12, 45)
end_time   = start_time
print("produce ndvi plot for ", start_time)
#base_dir_sat = start_time.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/%Y/%m/%d/")
#base_dir_nwc = start_time.strftime("/data/OWARNA/hau/database/meteosat/SAFNWC/%Y/%m/%d/"+p_+"/")        #v2016, EUMETSAT
base_dir_sat = start_time.strftime("/data/cinesat/in/eumetcast1/")
base_dir_nwc = start_time.strftime("/data/cinesat/in/eumetcast1/")        #v2016, netCDF, EUMETSAT product for Europe area 

#base_dir_nwc = start_time.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/"+p_+"/")  #v2016, Alps

print("===============================")
print("plot an ndvi image for date", start_time)

#def find_files_and_readers(start_time=None, end_time=None, base_dir=None,
#                           reader=None, sensor=None, ppp_config_dir=get_environ_config_dir(),
#                           filter_parameters=None, reader_kwargs=None):


files_sat = find_files_and_readers(sensor='seviri',  
                               start_time=start_time,  
                               end_time=end_time,  
                               base_dir=base_dir_sat,  
                               #base_dir=start_time.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/%Y/%m/%d/"),  
                               reader='seviri_l1b_hrit')

# remove all other MSG satellites (except MSG4) and unused channels
sat="MSG4"
files = deepcopy(files_sat['seviri_l1b_hrit'])
for f in files:
    if not (sat in f):
        files_sat['seviri_l1b_hrit'].remove(f)
        continue
    if ("HRV" in f)  or ("IR_016" in f) or ("IR_039" in f):  # or ("VIS006" in f) or ("VIS008" in f)
        files_sat['seviri_l1b_hrit'].remove(f)
        continue
    if  ("WV_062" in f) or ("WV_073" in f)  or ("IR_087" in f) or ("IR_097" in f) or ("IR_108" in f) or ("IR_120" in f) or ("IR_134" in f):
        files_sat['seviri_l1b_hrit'].remove(f)
        continue
#print (files_sat)

    
files_nwc = find_files_and_readers(sensor='seviri',
                               start_time=start_time,
                               # BUG: !!! VERY IMPORTANT TO SPECIFY END TIME, OTHERWISE ARRAY ARE CONCATINATED ALONG THE Y AXIS !!!
                               end_time=end_time,    
                               #base_dir="/data/COALITION2/database/meteosat/SAFNWC_v2013/2015/07/07/",
                               base_dir = base_dir_nwc,
                               #base_dir=start_time.strftime("/data/OWARNA/hau/database/meteosat/SAFNWC/%Y/%m/%d/"+p_+"/"),
                               reader='nwcsaf-geo')



###################################3
print("=======================")
print("read MSG files")
print(files_sat)
global_scene = Scene(filenames=files_sat)

#global_scene.load([0.6, 0.8, 10.8])
#global_scene.load(['IR_120', 'IR_134'])
#global_scene.load(['overview',0.6,0.8])
global_scene.load([0.6,0.8])
print(global_scene)

print("=======================")
print("files for NWCSAF")
print (files_nwc)

nwcsaf_scene = Scene(filenames=files_nwc)
#nwcsaf_scene.load([product])
#nwcsaf_scene.load(["cloudmask","cma"])
nwcsaf_scene.load(["cma"])

print("minimum ", product, np.nanmin(nwcsaf_scene[product].values))
print("maximum ", product, np.nanmax(nwcsaf_scene[product].values))
print("nwcsaf_scene.datasets",nwcsaf_scene.datasets)

print("=======================")
print("show ",product)
#nwcsaf_scene[product].plot()

plt.imshow(nwcsaf_scene[product].values, vmax=2)
plt.show()


global_scene.available_dataset_names()
#print(global_scene[0.6])            # works only if you load also the 0.6 channel, but not an RGB that contains the 0.6
#!!# print(global_scene['overview']) ### this one does only work in the develop version

#global_scene[0.8].plot()
#plt.show()

print("=======================")
print("calculate ndvi ",product)

global_scene["ndvi"] = (global_scene[0.8] - global_scene[0.6]) / (global_scene[0.8] + global_scene[0.6])

#from satpy import DatasetID
#my_channel_id = DatasetID(name='IR_016', calibration='radiance')
#global_scene.load([my_channel_id])
#print(scn['IR_016'])
print ("available_composite_names:", global_scene.available_composite_names())

# attributes of ndvi is empty
# attrs["area"] is not set for ndvi
# so we need to set at least the area to be able to resample the ndvi 
global_scene["ndvi"].attrs['area'] = global_scene["VIS008"].attrs['area']

#global_scene["ndvi"].plot()
#plt.show()

#area="EuropeCanaryS95"
area="mpef-ceu"
#local_scene = global_scene.resample("eurol")
local_scene = global_scene.resample(area)
nwc_local_scene = nwcsaf_scene.resample(area)

# NDVI is resampled when area attribut is set
#### !!! ndvi is not resampled!!!
###local_scene["ndvi"] = (local_scene[0.8] - local_scene[0.6]) / (local_scene[0.8] + local_scene[0.6])

#local_scene[0.8].plot()
#plt.show()

#local_scene["ndvi"].plot()
#plt.show()

nwc_local_scene[product].plot()
plt.imshow(nwc_local_scene[product].values, vmax=2)
plt.show()

local_scene["ndvi"].values =  np.where(nwc_local_scene[product].values == 0, local_scene["ndvi"].values, np.nan)

print("===========================")
print("fill missing (cloudy and night) areas with last observations")
import netCDF4 as nc
bg_file="MSG_NDVI-"+area+"_background.nc"
from os import path
if path.exists(bg_file):
    print("update data field with "+bg_file)
    fh_backg = nc.Dataset(bg_file, mode='r')
    ndvi_backg = fh_backg.variables["ndvi"][:]
    fh_backg.close()
    # update current observation with background 
    local_scene["ndvi"].values =  np.where(np.logical_or(~np.isnan(local_scene["ndvi"].values),local_scene["ndvi"].values>=0.0), local_scene["ndvi"].values, ndvi_backg)
else:
    print("no background available, initialize background file: "+bg_file)
    ##local_scene["ndvi"].to_netcdf(bg_file) this produces an error, wrong attribute values
    ##print(local_scene["ndvi"])

# save updated (or first observation of) NDVI as new background  
local_scene.save_dataset("ndvi", bg_file)
    
print("===========================")
print("save dataset")
#local_scene.show('overview')
#local_scene.save_dataset('overview', './local_overview.png')
#nwc_local_scene.save_dataset('cloudmask', './local_cloudmask.png')

#local_scene.save_dataset(0.6, './MSG4_VIS006.nc')
local_scene.save_dataset("ndvi", start_time.strftime('./MSG_NDVI-'+area+'_%y%m%d%H%M.nc'))

print("===========================")
print("produce troll image")
#local_scene.save_dataset('ndvi', './local_ndvi.png')
from trollimage.image import Image as trollimage
#from trollimage.colormap import rdylgn
from trollimage.colormap import ndvi
#rdylgn.set_range( -1., +1.)
img = trollimage(local_scene["ndvi"].values, mode="L")

print("===========================")
print("colorize troll image")
#img.colorize(rdylgn)
img.colorize(ndvi)
from pycoast import ContourWriterAGG
cw = ContourWriterAGG('/data/OWARNA/hau/maps_pytroll/')
# define area
proj4_string = local_scene[0.6].attrs['area'].proj4_string      
# e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
area_extent  = local_scene[0.6].attrs['area'].area_extent              
# e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
area_tuple = (proj4_string, area_extent)
PIL_image = img.pil_image()

print("===========================")
print("add borders to image")
cw.add_borders(PIL_image, area_tuple, outline='white', resolution='l', width=1)
cw.add_coastlines(PIL_image, area_tuple, outline='white', resolution='l', width=1)
PIL_image.save(start_time.strftime('./MSG_NDVIb-'+area+'_%y%m%d%H%M.png'))


print("===========================")
