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
import shelve


def check_position(mask_current_label):
    if np.logical_or( np.logical_or( sum(mask_current_label[:,0])>0, sum(mask_current_label[0,:])>0 ), 
                      np.logical_or( sum(mask_current_label[:,-1])>0, sum(mask_current_label[-1,:])>0 ) ):
        return True
    else:
        return False

def check_cell_same_ID(all_cells, ID):
    if ID in all_cells.keys():
        return True
    else:
        return False

def define_IDs_cell_same_ID(all_cells,mask_current_label,ID_label, new_id_num):
    ID = "ID" + str(ID_label)
    
    # if the area of the current cell is larger than the area of the other with the same ID, it gets the ID of the previous, the other gets a new ID               
    if sum(sum(mask_current_label)) > all_cells[ID].area_px:
        
        #the cell with the smaller area gets a new id
        all_cells["ID" + str(new_id_num)] = deepcopy(all_cells[ID])
        
        #delete the cell with the smaller area with the ID needed to make sure no mixing of info
        del all_cells[ID]
        
        #save IDs of current and previous (cell at t1 which had the same ID because it comes from the same cell at t0)
        id_current      = ID
        id_samePrevious = "ID" + str(new_id_num)
        
        #store the ID number which will be used to create the data_new (with numbers corresponding to ID cell) for next time step
        label_current = ID_label
        correct_id_already_created = new_id_num
    # if the area of the current cell is smaller than the area of the other with the same ID, it gets a new ID
    else:
        id_current = "ID" + str(new_id_num)
        id_samePrevious = ID
        
        correct_id_already_created = 0
        
        #store the ID number which will be used to create the data_new (with numbers corresponding to ID cell) for next time step
        label_current = new_id_num
    
    # Both cells get a split
    all_cells[id_samePrevious].split     = 1
    all_cells[id_current]                = Cells()
    all_cells[id_current].split          = 1 
    
    return id_current, id_samePrevious, correct_id_already_created, label_current,all_cells

def make_figureLabels(values, all_cells, obj_area, outputFile, colorbar = True, vmin = False, vmax = False, white_background = False, t = None):
    import matplotlib as mpl
    import pickle
    import matplotlib.pyplot as plt
    from mpop.projector import get_area_def
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    import numpy as np
    from mpop.imageo.TRTimage import fig2img    
    from mpop.imageo.HRWimage import prepare_figure
    

    
    if vmin == False:
        vmin = values.min()
    if vmax == False:
        vmax = values.max()
    
    if white_background: 
        #ma.masked_where(values == 0, values)
        values = np.flipud(values)
        values[values == 0] = np.nan    
        values = np.ma.array (values, mask=np.isnan(values))
        color = 'k'
    else:
        values = np.flipud(values)
        color = 'y'
    
    obj_area = get_area_def(area)
    
    fig, ax = prepare_figure(obj_area) 
    
    mappable = plt.imshow(values, vmin = vmin, vmax = vmax, origin="lower")
    for items in all_cells:
        item = all_cells[items]
        x = item.center[0]
        y = item.center[1]
        plt.text(int(y),int(values.shape[0]-x), items[2:], color = color,size = 8)
    
    
    if colorbar:
        position=fig.add_axes([0.93,0.2,0.02,0.35])  ## the parameters are the specified position you set: left, bottom, width, height
        color_bar = fig.colorbar(mappable,cax=position) ## 
        plt.setp(plt.getp(color_bar.ax.axes, 'yticklabels'), color='cyan')
    if t!=None:
        #position=fig.add_axes([0.93,0.2,0.02,0.35])
        plt.text(500,50,t,color = color, size = 14)
    
    PIL_image = fig2img ( fig )
    PIL_image.save(create_dir(outputFile)+"Labels_"+yearS+monthS+dayS+"_"+hourS+minS+".png")
    print "... display ",outputFile," &"
    plt.close( fig)

def create_dir(outputFile):

    path = dirname(outputFile)
    if not exists(path):
        print '... create output directory: ' + path
        makedirs(path)
    return outputFile

def correct_connections(connections, id_new, all_cells, id_old):
    
    ancestors = all_cells[id_samePrevious].id_prev
    
    if ancestors[0]== "I":
        cell1 = []
        cell1.append(ancestors)
        ancestors = deepcopy(cell1)    
    
    for ancestor in ancestors:
        for con in range(len(connections)):
            if connections[con][0] == ancestor:
                  if id_old in connections[con][1:]: 
                      connections[con][1:].remove(id_old)
                      connections[con].append(id_new)
    return connections    
    
class Cells:
        def __init__(self):
            self.idCell         = []
            self.mean108        = []
            self.t_start        = []
            self.id_prev        = []
            self.split          = []
            self.t_end          = []
            self.origin         = []
            self.end            = []
            self.area_px        = []
            self.center         = [] 
            self.merge          = []
            self.colors         = []
"""
def cell_history( data1, data0, IR_108, ....)


    return all_cells

def save_all_cells(all_cells):
...
"""
if __name__ == '__main__':
    delay = 0

    if len(sys.argv) >= 6:
            year   = int(sys.argv[1])
            month  = int(sys.argv[2])
            day    = int(sys.argv[3])
            hour   = int(sys.argv[4])
            minute = int(sys.argv[5])
            t1 = datetime(year, month, day, hour, minute)
            if len(sys.argv)>6:
                yearStop   = int(sys.argv[6])
                monthStop  = int(sys.argv[7])
                dayStop    = int(sys.argv[8])
                hourStop   = int(sys.argv[9])
                minuteStop = int(sys.argv[10])
                tStop = datetime(yearStop, monthStop, dayStop, hourStop, minuteStop)
            else:
                tStop = deepcopy(t1)            
            
    else:
            if True:  # automatic choise of last 5min 
                    from my_msg_module import get_last_SEVIRI_date
                    time_slot = get_last_SEVIRI_date(True)
                    if delay != 0:
                        time_slot -= timedelta(minutes=delay)
                    nrt = True
                    time_slotSTOP = time_slot 
                    print "... chose time (automatically): ", str(time_slotSTOP)
            else:
                    print "***           "
                    print "*** Warning, please specify date and time completely, e.g."
                    print "***          python plot_radar.py 2014 07 23 16 10 "
                    print "***           "
                    quit() # quit at this point     
    
    first_time_step = False
    rgb_load = ['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134','CTP','CTT']
    #rgb_out = 'WV_062minusIR_108'
    only_obs_noForecast = False
    rapid_scan_mode = True
    
    if only_obs_noForecast == True:
        in_dir = "/opt/users/lel/PyTroll/scripts//Mecikalski_obs/cosmo/Channels/labels/"
    elif rapid_scan_mode == True:
        in_dir = "/opt/users/lel/PyTroll/scripts//Mecikalski_RapidScan/cosmo/Channels/labels//"
    else:
        in_dir = "/opt/users/lel/PyTroll/scripts//Mecikalski/cosmo/Channels/labels/"    
       
    # load a few standard things 
    from get_input_msg import get_input_msg
    in_msg = get_input_msg('input_template')
    in_msg.resolution = 'i'
    in_msg.sat_nr = 9
    in_msg.add_title = False
    in_msg.outputDir = './pics/'
    in_msg.outputFile = 'WS_%(rgb)s-%(area)s_%y%m%d%H%M'
    in_msg.fill_value = [0,0,0] # black    
    in_msg.reader_level = "seviri-level4"
      
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
    
    mean_108_evolution = []
    
    area34 = []
    
    split34 = []
    
    merge34 = []
    
    t_start34 = 0
    
    t_end34 = 0
    lonely_cells = 0
    cell_interesting = 77
    count_double = 0
    while t1 <= tStop:
          print in_msg.sat, str(in_msg.sat_nr), "seviri", t1
          
          # now read the data we would like to forecast
          global_data = GeostationaryFactory.create_scene(in_msg.sat, str(in_msg.sat_nr), "seviri", t1)
          #global_data_RGBforecast = GeostationaryFactory.create_scene(in_msg.sat, str(10), "seviri", time_slot)
      
          # area we would like to read
          area_loaded = get_area_def("EuropeCanary95")#(in_windshift.areaExtraction)  
      
          # load product, global_data is changed in this step!
          area_loaded = load_products(global_data, rgb_load, in_msg, area_loaded)
          
          print '... project data to desired area ', area
          data = global_data.project(area)
          
          yearS  = str(t1.year)
          monthS = "%02d" % t1.month
          dayS   = "%02d" % t1.day
          hourS  = "%02d" % t1.hour
          minS   = "%02d" % t1.minute
          
          nx,ny = data[rgb_load[0]].data.shape
          print nx,ny
          values_rgb = np.zeros((len(rgb_load),nx,ny))
          print values_rgb.shape
          for rrgb in range(len(rgb_load)):
              these = data[rgb_load[rrgb]].data
              values_rgb[rrgb,:,:] =  these #-data_108[rgb_load[1]].data
          
          #filename = 'labels/Labels_%s.shelve'%(yearS+monthS+dayS+hourS+minS)   
          filename = '/data/cinesat/out/labels/Labels_%s.shelve'%(yearS+monthS+dayS+hourS+minS)
          print "opening ", filename    
          myShelve = shelve.open(filename)  
          
          data1 = deepcopy(myShelve['labels'])
          metadata = deepcopy(myShelve['metadata'])
          myShelve.close()
          
          #data1 = pickle.load( open(in_dir + "labels_"+ yearS+monthS+dayS+hourS+minS+".p", "rb" ) )
          
          qwertz = 0
          data_new = np.zeros (data1.shape)
          all_cells = {}
          
        
      
          if first_time_step: #MUST BE UPDATED IF USED
              print("the option First Step is not yet corrected!!!")
              quit()
          
              # these labels are random numbers assigned in COALITION2 (different number for each cell)
              labels0 = np.unique(data1)
              
              id_data = yearS+monthS+dayS+hourS+minS
              #list_id = []
      
              all_cells['time'] = t1
              
              for i in range(1,len(labels0)+1):
              
                  values1 =[]
                  for rrgb in range(len(rgb_load)):
                      these = values_rgb[rrgb,:,:]
                      values_cell = these[np.where(mask_current_label == 1)]
                      values1.append(values_cell.mean())
                      
                  # make this binary ...
                  mask_current_label = np.zeros(data1.shape)
                  mask_current_label = np.where(data1 == i, 0, -1000000000) # True False
                  
                  values =[]
                  for rrgb in range(len(rgb_load)):
                      values_cell = values_rgb[rrgb,np.where(mask_current_label == 0)]
                      values.append(values_cell.mean())
                  #values = values_interest[np.where(mask_current_label == 0)] # True
                          
                  all_cells["ID"+str(i)] = Cells()
                  
                  all_cells["ID"+str(i)].mean108        = values
                  all_cells["ID"+str(i)].t_start        = [t1.year, t1.month, t1.day, t1.hour, t1.minute] # True
                  all_cells["ID"+str(i)].origin         = "t0"  # "start_programm", "day_before", "merge", "split", "enters_area", "appear"
                  
                  count_px = np.where(mask_current_label == 0,1,0)
                  
                  all_cells["ID"+str(i)].area_px        = sum(sum(count_px))
          
                  #list_id.append(id_data+"_"+str(i)) 
          
          else:
              t0 = t1 - timedelta(minutes=5)
             
              year0S  = str(t0.year)
              month0S = "%02d" % t0.month
              day0S   = "%02d" % t0.day
              hour0S  = "%02d" % t0.hour
              min0S   = "%02d" % t0.minute
      
      
              id_data0 = year0S+month0S+day0S+hour0S+min0S
              
              # !!! don't take the original data, produced by COALITION2, but the new one produced the previous timestep
              
              #filename = 'labels/Labels_%s.shelve'%(year0S+month0S+day0S+hour0S+min0S)   
              filename = '/data/cinesat/out/labels/Labels_%s.shelve'%(year0S+month0S+day0S+hour0S+min0S)     
              myShelve = shelve.open(filename)  
              data0 = deepcopy(myShelve['labels'])
              #metadata = myShelve['metadata'].data
              myShelve.close()

              #data0 = pickle.load( open(in_dir +"labels_"+year0S+month0S+day0S+hour0S+min0S+".p", "rb" ) )
              #data0 = data0.astype(int)
              #these labels correspond to the ID at t0
              data0 = np.array(data0,'uint32')
              labels0 = np.unique(data0[data0>0])
              
              print "this should match with output previous step \n", labels0
              
              connections = []
              
              for con in labels0:
                  connections.append(["ID"+str(con)])
              
              #these labels are random numbers assigned in COALITION2 (different number for each cell)
              data1 = np.array(data1,'uint32')
              labels1 = np.unique(data1)
              
              
              # new id number for the new cells at t1
              new_id_num = labels0.max()+1
              
              #list to make sure you record every split
              list_previous = []
              print "labels0", labels0
              print "labels1", labels1
              #loop through cells at t1
              for i in labels1: #range(1,len(labels1)+1):
                
                print i
                if i != 0:  
                  
                  #required to correct the output "data_new" if the ID of a cell changes because a bigger cell takes it!!!  
                  correct_id_already_created = 0
                  
                  #create a mask which has 1s only where the current cell is
                  mask_current_label = np.zeros(data1.shape)
                  mask_current_label = np.where(data1 == i, 1, 0)
                  
                  #store coordinates center of mass
                  center = ndimage.measurements.center_of_mass(mask_current_label)
                  
                  center = np.rint(center)
                  
                  values1 =[]
                  for rrgb in range(len(rgb_load)):
                      these = values_rgb[rrgb,:,:]
                      values_cell = these[np.where(mask_current_label == 1)]
                      values1.append(values_cell.mean())
                  
                  ## put calculation of mean value in a function (and also consider more properties later)
                  #take the values of the 10.8 channel for the current cell
                  #values1 = values_interest[np.where(mask_current_label == 1)]
                  
                  # consider the area of the current cell in the previous time step (TEST OVERLAPPING)
                  previous_t = data0 * mask_current_label
                  
                  # store the ID number of all the overlapping cells at t0 !!! (change to minimum overlapping to consider them)
                  labels_previous = np.unique(previous_t[previous_t>0])
                  
                  ##### new cell with no correspondence in previous time step #####
                  if len(labels_previous) == 0:
                      
                      #Store the values for the current cell, with the new ID
                      all_cells["ID"+str(new_id_num)] = Cells()
                      
                      all_cells["ID"+str(new_id_num)].t_start        = [t1.year, t1.month, t1.day, t1.hour, t1.minute]  # True
                      
                      #check if the cell appeared in the middle of the area or came from outside the domain
                      if check_position(mask_current_label):
                          all_cells["ID"+str(new_id_num)].origin     = "from_outside"
                      else:
                          all_cells["ID"+str(new_id_num)].origin     = "appear"
                      
                      all_cells["ID"+str(new_id_num)].mean108        = values1 #.mean()
                      all_cells["ID"+str(new_id_num)].area_px        = sum(sum(mask_current_label))
                      
                      #store the ID number which will be used to create the data_new (with numbers corresponding to ID cell) for next time step
                      label_current = new_id_num
                      print "appearing ", "ID"+str(new_id_num)
                      
                      new_id_num += 1
                      
                  ##### cell with one correspondence in previous time step #####  
                  elif len(labels_previous) == 1:
                      
                      #check if a cell exists at current time already with the same ID (derived from same cell at previous time step)
                      if check_cell_same_ID(all_cells, "ID" + str(labels_previous[0])): #if "ID" + str(labels_previous[0]) in all_cells.keys():
                          id_current, id_samePrevious, correct_id_already_created, label_current,all_cells = define_IDs_cell_same_ID(all_cells,mask_current_label,labels_previous[0], new_id_num)
                          
                          #if correct_id_already_created != 0:
                          #      connections = correct_connections(connections, id_samePrevious, all_cells, id_current)
                          
                          new_id_num += 1
                          print "one correspondence but doble name "#, id_samePrevious, id_current
                      # If there is no cell with that ID yet, the current cell gets it
                      else:
                          id_current      = "ID" + str(labels_previous[0])
                          all_cells[id_current]                = Cells()
                          #store the ID number which will be used to create the data_new (with numbers corresponding to ID cell) for next time step
                          label_current = labels_previous[0]
                          print "one correspondence ", id_current
                      #Store the values for the current cell
                  
                      all_cells[id_current].origin         = "from_previous"
                  
                      all_cells[id_current].id_prev        = ["ID" + str(labels_previous[0])] 
                      
                      
                      all_cells[id_current].area_px        = sum(sum(mask_current_label)) 
                      all_cells[id_current].mean108        = values1 #.mean()
                      
                      """
                      lc=0
                      for con in range(len(connections)):
                          if connections[con][0] == "ID" + str(labels_previous[0]):
                                print "id_current",id_current
                                lc+=1
                                connections[con].append(id_current)
                      
                      if lc == 0:
                          lonely_cells+=1                        
                      """    
                      #add the label of the previous cell (t0) which will be used at the end to make sure all split are recognized
                      list_previous.append(labels_previous[0])
                  
                  ##### cell with more then one correspondence in previous time step #####
                  else:
                      largest_previous = labels_previous[0]
                      max_tot_px = 0
                      
                      #scan through the cells the current comes from and look for the biggest (you'll use that ID num)
                      for h in range(len(labels_previous)):
                          current_label = labels_previous[h]
                          count_px = np.where(data0 == current_label,1,0)
                          tot_px = sum(sum(count_px))
                          if tot_px > max_tot_px:
                              largest_previous = current_label
                              max_tot_px = tot_px
                          #add the label of the previous cell (t0) which will be used at the end to make sure all split are recognized
                          list_previous.append(current_label) 
                          """
                          lc = 0 
                          for con in range(len(connections)):
                                  if connections[con][0] == "ID" + str(labels_previous[h]):
                                        connections[con].append("ID" + str(current_label)) 
                                        lc +=1
                          if lc == 0:
                              lonely_cells +=1
                          """
                      id_current = "ID" + str(largest_previous)
                      if check_cell_same_ID(all_cells, id_current): #if "ID" + str(labels_previous[0]) in all_cells.keys():
                          id_current, id_samePrevious, correct_id_already_created, label_current,all_cells = define_IDs_cell_same_ID(all_cells,mask_current_label,largest_previous, new_id_num)
                          
                          #if correct_id_already_created != 0:
                          #      connections = correct_connections(connections, id_samePrevious, all_cells, id_current)                      
                          
                          new_id_num = new_id_num + 1
                      else:
                          label_current = largest_previous
                          id_current = "ID"+str(largest_previous)       
                      
                      all_cells[id_current] = Cells()
                      
                      all_cells[id_current].mean108        = values1  #.mean()
                      
                      all_cells[id_current].origin         = "merge"
                      
                      all_cells[id_current].area_px        = sum(sum(mask_current_label))
                      
                      all_cells[id_current].id_prev        = ["ID"+str(labels_previous[lp]) for lp in range(len(labels_previous))]    
                      
                      print "more correspondence ", ("ID" + str(largest_previous)), "coming from ", ["ID"+str(labels_previous[lp]) for lp in range(len(labels_previous))]
                      
                      
                  if correct_id_already_created != 0:
                  
                      #fig = plt.figure()
                      #plt.subplot(121)
                      #plt.imshow(data_new)
                      print np.unique(data_new)
                      data_new[data_new == label_current] = correct_id_already_created
                      print np.unique(data_new)
                      #plt.subplot(122)
                      #plt.imshow(data_new)
                      #fig.savefig("Double_id_%s_%s"%(yearS+monthS+dayS+hourS+minS,count_double))
                      #plt.close(fig)
                      #count_double +=1
                  
                  
                  data_new [mask_current_label == 1] = label_current
                  all_cells["ID"+str(label_current)].center = center
                  
              #identify labels the current cells are created from that are repeated (meaning the cell split)    
              labels_repeated = np.unique(["ID"+str(x) for x in list_previous if list_previous.count(x) > 1])
              
              
              if False:
                  
                  fig = plt.figure()
                  plt.subplot(131)
                  plt.imshow(data0, vmin = 0, vmax = new_id_num)
                  plt.title("t0")
                  plt.subplot(132)
                  plt.imshow(data_new, vmin = 0, vmax = new_id_num)
                  plt.title("t1")    
                  plt.subplot(133)
                  plt.imshow(data1, vmin = 0, vmax = new_id_num)
                  plt.title("t1_old")
                  fig.savefig("LabelsAll_%s.png"%(yearS+monthS+dayS+hourS+minS))
                  plt.close(fig)         
              print "data new \n",np.unique(data_new)  
              
              print "data old \n",np.unique(data1)  
              #make sure that the cells that come from splitting cells get a split
              for items in all_cells:
                  item = all_cells[items]
                  if item.split != 1:
                      for n_prev in range(len(item.id_prev)):
                          if item.id_prev[n_prev] in labels_repeated:
                              item.split = 1
      
              #labels1_new = np.unique(data_new)        
              
              labels, numobjects = ndimage.label(data_new)
              
              print "number cells produced ", len(np.unique(data_new))
              print "number cells in data_new ", numobjects
              print "\n \n \n \n"
              print all_cells.keys()
              
              print np.unique(data_new)
      
              #im = Image.fromarray(np.uint8(plt.cm.gist_heat(data_new/data_new.max())*255))

              #d = ImageDraw.Draw(im)        
              #fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 40)
              outputFile = "/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/labels/"
              make_figureLabels(deepcopy(data_new), all_cells, obj_area, "fig_labels/", colorbar = False, vmin = False, vmax = False, white_background = True, t = t1)
              #make_figureLabels(data_new, all_cells, obj_area, outputFile, colorbar = False, vmin = False, vmax = False)
              data_new = data_new.astype('uint32') #unsigned char int  https://docs.python.org/2/library/array.html
              
              print data_new.dtype
              
              #pickle.dump(data_new, open(in_dir + "labels_"+yearS+monthS+dayS+hourS+minS+".p", "wb" ) )
              
              #filename = 'labels/Labels_%s.shelve'%(yearS+monthS+dayS+hourS+minS)
              filename = '/data/cinesat/out/labels/Labels_%s.shelve'%(yearS+monthS+dayS+hourS+minS)
              myShelve = shelve.open(filename)
              myShelve['labels'] = deepcopy(data_new )
              myShelve.close()              
              
              if False:
                  myShelve = shelve.open(filename)
                  test_labels = deepcopy(myShelve['labels'])
                  test_test_labels = test_labels - data_new
                  myShelve.close()
                  if sum(sum(test_test_labels))!=0:
                      print "something very wrong"
                      quit()
              
              if False:
                  if t_end34 == 0:
                      if "ID" + str(cell_interesting) in all_cells.keys():
                            mean_108_evolution.append(all_cells["ID" + str(cell_interesting)].mean108)
                            area34.append(all_cells["ID" + str(cell_interesting)].area_px)
                            print "**************mean 108: ", all_cells["ID" + str(cell_interesting)].mean108
                            if all_cells["ID" + str(cell_interesting)].split == 1:
                                split34.append(1)
                            else:
                                split34.append(0)
                            if len(all_cells["ID" + str(cell_interesting)].id_prev)>1 and len(all_cells["ID" + str(cell_interesting)].id_prev)!=4:
                                print len(all_cells["ID" + str(cell_interesting)].id_prev)
                                print all_cells["ID" + str(cell_interesting)].id_prev
                                merge34.append(1)
                            else:
                                merge34.append(0)
                            
                            if t_start34 == 0:
                                t_start34_time = t1
                                t_end34_time = t1
                                t_start34 = 5
                      elif t_start34 == 5:
                            t_end34_time = t1     
                            t_end34 = 1
                            print t_start34_time
                            print t_end34_time

              #pickle.dump(all_cells, open("Cells_"+yearS+monthS+dayS+hourS+minS+".p","wb"))
              #filename = 'cells/%s.shelve'%(yearS+monthS+dayS+hourS+minS)
              filename = '/data/cinesat/out/labels/Cells_%s.shelve'%(yearS+monthS+dayS+hourS+minS)
              print "*** writing variables ", filename
              myShelve = shelve.open(filename)
              # write data as dictionary into the shelve
              dict_cells = {'cells': all_cells, 'labels':data_new , 'metadata': metadata}
              myShelve.update(dict_cells)
              # close the shelve
              myShelve.close()
              
              list_cells = all_cells.keys()
              for cell_connection in list_cells:
                  print "the cell you look for ancestors is ", cell_connection
                  ancestors = all_cells[cell_connection].id_prev
                  print "its ancestors are: ", ancestors
                  """
                  if ancestors[0]=="I":
                      if ancestors[0]== "I":
                          cell1 = []
                          cell1.append(ancestors)
                          ancestors = deepcopy(cell1)    
                  """
                  for ancestor in ancestors:
                      
                      for con in range(len(connections)):
                          if connections[con][0] == ancestor:
                                connections[con].append(cell_connection)
       
              filename = 'cells/%s.shelve'%(year0S+month0S+day0S+hour0S+min0S)
              d = shelve.open(filename)
              d['connections'] = deepcopy(connections)
              d.close()
              
              t1 = t1 + timedelta(minutes=5)  
              print connections
              
              print "LONELY CELLS", lonely_cells
              
    
    if False:
          import matplotlib.patches as mpatches
          from matplotlib import dates
          
          pickle.dump(mean_108_evolution, open("rgbs.p", "wb" ) )
          
          
          classes = ['split and merge','split','merge','no split or merge']
          class_colours = ['r','y','g','b']
          recs = []
          for i in range(0,len(class_colours)):
              recs.append(mpatches.Rectangle((0,0),1,1,fc=class_colours[i]))
      
          if t_end34_time == t_start34_time:
                t_end34_time = t1 - timedelta(minutes=5)
          t34 = t_start34_time
        
          x_time = 0
          print mean_108_evolution
          print split34
          print merge34
          cvb = 0
          #hfmt = dates.DateFormatter('%m/%d %H:%M')
          
          x_time = []
          color_list = []
          while t34 <= t_end34_time:
              if split34[cvb] == 1:
                  if merge34[cvb]==1:
                      color_split_merge = 'r'
                  else:
                      color_split_merge = 'y'
              else: 
                  if merge34[cvb]==1:
                      color_split_merge = 'g'
                  else:
                      color_split_merge = 'b'   
              color_list.append(color_split_merge)
              #plt.scatter(t34, mean_108_evolution[cvb], c = color_split_merge, s = 40)
              #x_time = x_time + 5 
              x_time.append(t34)
              t34 = t34 + timedelta(minutes=5)
              cvb = cvb + 1
          t_min = x_time[0] - timedelta(minutes = 5)
          t_max = x_time[-1] + timedelta(minutes = 5)
          
          for rrgb in range(len(rgb_load)):
              rgb_out = rgb_load[rrgb]
              fig = plt.figure()
              ax = plt.subplot(111)
              plt.xlabel("%s %s %s"%(str(t_start34_time.day),str(t_start34_time.month),str(t_start34_time.year)))
              plt.ylabel(rgb_out)  
              print x_time
              for gg in range(len(mean_108_evolution)):
                  ax.plot_date(x_time[gg], mean_108_evolution[gg][rrgb], fmt='o', xdate = True, ydate=False, c = color_list[gg])#, s = 40)
              #ax=plt.gca()
              xfmt = dates.DateFormatter('%H:%M')
              ax.xaxis.set_major_formatter(xfmt)
              #ax = plt.gca()
              #ax.xaxis.set_major_locator(dates.MinuteLocator())
              #ax.xaxis.set_major_formatter(hfmt) 
              plt.xticks(rotation='vertical')
              ax.set_xlim([t_min, t_max])
              #plt.gcf().autofmt_xdate()
              #box = ax.get_position()
              #ax.set_position([box.x0,box.y0, box.width * 0.8, box.height])
              lgd = ax.legend(recs,classes,loc='center left',bbox_to_anchor=(1,0.5))
              fig.savefig("/data/COALITION2/PicturesSatellite/LEL_results_wind/cell_properties/one_cell_properies/"+rgb_out+"mean.png",bbox_extra_artists=(lgd,), bbox_inches = 'tight')
              plt.close(fig)
      
          fig = plt.figure()
          ax = plt.subplot(111)
          plt.xlabel("%s %s %s"%(str(t_start34_time.day),str(t_start34_time.month),str(t_start34_time.year)))
          plt.ylabel("area")  
          print x_time
          for gg in range(len(mean_108_evolution)):
              ax.plot_date(x_time[gg], area34[gg], fmt='o', xdate = True, ydate=False, c = color_list[gg])#, s = 40)
          #ax=plt.gca()
          ax.set_xlim([t_min, t_max])
          xfmt = dates.DateFormatter('%H:%M')
          ax.xaxis.set_major_formatter(xfmt)
          #ax = plt.gca()
          #ax.xaxis.set_major_locator(dates.MinuteLocator())
          #ax.xaxis.set_major_formatter(hfmt)
          plt.xticks(rotation='vertical')
          #plt.gcf().autofmt_xdate()
          #box = ax.get_position()
          #ax.set_position([box.x0,box.y0, box.width * 0.8, box.height])
          lgd = ax.legend(recs,classes,loc='center left',bbox_to_anchor=(1,0.5))
          fig.savefig("/data/COALITION2/PicturesSatellite/LEL_results_wind/cell_properties/one_cell_properies/Area.png",bbox_extra_artists=(lgd,), bbox_inches = 'tight')
          plt.close(fig)
          
          pickle.dump(x_time, open("rgbs_x.p", "wb" ) )
          pickle.dump(color_list, open("rgbs_colors.p", "wb" ) )
          pickle.dump(area34, open("rgbs_area.p","wb"))
"""
            if len(sys.argv)>6:
                if sys.argv[6] == "first":
                      first_time_step = True
                else:
                      first_time_step = False
            else:
                first_time_step = False    
"""
