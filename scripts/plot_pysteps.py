from netCDF4 import Dataset
import datetime
import pyresample
import numpy as np
from mpop import CONFIG_PATH
import os
import subprocess
from copy import deepcopy
from os.path import exists, dirname
from os import makedirs

time_slot = datetime.datetime(2018,8,7,15,0)

mv_file=time_slot.strftime("/data/COALITION2/PicturesSatellite/results_JMZ/2_input_NOSTRADAMUS_ANN/UV_precalc/%Y%m%d_RZC_disparr_UV.nc")
print "... read motion vector from ", mv_file
ncfile = Dataset(mv_file,'r')
#Dx = ncfile.variables["Dx"][:,:,:]
#Dy = ncfile.variables["Dy"][:,:,:]

# volocity in pixel per 5min in x and y
Vx = ncfile.variables["Vx"][:,:,:]
Vy = ncfile.variables["Vy"][:,:,:]

ps_time = ncfile.variables["time"][:]

ref_time = datetime.datetime(2018,8,8,0,0)
ps_times = np.array([ref_time + datetime.timedelta(minutes=int(tt)) for tt in ps_time])

smooth_in_time=True
if smooth_in_time:
    print "smooth in time"
    Vx2 = deepcopy(Vx)
    Vy2 = deepcopy(Vy)
    for it in range(1,ps_times.size-1):
        Vx2[it,:,:] = (Vx[it-1,:,:]+Vx[it,:,:]+Vx[it+1,:,:])*(1./3.)
    for it in range(1,ps_times.size-1):
        Vy2[it,:,:] = (Vy[it-1,:,:]+Vy[it,:,:]+Vy[it+1,:,:])*(1./3.)
    Vx = Vx2
    Vy = Vy2

mv_area = pyresample.utils.load_area(os.path.join(CONFIG_PATH, "areas.def"), 'ccs4')

it = np.where(ps_times == time_slot)[0][0]
from mpop.imageo.HRWimage import HRWstreamplot
from mpop.imageo.HRWimage import prepare_figure
from mpop.imageo.TRTimage import fig2img
result_dir="/data/COALITION2/PicturesSatellite/%Y-%m-%d/"

for it in range(1,ps_times.size):
#for it in [140]:

    mv_File = ps_times[it].strftime(result_dir+ "%Y-%m-%d_MV_ccs4//PS_MV-ccs4_%y%m%d%H%M.png")
    
    streamplot=False
    if streamplot:
        # !!! should be checked once more, if 12 (as Vx in pix(1km)/5min, and 12*5min=1h) is correct and if x and y is correct !!! 
        mv_PIL_image = HRWstreamplot( 12*Vx[it,:,:], -12*Vy[it,:,:], mv_area, '', color_mode='speed', vmax=25, linewidth_max=1.2, colorbar=False) # , colorbar=False, legend=True, legend_loc=3
        mv_PIL_image.save(mv_File)
        print "display "+mv_File+" &"

    quiverplot=False
    if quiverplot:
        fig, axes = prepare_figure(mv_area)
        
        ## Prepare UV field for quiver plot
        UV_field = np.moveaxis(np.dstack((Vx[it,:,:],Vy[it,:,:])),2,0)
        step = 40; X,Y = np.meshgrid(np.arange(UV_field.shape[2]),np.arange(UV_field.shape[1]))
        UV_ = UV_field[:, 0:UV_field.shape[1]:step, 0:UV_field.shape[2]:step]
        X_ = X[0:UV_field.shape[1]:step, 0:UV_field.shape[2]:step]; Y_ = Y[0:UV_field.shape[1]:step, 0:UV_field.shape[2]:step]
        #axes.quiver(X_, Y_, UV_[0,:,:], -UV_[1,:,:], pivot='tip', color='lightgrey')
        axes.quiver(X_, Y_, UV_[0,::-1,:], -UV_[1,:,:], pivot='tip', color='grey')

        mv_PIL_image = fig2img(fig)
        mv_File = ps_times[it].strftime(result_dir+ "%Y-%m-%d_MV_ccs4//PS_MV-ccs4_%y%m%d%H%M.png")
        mv_PIL_image.save(mv_File)
        print "display "+mv_File+" &"        
        
    create_composite=True
    if create_composite:
        #mv_File = ps_times[it].strftime(result_dir+ "%Y-%m-%d_MV_ccs4//PS_MV-ccs4_%y%m%d%H%M.png")
        TRT_File  = ps_times[it].strftime(result_dir+ "%Y-%m-%d_TRT-radar-HRVir108_ccs4/MSG_TRT-radar-HRVir108-ccs4_%y%m%d%H%M.png")
        comp_file = ps_times[it].strftime(result_dir+ "%Y-%m-%d_MV-TRT-radar-HRVir108_ccs4/MSG_MV-TRT-radar-HRVir108-ccs4_%y%m%d%H%M.png")
        if not exists(dirname(comp_file)):
            makedirs(dirname(comp_file))
        command="/usr/bin/composite -depth 8 "+mv_File+" "+TRT_File+" "+comp_file
        print command
        subprocess.call(command, shell=True)
        print "display "+comp_file+" &"
