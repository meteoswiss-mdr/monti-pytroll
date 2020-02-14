from __future__ import division
from __future__ import print_function

#!/usr/bin/python
import datetime
import logging

from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def

from pyresample import plot
import numpy as np
from pydecorate import DecoratorAGG
import aggdraw
from trollimage.colormap import rainbow, RainRate
from trollimage.image import Image as trollimage
from PIL import ImageFont, ImageDraw 
from pycoast import ContourWriterAGG
import sys

LOG = logging.getLogger(__name__)

delay=10

if len(sys.argv) > 1:
    if len(sys.argv) != 6:
        print("***           ")
        print("*** Warning, please specify date and time completely, e.g.")
        print("***          python plot_hsaf.py 2014 07 23 16 10 ")
        print("***           ")
        quit() # quit at this point
    else:
        print("*** get date from command line")
        year   = int(sys.argv[1])
        month  = int(sys.argv[2])
        day    = int(sys.argv[3])
        hour   = int(sys.argv[4])
        minute = int(sys.argv[5])
else:
    if True:  # automatic choise of last 5min 
        from my_msg_module import get_last_SEVIRI_date
        datetime1 = get_last_SEVIRI_date(False, delay=10)
        year  = datetime1.year
        month = datetime1.month
        day   = datetime1.day
        hour  = datetime1.hour
        minute = datetime1.minute
    else: # fixed date for text reasons
        year = 2015
        month = 12
        day = 16
        hour = 13
        minute = 30

datetime1=datetime.datetime(year,month,day,hour,minute)

#prop_str='DBZH'
prop_str='RATE'

#if len(sys.argv) > 1:
#   prop_str = sys.argv[1]

yearS = str(year)
#yearS = yearS[2:]
monthS = "%02d" % month
dayS   = "%02d" % day
hourS  = "%02d" % hour
minS   = "%02d" % minute
dateS=yearS+'-'+monthS+'-'+dayS
timeS=hourS+':'+minS+'UTC' 

#import sys, string, os
#sys.path.insert(0, "/opt/users/mbc/pytroll/install/lib/python2.6/site-packages")
#from mpop.utils import debug_on
#debug_on()

#time_slot = datetime.datetime(year, 12, 16, 13, 30)
time_slot = datetime.datetime(year, month, day, hour, minute )

load_radar=True
load_sat=True

#channel_list=['VIS006','VIS008','IR_016','IR_039','WV_062','WV_073','IR_087','IR_097','IR_108','IR_120','IR_134','HRV']
channel_list=['VIS006','VIS008','IR_016','IR_039','WV_062','WV_073','IR_087','IR_097','IR_108','IR_120','IR_134']
#channel_list=['IR_108']

if load_radar:
    global_radar = GeostationaryFactory.create_scene("odyssey", "", "radar", time_slot)
    global_radar.load([prop_str])
    print(global_radar)
    print("=========================")

if load_sat:
    global_sat = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot)
    #global_sat.load(['IR_108'], reader_level="seviri-level2") 
    global_sat.load(channel_list, reader_level="seviri-level2")
    print(global_sat)
    print("=========================")


color_mode='RainRate'

loutputDir = "/data/cinesat/out/"
#outputFile = "/tmp/test1."+prop_str+".png"

#print "global_radar[prop_str].product_name=",global_radar[prop_str].product_name

#area='odyssey'
#area='odysseyS25'
#area='EuropeCanary95'
area='EuropeOdyssey95'

reproject=True
if reproject:
   print('-------------------')
   print("start projection")
   # PROJECT data to new area 
   if load_radar:
       data_radar = global_radar.project(area, precompute=True)
       #data[prop_str].product_name = global_radar[prop_str].product_name
       #data[prop_str].units = global_radar[prop_str].units
       global_radar = data_radar
   if load_sat:
       data_sat = global_sat.project(area, precompute=True)
       global_sat = data_sat

       from pyorbital.astronomy import sun_zenith_angle
       lonlats = global_sat[channel_list[0]].area.get_lonlats()
       sza = sun_zenith_angle(datetime1, lonlats[0], lonlats[1])

       mask_sat=False
       if mask_sat:
           global_sat["IR_108"].data.mask = True-global_radar[prop_str+'-MASK'].data.mask
        

plot_radar = False
plot_sat = False

add_logos=True
add_colorscale=False
add_title=True
add_borders=True
verbose=True 
resolution='l'

# define area for drawing borders
print('-------------------')
obj_area = get_area_def(area)
print('obj_area ', obj_area)

if plot_radar or plot_sat:
    proj4_string = obj_area.proj4_string     
    # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
    print('proj4_string ',proj4_string)
    area_extent = obj_area.area_extent              
    # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
    area_def = (proj4_string, area_extent)
    print('-------------------')
    print('area_def ', area_def)


if plot_radar and load_radar:

    prop = global_radar[prop_str].data

    fill_value=None # transparent background 
    #fill_value=(1,1,1) # white background 
    min_radar = 0.0
    max_radar = 150
    colormap = RainRate

    if prop_str == 'RATE':
    #   prop = np.log10(prop)
    #   min_radar = prop.min()
    #   #max_radar = prop.max()
    #   #min_radar = -0.25 
    #   #max_radar = 1.9
    #   min_radar = -0.2 # log(0.63)
    #   max_radar = 2.41  # log(260)
    #   units='log(RR)'
    #   tick_marks = 1           # default
    #   minor_tick_marks = 0.1   # default
       lower_value=0.15

    if prop_str == 'DBZH':
       min_radar = -20
       max_radar = 70
       colormap = rainbow
       lower_value=13

    if prop_str == 'ACRR':
       min_radar = 0
       max_radar = 250
       lower_value=0.15

    if lower_value > -1000:
       prop [prop < lower_value ] = np.ma.masked

    LOG.debug("min_radar/max_radar: "+str(min_radar)+" / "+str(max_radar))
    colormap.set_range(min_radar, max_radar)

    img = trollimage(prop, mode="L", fill_value=fill_value)
    img.colorize(colormap)
    PIL_image=img.pil_image()
    dc = DecoratorAGG(PIL_image)

    layer=' 2nd layer'

    if add_borders:
        print("*** add borders") 
        cw = ContourWriterAGG('/data/OWARNA/hau/pytroll/shapes/')
        cw.add_coastlines(PIL_image, area_def, outline='white', resolution=resolution, outline_opacity=127, width=1, level=2)  #, outline_opacity=0

        outline = (255, 0, 0)
        outline = 'red'
        cw.add_coastlines(PIL_image, area_def, outline=outline, resolution=resolution, width=2)  #, outline_opacity=0
        cw.add_borders(PIL_image, area_def, outline=outline, resolution=resolution, width=2)       #, outline_opacity=0 

    ticks=20
    tick_marks=20        # default
    minor_tick_marks=10  # default
    title_color='white'
    units=global_radar[prop_str].info["units"]
    #global_radar[prop_str].units

    if add_logos:
       if verbose:
          print('... add logos')
       dc.align_right()
       if add_colorscale:
          dc.write_vertically()
       #dc.add_logo("../logos/meteoSwiss3.jpg",height=60.0)
       #dc.add_logo("../logos/pytroll3.jpg",height=60.0)
       dc.add_logo("/opt/users/common/logos/meteoSwiss.png",height=40.0)

    #font_scale = aggdraw.Font("black","/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif-Bold.ttf",size=16)
    fontsize=18
    font = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", fontsize)

    if add_colorscale:
       print('... add colorscale ranging from min_radar (',min_radar,') to max_radar (',max_radar,')')
       dc.align_right()
       dc.write_vertically()
       #font_scale = ImageFont.truetype("/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf", fontsize)
       colormap_r = colormap.reverse()
       #rainbow_r.set_range(min_radar, max_radar)
       dc.add_scale(colormap_r, extend=True, ticks=ticks, tick_marks=tick_marks, minor_tick_marks=minor_tick_marks, font=font, line_opacity=100, unit=units) #

    indicate_range=True
    if indicate_range:
        mask = global_radar[prop_str+'-MASK'].data
        img = trollimage(mask, mode="L", fill_value=None) #fill_value,[1,1,1], None
        from trollimage.colormap import greys
        img.colorize(greys)
        img.putalpha(mask*0+0.4)
        PIL_mask = img.pil_image()
        from PIL import Image as PILimage 
        PIL_image = PILimage.alpha_composite(PIL_mask, PIL_image)

    if add_title:
       draw = ImageDraw.Draw(PIL_image)

       if layer.find('2nd') != -1:
          y_pos_title=20
       elif layer.find('3rd') != -1:
          y_pos_title=40
       else:
          y_pos_title=5
          layer = dateS+' '+timeS
       if len(layer) > 0:
          layer=layer+':'

       #title = layer+' radar, '+prop_str+' ['+global_radar[prop_str].units+']'
       title = layer+' ODYSSEY, '+'precipitation rate'+' ['+global_radar[prop_str].info["units"]+']'
       draw.text((0, y_pos_title),title, title_color, font=font)

    outputFile = outputDir+'ODY_'+prop_str+'-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS +'.png'
    PIL_image.save(outputFile)
    print('... save image as ', outputFile)


global_sat = global_sat.parallax_corr(fill='bilinear', estimate_cth='standard', replace=True)

if plot_sat and load_sat:

    outputFile = outputDir+'SAT_'+prop_str+'-'+area+'_'+yearS[2:]+monthS+dayS+hourS+minS +'.png'
    img = global_sat.image.channel_image('IR_108')
    PIL_image=img.pil_image()
    if add_borders:
        print("*** add borders") 
        cw = ContourWriterAGG('/data/OWARNA/hau/pytroll/shapes/')
        outline = 'red'
        cw.add_coastlines(PIL_image, area_def, outline=outline, resolution=resolution, width=2)  #, outline_opacity=0
        cw.add_borders(PIL_image, area_def, outline=outline, resolution=resolution, width=2)       #, outline_opacity=0 

    PIL_image.save(outputFile)
    print('... save image as ', outputFile)

# obj_area.shape  # (480, 850)
# obj_area.size   # 408000
# obj_area.x_size # 850
# obj_area.y_size # 480

#mask = global_radar[prop_str+'-MASK'].data
#print type(mask), mask.min(), mask.max(), mask.fill_value
#print type()

#lonlats = self["IR_108"].area.get_lonlats()
#sza = sun_zenith_angle(self.time_slot, lonlats[0], lonlats[1])


area_size = global_sat["IR_108"].data.size

fitting=False
if fitting:
    print("*** start fitting")

    import matplotlib.pyplot as plt

    x0 = global_sat["IR_108"].data.reshape(area_size)
    y = global_radar[prop_str].data.reshape(area_size)
    m = global_radar[prop_str+'-MASK'].data.reshape(area_size)
    
    x = global_sat["IR_108"].data.reshape(area_size)
    x = np.ma.masked_array(x)
    x.mask = m
    
    x_min = 200
    x_max = 330
    x = (x - x_min) / (x_max - x_min)
    print("x min/max", x.min(), x.max())

    y_min =   1.0
    y_max = 100.0
    y = np.ma.masked_less_equal(y, y_min)
    print("y min/max (masked)", y.min(), y.max())

    #y[y<y_min] = y_min
    y[y>y_max] = y_max

    #normalisation='log'
    #normalisation='min_max'
    normalisation='none'

    if normalisation=='log':
        y = np.log(y)
        print("y min/max (log)", y.min(), y.max())
    elif normalisation=='min_max':
        y = (y - y_min) / (y_max - y_min)
        print("y min/max (norm)", y.min(), y.max())
    #elif normalisation=='min_max':
    #    pass

plot_scatter = False
if plot_scatter:
    fig, ax = plt.subplots()
    ax.scatter(x, y)  # , c=z, s=100, edgecolor=''
    #ax.scatter(global_sat["IR_108"].data, global_radar[prop_str].data)  # , c=z, s=100, edgecolor=''
    plt.xlabel('IR_108')
    plt.ylabel('Odyssey Rain Rate')


plot_fit = False
if plot_fit:
    from pylab import polyfit, poly1d
    fit = polyfit(x, y, 1)
    fit_fn = poly1d(fit)
    plt.plot( x, fit_fn(x), 'r')

plot_fit2 = False
if plot_fit2:

    # keep values where mask is False
    x1 = x[m==False]
    y  = y[m==False]

    #print "x1 min/max", x1.min(), x1.max()
    #print "y min/max", y.min(), y.max()

    model="linear"

    if model=="example":
        X = np.column_stack((x1, np.sin(x1), (x1-5)**2))
    elif model=="linear":
        #X = np.column_stack((x1))
        X = x1
    elif model=="2nd_degree_polynom":
        X = np.column_stack((x1, x1**2))
    elif model=="3rd_degree_polynom":
        X = np.column_stack((x1, x1**2, x1**3))
    elif model=="5th_degree_polynom":
        X = np.column_stack((x1, x1**2, x1**3, x1**4, x1**5))
    elif model=="linear_exp":
        X = np.column_stack((x1, np.exp(-x1) ))
    #elif model=="linear_exp_exp":
    #    X = np.column_stack((x1, np.exp(-x1), np.exp(-0.5*x1) ))
    elif model=="linear_exp_exp":
        X = np.column_stack((x1*dt, np.exp(-x1*dt/dtau1), np.exp(-x1*dt/dtau2) ))
    elif model =="constant":
        X = x1

    import statsmodels.api as sm
    X = sm.add_constant(X)

    # Estimation
    if verbose:
        print ("*** Estimation")
    #print ("y.shape ",y.shape,", X.shape ", X.shape)
    olsmod = sm.OLS(y, X)
    olsres = olsmod.fit()
    if verbose:
        print((olsres.summary()))

    #x_pred = np.linspace(x1.min(), x1.max(), 50)

    ypred = olsres.predict(X)

    #radar_pred = ypred.reshape((global_sat["IR_108"].data.shape))

    ax.plot(x1, ypred, '-', color='darkorchid', linewidth=2)

if plot_scatter or plot_fit or plot_fit2:
    plt.show()

plot_sns=False
if plot_sns:
    import numpy as np, pandas as pd; np.random.seed(0)
    import seaborn as sns
    tips = sns.load_dataset("tips")
    print(type(tips))
    g = sns.jointplot(x="total_bill", y="tip", data=tips, kind='reg',
                  joint_kws={'color':'green'}) # Scatter and regression all green



write_netCDF=True
if write_netCDF:

    nc_outfile = '/data/COALITION2/database/radar/odyssey/machine_learning/ODYRATE_SEVIRI_' + datetime1.strftime("%Y%m%d_%H%M") + '.nc'
    print("*** write data to: ncdump ", nc_outfile)

    import netCDF4 as nc4
    f = nc4.Dataset(nc_outfile,'w', format='NETCDF4')

    tempgrp = f.createGroup('collocated odyssey rain rate and SEVIRI reflectances and brightness temperatures')

    m = global_radar[prop_str+'-MASK'].data.reshape(area_size)
    y = global_radar[prop_str].data.reshape(area_size)
    y  = y[m==False]
    print("dataset length", len(y))

    xx = global_sat['IR_108'].data.reshape(area_size)  
    xx = xx[m==False]

    #import pdb
    #pdb.set_trace()

    lon = lonlats[0].reshape(area_size)
    lat = lonlats[1].reshape(area_size)
    sza = sza.reshape(area_size)
    lon  = lon[m==False]
    lat  = lat[m==False]
    sza  = sza[m==False]
    cos_sza =  np.cos(np.deg2rad(sza))

    for i in range(100):
        print(y.tolist(0)[i], xx[i], lon[i], lat[i], np.cos(np.deg2rad(sza[i])))

    #tempgrp.createDimension('idata', area_size)
    tempgrp.createDimension('ndata', len(y))

    #IR_108 = tempgrp.createVariable('IR_108', 'f4', 'idata')

    varids = list(range(len(channel_list)))
    for chn,i in zip(channel_list,list(range(len(channel_list)))):
        print(chn, i)
        varids[i] = tempgrp.createVariable(chn, 'f4', 'ndata')
    ODY_RAINRATE = tempgrp.createVariable('ODY_RAINRATE','f4', 'ndata')
    #time = tempgrp.createVariable('Time', 'i4', 'time')

    longitude   = tempgrp.createVariable('Longitude', 'f4', 'ndata')
    latitude    = tempgrp.createVariable('Latitude', 'f4',  'ndata')
    csza        = tempgrp.createVariable('Cosine Solar Zenith Angle','f4', 'ndata')

    ODY_RAINRATE[:] = y.tolist(0)
    longitude[:]    = lon
    latitude[:]     = lat
    csza[:]         = cos_sza


    for chn,i in zip(channel_list,list(range(len(channel_list)))):

        x = global_sat[chn].data.reshape(area_size)  
        x = x[m==False]

        print(chn, i)
        varids[i][:] = x


    #IR_108[:] = x.tolist(0)
    #IR_108[:] = global_sat["IR_108"].data.reshape(area_size) #The "[:]" at the end of the variable instance is necessary

    f.close()
