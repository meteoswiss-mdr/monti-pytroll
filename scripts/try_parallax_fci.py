from satpy import Scene
from glob import glob

from source.parallax import ParallaxCorrection as IussiParallaxCorrection
from satpy.modifiers.parallax import ParallaxCorrection as SatpyParallaxCorrection

from satpy.utils import debug_on; debug_on()


def get_cropped_fci_and_cth_inputs(fci_filenames, fci_dataset, oca_filename, oca_dataset):
    fci_scn = Scene(filenames=fci_filenames, reader='fci_l1c_nc')
    fci_scn.load([fci_dataset], upper_right_corner='NE')
    oca_scn = Scene(filenames=oca_filename, reader='fci_l2_nc')
    oca_scn.load([oca_dataset], upper_right_corner='NE')
    # add the L1 orbital parameters into the OCA product
    oca_scn[oca_dataset].attrs['orbital_parameters'] = fci_scn[fci_dataset].attrs['orbital_parameters']
    # resample to eurol1 area
    fci_scn_e = fci_scn.resample("eurol1", resampler='nearest')
    oca_scn_e = oca_scn.resample("eurol1", resampler='nearest')
    # crop around Central Europe
    fci_scn_c = fci_scn_e.crop(ll_bbox=[5, 40, 20, 50])
    oca_scn_c = oca_scn_e.crop(ll_bbox=[5, 40, 20, 50])

    return fci_scn_c, oca_scn_c


fci_filenames = sorted(glob("/tcenas/fbf/mtg/RollingBuffer/OPE/idpfi/FCI-L1/20250515/*FDHSI*__O_0040*"))
fci_dataset = "ir_105"

oca_filename = ["/tcenas/fbf/mtg/RollingBuffer/OPE/l2pf/FCI-L2/20250515/W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-2-OCA--FD------NC4E_C_EUMT_20250515064533_L2PF_OPE_20250515063000_20250515064000_N__C_0040_0000.nc"]
oca_dataset = "retrieved_cloud_top_height"

fci_scn_c, oca_scn_c = get_cropped_fci_and_cth_inputs(fci_filenames, fci_dataset, oca_filename, oca_dataset)

# save the original datasets images
fci_scn_c.save_dataset(fci_dataset, filename="/tcenas/home/andream/tmp/plax_test/fci_scn_c.png", writer="simple_image")
oca_scn_c.save_dataset(oca_dataset, filename="/tcenas/home/andream/tmp/plax_test/oca_scn_c.png", writer="simple_image")

#### JUSSI ##########
iussi_parallax_correction = IussiParallaxCorrection(fci_scn_c[fci_dataset].attrs["area"])
plax_corr_area = iussi_parallax_correction(oca_scn_c[oca_dataset])

# resample to the new SwathDefinition
fci_scn_c_plax_res = fci_scn_c.resample(plax_corr_area, resampler='nearest', mask_area=True, radius_of_influence=10e6)
fci_scn_c_plax_res.save_dataset(fci_dataset, filename="/tcenas/home/andream/tmp/plax_test/fci_scn_c_plax_res.png", writer="simple_image")

# copy the data into the original AreaDefinition and run a new resampling to fill the gaps

## ATTENTION: for the following lines to work you have to comment out these lines in your
# pyresample, otherwise the gapfilling will be skipped as the areas are the same
# https://github.com/pytroll/pyresample/blob/3c072554474a7d0087e98b8c3c3396557d631ea9/pyresample/resampler.py#L121-L122
# see according issue https://github.com/pytroll/pyresample/issues/660
fci_scn_c_plaxcorr = fci_scn_c.copy()
fci_scn_c_plaxcorr[fci_dataset].data = fci_scn_c_plax_res[fci_dataset].data
fci_scn_c_plaxcorr_gapfilled = fci_scn_c_plaxcorr.resample(fci_scn_c[fci_dataset].attrs["area"], resampler='nearest', mask_area=True, radius_of_influence=10e6)
fci_scn_c_plaxcorr_gapfilled.save_dataset(fci_dataset, filename="/tcenas/home/andream/tmp/plax_test/fci_scn_c_plaxcorr_gapfilled.png", writer="simple_image")


# ###### SATPY #########
# # Have to start from scratch with new Scenes since .copy() on a Scene seems to be not deep enough
# and there's a leak leading to the parallax correction being applied twice otherwise....
fci_scn_c, oca_scn_c = get_cropped_fci_and_cth_inputs(fci_filenames, fci_dataset, oca_filename, oca_dataset)

satpy_parallax_correction = SatpyParallaxCorrection(fci_scn_c[fci_dataset].attrs["area"])
satpy_plax_corr_area = satpy_parallax_correction(oca_scn_c[oca_dataset])

fci_scn_c_plax_res_satpy = fci_scn_c.resample(satpy_plax_corr_area, resampler='nearest', mask_area=True, radius_of_influence=10e6)
fci_scn_c_plax_res_satpy.save_dataset(fci_dataset, filename="/tcenas/home/andream/tmp/plax_test/fci_scn_c_plax_res_satpy.png", writer="simple_image")

fci_scn_c_plaxcorr_satpy = fci_scn_c.copy()
fci_scn_c_plaxcorr_satpy[fci_dataset].data = fci_scn_c_plax_res_satpy[fci_dataset].data
fci_scn_c_plaxcorr_gapfilled_satpy = fci_scn_c_plaxcorr_satpy.resample(fci_scn_c[fci_dataset].attrs["area"], resampler='nearest', mask_area=True, radius_of_influence=10e6)
fci_scn_c_plaxcorr_gapfilled_satpy.save_dataset(fci_dataset, filename="/tcenas/home/andream/tmp/plax_test/fci_scn_c_plaxcorr_gapfilled_satpy.png", writer="simple_image")

