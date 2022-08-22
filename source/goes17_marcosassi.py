#!/usr/bin/python
#
#  python  geos17_processing.py

# general modules
# -------------------------
import glob
import os
import sys
import time, datetime
from path import Path
from PIL import Image, ImageFont, ImageDraw, PngImagePlugin
import numpy as np
import shutil

# Pytroll modules
# -------------------------
from satpy.scene import Scene
from satpy.utils import debug_on
from satpy.writers import to_image, get_enhanced_image
import pyninjotiff
from pycoast import ContourWriter

# debug mode for Pytroll modules
# -------------------------
debug_on()
import warnings
warnings.filterwarnings("ignore")

# defines working variables
# -------------------------
goes_input_dir      = '/var/tmp/goes17/'
goes_PNG_output_dir = '/opt/pytroll/outbox/intranet/'
goes_TIF_output_dir = '/opt/pytroll/outbox/ninjo/'
goes_TIF_PROD_dir   = '/opt/pytroll/outbox/ninjo_prod/'
shapes_dir          = '/opt/pytroll/shapes/'
tiffdump_file       = '/var/tmp/goes17.tif'

sat_live = True

print("")
print("---------------------------------------")
print("---------- GOES-17 processing ---------")
print("---------------------------------------")
print("")

# extract timestamp from last incoming ABI file
# ---------------------------------------------
ABI_files = glob.glob(goes_input_dir + 'OR_ABI-L1b*.nc')

if not ABI_files:
    print("===============================================")
    print("GOES-17 data not available, skip processing....")
    print("===============================================")
    sys.exit()

latest_ABI_file = os.path.basename(max(ABI_files, key=os.path.getctime))
print("latest GOES17 file-> ", latest_ABI_file)

starttime = (latest_ABI_file[latest_ABI_file.find("s")+1:latest_ABI_file.find("_e")])
year   = starttime[0:4]
julian = starttime[4:7]
hours  = starttime[7:9]
min    = starttime[9:11]
stime  = datetime.datetime(int(year), 1, 1) + datetime.timedelta(int(julian)-1) + datetime.timedelta(hours=int(hours)) + datetime.timedelta(minutes=int(min))
print("starttime --> ", stime)

# timestamp for final products
timestamp = year + str(stime.month).zfill(2) + str(stime.day).zfill(2) + hours + min

endtime = (latest_ABI_file[latest_ABI_file.find("e")+1:latest_ABI_file.find("_c")])
year   = endtime[0:4]
julian = endtime[4:7]
hours  = endtime[7:9]
min    = endtime[9:11]
etime  = datetime.datetime(int(year), 1, 1) + datetime.timedelta(int(julian)-1) + datetime.timedelta(hours=int(hours)) + datetime.timedelta(minutes=int(min))
print("endtime     --> ", etime)

# select channels
# -----------------------------

channels = ['C02', 'C08', 'C13']
channel_list_to_process = [] 

channels_to_ninjo = {}
channels_to_ninjo['C02'] = [ 'GOES-17 channel C02', 'VIS006', 'nrGOESW8km']
channels_to_ninjo['C08'] = [ 'GOES-17 channel C08', 'WV062', 'nrGOESW8km']
channels_to_ninjo['C13'] = [ 'GOES-17 channel C13', 'IR107', 'nrGOESW8km']

# check which channel is available, with a correct timestamp
for goes17_channel in channels:
    pattern = 'OR_ABI-L1b*M?' + goes17_channel + '*' + starttime + '*.nc'
    if glob.glob(goes_input_dir + pattern):
        print ("GOES-17 data channel " + goes17_channel + " is available")
        channel_list_to_process.append(goes17_channel)
    else:
        print ("GOES-17 data channel " + goes17_channel + " is not available")


# exit if there are no products to process
# ---------------------------------------
if not channel_list_to_process:
    print("=======================================")
    print("no realtime GOES-17 data to process")
    sys.exit("no products to process --> exit")

# exit if data timestamp older is than 1 hour
# -------------------------------------------
now = datetime.datetime.now()
if now - datetime.timedelta(minutes=60) <= stime <= now:
    print "GOES-17 data are on time"
else:
    print("===================================================")
    sys.exit("GOES-17 data are older than 1 hour --> exit")


# build scene 
# -------------------------------
try:
#    scn = Scene(
#        platform_name = "GOES-17",   
#        sensor = "abi",
#        start_time = stime,
#        end_time = etime,
#        base_dir = goes_input_dir,
#        reader = 'abi_l1b'
#    )

    scn = Scene(reader="abi_l1b", filenames=ABI_files)

except:
    print("===================================================")
    sys.exit("GOES-17 data could not be loaded (different timestamp?)")

cw = ContourWriter(shapes_dir)

# start resampling and produce output  
# ------------------------------------
from satpy.resample import get_area_def
areaid = 'NinJoGOESWregion'
areadef = get_area_def(areaid)

for channel in channel_list_to_process:
    print ("Processing channel " + channel + "...")
    # file name build on Cinesat  "pattern" --> GOES15-W_IR107_nrGOESW8km_1709130700.tif
    outfile = 'GOES17-W_' + channels_to_ninjo.get(channel)[1] + '_' + channels_to_ninjo.get(channel)[2] + '_' + timestamp[2:]
    
    try:
        scn.load([channel])
    except:
        print("===================================================")
        sys.exit("GOES-17 data " + channel + " could not be loaded (different timestamp?)")


    lcd = scn.resample(areadef, cache_dir='/var/tmp/sam/')

    if channel == 'C02':
        lcd.save_dataset(channel, filename = tiffdump_file,
                         writer='ninjotiff',
                         ninjo_product_name = 'G17_'+ channel,
                         zero_seconds=True)
    else:
        # Min and max values in Celsius
        value_min = -87.5
        value_max = 40

     #   lcd[channel].clip(value_min - 273.15, value_max - 273.15)

        # physic_unit='C' is used to invert the color table
        lcd.save_dataset(channel, filename = tiffdump_file,
                         writer='ninjotiff',
                         ninjo_product_name = 'G17_'+ channel,
                         physic_unit='K',
                         zero_seconds=True,
                         enhancement_config=False,
                         fill_value=255,
                         ch_max_measurement_unit=value_max,
                         ch_min_measurement_unit=value_min)
                         
    
    # make a copy just for NinJO....
    shutil.copyfile(tiffdump_file, goes_TIF_output_dir + outfile + '.tif')
    print('copied to --> ', goes_TIF_output_dir + outfile + '.tif')

    # make a copy for the PROD delivery to NinJo
    shutil.copyfile(tiffdump_file, goes_TIF_PROD_dir + outfile + '.tif')
    print('copied to --> ', goes_TIF_PROD_dir + outfile + '.tif')

    # save as PNG graphic file
    img = get_enhanced_image(lcd[channel])
    if channel <> 'C02': img.invert()
    # stretching needed because was deactivated as "dummy" in satpy/etc/enhancements/generic.yaml to avoid "stretching" for ninjotiff
    img.save(goes_PNG_output_dir + outfile + '.png')

    # add borders & coasts
    img = Image.open(goes_PNG_output_dir + outfile  + '.png')
    cw.add_coastlines(img, areadef)
    cw.add_borders(img, areadef, resolution='i')

    # save as png graphic file
    img.save(goes_PNG_output_dir + outfile + '.png')

    # GOES-17 images resized only for the satellite LIVE
    # --------------------------------------------------
    if sat_live:
        basewidth=1200
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        img = img.crop((0+basewidth/7, 0+hsize/7, basewidth-basewidth/7, hsize-hsize/7))
        img.convert('RGB').save(goes_PNG_output_dir + outfile + '.jpg')

# ----------------------
# cleanup
# -----------------------
d = Path(goes_PNG_output_dir)

removed = 0
hours = 6
time_in_secs = time.time() - hours*3600

for file in d.walk():
    if file.isfile():
        if file.mtime <= time_in_secs:
            file.remove()
            removed += 1

print "---------"
print "removed old GOES-17 products --> ", removed
print("---------------------------------------")
