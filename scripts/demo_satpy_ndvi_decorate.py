
#from satpy import Scene
from satpy.utils import debug_on
debug_on()

#from glob import glob
#base_dir="/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/2015/07/07/"
#import os
#os.chdir(base_dir)
#filenames = glob("*201507071200*__")
#print(base_dir)
#print(filenames)
##global_scene = Scene(reader="hrit_msg", filenames=filenames, base_dir=base_dir, ppp_config_dir="/opt/users/hau/PyTroll//cfg_offline/")
#global_scene = Scene(reader="hrit_msg", filenames=filenames, base_dir=base_dir, ppp_config_dir="/opt/users/hau/PyTroll/packages/satpy/satpy/etc")

#from satpy import available_readers
#available_readers()


# new version of satpy after 0.8
#################################
from satpy import find_files_and_readers, Scene
from datetime import datetime
import numpy as np
from copy import deepcopy

show_details=False
save_overview=True

files_sat = find_files_and_readers(sensor='seviri',
                               start_time=datetime(2015, 7, 7, 12, 0),
                               end_time=datetime(2015, 7, 7, 12, 0),
                               base_dir="/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/2015/07/07/",
                               reader="seviri_l1b_hrit")

#print (files_sat)
#files = dict(files_sat.items() + files_nwc.items())
#files = dict(files_sat.items())
sat="MSG2"
print("=============================")
print("remove all other MSG satellites (except MSG4) and unused channels")
files = deepcopy(files_sat['seviri_l1b_hrit'])
for f in files:
    if not (sat in f):
        files_sat['seviri_l1b_hrit'].remove(f)
        continue
    if ("HRV" in f) or ("IR_016" in f) or ("IR_039" in f):  # or ("VIS006" in f) or ("VIS008" in f) 
        files_sat['seviri_l1b_hrit'].remove(f)
        continue
    if  ("WV_062" in f) or ("WV_073" in f)  or ("IR_087" in f) or ("IR_097" in f)  or ("IR_120" in f) or ("IR_134" in f): # or ("IR_108" in f)
        files_sat['seviri_l1b_hrit'].remove(f)
        continue
for f in files_sat['seviri_l1b_hrit']:
    print(f)


global_scene = Scene(filenames=files_sat) # not allowed any more: reader="hrit_msg", 

print(dir(global_scene))

#global_scene.load([0.6, 0.8, 10.8])
#global_scene.load(['IR_120', 'IR_134'])
if save_overview:
    global_scene.load(['overview',0.6, 0.8])
else:
    global_scene.load([0.6,0.8])
#print(global_scene[0.6])            # works only if you load also the 0.6 channel, but not an RGB that contains the 0.6
#!!# print(global_scene['overview']) ### this one does only work in the develop version

global_scene.available_dataset_names()

global_scene["ndvi"] = (global_scene[0.8] - global_scene[0.6]) / (global_scene[0.8] + global_scene[0.6])
# !!! BUG: will not be resampled in global_scene.resample(area)

#from satpy import DatasetID
#my_channel_id = DatasetID(name='IR_016', calibration='radiance')
#global_scene.load([my_channel_id])
#print(scn['IR_016'])

#area="eurol"
#area="EuropeCanaryS95"
area="ccs4"
local_scene = global_scene.resample(area)

if show_details:
    help(local_scene)
    print( global_scene.available_composite_ids() )
    print( global_scene.available_composite_names() )
    print( global_scene.available_dataset_names() )
    print( global_scene.available_writers() )
    
if save_overview:
    #local_scene.show('overview')
    local_scene.save_dataset('overview', './overview_'+area+'.png', overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 255, 255), 'resolution': 'i'})
    print ('display ./overview_'+area+'.png &')

print("===============")
print("calcuate NDVI")
local_scene["ndvi"] = (local_scene[0.8] - local_scene[0.6]) / (local_scene[0.8] + local_scene[0.6])
#local_scene["ndvi"].area = local_scene[0.8].area
print ("local_scene[\"ndvi\"].min()", local_scene["ndvi"].compute().min())
print ("local_scene[\"ndvi\"].max()", local_scene["ndvi"].compute().max())

print("===============")
print("load land sea mask")
lsmask_file="/data/COALITION2/database/Land/LandSeaMask/SEVIRI/LandSeaMask_"+area+".nc"
from netCDF4 import Dataset
ncfile = Dataset(lsmask_file,'r')
# Read variable corresponding to channel name
lsmask = ncfile.variables['lsmask'][:,:] # attention [:,:] or [:] is really necessary

import dask.array as da
#print ('type(local_scene["ndvi"].data)', type(local_scene["ndvi"].data), local_scene["ndvi"].data.compute().shape)
#print ("type(lsmask)", type(lsmask), lsmask.shape, lsmask[:,:,0].shape,)
#local_scene["ndvi"].data.compute()[lsmask[:,:,0]==0]=np.nan
ndvi_numpyarray=local_scene["ndvi"].data.compute()
if area=="EuropeCanaryS95":
    ndvi_numpyarray[lsmask[::-1,:,0]==0]=np.nan
else:
    ndvi_numpyarray[lsmask[:,:,0]==0]=np.nan

local_scene["ndvi"].data = da.from_array(ndvi_numpyarray, chunks='auto')
#local_scene["ndvi"].data = local_scene["ndvi"].data.where(lsmask!=0)  

colorized=True

if not colorized:
    outfile='./ndvi_'+area+'.png'
    print("===============")
    print("plot black-white version: display "+outfile)
    #local_scene.save_dataset('ndvi', outfile)
    local_scene.save_dataset('ndvi', outfile, overlay={'coast_dir': '/data/OWARNA/hau/maps_pytroll/', 'color': (255, 255, 255), 'resolution': 'i'})
    #print (dir(local_scene.save_dataset))
else:    
    # https://github.com/pytroll/satpy/issues/459
    # from satpy.enhancements import colorize
    # colorize(img, **kwargs)
    # 'ylgn'
    # https://satpy.readthedocs.io/en/latest/writers.html
    # nice NDVI colourbar here:
    # https://www.researchgate.net/figure/NDVI-maps-Vegetation-maps-created-by-measuring-the-Normalized-Vegetation-Difference_fig7_323885082

    outfile='./ndvi_'+area+'.png'
    print("===============")
    print("plot colored version: display "+outfile)
    
    # colorize with satpy compositor, BWCompositor does not exits any more
    if False: 
        # from satpy.composites import BWCompositor does not exist anymore
        from satpy.composites import GenericCompositor
        from satpy.enhancements import colorize
        from satpy.writers import to_image

        compositor = GenericCompositor("test", standard_name="ndvi")
        composite = compositor((local_scene["ndvi"], ))
        img = to_image(composite)
        #from trollimage import colormap
        #dir(colormap)
        # 'accent', 'blues', 'brbg', 'bugn', 'bupu', 'colorbar', 'colorize', 'dark2', 'diverging_colormaps', 'gnbu', 'greens',
        # 'greys', 'hcl2rgb', 'np', 'oranges', 'orrd', 'paired', 'palettebar', 'palettize', 'pastel1', 'pastel2', 'piyg', 'prgn',
        # 'pubu', 'pubugn', 'puor', 'purd', 'purples', 'qualitative_colormaps', 'rainbow', 'rdbu', 'rdgy', 'rdpu', 'rdylbu', 'rdylgn',
        # 'reds', 'rgb2hcl', 'sequential_colormaps', 'set1', 'set2', 'set3', 'spectral', 'ylgn', 'ylgnbu', 'ylorbr', 'ylorrd'

        #    kwargs = {"palettes": [{"colors": 'ylgn',
        #                            "min_value": -0.1, "max_value": 0.9}]}

        #arr = np.array([[230, 227, 227], [191, 184, 162], [118, 148, 61], [67, 105, 66], [5, 55, 8]])
        arr = np.array([ [ 95,  75,  49], [210, 175, 131], [118, 148, 61], [67, 105, 66], [28, 29, 4]])
        np.save("/tmp/binary_colormap.npy", arr)

        kwargs = {"palettes": [{"filename": "/tmp/binary_colormap.npy",
                                "min_value": -0.1, "max_value": 0.8}]}


        colorize(img, **kwargs)

    # colorize with trollimage: does not produce correct type of image
    if True:
        from trollimage.image import Image as trollimage
        #from trollimage.colormap import rdylgn
        from trollimage.colormap import ndvi
        #rdylgn.set_range( -1., +1.)
        img = trollimage(local_scene["ndvi"].values, mode="L")
        #img.colorize(rdylgn)
        img.colorize(ndvi)

    # last try not finished ... 
    if False:
        from satpy.composites import PaletteCompositor
        compositor = PaletteCompositor("palcomp")
        composite = compositor([local_scene['ndvi'], local_scene['cma_pal']])

        
    from satpy.writers import add_decorate, add_overlay

    decorate = {
        'decorate': [
            {'logo': {'logo_path': '/opt/users/common/logos/meteoSwiss.png', 'height': 60, 'bg': 'white','bg_opacity': 255, 'align': {'top_bottom': 'top', 'left_right': 'right'}}},
            {'text': {'txt': ' MSG, '+local_scene.start_time.strftime('%Y-%m-%d %H:%MUTC')+', '+ area+', NDVI',
                      'align': {'top_bottom': 'top', 'left_right': 'left'},
                      'font': "/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf",
                      'font_size': 19,
                      'height': 25,
                      'bg': 'white',
                      'bg_opacity': 0,
                      'line': 'white'}}
        ]
    }

    print("############################")
    print(type(img))
    print("add_decorate")
    #img = add_decorate(img, **decorate) #, fill_value='black'
    print("add_overlay")    
    #img = add_overlay(img, area, '/data/OWARNA/hau/maps_pytroll/', color='red', width=0.5, resolution='i', level_coast=1, level_borders=1, fill_value=None)

    #from satpy.writers import compute_writer_results
    #res1 = scn.save_datasets(filename="/tmp/{name}.png",
    #                         writer='simple_image',
    #                         compute=False)
    #res2 = scn.save_datasets(filename="/tmp/{name}.tif",
    #                         writer='geotiff',
    #                         compute=False)
    #results = [res1, res2]
    #compute_writer_results(results)

    
    #img.show()
    img.save(outfile)


print ('display '+outfile+' &')
