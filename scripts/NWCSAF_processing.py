###
###!/opt/users/common/packages/anaconda351/envs/PyTroll_sam/bin/python

#
# -->  python  read_NWCSAF_nc.py  2017-04-11T11:30:00Z

# general modules
# -------------------------
import sys
import os
import re
import glob
import nwcsaf
import itertools
import logging
import time 
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw, ImageOps, PngImagePlugin

# Pytroll modules
# -------------------------
from satpy import Scene, find_files_and_readers
from satpy.utils import debug_on
from satpy.writers import to_image
from pycoast import ContourWriter
import pyninjotiff

# debug mode for Pytroll modules
# -------------------------
debug_on()

# defines working variables
# -------------------------
NWCSAF_dir       = "/opt/safnwc/"
#sat_input_dir    = NWCSAF_dir + "import/Sat_data/"
sat_input_dir    = "/data/cinesat/in/eumetcast1/"
#input_dir        = NWCSAF_dir + "postprocessing/"
input_dir        = "/data/cinesat/in/safnwc/"
#output_dir       = NWCSAF_dir + "export/PNG/"
output_dir       = "/data/cinesat/out/"
#output_ninjo_dir = NWCSAF_dir + "export/ninjo/"
output_ninjo_dir = "/data/cinesat/out/"
log_dir          = NWCSAF_dir + "export/LOG/"
log_dir          = "/data/cinesat/out/"
shapes_dir       = '/opt/users/common/shapes'
Lucida_font      = '/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf'

HRIT_EPI_pattern = 'H-000-MSG?__-MSG?_???____-_________-EPI______-*-__'
SAFNWC_pattern   = 'S_NWC_*.nc'

os.chdir(input_dir)

# graphical PNG options
# -------------------------
borders      = True
legend       = False
header       = True
png_metadata = False
display_info = False

# Generate NWCSAF  ninjo tiff products
ninjoTiff    = True

# function to extract keywords from log file
# -------------------------------------------
def extract_data_from_log(keywords, logfile) :
# -------------------------------------------
    os.chdir(log_dir)
    metadata = []
    pattern = re.compile('|'.join(keywords))
    logfile_name = [os.path.basename(x) for x in glob.glob(logfile)]

    try:
        with open(logfile_name[0], 'rb') as f:
            textfile_temp = f.readlines()
            for line in textfile_temp:
                if pattern.search(line):
                     metadata.append(str.rsplit(line, '[I]')[-1].strip())
        return metadata

    except :
        print ('LOG file ' + logfile + ' not found!')
        return ['']



# --------------------------------------------------------------------------
# find the sat_mode (RSS or NOMINAL) parsing the last file name in the SAT input folder
list_of_files_import_Sat = glob.glob(sat_input_dir + HRIT_EPI_pattern)
latest_file_import_Sat = max(list_of_files_import_Sat, key=os.path.getctime)

# find the sat data (name and id) parsing the last file name in the input processing folder
sat_name = 'MeteoSat-11'
sat_id   = 'MSG4'
RSS = False
if glob.glob(input_dir + SAFNWC_pattern):
    list_of_files = glob.glob(input_dir + SAFNWC_pattern)
    latest_file = max(list_of_files, key=os.path.getctime)
    print('FILENAME --> ', latest_file)
    if 'RSS' in latest_file_import_Sat:
        RSS = True
    else:
        RSS = False

    if 'MSG2' in latest_file:
        sat_name = 'MeteoSat-9'
        sat_id   = 'MSG2'
    elif 'MSG3' in latest_file:
        sat_name = 'MeteoSat-10'
        sat_id   = 'MSG3'
    else:
        sat_name = 'MeteoSat-11'
        sat_id   = 'MSG4'
else:
    print('NO DATA in postprocessing --> assuming MSG4')



# read timestamp parameter and extract single values
# ---------------------------------------------------
if len(sys.argv) > 1:
    timeslot = sys.argv[1]    # input string --> '2017-04-11T11:30:00Z'
else:
    from my_msg_module import get_last_SEVIRI_date
    RSS=True
    start_time = get_last_SEVIRI_date(RSS, delay=5)
    timeslot = start_time.strftime("%Y-%m-%dT%H:%M:00Z")
    #print ("Terminating NWCSAF processing -->  missing timestamp as argument")    
    #sys.exit()
#
year  = timeslot[0:4]
month = timeslot[5:7]
day   = timeslot[8:10]
hours = timeslot[11:13]
min   = timeslot[14:16]

timestamp = year+month+day+hours+min
timestamp_NWCSAF = year+month+day+ 'T' + hours+min+'00Z'
time_slot = datetime(int(year), int(month), int(day), int(hours), int(min))
print ("PROCESSING timestamp : ", year, month, day, hours, min)



# verify which products can be processed
# --------------------------------------
#product_list = ['CMA', 'CT', 'CTTH', 'CMIC', 'PC', 'CRR', 'iSHAI', 'CI', 'RDT-CW', 'ASII-NG']   #PC-Ph, CRR-Ph, HRW,  
product_list = ['CMA', 'CT', 'CTTH']   #PC-Ph, CRR-Ph, HRW,  
#product_list = ['CMA', 'CT']   #PC-Ph, CRR-Ph, HRW,
product_list_to_process = []

# example --> S_NWC_LOG_MSG3_alps_20170509T083000Z.log
LOG_filename= log_dir + 'S_NWC_LOG_' + sat_id + '_*_'+ timestamp_NWCSAF + '.log'

# check which product is available...
# -----------------------------------
extension = '.nc'
# only cloud products have PLAX correction
# if product.startswith('cloud'):
#    extension = '_PLAX.nc'

for product in product_list:
    #reader:
    # description: NetCDF4 reader for the NWCSAF MSG 2016 format
    # name: nc_nwcsaf_msg
    # reader: !!python/name:satpy.readers.yaml_reader.FileYAMLReader
    #file_types:
    #   nc_nwcsaf_cma:
    #       file_reader: !!python/name:satpy.readers.nc_nwcsaf_msg.NcNWCSAFMSG
    #       file_patterns: ['S_NWC_CMA_{platform_id}_{region_id}_{start_time:%Y%m%dT%H%M%S}Z.nc']

    # check if product exist otherwise exit the script
    # example --> S_NWC_CTTH_MSG3_alps-VISIR_20170509T084500Z.nc
    file_pattern='S_NWC_' + product + '_' + sat_id + '_*_' + timestamp_NWCSAF + extension
    print("... search for "+file_pattern)

    if glob.glob(file_pattern):
        print ("NWCSAF data product " + product + " exists and is readable")
        # creates list of available products
        product_list_to_process.append(nwcsaf.product.get(product)[:])
    else:
        print ("NWCSAF data product " + product + " is missing or is not readable")

print (' ')
product_list_to_process = list(itertools.chain(*product_list_to_process))

# exit if there are no products to process
# ---------------------------------------
if not product_list_to_process:
    print("no realtime products to process")
    sys.exit("no products to process --> exit") 


#cw = ContourWriterAGG(shapes_dir)
cw = ContourWriter(shapes_dir)

# Loading scene with satpy
# ------------------------
#   satpy 0.62
#   global_scene = Scene(reader="nc_nwcsaf_msg", start_time=time_slot)

#   satpy 0.83
#files = find_files_and_readers(base_dir=input_dir, reader="nc_nwcsaf_msg", start_time=time_slot, end_time=time_slot)
files = find_files_and_readers(base_dir=input_dir, reader='nwcsaf-geo', start_time=time_slot, end_time=time_slot)
global_scene = Scene(filenames=files, start_time=time_slot)

# ccs4 area definition
# ------------------------
from satpy.resample import get_area_def

# load data into scene
# ------------------------
print("... load data: ", product_list_to_process)
global_scene.load(product_list_to_process)

# resample scene into ccs4-projection
# ---------------------------------------
areadef_ccs4 = get_area_def('ccs4')
local_scene_ccs4 = global_scene.resample(areadef_ccs4)

# resample data to a NinJo projection
areaid_ninjo = 'swissLarge1600m'
#areaid_ninjo = 'nqceur1km'
#areaid_ninjo = 'ccs'
areadef_ninjo = get_area_def(areaid_ninjo)
local_scene_ninjo = global_scene.resample(areadef_ninjo)

# loop through the available products and generates PNGs
# ---------------------------------------
for product in product_list_to_process:

    # define product output name
    outfile = output_dir + 'S_NWC_' + product + '_' + timestamp
    outfile_g = outfile + '.png'

    # remove png if already exists before processing it again...
    if glob.glob(outfile_g):
         print ('file ' + outfile_g + ' exist  --> DELETE')
         os.remove(outfile_g)

    local_scene_ccs4.save_dataset(product, outfile_g)
    img = Image.open(outfile_g)

    # add legend
#    if legend:
#        dc = DecoratorAGG(img)
#        dc.align_bottom()
#        dc.add_logo(NWCSAF_dir + "legends/legend.gif")

    # add borders
    if borders:
        cw.add_borders(img, areadef_ccs4, resolution='i', level=2, outline=(0, 0, 255))

    # add header at the top (sat, utc, product) 
    if header:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(Lucida_font, 12)
        draw.rectangle([(0, 0), (img.size[0], 20)], fill=(255,165,0,200))
        textSizeProd = draw.textsize(product[:36], font=font)
        textSizeDate = draw.textsize(year+"-"+month+"-"+day+" "+hours+":"+min+" UTC", font=font)
        draw.text((5, 2), sat_name,(25,25,25),font=font)
        draw.text((img.size[0]-textSizeProd[0]-5,2), product[:36],(25,25,25),font=font)
        draw.text((img.size[0]/2-textSizeDate[0]/2, 2), year+"-"+month+"-"+day+" "+hours+":"+min+" UTC",(25,25,25),font=font)

    # collect metadata
    meta = PngImagePlugin.PngInfo()
    if png_metadata:
        # collect metadata 
        # meta = PngImagePlugin.PngInfo()
        # only cloud products have specific metadata
        if product.startswith('cloud'):

            if product in nwcsaf.product['CMA']:
                data_from_log = extract_data_from_log(nwcsaf.keywords_CMA, LOG_filename)
            elif product in nwcsaf.product['CT']:
                data_from_log = extract_data_from_log(nwcsaf.keywords_CT, LOG_filename)
            elif product in nwcsaf.product['CTTH']:
                data_from_log = extract_data_from_log(nwcsaf.keywords_CTTH, LOG_filename)
            else:  # CMIC
                data_from_log = extract_data_from_log(nwcsaf.keywords_CMIC, LOG_filename)

            metadata = {"version":"NWCSAF/GEO v2016", "data": data_from_log }
            #print(metadata)
            for x in metadata:
                meta.add_text(x, str(metadata[x]))
        else:
            print ('product ' + product + ' without metadata')

        if display_info:
            # add metadata to png    
            font = ImageFont.truetype(Lucida_font, 10)
            draw.text((5,img.size[1]-12), str(metadata['data']), (0,0,255), font=font)
    
    # save the final image
    img.save(outfile_g, pnginfo=meta)


    # generate tiff for NinJo (with Cinesat pattern..)
    if ninjoTiff  and  product in ['cloudmask', 'cloudtype', 'cloud_top_height', 'cloud_top_temperature', 'convective_rain_rate']:

        print('producing ' + product + ' NINJO-TIFF')

        outfile_tiff = nwcsaf.ninjo_suffix + '_' + nwcsaf.ninjo_def[product][0] + '_cosmo2-' + areaid_ninjo + '_' + timestamp[2:] + '.tif'

        local_scene_ninjo.save_dataset(product, filename = output_ninjo_dir + outfile_tiff, writer = 'ninjotiff', ninjo_product_name = nwcsaf.ninjo_def[product][1])




