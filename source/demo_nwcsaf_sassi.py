from __future__ import division
from __future__ import print_function

# Marco Sassi's program
# zueub428:/opt/pytroll/nwcsaf/nwcsaf-processing/bin/NWCSAF_processing.py
# old version: zueub428:/opt/safnwc/bin/NWCSAF_processing.py
# see also https://github.com/pytroll/pytroll-examples/blob/master/satpy/ears-nwc.ipynb

#from satpy.utils import debug_on
#debug_on()

map_dir="/opt/users/common/shapes/"

import nwcsaf
import numpy as np
import sys

from satpy import Scene, find_files_and_readers
from datetime import datetime

#product = {}
product_list = ['CMA']
#product_list = ['CTTH']
#product_list = ['CT']
## 'ASII-NG' and 'RDT-CW' do not work!!
# sam's product_list = ['CMA', 'CT', 'CTTH', 'CMIC', 'PC', 'CRR', 'iSHAI', 'CI', 'RDT-CW', 'ASII-NG']
## 'ASII-NG' and 'RDT-CW' do not work!!
# product_list = ['ASII-NG', 'CI', 'CMA', 'CMIC', 'CRR', 'CRR-Ph', 'CT', 'CTTH', 'HRW', 'iSHAI', 'PC', 'PC-Ph', 'PLAX', 'RDT-CW']
# product.keys() ['ASII-NG', 'CI', 'CMA', 'CMIC', 'CRR', 'CRR-Ph', 'CT', 'CTTH', 'HRW', 'iSHAI', 'PC', 'PC-Ph', 'RDT-CW']
# sam's product_list = ['CMA', 'CT', 'CTTH', 'CMIC', 'PC', 'CRR', 'iSHAI', 'CI', 'RDT-CW', 'ASII-NG']

read_RGBs = True

product = {}
product['CMA']     = [ 'cloudmask']
#product["CTTH"]    = [ 'cloud_top_height', 'cloud_top_pressure', 'cloud_top_temperature']
product_ids = {}
product_ids['CT'] = ['ct']
product_ids['CTTH'] = ['cth']

print(len(sys.argv))
if len(sys.argv) == 6:
    fixed_date=True
    print(sys.argv[1],sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    start_time = datetime(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]))
    end_time   = start_time
else:
    fixed_date=False
    from my_msg_module import get_last_SEVIRI_date
    start_time = get_last_SEVIRI_date(False, delay=10)
    end_time   = start_time
    base_dir="/data/cinesat/in/eumetcast1/"

result_dir="./"
result_dir=start_time.strftime("/data/COALITION2/PicturesSatellite/%Y-%m-%d/")

for p_ in product_list:
       
    #file_pattern='S_NWC_' + product + '_' + sat_id + '_*_' + timestamp_NWCSAF + extension
    #if glob.glob(file_pattern):
    #    print ("NWCSAF data product " + product + " exists and is readable")
    #    # creates list of available products
    #    product_list_to_process.append(nwcsaf.product.get(product)[:])
    #else:
    #    print ("NWCSAF data product " + product + " is missing or is not readable")

    if fixed_date:
        #base_dir=start_time.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2013/%Y/%m/%d/")
        base_dir=start_time.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/"+p_+"/")
        #base_dir=start_time.strftime("/data/OWARNA/hau/database/meteosat/SAFNWC/%Y/%m/%d/"+p_+"/")
    
    print("======================")
    print("======================")
    print ("... search files in "+ base_dir)
    files_nwc = find_files_and_readers(sensor='seviri',
                                       start_time=start_time,
                                       end_time=end_time,
                                       base_dir=base_dir,
                                       reader='nwcsaf-geo')
    #print (files_nwc)
    #files = dict(files_sat.items() + files_nwc.items())
    #files = dict(list(files_nwc.items()))


        
    print("======================")
    print("======================")
    print ("... define global scene ")
    global_scene = Scene(filenames=files_nwc)

    global_scene.available_dataset_names()
    #!!# print(global_scene['overview']) ### this one does only work in the develop version
    print ("")
    print ("available_composite_names")
    print (global_scene.available_composite_names())

    if read_RGBs:
    
        # this will load RGBs ready to plot
        print("======================")
        print("======================")
        print("... load ", nwcsaf.product[p_])
        global_scene.load(nwcsaf.product[p_])
        #global_scene.load([ 'cloud_top_height', 'cloud_top_pressure', 'cloud_top_temperature'])
        #global_scene.load(['cloudtype'])

        print("global_scene.keys()", global_scene.keys())
        #[DatasetID(name='cloud_top_height', wavelength=None, resolution=None, polarization=None, calibration=None, level=None, modifiers=None)]

        # 'cloud_top_height' is loaded in RGB mode already 
        #print(global_scene['cloud_top_height'].data.shape)
        #print(global_scene['cloud_top_height'].data.compute())
        #print(global_scene['cloud_top_height'].values)

    else:
        # work with scientific data
        print("======================")
        print("======================")
        print("... load ", product_ids[p_])
        global_scene.load(product_ids[p_])
        #global_scene.load(['ctth_alti'])

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

    if False:
        global_scene.save_dataset('cloudmask', "cloudmask.png", overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 255, 255), 'resolution': 'i'})

    if not read_RGBs:
        import matplotlib.pyplot as plt
        #global_scene["cma"].plot()
        for p__ in product_ids[p_]: 
            plt.imshow(global_scene[p__].values)
            plt.show()

    
    # resample to another projection
    print("resample")
    #area="ccs4"
    #area="EuropeCanaryS95"
    #area="europe_center"
    area="cosmo1"
    local_scene = global_scene.resample(area)
    print("dir(local_scene)", dir(local_scene))
    
    for p_name in nwcsaf.product[p_]:
        
        #local_scene.show('cloudtype')
        #local_scene.save_dataset('cloudtype', './local_cloudtype.png')
        #print "display ./local_cloudtype.png &"
        print("======================")
        print("======================")
        print(p_name)
        print(global_scene[p_name])
        print(global_scene[p_name].attrs['area'])
        print(global_scene[p_name].attrs["start_time"])
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
    
    if read_RGBs:

        for p_name in nwcsaf.product[p_]: 
            
            #print ("p_name, type(local_scene[p_name]), type(local_scene[p_name].data)")
            #print (p_name, type(local_scene[p_name]), type(local_scene[p_name].data))

            png_file = start_time.strftime(result_dir+ "/MSG_"+p_name+"-"+area+"_%y%m%d%H%M.png")
            #title = start_time.strftime(" "+local_scene[p_name].platform_name+', %y-%m-%d %H:%MUTC, '+p_name)
            title=""
            #local_scene.show(p_name)
            #local_scene.show(p_name, overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 0, 0), 'resolution': 'i'})


            #def save_dataset(self, dataset_id, filename=None, writer=None,
            #         overlay=None, decorate=None, compute=True, **kwargs):

            decorate = {
                'decorate': [
                    {'text': {'txt': title,
                              'align': {'top_bottom': 'top', 'left_right': 'left'},
                              'font': "/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf",
                              'font_size': 18,
                              'height': 26,
                              'bg': 'black',
                              'bg_opacity': 255,
                              'line': 'white'}}
                ]
            }
            
            
            local_scene.save_dataset(p_name, png_file, fill_value=0,
                                     overlay={'coast_dir': map_dir, 'color': (255, 255, 255), 'resolution': 'i', 'width':2},
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

        for p_name in product_ids[p_]:
            print (type(local_scene[p_name].values))
            print (local_scene[p_name].values.shape)
            print (np.nanmin(local_scene[p_name].values))
            print (np.nanmax(local_scene[p_name].values))
                
