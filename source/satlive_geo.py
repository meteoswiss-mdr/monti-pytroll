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
from time import sleep 
from glob import glob
from PIL import Image, ImageFont
import numpy as np
import dask as da
from os.path import exists, getsize 

from satpy import Scene, find_files_and_readers
from satpy.writers import to_image
from satpy.composites import LuminanceSharpeningCompositor
from satpy.composites import SandwichCompositor
from satpy.resample import get_area_def
from satpy.writers import add_decorate, add_overlay

from copy import deepcopy 

from my_msg_module_py3 import get_last_SEVIRI_date, format_name
from get_input_msg_py3 import parse_commandline_and_read_inputfile

from parallax_jussi import save_image

from pycoast import ContourWriter

from get_input_msg_py3 import get_input_msg 

import warnings
import subprocess

def rename_outputFile(outputFile):
    outputFile = outputFile.replace("-ir108", "ir108")
    outputFile = outputFile.replace("-vis-with-ir", "HRVir108")
    outputFile = outputFile.replace("natural-color", "natural")
    return outputFile 

if sys.version_info < (2, 5):
    import time

    def strptime(string, fmt=None):
        """This function is available in the datetime module only
        from Python >= 2.5.
        """

        return datetime(*time.strptime(string, fmt)[:6])

else:
    strptime = datetime.strptime

#####################################
# from https://stackoverflow.com/questions/37662180/interpolate-missing-values-2d-python

def interpolate_missing_pixels(
        image: np.ndarray,
        mask: np.ndarray,
        method: str = 'nearest',
        fill_value: int = 0):
    """
    :param image: a 2D image
    :param mask: a 2D boolean image, True indicates missing values
    :param method: interpolation method, one of
        'nearest', 'linear', 'cubic'.
    :param fill_value: which value to use for filling up data outside the
        convex hull of known pixel values.
        Default is 0, Has no effect for 'nearest'.
    :return: the image with missing values interpolated
    """
    from scipy import interpolate

    h, w = image.shape[:2]
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))

    known_x = xx[~mask]
    known_y = yy[~mask]
    known_v = image[~mask]
    missing_x = xx[mask]
    missing_y = yy[mask]

    interp_values = interpolate.griddata(
        (known_x, known_y), known_v, (missing_x, missing_y),
        method=method, fill_value=fill_value
    )

    interp_image = image.copy()
    interp_image[missing_y, missing_x] = interp_values

    return interp_image


# https://docs.xarray.dev/en/stable/generated/xarray.DataArray.interpolate_na.html
# xr.DataArray(array, coords=da.coords, dims=da.dims, attrs=da.attrs)
#############################################################


def adjust_gamma(image, gamma=1.0):
    # import the necessary packages
    import cv2
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
		      for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

#######################################################
    
if __name__ == '__main__':

    # interpret command line arguments (first argument is configuration file) and read configuration file 
    in_msg = parse_commandline_and_read_inputfile()
    
    print("... produce satellite image for: "+in_msg.datetime.strftime("%Y-%m-%d, %H:%M:%S"))
        
    print("... check if RSS is available by counting RSS files 5 min ago") 
    print("")
    time_string = in_msg.datetime.strftime("%Y%m%d%H%M")
    t_minus5 = in_msg.datetime - timedelta(minutes=5)
    sat="MSG3"
    
    if (in_msg.nrt):
        data_hrit_in="/data/cinesat/in/eumetcast1/"
        data_nwcsaf_in="/data/cinesat/in/safnwc/"
    else:
        data_hrit_in=in_msg.datetime.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/%Y/%m/%d/")
        data_nwcsaf_in=in_msg.datetime.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/*/")        
            
    n_files = len(glob(data_hrit_in+'/H*'+sat+'*'+t_minus5.strftime("%Y%m%d%H%M")+'*'))
    if n_files > 38:   # 44 files are full delivery, but only 39 files are archived 
        # assume that RSS is delivered
        print("... found "+str(n_files)+" files of RSS mode in "+data_hrit_in+", use MSG3")
        
    else:
        # need to use full disk service
        print("*** Warning, found not sufficient RSS files (",n_files,") in "+data_hrit_in+", use full disk service instead")
        sat="MSG4"
        #if len(sys.argv) < 2:
        #    time_slot = get_last_SEVIRI_date(False, delay=5)
        if in_msg.datetime.minute % 15 == 0:
            print("... Full Disk Service available, switch to "+sat)
        else:
            print("... no Full Disk Service for this time slot, full stop")
            quit()

    # loop until EPI satellite data has arrived in folder
    for i in range(30):   # maximum waiting time 30x30s = 15min = 1 Full Disk Scan 
        EPI_file=glob(data_hrit_in+'/H*'+sat+'*'+"EPI"+"*"+time_string+'*')
        if len(EPI_file) > 0:
            if getsize(EPI_file[0]) > 370000:
                print("... Epilog file (", EPI_file[0],") has arrived and its size is ", getsize(EPI_file[0]))
                break
        print("... Epilog file (", data_hrit_in+'/H*'+sat+'*'+"EPI"+"*"+time_string+'*',") has not arrived yet, sleep 30s")
        sleep(30)
    
    print("")
    print("search HRIT   input files for "+sat+" "+str(in_msg.datetime)+": " + data_hrit_in+'/H*'+sat+'*'+time_string+'*')
    files_hrit=glob(data_hrit_in+'/H*'+sat+'*'+time_string+'*')
    print("   found ", len(files_hrit), " files")
    #print(files_hrit)
    print("")
    print("search NWCSAF input files for "+sat+" "+str(in_msg.datetime)+" in " + data_nwcsaf_in, ":",
          data_nwcsaf_in+'/S_NWC*'+sat+'*'+in_msg.datetime.strftime("%Y%m%dT%H%M")+'*.nc')
    files_nwcsaf=glob(data_nwcsaf_in+'/S_NWC*'+sat+'*'+in_msg.datetime.strftime("%Y%m%dT%H%M")+'*.nc')
    print("   found ", len(files_nwcsaf), " files")
    #print(files_nwcsaf)
    print("")

    print("... create satpy scene with all files")
    #print(glob(data_hrit_in+'/H*MSG3*'+time_string+'*'))
    #print(glob(data_nwcsaf_in+'/S_NWC*MSG3*'+time_string_nwcsaf+'*.nc'))
    #global_scene = Scene(filenames={'seviri_l1b_hrit': files_hrit,'nwcsaf-geo': files_nwcsaf})
    global_scene = Scene(filenames={'seviri_l1b_hrit': files_hrit})
    #global_scene = Scene(platform_name="Meteosat-9", sensor="seviri", reader="hrit_msg", start_time=in_msg.datetime)
    
    print("")
    print("... load composites")
    for comp in in_msg.RGBs:
        print("   "+comp.replace("_", "-")+"  scp:", comp in in_msg.scpProducts)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        #global_scene.load(["VIS006",'ctth_alti'])
        #global_scene.load(["IR_108",'ctth_alti'])
        #global_scene["ctth_alti"].attrs['orbital_parameters']=global_scene["IR_108"].attrs['orbital_parameters']
        global_scene.load(in_msg.RGBs)
    
    for area in in_msg.areas:

        areadef = get_area_def(area)

        print("... resample to area "+area)
        # https://satpy.readthedocs.io/en/stable/resample.html
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            warnings.filterwarnings("ignore", category=UserWarning)
            #resampler="bilinear"
            resampler="nearest"
            if area=="ccs4":
                #local_scene = global_scene.resample(area, resampler=resampler, cache_dir='/tmp/', precompute=True)
                #local_scene = global_scene.resample(area, resampler=resampler, cache_dir='/tmp/')
                local_scene = global_scene.resample(area, resampler=resampler, precompute=True)
            else:
                local_scene = global_scene.resample(area, radius_of_influence=5000, precompute=True)

            # reload composites
            print("... reload composites")
            local_scene.load(in_msg.RGBs)
        
            for comp in in_msg.RGBs:
            #for comp in []:

                # show interactively 
                if False:
                    #local_scene.show(comp)
                    local_scene.show(comp, overlay={'coast_dir': in_msg.mapDir, 'color': (255, 0, 0),
                                                    'resolution': 'i', 'width': 1.0})    #does not work level_coast=1, level_borders=1
                # save as png file 
                if True:
                    print(in_msg.datetime)
                    print("==============")
                    outputFile = in_msg.outputDir+"MSG_"+comp.replace("_", "-")+"-"+ area+"_"+in_msg.datetime.strftime("%y%m%d%H%M")+".png"
                    outputFile = rename_outputFile(outputFile)
                    #print("... create "+outputFile)
                    title    = in_msg.datetime.strftime(" "+sat[0:3]+"-"+sat[3]+', %y-%m-%d %H:%MUTC, '+area+', '+comp)
                    decorate = {
                        'decorate': [
                            {'logo': {'logo_path': '/opt/users/common/logos/meteoSwiss.png', 'height': 60, 'bg': 'white',
                                      'bg_opacity': 255, 'align': {'top_bottom': 'top', 'left_right': 'right'}}},
                            {'text': {'txt': title,
                                      'align': {'top_bottom': 'top', 'left_right': 'left'},
                                      'font': "/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf",
                                      'font_size': 18,
                                      'height': 26,
                                      'bg': 'black',
                                      'bg_opacity': 50,
                                      'line': 'white'}}
                        ]
                    }
                    
                    local_scene.save_dataset(comp, outputFile, decorate=decorate)
                    #img = to_image(local_scene[comp])     # does not work with airmass, overview ... 
                    #if (comp=="HRoverview"):              # only works for pytroll img, not for PIL image
                    #    print("*** apply gamma enhancement")
                    #    img.gamma(2.0)                    # only works for pytroll img, not for PIL image
                    #img.save(outputFile)                     
                    #original = cv2.imread(outputFile)
                    #if (comp=="HRoverview"):                    # looks too yellowish, bright 
                    #    print("*** apply gamma enhancement")
                    #    img = adjust_gamma(original, gamma=2)
                    #    cv2.imwrite(outputFile, img)
                    img = Image.open(outputFile)
                    cw = ContourWriter(in_msg.mapDir)
                    cw.add_coastlines(img, areadef, resolution='i', outline='red')
                    cw.add_borders(img, areadef, resolution='i', outline='red')
                    #cw.add_rivers(img, areadef, resolution='i', outline='blue')     # h and f does not work
                    #font = ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf",16)
                    #cw.add_grid(img, areadef, (2.0,2.0), (0.5,0.5), font, fill='blue', outline='blue', minor_outline='white')
                    img.save(outputFile)
                    print("... display "+outputFile+" &")

                    # secure copy file to another place
                    if in_msg.scpOutput:
                        if (comp in in_msg.scpProducts) or ('all' in [x.lower() for x in in_msg.scpProducts if type(x)==str]):
                            scpOutputDir = format_name (in_msg.scpOutputDir, in_msg.datetime, area=area, rgb=comp.replace("_", "-") )
                            scpOutputDir = rename_outputFile(scpOutputDir)
                            if in_msg.compress_to_8bit:
                                command_line_command="scp "+in_msg.scpID+" "+outputFile.replace(".png","-fs8.png")+" "+scpOutputDir+" 2>&1 &"
                                if in_msg.verbose:
                                    print("... secure copy: "+command_line_command)
                                subprocess.call(command_line_command, shell=True)
                            else:
                                command_line_command="scp "+in_msg.scpID+" "+outputFile+" "+scpOutputDir+" 2>&1 &"
                                if in_msg.verbose:
                                    print("... secure copy: "+command_line_command)
                                subprocess.call(command_line_command, shell=True)
                    
                if False:
                    # for parallax corrected images, fill data gaps 
                    print("fill missing values in data file")
                    title    = in_msg.datetime.strftime(" "+sat[0:3]+"-"+sat[3]+', %y-%m-%d %H:%MUTC, parallax correction')
                    filename = in_msg.datetime.strftime(in_msg.outputDir+'MSG_'+comp+'-'+area+'_%y%m%d%H%M_.png')
                    show_interactively=False
                    my_data = deepcopy(local_scene[comp].data)
                    mask = np.isnan(local_scene[comp].data.compute())
                    local_scene[comp].data = da.array.from_array(interpolate_missing_pixels(local_scene[comp].data.compute(), mask, method='linear'))
                    save_image(local_scene, area, comp, title=title, filename=filename, show_interactively=show_interactively)
                    

        LuminanceSharpening=False
        #LuminanceSharpening=True
        comp=in_msg.RGBs[0]
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
            outputFile=in_msg.outputDir+"MSG_HR"+comp+"-" + area + "_" + in_msg.datetime.strftime("%y%m%d%H%M") + ".png"
            img.save(outputFile)
            print("display "+outputFile+" &")
            print()

        #Sandwich=True
        Sandwich=False
        if Sandwich:
            vis_data = local_scene['_hrv']
            base_image = local_scene[comp]
            compositor = SandwichCompositor("SW"+comp)
            composite = compositor([vis_data, base_image])
            img = to_image(composite)
            outputFile=in_msg.outputDir+"MSG_SW"+comp+"-" + area + "_" + in_msg.datetime.strftime("%y%m%d%H%M") + ".png"
            img.save(outputFile)
            print("display "+outputFile+" &")
            print()
