from __future__ import division
from __future__ import print_function

# Marco Sassi's program
# zueub428:/opt/pytroll/nwcsaf/nwcsaf-processing/bin/NWCSAF_processing.py
# old version: zueub428:/opt/safnwc/bin/NWCSAF_processing.py
# see also https://github.com/pytroll/pytroll-examples/blob/master/satpy/ears-nwc.ipynb

# Known bugs: for RGB and ccs4, it does not produce national borders 

#from satpy.utils import debug_on
#debug_on()

import nwcsaf
import numpy as np
import sys
from copy import deepcopy
import socket
from datetime import datetime

# Import the library OpenCV
import cv2

from satpy import Scene, find_files_and_readers

from my_msg_module_py3 import format_name
from my_msg_module_py3 import get_input_dir

if "tsa" in socket.gethostname():
    #CSCS
    map_dir="/store/msrad/sat/pytroll/shapes/"
    #map_dir="/store/msrad/utils/shapes/"
    logo_dir="/store/msrad/sat/pytroll/logos/"
    font_file="/usr/share/fonts/dejavu/DejaVuSans.ttf"
    result_dir="./"
    cache_dir="/scratch/hamann/tmp/"
elif "zue" in socket.gethostname():
    # meteoswiss
    map_dir="/opt/users/common/shapes/"
    logo_dir="/opt/users/common/logos/"
    font_file="/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf"
    result_dir="/data/cinesat/out/"
    #result_dir="./"
    #result_dir=start_time.strftime("/data/COALITION2/PicturesSatellite/%Y-%m-%d/")
    cache_dir="/tmp/"
else:
    print("*** Error, unknown hostname: ",socket.gethostname())
    print("    please specify directories for shape files, logos, font etc")
    quit()


def remove_background(file_name):
    
    # Read the image
    src = cv2.imread(file_name, 1)
    
    # Convert image to image gray
    tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    
    # Applying thresholding technique
    _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
    
    # Using cv2.split() to split channels 
    # of coloured image
    b, g, r = cv2.split(src)
    
    # Making list of Red, Green, Blue
    # Channels and alpha
    rgba = [b, g, r, alpha]
    
    # Using cv2.merge() to merge rgba
    # into a coloured/multi-channeled image
    dst = cv2.merge(rgba, 4)
    
    # Writing and saving to a new image
    cv2.imwrite(file_name, dst)
    print("removed background in: display ", file_name, " &")


def print_info(global_scene):
    print("======================")
    print("======================")
    print("... global_scene")
    print(global_scene)
    #print(dir(global_scene))
    """
    ['__class__', '__contains__', '__delattr__', '__delitem__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__',
    '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
     '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_check_known_composites', '_compare_areas', '_compute_metadata_from_readers',
     '_generate_composite', '_get_prereq_datasets', '_get_sensor_names', '_ipython_key_completions_', '_read_composites', '_read_datasets', '_remove_failed_datasets',
     '_resampled_scene', '_slice_area_from_bbox', '_slice_data', '_slice_datasets', 'aggregate', 'all_composite_ids', 'all_composite_names', 'all_dataset_ids',
     'all_dataset_names', 'all_modifier_names', 'all_same_area', 'all_same_proj', 'attrs', 'available_composite_ids', 'available_composite_names', 'available_dataset_ids',
     'available_dataset_names', 'copy', 'cpl', 'create_reader_instances', 'crop', 'datasets', 'dep_tree', 'end_time', 'generate_composites', 'get', 'get_writer_by_ext',
     'id', 'images', 'iter_by_area', 'keys', 'load', 'max_area', 'min_area', 'missing_datasets', 'ppp_config_dir', 'read', 'readers', 'resample', 'resamplers',
     'save_dataset', 'save_datasets', 'show', 'slice', 'start_time', 'to_geoviews', 'to_xarray_dataset', 'unload', 'values', 'wishlist']
    """
    
    #!!# print(global_scene['overview']) ### this one does only work in the develop version
    print("")
    print("======================")
    print("======================")
    print("available_composite_names")
    print(global_scene.available_composite_names())
    print("")
    print("======================")
    print("======================")
    print("all_dataset_names")
    print(global_scene.all_dataset_names())
    print("")
    print("======================")
    print("======================")
    print("available_dataset_names")
    print(global_scene.available_dataset_names())
    print("")
    #print("datasets")
    #print(global_scene.datasets)


#==========================================================

# see https://github.com/pytroll/satpy/blob/main/satpy/etc/readers/nwcsaf-geo.yaml
#['asii_prob', 'cloud_drop_effective_radius', 'cloud_ice_water_path', 'cloud_liquid_water_path', 'cloud_optical_thickness', 'cloud_top_height', 'cloud_top_phase', 'cloud_top_pressure', 'cloud_top_temperature', 'cloudmask', 'cloudtype', 'convection_initiation_prob30', 'convection_initiation_prob60', 'convection_initiation_prob90', 'convective_precipitation_hourly_accumulation', 'convective_rain_rate', 'lifted_index', 'precipitation_probability', 'rdt_cell_type', 'showalter_index', 'total_precipitable_water']
composite_names = {}
composite_names['CMA']    = [ 'cloudmask']
composite_names["CTTH"]   = [ 'cloud_top_height', 'cloud_top_pressure', 'cloud_top_temperature']
composite_names["CRR"]    = [ 'convective_rain_rate']
composite_names["CRR-Ph"] = [ 'convective_precipitation_hourly_accumulation', 'convective_rain_rate']
composite_names["RDT-CW"] = [ 'rdt_cell_type' ]
dataset_names         = {}
dataset_names['CT']   = ['ct']
dataset_names['CTTH'] = ['cth']
#dataset_names['CRR']  = ['crr', 'crr_accum', 'crr_conditions', 'crr_intensity', 'crr_intensity_pal', 'crr_pal', 'crr_quality', 'crr_status_flag']  
dataset_names['CRR']  = ['crr']  
#dataset_names['CRR-Ph']  = ['crr', 'crr_accum', 'crr_accum_pal', 'crr_conditions', 'crr_intensity', 'crr_intensity_pal', 'crr_pal', 'crr_quality', 'crr_status_flag'] 
dataset_names['CRR-Ph']  = ['crrph_intensity']
dataset_names["RDT-CW"] = [ 'MapCellCatType', 'MapCellCatType_pal', 'MapCell_conditions', 'MapCell_quality' ]

if len(sys.argv) == 2:
    product_list=[sys.argv[1]]
    from my_msg_module_py3 import get_last_SEVIRI_date
    start_time = get_last_SEVIRI_date(False, delay=10)
    end_time   = start_time
    base_dir=start_time.strftime(get_input_dir("NWCSAF-v2016-alps", nrt=True))
    #base_dir="/data/cinesat/in/safnwc/"
elif len(sys.argv) == 7:
    product_list=[sys.argv[1]]
    fixed_date=True
    start_time = datetime(int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]))
    end_time   = start_time
    base_dir=start_time.strftime(get_input_dir("NWCSAF-v2016-alps", nrt=False)+"/%Y/%m/%d/")
    #base_dir=start_time.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/"+p_+"/")
    #base_dir=start_time.strftime("./data/")
    #base_dir=start_time.strftime("/data/OWARNA/hau/database/meteosat/SAFNWC/%Y/%m/%d/"+p_+"/")
else:
    print("Wrong number of arguments:", len(sys.argv))
    print("Usage: python demo_satpy_nwcsaf_py3.py PROD [YYYY MM DD hh mm]")
    print("       where PROD might be: 'CMA', 'CT', 'CTTH', 'CMIC', 'PC', 'CRR', 'CRR-Ph', 'iSHAI', 'CI', 'RDT-CW', or 'ASII-NG'")
    #product_list = ['CMA']
    #product_list = ['CTTH']
    #product_list = ['CT']
    #product_list = ['CRR']
    #product_list = ['CRR-Ph']
    ## 'ASII-NG' and 'RDT-CW' do not work!!
    # sam's product_list = ['CMA', 'CT', 'CTTH', 'CMIC', 'PC', 'CRR', 'iSHAI', 'CI', 'RDT-CW', 'ASII-NG']
    ## 'ASII-NG' and 'RDT-CW' do not work!!
    # product_list = ['ASII-NG', 'CI', 'CMA', 'CMIC', 'CRR', 'CRR-Ph', 'CT', 'CTTH', 'HRW', 'iSHAI', 'PC', 'PC-Ph', 'PLAX', 'RDT-CW']
    # product.keys() ['ASII-NG', 'CI', 'CMA', 'CMIC', 'CRR', 'CRR-Ph', 'CT', 'CTTH', 'HRW', 'iSHAI', 'PC', 'PC-Ph', 'RDT-CW']
    # sam's product_list = ['CMA', 'CT', 'CTTH', 'CMIC', 'PC', 'CRR', 'iSHAI', 'CI', 'RDT-CW', 'ASII-NG']
    quit()


if product_list[0]=="CT" or product_list[0]=="CMA":
    read_RGBs = True
else:
    read_RGBs = False

for p_ in product_list:

    if len(sys.argv) == 2:
        base_dir_=base_dir
    else:
        base_dir_=base_dir+"/"+p_+"/"
    
    #file_pattern='S_NWC_' + product + '_' + sat_id + '_*_' + timestamp_NWCSAF + extension
    #if glob.glob(file_pattern):
    #    print ("NWCSAF data product " + product + " exists and is readable")
    #    # creates list of available products
    #    product_list_to_process.append(nwcsaf.product.get(product)[:])
    #else:
    #    print ("NWCSAF data product " + product + " is missing or is not readable")

    print("======================")
    print("======================")
    print ("... search files in "+ base_dir_ + " for "+ str(start_time))
    files_nwc = find_files_and_readers(sensor='seviri',
                                       start_time=start_time,
                                       end_time=end_time,
                                       base_dir=base_dir_,
                                       reader='nwcsaf-geo')

    print ("*** found following NWCSAF files:", files_nwc)
    files = deepcopy(files_nwc['nwcsaf-geo'])
    for f in files:
        if not (product_list[0] in f):
            files_nwc['nwcsaf-geo'].remove(f)
            continue

    print ("=== found following NWCSAF files:", files_nwc)
    #files = dict(files_sat.items() + files_nwc.items())
    #files = dict(list(files_nwc.items()))

    print("======================")
    print("======================")
    print ("... define global scene ")
    global_scene = Scene(filenames=files_nwc)

    #print_info(global_scene)

    if read_RGBs:
    
        # this will load RGBs ready to plot
        print("======================")
        print("======================")
        print("... load ", nwcsaf.product[p_])
        global_scene.load(nwcsaf.product[p_])
        #global_scene.load([ 'cloud_top_height', 'cloud_top_pressure', 'cloud_top_temperature'])
        #global_scene.load(['cloudtype'])

        #print("global_scene.keys()", global_scene.keys())
        #[DatasetID(name='cloud_top_height', wavelength=None, resolution=None, polarization=None, calibration=None, level=None, modifiers=None)]

        # 'cloud_top_height' is loaded in RGB mode already 
        #print(global_scene['cloud_top_height'].data.shape)
        #print(global_scene['cloud_top_height'].data.compute())
        #print(global_scene['cloud_top_height'].values)

    else:
        # work with scientific data
        print("======================")
        print("======================")
        print("... load ", dataset_names[p_])
        global_scene.load(dataset_names[p_])

    #global_scene.save_dataset('cloudmask', "cloudmask.png", overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 255, 255), 'resolution': 'i'})
    
    # resample to another projection
    area="ccs4"
    #area="EuropeCanaryS95"
    #area="europe_center"
    #area="cosmo1"
    print("======================")
    print("======================")
    print("... resample to area: ", area)
    if read_RGBs:
        local_scene = global_scene.resample(area, resampler='nearest', cache_dir=cache_dir, radius_of_influence=15000)
    else:
        local_scene = global_scene.resample(area, cache_dir=cache_dir)
        
        #print("dir(local_scene)", dir(local_scene))

    if read_RGBs:
    
        for p_name in nwcsaf.product[p_]: 

            #local_scene.show('cloudtype')
            #local_scene.save_dataset('cloudtype', './local_cloudtype.png')
            #print "display ./local_cloudtype.png &"
            print("======================")
            print("======================")
            print(p_name)
            ##print(global_scene[p_name])
            ##print(global_scene[p_name].attrs['area'])
            ##print(global_scene[p_name].attrs["start_time"])
            #long_name:               NWC GEO CTTH Cloud Top Altitude
            #level:                   None
            #end_time:                2017-07-07 12:03:32
            #sensor:                  seviri
            #valid_range:             [    0 27000]
            #ancillary_variables:     [<xarray.DataArray 'ctth_status_flag' (y: 151, x...
            #area:                    Area ID: some_area_name\nDescription: On-the-fly...
            #resolution:              3000
            #polarization:            None
            #start_time:              2017-07-07 12:03:02
            #comment:
            #name:                    cloud_top_height
            #standard_name:           cloud_top_height
            #platform_name:           Meteosat-9
            #wavelength:              None
            #_FillValue:              nan
            #units:                   m
            #modifiers:               None
            #prerequisites:           ['ctth_alti', 'ctth_alti_pal']
            #optional_prerequisites:  []
            #calibration:             None
            #mode:                    RGB
        
            print(np.nanmin(global_scene[p_name].values))
            print(np.nanmax(global_scene[p_name].values))
            print("======================")
            print("======================")

            #print ("p_name, type(local_scene[p_name]), type(local_scene[p_name].data)")
            #print (p_name, type(local_scene[p_name]), type(local_scene[p_name].data))

            png_file = start_time.strftime(result_dir+ "/MSG_"+p_+"-"+area+"_%y%m%d%H%M.png")
            title = start_time.strftime(" "+local_scene[p_name].platform_name+', %y-%m-%d %H:%MUTC, '+p_name)
            #title=""
            #local_scene.show(p_name)
            #local_scene.show(p_name, overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 0, 0), 'resolution': 'i'})


            #def save_dataset(self, dataset_id, filename=None, writer=None,
            #         overlay=None, decorate=None, compute=True, **kwargs):

            decorate = {
                'decorate': [
                    {'logo': {'logo_path': '/opt/users/common/logos/meteoSwiss.png', 'height': 60, 'bg': 'white',
                              'bg_opacity': 255, 'align': {'top_bottom': 'top', 'left_right': 'right'}}},
                    {'text': {'txt': title,
                              'align': {'top_bottom': 'top', 'left_right': 'left'},
                              'font': "/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf",
                              'font_size': 14,
                              'height': 26,
                              'bg': 'black',
                              'bg_opacity': 255,
                              'line': 'white'}}
                ]
            }
            
            
            local_scene.save_dataset(p_name, png_file, fill_value=0,
                                     overlay={'coast_dir': map_dir, 'color': (255, 255, 255), 'resolution': 'i', 'width':1, 'level_coast': 1, 'level_borders': 2},
                                     decorate=decorate) 


            ## local_scene.save_dataset( 'lscl', png_file )
            #from pyresample.utils import load_area
            #swiss = load_area("/opt/users/hau/monti-pytroll/etc/areas.def", area)
            #
            #from PIL import Image
            #from PIL import ImageFont
            #from PIL import ImageDraw
            #
            #from pycoast import ContourWriterAGG
            #cw = ContourWriterAGG(map_dir)
            #cw.add_borders_to_file(png_file, swiss, outline="green", resolution='i', level=3, width=2)
            #
            #img = Image.open(png_file)
            #draw = ImageDraw.Draw(img)
            #draw.rectangle([(0, 0), (img.size[0]*0.7, 25)], fill=(0,0,0,200))
            #font = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", 18)
            #title = start_time.strftime(" "+local_scene[p_name].platform_name+', %y-%m-%d %H:%MUTC, '+p_name)
            #draw.text( (1, 1), title, "black" , font=font)  # (255,255,255)
            #img.save(png_file)


            
            print ("display "+png_file+" &")
    else:

        #global_scene["cma"].plot()
        for p__ in dataset_names[p_]: 
            #print (type(local_scene[p__].values))
            #print (local_scene[p__].values.shape)
            #print (np.nanmin(local_scene[p__].values))
            #print (np.nanmax(local_scene[p__].values))

            crr = local_scene[p__].values.astype(np.float32)
            print (np.nanmin(crr))
            print (np.nanmax(crr))

            crr[crr==0.0] = np.nan 
            crr = np.where(crr==0.0, np.nan, crr)

            from trollimage.colormap import set3, rdbu, RainRate
            from trollimage.image import Image as trollimage
            
            img = trollimage(crr, mode="L", fill_value=None)
            print("***********************")
            #print(dir(RainRate))            
            #print(RainRate.values)
            #print(RainRate.colors)
            print("***********************")
            #set3.set_range(0, 8)
            #img.palettize(set3)
            #rdbu.set_range(0, 15)
            #img.colorize(rdbu)
            img.colorize(RainRate)

            product_dict={}
            product_dict['CRR']="CRR"
            product_dict['CRR-Ph']="CRPh"
            product_dict['CT']="CT"
            
            outFile=result_dir+'/MSG_%(rgb)s-%(area)s_%y%m%d%H%M.png'
            outputFile = format_name(outFile, start_time, area=area, rgb=product_dict[p_])

            print("display "+outputFile+" &")
            #img.save(outputFile)
            PIL_image=img.pil_image()
            PIL_image.save(outputFile)  
            
            remove_background(outputFile)
