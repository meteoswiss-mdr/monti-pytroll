from __future__ import division
from __future__ import print_function

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2011, 2014 SMHI

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>
#   modified by Ulrich Hamann 

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Minimal script for geostationary production.

We take the case of HRIT data from meteosat 10, as send through eumetcast.

- Install mipp, satpy, and pyresample
- Don't forget to set up the PPP_CONFIG_DIR variable to point to your
  configuration files.

- Data must be provided in `data_hrit_in`
  where `data_hrit_in` has to be changed to anything that suits your
  environment.

- Here is an example of a more extensive script that has to be called as soon as an
  MSG slot has arrived (usually, watching the arrival of the epilogue file
  suffices)

- see further examples here:
  https://nbviewer.org/github/pytroll/pytroll-examples/tree/main/satpy/

"""

#from satpy.utils import debug_on
#debug_on()
import sys
from datetime import datetime, timedelta
from glob import glob
from PIL import Image, ImageFont

from satpy import Scene, find_files_and_readers
from satpy.writers import to_image
from satpy.composites import LuminanceSharpeningCompositor
from satpy.composites import SandwichCompositor
from satpy.resample import get_area_def
from satpy.writers import add_decorate, add_overlay

from my_msg_module_py3 import get_last_SEVIRI_date

from pycoast import ContourWriter

if sys.version_info < (2, 5):
    import time

    def strptime(string, fmt=None):
        """This function is available in the datetime module only
        from Python >= 2.5.
        """

        return datetime(*time.strptime(string, fmt)[:6])

else:
    strptime = datetime.strptime


# import the necessary packages
import numpy as np
import cv2
def adjust_gamma(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
		      for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

#######################################################
    
if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        data_hrit_in="/data/cinesat/in/eumetcast1/"
        data_nwcsaf_in="/data/cinesat/in/safnwc/"
        time_slot = get_last_SEVIRI_date(True, delay=5)
        t_minus5 = time_slot - timedelta(minutes=5)
        n_files = len(glob(data_hrit_in+'/H*MSG3*'+t_minus5.strftime("%Y%m%d%H%M")+'*'))
        if n_files > 43:
            # assume that RSS is delivered 
            sat="MSG3"
        else:
            # need to use full disk service
            print("*** Warning, found not sufficient RSS files (",n_files,"), use full disk service instead")
            time_slot = get_last_SEVIRI_date(False, delay=5)
            sat="MSG4"
        time_string = time_slot.strftime("%Y%m%d%H%M")
    elif(len(sys.argv) == 2):
        time_string = sys.argv[1]
        sat="MSG3"
        time_slot = strptime(time_string, "%Y%m%d%H%M")
        data_hrit_in=time_slot.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/%Y/%m/%d/")
        data_nwcsaf_in=time_slot.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/\*/")
    else:
        print("Usage: " + sys.argv[0] + " time_string(%Y%m%d%H%M)")
        sys.exit()
        
    time_string_nwcsaf = time_slot.strftime("%Y%m%dT%H%M")
    #print(glob(data_hrit_in+'/H*MSG3*'+time_string+'*'))
    #print(glob(data_nwcsaf_in+'/S_NWC*MSG3*'+time_string_nwcsaf+'*.nc'))
    global_scene = Scene(filenames={'seviri_l1b_hrit': glob(data_hrit_in+'/H*'+sat+'*'+time_string+'*'),
                                    'nwcsaf-geo': glob(data_nwcsaf_in+'/S_NWC*'+sat+'*'+time_string_nwcsaf+'*.nc')})
    #global_scene = Scene(platform_name="Meteosat-9", sensor="seviri", reader="hrit_msg", start_time=time_slot)
    #global_data = Scene.create_scene("meteosat", "09", "seviri", time_slot)

    #outputDir="/data/cinesat/out/"
    outputDir="./satlive/"
  
    ##############################################################
    wishlist=[]
    #### channels of SEVIRI
    #wishlist.append("HRV")
    #wishlist.append("VIS006")
    #wishlist.append("VIS008")
    #wishlist.append("IR_016")
    #wishlist.append("IR_039")
    wishlist.append("WV_062")
    #wishlist.append("WV_073")
    #wishlist.append("IR_097")
    #wishlist.append("IR_108")
    #wishlist.append("IR_120")
    #wishlist.append("IR_134")
    #### modified channels of SEVIRI, see satpy/satpy/etc/composites/seviri.yaml 
    #wishlist.append("_vis06")
    #wishlist.append("_hrv")
    #wishlist.append("_vis06_filled_hrv")
    wishlist.append("_ir108")
    wishlist.append("_vis_with_ir")
    #### modified channels for VISIR, see satpy/satpy/etc/composites/visir.yaml
    #wishlist.append("ir108_3d")
    #wishlist.append("ir_cloud_day")
    #### backgrounds, see satpy/satpy/etc/composites/visir.yaml)
    #wishlist.append("_night_background")
    #wishlist.append("_night_background_hires")
    # composites for SEVIRI, see, see satpy/satpy/etc/composites/seviri.yaml)
    #wishlist.append("ct_masked_ir")
    #wishlist.append("nwc_geo_ct_masked_ir")
    wishlist.append("cloudtop")
    #wishlist.append("cloudtop_daytime")
    #wishlist.append("convection")
    wishlist.append("night_fog")
    #wishlist.append("snow")
    #wishlist.append("day_microphysics")
    #wishlist.append("day_microphysics_winter")
    #wishlist.append("natural_color_raw")
    wishlist.append("natural_color")
    #wishlist.append("natural_color_nocorr")
    wishlist.append("fog")
    #wishlist.append("cloudmask")
    #wishlist.append("cloudtype")
    #wishlist.append("cloud_top_height")
    #wishlist.append("cloud_top_pressure")
    #wishlist.append("cloud_top_temperature")
    #wishlist.append("cloud_top_phase")
    #wishlist.append("cloud_drop_effective_radius")
    #wishlist.append("cloud_optical_thickness")
    #wishlist.append("cloud_liquid_water_path")
    #wishlist.append("cloud_ice_water_path")
    #wishlist.append("precipitation_probability")
    #wishlist.append("convective_rain_rate")
    #wishlist.append("convective_precipitation_hourly_accumulation")
    #wishlist.append("total_precipitable_water")
    #wishlist.append("showalter_index")
    #wishlist.append("lifted_index")
    #wishlist.append("convection_initiation_prob30")
    #wishlist.append("convection_initiation_prob60")
    #wishlist.append("convection_initiation_prob90")
    #wishlist.append("asii_prob")
    #wishlist.append("rdt_cell_type")
    #wishlist.append("realistic_colors")
    #wishlist.append("ir_overview")
    #wishlist.append("overview_raw")
    wishlist.append("overview")
    wishlist.append("green_snow")
    #wishlist.append("colorized_ir_clouds")
    #wishlist.append("vis_sharpened_ir")
    #wishlist.append("ir_sandwich")
    #wishlist.append("natural_enh")
    wishlist.append("hrv_clouds")
    #wishlist.append("hrv_fog")
    #wishlist.append("hrv_severe_storms")
    #wishlist.append("hrv_severe_storms_masked")
    #wishlist.append("natural_with_night_fog")
    #wishlist.append("natural_color_with_night_ir")
    #wishlist.append("natural_color_raw_with_night_ir")
    #wishlist.append("natural_color_with_night_ir_hires")
    #wishlist.append("natural_enh_with_night_ir")
    #wishlist.append("natural_color_with_night_ir_hires")
    #wishlist.append("natural_enh_with_night_ir")
    #wishlist.append("natural_enh_with_night_ir_hires")
    #wishlist.append("night_ir_alpha")
    #wishlist.append("night_ir_with_background")
    #wishlist.append("night_ir_with_background_hires")
    #wishlist.append("vis_with_ir_cloud_overlay")
    # general VISIR composites, see satpy/satpy/etc/composites/visir.yaml
    wishlist.append("airmass")
    wishlist.append("ash")
    wishlist.append("cloudtop")
    #wishlist.append("convection")
    wishlist.append("snow")
    #wishlist.append("day_microphysics")
    wishlist.append("dust")
    wishlist.append("fog")
    wishlist.append("green_snow")
    #wishlist.append("natural_enh")
    #wishlist.append("natural_color_raw")
    #wishlist.append("natural_color")
    ##wishlist.append("night_fog")
    ##wishlist.append("overview")
    #wishlist.append("true_color_raw")          
    #wishlist.append("natural_with_night_fog")
    #wishlist.append("precipitation_probability")
    #wishlist.append("cloudmask_extended")
    #wishlist.append("cloudmask_probability")
    #wishlist.append("cloud_drop_effective_radius")
    #wishlist.append("cloud_optical_thickness")
    #wishlist.append("night_microphysics")
    #wishlist.append("cloud_phase_distinction")
    #wishlist.append("cloud_phase_distinction_raw")
    ###### CMIC products 
    #wishlist.append("cloud_water_path")
    #wishlist.append("ice_water_path")
    #wishlist.append("liquid_water_path")
    #wishlist.append("cloud_phase")          # needs 1.6, 2.2, 0.67
    #wishlist.append("cloud_phase_raw")      # needs 1.6, 2.2, 0.67
    #wishlist.append("cimss_cloud_type")     # needs 1.4, 04, 1.6
    #wishlist.append("cimss_cloud_type_raw") # needs 1.4, 04, 1.6
    #### self specified composites (need a modified satpy/satpy/etc/composites/seviri.yaml)
    wishlist.append("DayNightMicrophysics")
    wishlist.append("DayNightFog")
    wishlist.append("DayConvectionNightMicrophysics")
    wishlist.append("DayNightOverview")
    #wishlist.append("SWconvection")
    wishlist.append("DaySWconvectionNightMicrophysics")
    
    shapes_dir='/opt/users/common/shapes/'

    ###############################################################

    #composites=["day_microphysics","_hrv"]  # does not work with to_image, only with show!!!
    #composites=["convection","_hrv"]  # does not work with to_image, only with show!!!
    #composites=["overview_raw","_hrv"]
    #composites=["overview","_hrv"]
    #composites=["vis_with_ir_cloud_overlay"]
    #composites=["cloud_top_height"]
    #composites=["DayNightMicrophysics"]
    #composites=["DayNightFog"]
    #composites=["DayConvectionNightMicrophysics"]
    #composites=["HRoverview"]           # more yellowish than LuminanceSharpened overview_raw ??? 
    #composites=["DayNightOverview","HRoverview"]
    composites=wishlist 
    
    print("... load composites: ", composites)
    for comp in composites:
        print("   "+comp)
    global_scene.load(composites)

    areas=[]
    #areas.append("ccs4")
    areas.append('EuropeCenter')
    
    for area in areas:

        areadef = get_area_def(area)

        print("... resample to area "+area)
        # https://satpy.readthedocs.io/en/stable/resample.html
        if area=="ccs4":
            #local_scene = global_scene.resample(area, resampler="bilinear", cache_dir='/tmp/', precompute=True)
            #local_scene = global_scene.resample(area, resampler="bilinear", cache_dir='/tmp/')
            local_scene = global_scene.resample(area, resampler="bilinear", precompute=True)
        else:
            local_scene = global_scene.resample(area, radius_of_influence=5000, precompute=True)

        # reload composites
        print("... reload composites")
        local_scene.load(composites)
            
        for comp in composites:
        #for comp in []:
            
            if False:
              #local_scene.show(comp)
              local_scene.show(comp, overlay={'coast_dir': shapes_dir, 'color': (255, 0, 0),
                                                'resolution': 'i', 'width': 1.0})    #does not work level_coast=1, level_borders=1
            else:
              pngfile = outputDir+comp+"_"+ area+"_"+time_string+".png"
              print("... create "+pngfile)
              local_scene.save_dataset(comp, pngfile)
              #img = to_image(local_scene[comp])     # does not work with airmass, overview ... 
              #if (comp=="HRoverview"):              # only works for pytroll img, not for PIL image
              #    print("*** apply gamma enhancement")
              #    img.gamma(2.0)                    # only works for pytroll img, not for PIL image
              #img.save(pngfile)                     
              ##original = cv2.imread(pngfile)
              ##if (comp=="HRoverview"):                    # looks too yellowish, bright 
              ##    print("*** apply gamma enhancement")
              ##    img = adjust_gamma(original, gamma=2)
              ##    cv2.imwrite(pngfile, img)
              img = Image.open(pngfile)
              cw = ContourWriter(shapes_dir)
              cw.add_coastlines(img, areadef, resolution='i', outline='red')
              cw.add_borders(img, areadef, resolution='i', outline='red')
              #cw.add_rivers(img, areadef, resolution='i', outline='blue')     # h and f does not work
              #font = ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf",16)
              #cw.add_grid(img, areadef, (2.0,2.0), (0.5,0.5), font, fill='blue', outline='blue', minor_outline='white')
              img.save(pngfile)
              print("display "+pngfile+" &")
              print()

        LuminanceSharpening=False
        #LuminanceSharpening=True
        comp=composites[0]
        if LuminanceSharpening:
            vis_data = local_scene['_hrv']
            base_image = local_scene[comp]
            compositor = LuminanceSharpeningCompositor("HR"+comp)
            composite = compositor([vis_data, base_image])
            img = to_image(composite)
            if (comp=="overview" or comp=="overview_raw"): 
                #from satpy.enhancements import gamma
                #gamma(img, gamma=2)
                img.gamma(2.0)
            pngfile=outputDir+"HR"+comp+"_" + area + "_" + time_string + ".png"
            img.save(pngfile)
            print("display "+pngfile+" &")
            print()

        #Sandwich=True
        Sandwich=False
        if Sandwich:
            vis_data = local_scene['_hrv']
            base_image = local_scene[comp]
            compositor = SandwichCompositor("SW"+comp)
            composite = compositor([vis_data, base_image])
            img = to_image(composite)
            pngfile=outputDir+"SW"+comp+"_" + area + "_" + time_string + ".png"
            img.save(pngfile)
