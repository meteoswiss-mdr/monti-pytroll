from __future__ import division
from __future__ import print_function


#from satpy.utils import debug_on
#debug_on()

import nwcsaf
import numpy as np
#product = {}
#product['CMA']     = [ 'cloudmask']

product_list = ['CTTH']
## 'ASII-NG' and 'RDT-CW' do not work!!
# sam's product_list = ['CMA', 'CT', 'CTTH', 'CMIC', 'PC', 'CRR', 'iSHAI', 'CI', 'RDT-CW', 'ASII-NG']
# product_list = ['ASII-NG', 'CI', 'CMA', 'CMIC', 'CRR', 'CRR-Ph', 'CT', 'CTTH', 'HRW', 'iSHAI', 'PC', 'PC-Ph', 'PLAX', 'RDT-CW']
# product.keys() ['ASII-NG', 'CI', 'CMA', 'CMIC', 'CRR', 'CRR-Ph', 'CT', 'CTTH', 'HRW', 'iSHAI', 'PC', 'PC-Ph', 'RDT-CW']

# Marco Sassi's program
# zueub428:/opt/pytroll/nwcsaf/nwcsaf-processing/bin/NWCSAF_processing.py
# old version: zueub428:/opt/safnwc/bin/NWCSAF_processing.py

# CTT: prerequisites:           ['ctth_tempe', 'ctth_tempe_pal']
# CTH: prerequisites:           ['ctth_alti', 'ctth_alti_pal']
# CTP: prerequisites:           ['ctth_pres', 'ctth_pres_pal']
# CT:  prerequisites:           ['ct', 'ct_pal']
# CMA: prerequisites:           ['cma', 'cma_pal']

from satpy import Scene, find_files_and_readers
from datetime import datetime

for p_ in product_list:

    start_time=datetime(2017, 7, 7, 12, 0)
    end_time=datetime(2017, 7, 7, 12, 0)
    
    #file_pattern='S_NWC_' + product + '_' + sat_id + '_*_' + timestamp_NWCSAF + extension
    #if glob.glob(file_pattern):
    #    print ("NWCSAF data product " + product + " exists and is readable")
    #    # creates list of available products
    #    product_list_to_process.append(nwcsaf.product.get(product)[:])
    #else:
    #    print ("NWCSAF data product " + product + " is missing or is not readable")
    
    print("... search files in "+ "/data/COALITION2/database/meteosat/SAFNWC_v2016/2017/07/07/"+p_+"/")
    files_nwc = find_files_and_readers(sensor='seviri',
                                       start_time=start_time,
                                       end_time=end_time,
                                       #base_dir="/data/COALITION2/database/meteosat/SAFNWC_v2013/2015/07/07/",
                                       base_dir="/data/COALITION2/database/meteosat/SAFNWC_v2016/2017/07/07/"+p_+"/",
                                       reader='nwcsaf-geo')
    #print files_nwc
    #files = dict(files_sat.items() + files_nwc.items())
    files = dict(list(files_nwc.items()))

    global_scene = Scene(filenames=files)
    
    #global_scene.load(['cloudtype'])
    global_scene.load(nwcsaf.product[p_])

    print("")
    print("global_scene")
    print(global_scene)
    print(dir(global_scene))
    # ['__class__', '__contains__', '__delattr__', '__delitem__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_check_known_composites', '_compare_areas', '_compute_metadata_from_readers', '_generate_composite', '_get_prereq_datasets', '_get_sensor_names', '_ipython_key_completions_', '_read_composites', '_read_datasets', '_remove_failed_datasets', '_resampled_scene', '_slice_area_from_bbox', '_slice_data', '_slice_datasets', 'aggregate', 'all_composite_ids', 'all_composite_names', 'all_dataset_ids', 'all_dataset_names', 'all_modifier_names', 'all_same_area', 'all_same_proj', 'attrs', 'available_composite_ids', 'available_composite_names', 'available_dataset_ids', 'available_dataset_names', 'copy', 'cpl', 'create_reader_instances', 'crop', 'datasets', 'dep_tree', 'end_time', 'generate_composites', 'get', 'get_writer_by_ext', 'id', 'images', 'iter_by_area', 'keys', 'load', 'max_area', 'min_area', 'missing_datasets', 'ppp_config_dir', 'read', 'readers', 'resample', 'resamplers', 'save_dataset', 'save_datasets', 'show', 'slice', 'start_time', 'to_geoviews', 'to_xarray_dataset', 'unload', 'values', 'wishlist']

    print(global_scene.available_dataset_names())
    
    #!!# print(global_scene['overview']) ### this one does only work in the develop version
    print("")
    print("available_composite_names")
    print(global_scene.available_composite_names())
    print(global_scene.all_dataset_names())
    print(global_scene.available_dataset_names())
    print(global_scene.datasets)
    
    print("resample")
    local_scene = global_scene.resample("ccs4")

    for p_name in nwcsaf.product[p_]:
        
        #local_scene.show('cloudtype')
        #local_scene.save_dataset('cloudtype', './local_cloudtype.png')
        #print "display ./local_cloudtype.png &"
        print("======================")
        print("======================")        
        print(global_scene['cloud_top_temperature'])
        print(global_scene['cloud_top_temperature'].attrs['area'])
        print(global_scene['cloud_top_temperature'].attrs["start_time"])
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
        
        print(np.nanmin(global_scene['cloud_top_temperature'].values))
        print(np.nanmax(global_scene['cloud_top_temperature'].values))
        print("======================")
        print("======================")        
 
        
        #local_scene.show(p_name)
        #local_scene.show(p_name, overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 0, 0), 'resolution': 'i'})
        local_scene.save_dataset(p_name, "./local_"+p_name+".png", overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 0, 0), 'resolution': 'i'})
        print("display ./local_"+p_name+".png &")


