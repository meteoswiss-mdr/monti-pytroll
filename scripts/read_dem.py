"""Loader for DEM (topography) in netcdf format.
"""
from mpop import CONFIG_PATH
import os
from netCDF4 import Dataset
import numpy.ma as ma
from glob import glob
from mpop.projector import get_area_def

def read_dem():
    """Read digital elevation model (DEM) in netCDF format.
    """

    filename = "/data/COALITION2/database/topography/GTOPO30/dtm_acquire_ccs4_float_v3.nc" 

    print "... read from file: ", filename

    # Load data from netCDF file
    ds = Dataset(filename, 'r')

    data = ds.variables[chn_name][:,:]
    print type(data)
    print type(ma.asarray(data))

    area_def = get_area_def("ccs4")
