
from satpy.utils import debug_on
debug_on()

from numpy import nanmin, nanmax

# Marco Sassi's program
# zueub428:/opt/pytroll/nwcsaf/nwcsaf-processing/bin/NWCSAF_processing.py
# old version: zueub428:/opt/safnwc/bin/NWCSAF_processing.py
# see also https://github.com/pytroll/pytroll-examples/blob/master/satpy/ears-nwc.ipynb

import nwcsaf
#product_list = ['CMA']
#product_list = ['CTTH']
product_list = ['CT']
# product_list = ['ASII-NG', 'CI', 'CMA', 'CMIC', 'CRR', 'CRR-Ph', 'CT', 'CTTH', 'HRW', 'iSHAI', 'PC', 'PC-Ph', 'PLAX', 'RDT-CW']
# product.keys() ['ASII-NG', 'CI', 'CMA', 'CMIC', 'CRR', 'CRR-Ph', 'CT', 'CTTH', 'HRW', 'iSHAI', 'PC', 'PC-Ph', 'RDT-CW']
## 'ASII-NG' and 'RDT-CW' do not work!!
# sam's product_list = ['CMA', 'CT', 'CTTH', 'CMIC', 'PC', 'CRR', 'iSHAI', 'CI', 'RDT-CW', 'ASII-NG']

#product = {}
#product['CMA']     = [ 'cloudmask']
#product["CTTH"]    = [ 'cloud_top_height', 'cloud_top_pressure', 'cloud_top_temperature']
product_ids = {}
#product_ids["CTTH"] = ['ctth_alti','ctth_alti_pal','ctth_effectiv','ctth_effectiv_pal','ctth_pres','ctth_pres_pal','ch_tempe','ctth_tempe_pal']
product_ids["CTTH"] = ['ctth_alti']

make_images=True

from satpy import Scene, find_files_and_readers
from datetime import datetime

for p_ in product_list:

    fixed_date=False
    if fixed_date:
        start_time = datetime(2017, 7, 7, 12, 0)
        end_time   = datetime(2017, 7, 7, 12, 0)
        #base_dir="/data/COALITION2/database/meteosat/SAFNWC_v2013/2015/07/07/",
        base_dir="/data/COALITION2/database/meteosat/SAFNWC_v2016/2017/07/07/"+p_+"/",
    else:
        from my_msg_module import get_last_SEVIRI_date
        start_time = get_last_SEVIRI_date(False, delay=3)
        end_time   = start_time
        base_dir="/data/cinesat/in/eumetcast1/"
        
    #file_pattern='S_NWC_' + product + '_' + sat_id + '_*_' + timestamp_NWCSAF + extension
    #if glob.glob(file_pattern):
    #    print ("NWCSAF data product " + product + " exists and is readable")
    #    # creates list of available products
    #    product_list_to_process.append(nwcsaf.product.get(product)[:])
    #else:
    #    print ("NWCSAF data product " + product + " is missing or is not readable")
    
    print "... search files in "+ base_dir
    files_nwc = find_files_and_readers(sensor='seviri',
                                       start_time=start_time,
                                       end_time=end_time,
                                       base_dir=base_dir,
                                       reader='nwcsaf-geo')
    #print files_nwc
    #files = dict(files_sat.items() + files_nwc.items())
    files = dict(files_nwc.items())

    global_scene = Scene(filenames=files)

    global_scene.available_dataset_names()
    #!!# print(global_scene['overview']) ### this one does only work in the develop version
    print ""
    print "available_composite_names"
    print global_scene.available_composite_names()
    
    if make_images:
    
        # this will load RGBs ready to plot
        global_scene.load(nwcsaf.product[p_])
        #global_scene.load([ 'cloud_top_height', 'cloud_top_pressure', 'cloud_top_temperature'])
        #global_scene.load(['cloudtype'])

        print "global_scene.keys()", global_scene.keys()
        #[DatasetID(name='cloud_top_height', wavelength=None, resolution=None, polarization=None, calibration=None, level=None, modifiers=None)]

        # 'cloud_top_height' is loaded in RGB mode already 
        # print(global_scene['cloud_top_height'].data.shape)
        #print(global_scene['cloud_top_height'].data.compute())

    else:
        # work with scientific data
        
        global_scene.load(product_ids["CTTH"])
        #global_scene.load(['ctth_alti'])

        
    print "global_scene"
    print global_scene
    print global_scene['cloudtype'].comment
    quit()

    
    # resample to another projection
    area="ccs4"
    area="EuropeCanaryS95"
    local_scene = global_scene.resample(area)

    if make_images:

        for p_name in nwcsaf.product[p_]:
            
            print "p_name, type(local_scene[p_name]), type(local_scene[p_name].data)"
            print p_name, type(local_scene[p_name]), type(local_scene[p_name].data)
            #local_scene.show('cloudtype')
            #local_scene.save_dataset('cloudtype', './local_cloudtype.png')
            #print "display ./local_cloudtype.png &"
            
            print "dir(local_scene)", dir(local_scene)

            filename="./local_"+p_name+"_"+area+".png"
            #local_scene.show(p_name)
            #local_scene.show(p_name, overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 0, 0), 'resolution': 'i'})
            local_scene.save_dataset(p_name, filename, overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 255, 255), 'resolution': 'i'})
            print "display "+filename+" &"
    else:

        for p_name in product_ids[p_]:
            print type(local_scene[p_name].values)
            print local_scene[p_name].values.shape
            print nanmin(local_scene[p_name].values)
            print nanmax(local_scene[p_name].values)
                

