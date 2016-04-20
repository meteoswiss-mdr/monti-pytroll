from datetime import datetime
import sys, string, os
import logging
sys.path.insert(0, "/home/lom/users/cll/pytroll/install/lib/python2.6/site-packages")
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from mpop.utils import debug_on
from pyresample import plot
import numpy as np
import aggdraw
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from os.path import dirname, exists
from os import makedirs
from mpop.imageo.HRWimage import HRW_2dfield # , HRWstreamplot, HRWimage
from datetime import timedelta
from plot_msg import create_PIL_image, add_border_and_rivers, add_title
from pycoast import ContourWriterAGG
from pydecorate import DecoratorAGG
from my_msg_module import format_name, fill_with_closest_pixel
from copy import deepcopy 
from my_msg_module import convert_NWCSAF_to_radiance_format, get_NWC_pge_name
from mpop.imageo.palettes import convert_palette2colormap
from plot_msg import load_products
import matplotlib.pyplot as plt
import time
import copy
from particles_displacement import particles_displacement
import numpy.ma as ma
import netCDF4
import pickle
import subprocess

from trollimage.colormap import rainbow
from trollimage.image import Image as trollimage

from skimage import morphology
from scipy import ndimage


if __name__ == '__main__':
    # input 
#time_slot = datetime(year, month, day, hour, minute)
    
    class Cells:
        def __init__(self,idCell)
            self.idCell         = idCell
            self.mean108        = []
            self.t_start        = []
            self.id_prec        = []
            self.t_split        = []
            self.t_end          = []
            self.origin         = []
            self.end            = []
            self.area_px        = []
            

     if len(sys.arg) >= 6:
            year   = int(sys.argv[1])
            month  = int(sys.argv[2])
            day    = int(sys.argv[3])
            hour   = int(sys.argv[4])
            minute = int(sys.argv[5])
            t1 = datetime(year, month, day, hour, minute)
            if len(sys.arg)>6:
                if sys.argv[6] == "first":
                      first_time_step = True
                else:
                      first_time_step = False
     else:
            print "***           "
            print "*** Warning, please specify date and time completely, e.g."
            print "***          python plot_radar.py 2014 07 23 16 10 "
            print "***           "
            quit() # quit at this point            

    
    area = "ccs4" #c2"#"ccs4" #in_windshift.ObjArea

    # satellite for HRW winds
    sat_nr = "08" #in_windshift.sat_nr

    # define area object 
    obj_area = get_area_def(area)#(in_windshift.ObjArea)

    # define area
    proj4_string = obj_area.proj4_string            
    # e.g. proj4_string = '+proj=geos +lon_0=0.0 +a=6378169.00 +b=6356583.80 +h=35785831.0'
    area_extent = obj_area.area_extent              
    # e.g. area_extent = (-5570248.4773392612, -5567248.074173444, 5567248.074173444, 5570248.4773392612)
    area_tuple = (proj4_string, area_extent)
    
    print in_msg.sat, str(in_msg.sat_nr).zfill(2), "seviri", t1
    
    # now read the data we would like to forecast
    global_data = GeostationaryFactory.create_scene(in_msg.sat, str(in_msg.sat_nr).zfill(2), "seviri", t1)
    #global_data_RGBforecast = GeostationaryFactory.create_scene(in_msg.sat, str(10), "seviri", time_slot)

    # area we would like to read
    area_loaded = get_area_def("EuropeCanary95")#(in_windshift.areaExtraction)  

    # load product, global_data is changed in this step!
    area_loaded = load_products(global_data, ['IR_108'], in_msg, area_loaded)
    
    print '... project data to desired area ', area
    
    data_108 = global_data.project(area)

    yearS  = str(t1.year)
    monthS = "%02d" % t1.month
    dayS   = "%02d" % t1.day
    hourS  = "%02d" % t1.hour
    minS   = "%02d" % t1.minute

    data1 = pickle.load( labels, open("labels_"+yearS+monthS+dayS+hourS+minS+".p", "rb" ) )
    
    if first_time_step:
    
        labels0 = np.unique(data1)
        
        id_data = yearS+monthS+dayS+hourS+minS
        #list_id = []
        
        for i in range(1,len(labels0)+1):
        
            mask_current_label = np.zeros(data1.shape)
            mask_current_label = np.where(data1 == i, 0, -1000000000)
            values = data.data[np.where(mask_current_label == 0)]
                    
            cell = Cells(id_data+"_ID"+str(i))
            
            cell.mean108        = values.mean()
            cell.t_start        = [t1.year, t1.month, t1.day, t1.hour, t1.minute]
            cell.origin         = "t0"
            
            count_px = np.where(mask_current_label == 0,1,0)
            
            cell.area_px        = sum(sum(count_px))
    
            #list_id.append(id_data+"_"+str(i)) 
    
    else:
        t0 = t1 - timedelta(minutes=5)
       
        year0S  = str(t0.year)
        month0S = "%02d" % t0.month
        day0S   = "%02d" % t0.day
        hour0S  = "%02d" % t0.hour
        min0S   = "%02d" % t0.minute


        id_data0 = year0S+month0S+day0S+hour0S+min0S
        data0 = pickle.load( labels, open("labels_"+year0S+month0S+day0S+hour0S+min0S+".p", "rb" ) )
        
        labels0 = np.unique(data0)
        labels1 = np.unique(data1)
        new_id_num = labels0.max()+1
        
        for i in range(1,len(labels1)+1):
            mask_current_label = np.zeros(data1.shape)
            mask_current_label = np.where(data1 == i, 1, 0)
            values1 = data_108.data[np.where(mask_current_label == 0)]
            
            previous_t = data0 * mask_current_label
            labels_previous = np.unique(previous_t[previous_t>0])
            count_px = np.where(mask_current_label == 0,1,0)
            
            #new cell with no correspondence in previous time step
            if len(labels_previous) == 0:
                cell = Cells(id_data+"_ID"+str(new_id_num))
                cell.mean108        = values1.mean()
                cell.t_start        = [t1.year, t1.month, t1.day, t1.hour, t1.minute]
                cell.origin         = "new"
                
                cell.area_px        = sum(sum(count_px))
                
                new_id_num += 1
            
            #cell with one correspondence in previous time step   
            elif len(labels_previous) == 1:
                
                cell.area_px        = sum(sum(count_px))
                if isinstance(id_data + "_ID" + str(labels_previous), Cells):
                    cell = Cells(id_data + "_ID" + str(labels_previous)) 
                    cell.mean108        = values1.mean()
                    cell.origin         = "from_previous"
                    cell.id_prec        = id_data0 + "_ID" + str(labels_previous)   
            
            #cell with more then one correspondence in previous time step
            else:
                cell = Cells
                largest_previous = labels_previous[0]
                max_tot_px = 0
                
                for h in range(len(labels_previous)):
                    current_label = labels_previous[h]
                    count_px = np.where(data0 == current_label,1,0)
                    tot_px = sum(sum(count_px))
                    if tot_px > max_tot_px:
                        largest_previous = current_label
                        max_tot_px = tot_px
                    
                    
            
            elif len(labels_previous)==1:
            else:
                for j in range(0,len(labels_previous):
                    
        
        
        
        
        
        
        
        
        data1 = deepcopy(data2)
        labels1 = deepcopy(labels1)
    
    
    
    
    
    
"""
    if len(sys.argv) > 1:
        if len(sys.argv) < 6:
            print "***           "
            print "*** Warning, please specify date and time completely, e.g."
            print "***          python plot_radar.py 2014 07 23 16 10 "
            print "***           "
            quit() # quit at this point
        else:
            year   = int(sys.argv[1])
            month  = int(sys.argv[2])
            day    = int(sys.argv[3])
            hour   = int(sys.argv[4])
            minute = int(sys.argv[5])
            time_slot = datetime(year, month, day, hour, minute)
            
            if len(sys.argv) > 6:
                yearSTOP   = int(sys.argv[6])
                monthSTOP  = int(sys.argv[7])
                daySTOP    = int(sys.argv[8])
                hourSTOP   = int(sys.argv[9])
                minuteSTOP = int(sys.argv[10])
                time_slotSTOP = datetime(yearSTOP, monthSTOP, daySTOP, hourSTOP, minuteSTOP) 
            else:
                time_slotSTOP = time_slot 
    else:
        if False:  # automatic choise of last 5min 
            from my_msg_module import get_last_SEVIRI_date
            datetime1 = get_last_SEVIRI_date(True)
            if delay != 0:
                datetime1 -= timedelta(minutes=delay)
            year  = datetime1.year
            month = datetime1.month
            day   = datetime1.day
            hour  = datetime1.hour
            minute = datetime1.minute
        else: # fixed date for text reasons
            year   = 2015          # 2014 09 15 21 35
            month  =  7           # 2014 07 23 18 30
            day    =  7
            hour   = 13
            minute = 00
    t1 = time_slot - timedelta(minutes = 5)
    t2 = time_slot

    year1   = t1.year
    month1  = t1.month
    day1    = t1.day
    hour1   = t1.hour
    minute1 = t1.minute
    
    year1S  = str(year)
    month1S = "%02d" % month1
    day1S   = "%02d" % day1
    hour1S  = "%02d" % hour1
    min1S   = "%02d" % minute1
    date1S  = year1S+'-'+month1S+'-'+day1S
    time1S  = hour1S+':'+min1S+" UTC"

    year2   = t2.year
    month2  = t2.month
    day2    = t2.day
    hour2   = t2.hour
    minute2 = t2.minute
    
    year2S  = str(year)
    month2S = "%02d" % month2
    day2S   = "%02d" % day2
    hour2S  = "%02d" % hour2
    min2S   = "%02d" % minute2
    date2S  = year2S+'-'+month2S+'-'+day2S
    time2S  = hour2S+':'+min2S+" UTC"    
    
    