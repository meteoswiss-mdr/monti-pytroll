from __future__ import division
from __future__ import print_function


#from satpy.utils import debug_on
#debug_on()

import nwcsaf
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

    global_scene.available_dataset_names()
    #!!# print(global_scene['overview']) ### this one does only work in the develop version
    print("")
    print("available_composite_names")
    print(global_scene.available_composite_names())

    print("resample")
    local_scene = global_scene.resample("ccs4")

    for p_name in nwcsaf.product[p_]:
        
        #local_scene.show('cloudtype')
        #local_scene.save_dataset('cloudtype', './local_cloudtype.png')
        #print "display ./local_cloudtype.png &"

        #local_scene.show(p_name)
        #local_scene.show(p_name, overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 0, 0), 'resolution': 'i'})
        local_scene.save_dataset(p_name, "./local_"+p_name+".png", overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 0, 0), 'resolution': 'i'})
        print("display ./local_"+p_name+".png &")


