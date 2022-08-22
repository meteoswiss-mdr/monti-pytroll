# see also https://satpy.readthedocs.io/en/stable/composites.html

from datetime import datetime
import sys

#%matplotlib notebook
#import matplotlib.pyplot as plt
#import cartopy
#import cartopy.crs as ccrs
#from cartopy._crs import (CRS, Geodetic, Globe, PROJ4_VERSION, WGS84_SEMIMAJOR_AXIS, WGS84_SEMIMINOR_AXIS)

from my_msg_module_py3 import create_seviri_scene

from satpy.resample import get_area_def
from satpy.composites import GenericCompositor
from satpy.writers import to_image
from satpy.writers import get_enhanced_image
from pyresample import create_area_def
from time import time, sleep
from os import path
from satpy.writers import add_decorate, add_overlay

from my_msg_module_py3 import get_input_dir
from my_msg_module_py3 import format_name

import warnings

reader = 'seviri_l1b_hrit'

comp_names={}
comp_names["_vis_with_ir"]="HRVir108"
comp_names["airmass"]="airmass"
comp_names["overview"]="overview"

def plot_seviri_image(comp, start_time, area="ccs4", outFile="/data/cinesat/out/MSG_%(rgb)s-%(area)s_%y%m%d%H%M.png"):

    scn=None
    while scn==None:
        sat="MSG3"
        scn = create_seviri_scene(start_time, base_dir, sat=sat)
        if scn==None:
            sat="MSG4"
            print("*** no files found for MSG3, search for MSG4 files")
            scn = create_seviri_scene(start_time, base_dir, sat=sat)
        sleep(20)
            
    print("... load channels and create RGB in original projection")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        scn.load([comp])

    area_def = get_area_def(area)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        print("... resample channels to area: "+area)
        new_scn = scn.resample(area_def, resampler="bilinear")
        print("... reload composites: "+comp)
        new_scn.load([comp])

    img = to_image(new_scn[comp])

    outFileName  = format_name( outFile, start_time, area=area, rgb=comp_names[comp] )
    
    print("... produce png image")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        decorate = {
            'decorate': [
                {'logo': {'logo_path': '/opt/users/common/logos/meteoSwiss.png','height': 60,\
                          'bg': 'white','bg_opacity': 255, 'align': {'top_bottom': 'top', 'left_right': 'right'}}},
                {'logo': {'logo_path': '/opt/users/common/logos/pytroll3.jpg','height': 60,\
                          'bg': 'white','bg_opacity': 255, 'align': {'top_bottom': 'bottom', 'left_right': 'right'}}},
                {'text': {'txt': ' '+sat.replace("MSG", "MSG-")+', '+start_time.strftime('%Y-%m-%d %H:%MUTC')+', '+ area+', '+comp_names[comp],
                          'align': {'top_bottom': 'top', 'left_right': 'left'},
                          'font': "/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf",
                          'font_size': 18,
                          'height': 21,
                          'bg': 'white',
                          'bg_opacity': 0,
                          'line': 'white'}}
            ]
        }
        
        print("... add_overlay (borders)")
        img = add_overlay(img, area, '/data/OWARNA/hau/maps_pytroll/', color='red', width=1.0,
                          resolution='i', level_coast=1, level_borders=1, fill_value=None)
        print("... add_decorate")
        img = add_decorate(img, **decorate) #, fill_value='black'
        
        img.save(writer="simple_image",
                 filename = outFileName)
        print("display "+outFileName+" &")
        print("")

        if path.exists(outFileName) and path.getsize(outFileName) > 0:
            return True
        else:
            return False

####################################################
    
if __name__ == '__main__':

    #area="EuropeCanaryS95"
    area="ccs4"
    #output_dir="/data/cinesat/out/"
    delay=5
    composite="_vis_with_ir"
    #composite="airmass"  # does not work!
    #composite="overview" # does not work!
    
    if len(sys.argv) == 1:
        from my_msg_module_py3 import get_last_SEVIRI_date
        start_time = get_last_SEVIRI_date(True, delay=delay)
        base_dir = start_time.strftime(get_input_dir("MSG-HRIT-RSS", nrt=True))
    elif len(sys.argv) == 6:
        fixed_date=True
        start_time = datetime(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]))
        end_time   = start_time
        base_dir = start_time.strftime(get_input_dir("MSG-HRIT-RSS", nrt=False)+"/%Y/%m/%d/")

    print ("... search files in "+ base_dir + " for "+ str(start_time))

    delta_time =   30             # time in seconds to wait between the tries
    total_time = 1800             # maximum total time in seconds trying to get images

    event_time = time()
    end_time   = time()+total_time   # total time add time to try in seconds
    i=1
    
    while event_time < end_time:
        print("... try to produce SEVIRI images, try number ", i)
        i+=1
        file_produced = plot_seviri_image(composite, start_time, area=area)
        
        # exit loop, if no more images need to be processed
        if file_produced:
            break
        else:
            # sleep before next try
            sleep(delta_time)
            event_time=time()
