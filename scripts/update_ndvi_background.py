
f_background="./MSG_NDVI-EuropeCanaryS95_background.nc"
f_old="MSG_NDVI-EuropeCanaryS95_2002150915.nc"
f_new="MSG_NDVI-EuropeCanaryS95_2002151215.nc"
variableName =  'ndvi'

use_xarray=True
if use_xarray:
    import xarray as xr
    import numpy as np
    ds_bg = xr.open_dataset(f_old)
    #print("shape ndvi: ", ds_bg["ndvi"].values.shape)
    print("number of not a number elements (old): ", int(np.isnan(ds_bg["ndvi"]).sum()))
    ds_new = xr.open_dataset(f_new)
    print("number of not a number elements (new): ", int(np.isnan(ds_new["ndvi"]).sum()))
    ds_new["ndvi"].values = ds_new["ndvi"].fillna(ds_bg["ndvi"])
    #ds_new["ndvi"].values =  np.where(~np.isnan(ds_new["ndvi"]), ds_new["ndvi"], ds_bg["ndvi"])
    print("number of not a number elements (filled): ", int(np.isnan(ds_new["ndvi"]).sum()))
    ds_new.to_netcdf(f_background)
    
use_numpy=False
if use_numpy:
    import netCDF4 as nc
    import numpy as np

    fh_background = nc.Dataset(f_background, mode='r')
    background = fh_background.variables[variableName][:]
    fh_background.close()

    fh_new = nc.Dataset(f_new, mode='r')
    new = fh_new.variables[variableName][:]
    fh_new.close()

    print (type (background))

    background =  np.where(~np.isnan(new), new, background)

    #(nx,ny) = background.shape
    #for i in range(500,600,1):
    #    for j in range(200,300,1):
    #        #print i,j
    #        val[i][j] = -99900.0
    #        if val[i][j]> -99900.0:
    #           print val[i][j]

    ncfile="./MSG_NDVI-EuropeCanaryS95_background.nc"
    fh = nc.Dataset(ncfile, mode='r+')   # read plus update
    fh.variables[variableName][:]= background
    fh.close()
