from __future__ import division
from __future__ import print_function


from datetime import datetime
import sys, string, os
import logging
#sys.path.insert(0, "/home/lom/users/cll/pytroll/install/lib/python2.6/site-packages")
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
from plot_msg import create_PIL_image, add_title
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
import getpass

import glob
 
from trollimage.colormap import rainbow
from trollimage.image import Image as trollimage

from skimage import morphology
from scipy import ndimage
import shelve
from matplotlib import dates
import matplotlib.patches as mpatches
import pickle
import matplotlib.pyplot as plt
from mpop.projector import get_area_def
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
from mpop.imageo.TRTimage import fig2img    
from mpop.imageo.HRWimage import prepare_figure
from properties_cells import create_dir
from Cells import Cells
import matplotlib.dates as mdates
from get_input_msg import get_input_msg

import inspect
current_file = inspect.getfile(inspect.currentframe())


def string_date(t):
    yearS  = str(t.year)
    monthS = "%02d" % t.month
    dayS   = "%02d" % t.day
    hourS  = "%02d" % t.hour
    minS   = "%02d" % t.minute
    
    return yearS, monthS, dayS, hourS, minS

#class Cells:
#        def __init__(self):
#            self.idCell         = []
#            self.mean108        = []
#            self.t_start        = []
#            self.id_prev        = []
#            self.split          = []
#            self.t_end          = []
#            self.origin         = []
#            self.end            = []
#            self.area_px        = []
#            self.center         = []   
#            self.merge          = []
#            self.colors         = []
#        from Cells import Cells
        

def make_figureLabels(values, all_cells, obj_area, outputFile, colorbar = True, vmin = False, vmax = False, center = None):

    
    if vmin == False:
        vmin = values.min()
    if vmax == False:
        vmax = values.max()
    
    #obj_area = get_area_def(area)
    
    fig, ax = prepare_figure(obj_area) 
    
    mappable = plt.imshow(np.flipud(values), vmin = vmin, vmax = vmax, origin="lower")
    if center is not None:
            x = center[0]
            y = center[1]
            plt.scatter(int(y),int(values.shape[0]-x), color = 'y',s=15)
   
    
    if colorbar:
        position=fig.add_axes([0.93,0.2,0.02,0.35])  ## the parameters are the specified position you set: left, bottom, width, height
        color_bar = fig.colorbar(mappable,cax=position) ## 
        plt.setp(plt.getp(color_bar.ax.axes, 'yticklabels'), color='cyan')
    
    PIL_image = fig2img ( fig )
    PIL_image.save(create_dir(outputFile))
    print("... display ",outputFile," &")
    plt.close( fig)


def add_history(history_cell, t, id_prev, num_mean108, labels_dir): 
                          
    year0S  = str(t.year)
    month0S = "%02d" % t.month
    day0S   = "%02d" % t.day
    hour0S  = "%02d" % t.hour
    min0S   = "%02d" % t.minute    
    
    filename = labels_dir +'/Labels_%s.shelve'%(year0S+month0S+day0S+hour0S+min0S)
    myShelve = shelve.open(filename) 
    #print("cells available at current time("+year0S+"-"+month0S+"-"+day0S+" "+hour0S+":"+min0S+")\n", [key for key in myShelve['cells'].keys()])
    
    area_tmp = np.zeros(len(id_prev))
    id_prev_new_tmp = []
    mean108_tmp = np.zeros((len(id_prev),num_mean108))
    merge = 0
    split = 0
    if len(id_prev) == 1:
        #print("++++one previous")
        id_prev = id_prev[0]
        mean108 = np.array(myShelve['cells'][id_prev].mean108) 
        id_prev_new = myShelve['cells'][id_prev].id_prev
        area = myShelve['cells'][id_prev].area_px
        if myShelve['cells'][id_prev].split == 1:
            split = 1
        if len(id_prev_new)>1:
            merge = 1
    else:
        #print("++++more previous")
        for j in range(len(id_prev)):
            id_current = id_prev[j]

            id_prev_new_tmp.append(myShelve['cells'][id_current].id_prev)
            area_tmp[j] = myShelve['cells'][id_current].area_px
            mean108_tmp[j,:] = np.array(myShelve['cells'][id_current].mean108) * myShelve['cells'][id_current].area_px
            if myShelve['cells'][id_current].split == 1:
                split = 1
            if len(myShelve['cells'][id_current].id_prev)>1:
                merge = 1
        area = sum(area_tmp)
        id_prev_new = [item for sublist in id_prev_new_tmp for item in sublist]
        id_prev_new = list(set(id_prev_new))
        mean108 = np.zeros((1,num_mean108))
        #print "area: ", area
        for j in range(num_mean108):
        
              mean108 [0,j] =  (sum (mean108_tmp[:,j]))/float(area)
    if split == 1:
          if merge==1:
              history_cell.colors.append('r')
          else:
              history_cell.colors.append('y')
    else: 
          if merge==1:
              history_cell.colors.append('g')
          else:
              history_cell.colors.append('b')  
    
    history_cell.area_px.append(area)
    history_cell.id_prev.append(id_prev_new)
    history_cell.mean108 = np.vstack([history_cell.mean108, mean108])
    
    if split == 1:
        history_cell.split = t
    if merge == 1:
        history_cell.merge = t
    myShelve.close()
    return history_cell, id_prev_new

def add_history1(history_cell, cell_id, cells_to_correct, cells_known, t_to_correct, t_known, num_rgb, interesting_cell, backward, data_container,labels_dir,in_msg,history_correction): #(ancestors).(children)
    
    if backward == True:
        stop_history_when_small = in_msg.stop_history_when_smallForward
    else:
        stop_history_when_small = in_msg.stop_history_when_smallBackward
    
    threshold_stop_history_when_small = in_msg.threshold_stop_history_when_small
    
    verbose = False
    year2S, month2S, day2S, hour2S, min2S = string_date(t_known)
    year1S, month1S, day1S, hour1S, min1S = string_date(t_to_correct)
    
    string_id1, data_container = get_info_current_time(t_to_correct, data_container, labels_dir)
    string_id2, data_container = get_info_current_time(t_known, data_container, labels_dir)
        
    Atot_to_correct = 0
    Atot_known = 0
    
    AT_known = np.zeros(num_rgb)
    AT_to_correct = np.zeros(num_rgb)
    
    if verbose:
        print("string_id cells_to_correct",string_id1)
        print(cells_to_correct)
        print("string_id cells_known", string_id2)
        print(cells_known)
    
    try:
        labels_to_correct = deepcopy(data_container['all_labels'][string_id1]) #deepcopy(myShelve1['labels'])
    except KeyError:
        print("string_id1 ", string_id1)
        print("string_id2 ", string_id2)
        print("quitting in history_backward line 213")
        quit()
    labelsKnown = deepcopy(data_container['all_labels'][string_id2]) #deepcopy(myShelve2['labels'])
    
    labels_out_to_correct = np.zeros(labels_to_correct.shape)
    labels_outKnown = np.zeros(labelsKnown.shape)
    
    if cells_to_correct[0] == "I":
            cells_to_correct = [cells_to_correct]
    
    for ids in cells_to_correct:
        label = int(ids[2:])
        labels_out_to_correct[labels_to_correct==label] = label
        Atot_to_correct += data_container['all_cell_properties'][string_id1][ids].area_px
        for i in range(num_rgb):
            tmp_check = data_container['all_cell_properties'][string_id1][ids].mean108[i] * data_container['all_cell_properties'][string_id1][ids].area_px
            AT_to_correct[i] += tmp_check
    
    if cells_known[0] == "I":
            cells_known = [cells_known]    
            
    for ids in cells_known:
        label = int(ids[2:])
        labels_outKnown[labelsKnown==label] = label
        Atot_known += data_container['all_cell_properties'][string_id2][ids].area_px
        for i in range(num_rgb):
            AT_known[i] += data_container['all_cell_properties'][string_id2][ids].mean108[i]*data_container['all_cell_properties'][string_id2][ids].area_px     
    """
    PROBLEMS WITH knowing what is what see this older version. "known" should correspond to index 1 here and to_correct to index 0 here
        for ids in ancestors:
            label = int(ids[2:])
            labels_outAnc[labelsAnc==label] = label
            Atot0 += myShelve0['cells'][ids].area_px
            for i in range(num_rgb):
                AT0[i] += myShelve0['cells'][ids].mean108[i] * myShelve0['cells'][ids].area_px
            if t == t_1625 or t == t_1630 or t == t_1525 or t == t_1530: 
                print "t0: ", t
                print "id ancestor: ", ids
                print "area ancestor: ", myShelve0['cells'][ids].area_px
                print "temperature ancestor: ", myShelve0['cells'][ids].mean108[i]
        
        for ids in children:
            label = int(ids[2:])
            labels_outChild[labelsChild==label] = label
            Atot1 += myShelve1['cells'][ids].area_px
            for i in range(num_rgb):
                AT1[i] += myShelve1['cells'][ids].mean108[i]*myShelve1['cells'][ids].area_px     
            if t == t_1625 or t == t_1630 or t == t_1525 or t == t_1530: 
                print "t1 (tHistory): ", tHistory
                print "id children: ", ids
                print "area children: ", myShelve1['cells'][ids].area_px
                print "temperature children: ", myShelve1['cells'][ids].mean108[i]
        
        A1 = myShelve1['cells']["ID"+str(cell_id)].area_px
        A0 = A1 * Atot0/Atot1
        T1 = myShelve1['cells']["ID"+str(cell_id)].mean108
        T0 = T1 + AT0/Atot0 - AT1/Atot1                    
    """    
    
    
    A2 = data_container['all_cell_properties'][string_id2]["ID"+str(cell_id)].area_px
    A1 = A2 * Atot_to_correct/Atot_known
    Temp_known = data_container['all_cell_properties'][string_id2]["ID"+str(cell_id)].mean108
    Temp_to_correct = Temp_known + AT_to_correct/Atot_to_correct - AT_known/Atot_known
    
    """
    if float(A2)/float(Atot_known) >= threshold_stop_history_when_small:
        history_cell.test_size.append(True)
        if verbose:
            print("the test of the size gave: ",float(A2)/float(Atot_known))
    else:
        if verbose:
            print("The area was smaller than %s the total"%str(threshold_stop_history_when_small))
        history_cell.test_size.append(False)
    """
    #if np.logical_and(stop_history_when_small == True, history_cell.test_size[-1]==True) or stop_history_when_small == False:
    history_cell.test_size.append(True)
    history_cell.colors.append('k')
    history_cell.area_px.append(A1) 
    history_cell.mean108 = np.vstack([history_cell.mean108, Temp_to_correct])
    
    
    labels_outKnownPlus1 = deepcopy(labels_outKnown)
    
    labels_out_to_correctPlus1 = deepcopy(labels_out_to_correct)
    
    labels_out_to_correctPlus1[labels_out_to_correctPlus1>0] = 1

    #if backward:
    #    t = deepcopy(t_to_correct)
    #else:
    #    t = deepcopy(t_known)

    #t_interestPlus1 = t + timedelta(minutes=5)
    #t_interestMinus1 = t - timedelta(minutes=5)
    t_interestPlus1 = t_to_correct + timedelta(minutes=5)
    t_interestMinus1 = t_to_correct - timedelta(minutes=5)    
    test_KnownHistory = 0
    
    #displacement between tInterest (t) and tInterest - 5 min
    labels_outKnownPlus1 = np.zeros(labels_out_to_correctPlus1.shape)
    if history_correction != "follow_id":
        cells_to_use, data_container = find_ancestors(cells_to_correct,t_to_correct,data_container,labels_dir)
    else:
        cells_to_use = "ID"+str(cell_id)

    if cells_to_use == []:
        test_KnownHistory = 1 #there are no cells_to_correct of the current cells_to_correct! Displacement will be 0 and no image cells_to_correct
        
    else:
        string_idMinus1, data_container = get_info_current_time(t_interestMinus1, data_container, labels_dir)
        labels = deepcopy(data_container['all_labels'][string_idMinus1]) #deepcopy(myShelveMinus1['labels'])
        if cells_to_use[0] == "I": #not isinstance(cells_to_use,list):
            cells_to_use = [cells_to_use]
            
    
    if test_KnownHistory == 0:    
        for cell_id in cells_to_use:
            cell_label = int(cell_id[2:])
            labels_outKnownPlus1[labels==cell_label] = 1
    
    
    center_to_correct = ndimage.measurements.center_of_mass(labels_out_to_correctPlus1)
    #center_to_correct = np.rint(center_to_correct)
    center_to_correct = np.asarray(center_to_correct)    
    if test_KnownHistory != 1:       
        centerKnown = ndimage.measurements.center_of_mass(labels_outKnownPlus1)
        #centerKnown = np.rint(centerKnown)   
        centerKnown = np.asarray(centerKnown) 
        history_cell.displacement.append(center_to_correct-centerKnown)
        history_cell.center.append(center_to_correct)
    else:
        centerKnown = [0,0]    
        history_cell.displacement.append([0,0])
        history_cell.center.append([])
    

    if False:
            area = "ccs4"
            obj_area = get_area_def(area)
            #outputFile = "/data/COALITION2/PicturesSatellite/LEL_results_wind//"+year0S+"-"+month0S+"-"+day0S+"/cell_properties/"+interesting_cell+"/_to_correctestor/"+hour0S+min0S+"cells_to_correct.png"
            outputFile = year1S+"-"+month1S+"-"+day1S+"/cell_properties/"+interesting_cell+"/_to_correctestor/"+hour1S+min1S+"cells_to_correct.png"
            
            if verbose:
                print("in: ",outputFile)
            #make_figureLabels(labels_out_to_correct, None, obj_area, outputFile, colorbar = False, vmin = False, vmax = False, center = center_to_correct)
            #
            
            outputFile = "/data/COALITION2/PicturesSatellite/LEL_results_wind//"+year1S+"-"+month1S+"-"+day1S+"/cell_properties/"+interesting_cell+"/cells_known/"+hour1S+min1S+"cells_known_"+hour2S+min2S+".png"
            outputFile = year1S+"-"+month1S+"-"+day1S+"/cell_properties/"+interesting_cell+"/cells_known/"+hour1S+min1S+"cells_known_"+hour2S+min2S+".png"
            if verbose:
                print("in: ",outputFile)
            #make_figureLabels(labels_outKnown, None, obj_area, outputFile, colorbar = False, vmin = False, vmax = False)
            
            if False:
                    #outputFile = "/data/COALITION2/PicturesSatellite/LEL_results_wind//"+year0S+"-"+month0S+"-"+day0S+"/cell_properties/"+interesting_cell+"/evolution_CoM/"+hour0S+min0S+"cells_known.png"
                    outputFile = year1S+"-"+month1S+"-"+day1S+"/cell_properties/"+interesting_cell+"/evolution_CoM/"+hour1S+min1S+"cells_known.png"
                    make_figureLabels(labels_out_to_correctPlus1, None, obj_area, outputFile, colorbar = False, vmin = False, vmax = False, center = center_to_correct)
                    #outputFile = "/data/COALITION2/PicturesSatellite/LEL_results_wind//"+year0S+"-"+month0S+"-"+day0S+"/cell_properties/"+interesting_cell+"/evolution_CoM/"+hour0S+min0S+"cells_to_correct.png"
                    if test_KnownHistory != 2:
                        outputFile = year1S+"-"+month1S+"-"+day1S+"/cell_properties/"+interesting_cell+"/evolution_CoM/"+hour1S+min1S+"cells_to_correct.png"
                        make_figureLabels(labels_outKnownPlus1, None, obj_area, outputFile, colorbar = False, vmin = False, vmax = False, center = centerKnown)
        
    return history_cell, data_container


def find_ancestors(cell, t, data_container,labels_dir):
    
    verbose = False
    if verbose:
        print("**** finding ancestors \n", cell, t)
    ancestors = []
    
    string_id, data_container = get_info_current_time(t, data_container,labels_dir)
    
    if cell[0] == "I":
        cell1 = []
        cell1.append(cell)
        cell = deepcopy(cell1)
    
    for cell_curr in cell:
    
        try:
            ancestors.append(data_container['all_cell_properties'][string_id][cell_curr].id_prev)
            
        except KeyError: 
            print("current cells", cell_curr)
            print("all cells available:, ",list(data_container['all_cell_properties'][string_id].keys())) #myShelve['cells'].keys())
            print("key error in line 382 of history_backward")
            quit()
        
    
    ancestors = [item for sublist in ancestors for item in sublist]
    ancestors = list(set(ancestors))
    
    ancestors = list(np.unique(ancestors))
    
    if verbose:
        print("the ancestors are: ", ancestors)
    return ancestors, data_container  
    
    
    
def find_children(cell,t,data_container,labels_dir) :
    verbose = False
    if verbose:
        print("**** finding children \n", cell, t)
    children = []   
    string_id, data_container = get_info_current_time(t, data_container, labels_dir)
    
    connections = data_container['all_connections'][string_id]
    
    try:
        if cell[0] == "I":
            cell1 = []
            cell1.append(cell)
            cell = deepcopy(cell1)
    except IndexError:
        print("cell", cell)
        quit()
    for cell_curr in cell: 
        
        for con in range(len(connections)):
            if connections[con][0] == cell_curr:
                  children.append(deepcopy(connections[con][1:]))
    children = [item for sublist in children for item in sublist]
    children = list(set(children))
    children = list(np.unique(children))
    
    return children, data_container
    
def find_relatives(cellInterest, t1, t2, data_container,labels_dir): # tHistory, tInterest):
    #print("...finding relatives, directory labels: ",labels_dir)
    verbose = False
    children = deepcopy(cellInterest)
    
    t = deepcopy(t2) #(tHistory) #- timedelta(minutes = 5)
    ancestors_save = []
    children_save = []
    not_changing = 0
    time_disappear = 0
    
    while not_changing == 0 and time_disappear == 0:
        
        t = deepcopy(t2) #t = deepcopy(tHistory)

        while t > t1 and time_disappear==0: #while t > tInterest and time_disappear==0:  
            
            t_prev = t - timedelta(minutes = 5)
            
            ancestors, data_container = find_ancestors(children, t, data_container,labels_dir)
            
            if len(ancestors)==0:
                time_disappear = deepcopy(t)
                continue
            children = deepcopy(ancestors)
            t = t_prev
            
        
        if len(ancestors_save)!=0:
            if len(ancestors) == len(ancestors_save):
                not_changing = 1
                if verbose:
                    print("not changing = 1, ancestors")
            else:
                if verbose:
                    print("not changing still 0, ancestors")
        
        ancestors_save = deepcopy(ancestors)
        if verbose:
            print("TIME disappear", time_disappear)
        
        if not_changing == 0 and time_disappear ==0:
            while t < t2: # tHistory:    
                t_prev = deepcopy(t)
                children, data_container = find_children(children,t_prev, data_container,labels_dir)
                t += timedelta(minutes = 5)
                
            if len(children_save) !=0:
                if len(children) == len(children_save):
                    if verbose:
                        print("not changing = 1, children")
                    not_changing = 1    
                else:
                    if verbose:
                        print("not changing still 0, children")
                  
            children_save = deepcopy(children)
    
    if time_disappear == 0:
          return children_save, ancestors_save, data_container
    else:
          return [],[], data_container
     
def get_info_current_time(time, data_container, labels_dir): # all_connections = None, all_cell_properties = None, all_labels = None)
    
    """
    comment on general purpose, input and output of this function !HAU!

    input:
    * time [datetime object]: specifies current time
    * labels_dir [string]:    specifies where the shelves are saved

    input/output:
    * data_container [dictionary]:
         contains following keys:
         data_container['all_connections'][string_id]
         data_container['all_cell_properties'][string_id]
         data_container['all_labels'][string_id]

    output:
    * string_id [string]: id string the current time 

    """

    yearS, monthS, dayS, hourS, minS = string_date(time)
    string_id = yearS+monthS+dayS+hourS+minS
    
    # if information of current time "string_id" is not yet saved in data_container
    if string_id not in list(data_container['all_connections'].keys()):
        
        # read/get information from the shelve 
        filename = labels_dir+'/Labels_%s.shelve'%(yearS+monthS+dayS+hourS+minS)
        check_file_exists = glob.glob(filename+"*")
        if len(check_file_exists)>0:
              myShelve = shelve.open(filename)
              try:
                  data_container['all_connections'][string_id]     = myShelve['connections'] 
              except KeyError:
                  1+2
              except EOFError:
                  print("EOFError: ",filename, "quitting history_backward line 525")
                  quit()
                  #if you try to read the current timestep it won't find the connections yet!!! COULD BE DANGEROUS, could give error later
              try:
                  data_container['all_cell_properties'][string_id] = myShelve['cells']
              except KeyError:
                  print("ERROR reading: ", filename)
                  return None, None
              data_container['all_labels'][string_id]          = myShelve['labels'] 
        else:
              print("File doesn't exist: ",filename)
              return None, None  

    # !!!!!!!!! some can be returned as NONE if None as input ---> should always have all as output even if not needed/used/known !!!!!!!!!!    
    return string_id, data_container

def check_if_CenterOfMass_outside(labels_tmp, in_msg):
    x, y = ndimage.measurements.center_of_mass(labels_tmp)
    #print("x", x)
    #print("y", y)
    px_cut = in_msg.px_cut
    if x <= px_cut or x >= (640-px_cut) or y <= px_cut or y >= (710-px_cut):
        return True
    else:
        return False

def check_area_stop_history_when_small(threshold, cell_id, cells_known, t_known, data_container, labels_dir):
    verbose = False
    #year2S, month2S, day2S, hour2S, min2S = string_date(t_known)
    #year1S, month1S, day1S, hour1S, min1S = string_date(t_to_correct)
    
    #string_id1, data_container = get_info_current_time(t_to_correct, data_container, labels_dir)
    string_id2, data_container = get_info_current_time(t_known, data_container, labels_dir)
    #Atot_to_correct = 0
    Atot_known = 0
    
    #AT_known = np.zeros(num_rgb)
    #AT_to_correct = np.zeros(num_rgb)
    
    if verbose:
        print("string_id cells_known", string_id2)
        print(cells_known)
    
    try:
        labels_to_correct = deepcopy(data_container['all_labels'][string_id2]) #deepcopy(myShelve1['labels'])
    except KeyError:
        print("string_id2 ", string_id2)
        print("quitting in history_backward line 213")
        quit()
    labelsKnown = deepcopy(data_container['all_labels'][string_id2]) #deepcopy(myShelve2['labels'])
    
    #labels_out_to_correct = np.zeros(labels_to_correct.shape)
    #labels_outKnown = np.zeros(labelsKnown.shape)
    
    if cells_known[0] == "I":
            cells_known = [cells_known]    
            
    for ids in cells_known:
        #label = int(ids[2:])
        #labels_outKnown[labelsKnown==label] = label
        Atot_known += data_container['all_cell_properties'][string_id2][ids].area_px
    A2 = data_container['all_cell_properties'][string_id2]["ID"+str(cell_id)].area_px
    #A1 = A2 * Atot_to_correct/Atot_known
    #Temp_known = data_container['all_cell_properties'][string_id2]["ID"+str(cell_id)].mean108
    #Temp_to_correct = Temp_known + AT_to_correct/Atot_to_correct - AT_known/Atot_known
    
    if float(A2)/float(Atot_known) >= threshold:
        return True, data_container
    else:
        return False, data_container

def history_backward(time1, id_interesting_cell, backward, in_msg, t_stop = None, labels_dir = '/opt/users/'+getpass.getuser()+'/PyTroll/scripts/labels/',history_correction = True):

        """                                          
        --------------------------------------------------
        please describe the function a bit more. !HAU!
        general purpose
        input variables
        output variables
        """
        
        if backward == True:
            direction='backward'
            stop_history_when_small = in_msg.stop_history_when_smallForward
        else:
            direction='foreward'
            stop_history_when_small = in_msg.stop_history_when_smallBackward
        
        threshold_stop_history_when_small = in_msg.threshold_stop_history_when_small
        
        print("*** compute "+direction+" history of cell ID", id_interesting_cell)

        verbose = False
        
        data_container = {}
        data_container['all_connections'] = {}
        data_container['all_cell_properties'] = {}
        data_container['all_labels'] = {}
        
        interesting_cell = "ID"+str(id_interesting_cell)
        t_requestHist = deepcopy(time1)
        
        # comment what exactly is t_startDay and t_stopDay !HAU!
        if backward:
            if t_stop is not None:
                t_startDay = t_stop 
            else:
                # t_startDay might be undefined !HAU!
                # default start in the morning, 07:00 UTC
                t_startDay = datetime(time1.year, time1.month, time1.day, 7, 00)
                if   time1.day == 6 and time1.month == 6 and time1.year == 2015:  # avoid specific exceptions, that may produce hard to find bugs !HAU!
                    t_startDay = datetime(2015,6,6,11,25)
                elif time1.day == 7 and time1.month == 7 and time1.year == 2015:  # avoid specific exceptions, that may produce hard to find bugs !HAU!
                    t_startDay = datetime(2015,7,7,11,50)
            t_stopDay = deepcopy(time1) + timedelta(minutes = 5)
        else:
            t_startDay = deepcopy(time1) - timedelta(minutes = 5)
            
            if t_stop is not None:
                t_stopDay = t_stop
            else:
                # default stop time is 19:00 UTC
                t_stopDay = datetime(time1.year, time1.month, time1.day, 19, 00)
                if time1.day == 7 and time1.month == 7 and time1.year == 2015:  # avoid specific exceptions, that may produce hard to find bugs !HAU!
                    t_stopDay = datetime(2015,7,7,16,30)
                        
        yearS  = str(time1.year)
        monthS = "%02d" % time1.month
        dayS   = "%02d" % time1.day
        hourS  = "%02d" % time1.hour
        minS   = "%02d" % time1.minute
    
        # add some information from the shelve to the data_container
        string_id, data_container = get_info_current_time(time1, data_container, labels_dir)
        
        if string_id is None:
            return None, None, None, None, None
        
        labels_id = np.unique(data_container['all_labels'][string_id])
        
        #if verbose:
        #  print("labels_id including 0",labels_id) 
        labels_id = labels_id[labels_id>0]
        #if verbose:
        #    print("labels_id",labels_id)
        
        history_cell = {}
    
        rgb_load = ['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134'] #,'CTP','CTT']
            
        names = ["WV_062minusIR_108","WV_062minusWV_073","IR_108","WV_073minusIR_134","WV_062minusIR_097",\
                 "IR_087minusIR_120","IR_087minus2IR_108plusIR_120","IR_087minusIR_108","IR_120minusIR_108",\
                 "IR_097minusIR_134","WV_062minusIR_120","CloudTopPressure","CloudTopTemperature"]
        
        labels_tmp = np.where(data_container['all_labels'][string_id]==id_interesting_cell,1,0)

        if check_if_CenterOfMass_outside(labels_tmp,in_msg):
            print("*** center of mass outside for cell ID", id_interesting_cell)
            return None, None, None, None, None
        
        # loop over cells ... !HAU! is it nessesary to loop over the cells, cant you go directly to the interesting cell?
        for i in range(len(labels_id)):
            #if verbose:
            #print("history for cell: ", "ID"+str(labels_id[i]))
            #print(labels_id[i])

            if "ID"+str(labels_id[i]) == interesting_cell:
                if verbose:
                    print("processing interesting cell")
                
                t = deepcopy(time1)
                
                cell_id = labels_id[i]
                if verbose:
                    print("----cell ID", cell_id)
                
                current_cell = data_container['all_cell_properties'][string_id]["ID"+str(cell_id)]
                history_cell["ID"+str(cell_id)]                   = deepcopy(current_cell)
                history_cell["ID"+str(cell_id)].mean108           = np.array(history_cell["ID"+str(cell_id)].mean108)  # convert to np.array
                history_cell["ID"+str(cell_id)].area_px           = [history_cell["ID"+str(cell_id)].area_px]          # convert to list
                history_cell["ID"+str(cell_id)].colors.append('b')
                history_cell["ID"+str(cell_id)].displacement      = []                                                 # initialize with empty list
                history_cell["ID"+str(cell_id)].center            = [history_cell["ID"+str(cell_id)].center]           # convert to list
                history_cell["ID"+str(cell_id)].test_size         = [True]
                
                print ("you made it here ", history_cell["ID"+str(cell_id)].test_size)
                
                #id_prev = current_cell.id_prev
                count_stopped_hist = 0
                cell_large_enough = True
                while t > t_startDay and t < t_stopDay and cell_large_enough == True: # and len(id_prev) > 0: 
                    if np.logical_and(stop_history_when_small == True, history_cell["ID"+str(cell_id)].test_size[-1]==True) or stop_history_when_small == False:
                        children = "ID"+str(cell_id)
                        if verbose:
                            print("children ", children)
                        #print "inside cycle"
                        if backward:
                             t = t - timedelta (minutes = 5)
                        else:
                             t = t + timedelta (minutes = 5)
                             t_temp = deepcopy(time1)
                             while t_temp < t:
                                children, data_container = find_children(children, t_temp, data_container,labels_dir)
                                t_temp += timedelta(minutes = 5) 
                        
                        if verbose:
                            print("TIMESTEP ", t)
                        
                        """
                        if backward:
                                  children, ancestors, data_container = find_relatives(children, t, t_requestHist, data_container, labels_dir)
                        elif children!=[]:
                                  children, ancestors, data_container = find_relatives(children, t_requestHist, t, data_container, labels_dir)

                        if len(children)>0 and len(ancestors)>0:
                                  if verbose:
                                      print("after finding relatives \n Children",children, "\n Ancestors", ancestors)
                                  if backward:
                                        history_cell["ID"+str(cell_id)], data_container = add_history1(history_cell["ID"+str(cell_id)], cell_id, ancestors, children, t, t_requestHist,len(rgb_load), interesting_cell, backward,data_container,labels_dir,in_msg)
                                  else:
                                        history_cell["ID"+str(cell_id)], data_container = add_history1(history_cell["ID"+str(cell_id)], cell_id, children, ancestors, t, t_requestHist,len(rgb_load), interesting_cell, backward,data_container,labels_dir,in_msg)

                                  if verbose:
                                      print("history written for: ","ID",str(cell_id))
                        else:
                                  if verbose:
                                      print("no ancestors or children")
                                  break


                        """
                        
                        if backward:
                            children, ancestors, data_container = find_relatives(children, t, t_requestHist, data_container, labels_dir)
                            children_check = deepcopy(children)
                            ancestors_check = deepcopy(ancestors)  
                            if verbose:
                                print("done correct history")
                            if history_correction!=True:
                                t_no_correction = deepcopy(t_requestHist)
                                ancestors = deepcopy(interesting_cell)
                                children = deepcopy(interesting_cell)
                                if ancestors not in ancestors_check:
                                    ancestors = []
                                if verbose:
                                        print("Beginning \n children", children, "\n Ancestors:" ,ancestors)
                                        print("done history follow id")
                                if history_correction == False:
                                    ancestors = deepcopy(interesting_cell)
                                    children = deepcopy(interesting_cell)
                                    while t_no_correction > t:
                                        if verbose:
                                            print(t_no_correction)
                                            print("Before \n children", children, "\n Ancestors:", ancestors)
                                        ancestors, data_container = find_ancestors(ancestors, t_no_correction, data_container,labels_dir)
                                        if verbose:
                                            print("After \n children", children, "\n Ancestors:", ancestors)
                                        t_no_correction-=timedelta(minutes = 5)
                                    if verbose:
                                        print("Done history incorrect multiple ancestors/children")
                        elif children!=[]:
                            children, ancestors, data_container = find_relatives(children, t_requestHist, t, data_container, labels_dir) 
                            ancestors_check = deepcopy(ancestors)  
                            children_check = deepcopy(children)                            
                            if history_correction != True:
                                t_no_correction = deepcopy(t_requestHist)
                                ancestors = deepcopy(interesting_cell)
                                children = deepcopy(interesting_cell)
                                if children not in children_check:
                                    children = []
                                if history_correction == False:
                                    ancestors = deepcopy(interesting_cell)
                                    children = deepcopy(interesting_cell)                               
                                    while t_no_correction < t:
                                        if children != []:
                                            if verbose:
                                                print("looking for children of %s at "%(children), t_no_correction)
                                            children, data_container = find_children(children,t_no_correction, data_container,labels_dir)
                                            if verbose:
                                                print("children found are: ", children)
                                        else:
                                            print(interesting_cell,". requested: ",t_requestHist, "current time: ", t_no_correction)
                                            quit()
                                        t_no_correction+=timedelta(minutes = 5)
                                
                        if len(children)>0 and len(ancestors)>0 and len(children_check)>0 and len(ancestors_check)>0:
                            if verbose:
                              print("after finding relatives \n Children",children, "\n Ancestors", ancestors)
                            if backward:

                                cell_large_enough, data_container = check_area_stop_history_when_small(in_msg.threshold_stop_history_when_small, cell_id, children_check, t_requestHist, data_container, labels_dir)
                                
                                if cell_large_enough:
                                    if verbose:
                                        print("adding history: \n Children=", children, "at time:", t_requestHist, "\n Ancestors =", ancestors, "at time:", t) 
                                        print("To check you used: \n Children=", children_check, "at time:", t_requestHist, "The ancestors check are: ", ancestors_check, "at ", t)
                                    history_cell["ID"+str(cell_id)], data_container = add_history1(history_cell["ID"+str(cell_id)], cell_id, ancestors, children, t, t_requestHist, 
                                                                                                   len(rgb_load), interesting_cell, backward, data_container,labels_dir,in_msg,history_correction)
                                else:
                                    count_stopped_hist+=1
                                #quit()
                            else:
                                cell_large_enough, data_container = check_area_stop_history_when_small(in_msg.threshold_stop_history_when_small, cell_id, ancestors_check, t_requestHist, data_container, labels_dir)
                                if cell_large_enough:
                                    if verbose:
                                        print("adding history: \n Children=", children, "at time:", t, "\n Ancestors =", ancestors, "at time:", t_requestHist) 
                                        print("To check you used: \n Ancestors=", ancestors_check, "at time:", t_requestHist)                                    
                                    history_cell["ID"+str(cell_id)], data_container = add_history1(history_cell["ID"+str(cell_id)], cell_id, children, ancestors, t, t_requestHist, 
                                                                                                   len(rgb_load), interesting_cell, backward, data_container,labels_dir,in_msg,history_correction)
                                else:
                                    count_stopped_hist += 1
                            if verbose:
                              print("history written for: ","ID",str(cell_id))
                        else:
                            if verbose:
                              print("no ancestors or children")
                            break 
                    else:
                        break
                if verbose:
                    print("----is now a new cell", t, t_startDay)
            #else:
            #    if verbose:
            #        print("no match chosen ", interesting_cell, "and ID",str(labels_id[i]))

        if verbose:
            print("----beginning plotting")            
            print("*** cell chosen: ",interesting_cell)
        
        try:
            rgbs = history_cell[interesting_cell].mean108
        except KeyError:
            print(labels_id)
            print("quitting line 726 of history_backward")
            quit()
        area = history_cell[interesting_cell].area_px
        
        color_list = history_cell[interesting_cell].colors
        
        displacement = history_cell[interesting_cell].displacement
        
        center = history_cell[interesting_cell].center
    
        if rgbs.ndim >1:
            ind = np.zeros((rgbs.shape[0],11))
        else:
            ind = np.zeros((11))
        
        print("The number of times the history was not added because of the relative size of the cell is: ",count_stopped_hist)
        if ind.size>13:
              ind[:,0]  = rgbs[:,rgb_load.index('WV_062')] - rgbs[:,rgb_load.index('IR_108')] # cd 1 also us 6
              ind[:,1]  = rgbs[:,rgb_load.index('WV_062')] - rgbs[:,rgb_load.index('WV_073')] # cd 2 also us 1 & 4
              ind[:,2]  = rgbs[:,rgb_load.index('IR_108')]                                    # cd 3 also us 2 & 3
              ind[:,3]  = rgbs[:,rgb_load.index('WV_073')] - rgbs[:,rgb_load.index('IR_134')] # cd 4
              ind[:,4]  = rgbs[:,rgb_load.index('WV_062')] - rgbs[:,rgb_load.index('IR_097')] # cd 5
              ind[:,5]  = rgbs[:,rgb_load.index('IR_087')] - rgbs[:,rgb_load.index('IR_120')] # cd 6
          
              ind[:,6]  = rgbs[:,rgb_load.index('IR_087')] - rgbs[:,rgb_load.index('IR_108')]- rgbs[:,rgb_load.index('IR_108')] + rgbs[:,rgb_load.index('IR_120')] #gi 2
              ind[:,7]  = rgbs[:,rgb_load.index('IR_087')] - rgbs[:,rgb_load.index('IR_108')] # gi 4
              ind[:,8]  = rgbs[:,rgb_load.index('IR_120')] - rgbs[:,rgb_load.index('IR_108')] # gi 7
              
              ind[:,9]  = rgbs[:,rgb_load.index('IR_097')] - rgbs[:,rgb_load.index('IR_134')] # us 5
              ind[:,10] = rgbs[:,rgb_load.index('WV_062')] - rgbs[:,rgb_load.index('IR_120')] # us 7
              
              #ind[:,11] = rgbs[:,rgb_load.index('CTP')]
              #ind[:,12] = rgbs[:,rgb_load.index('CTT')]
        else:
              ind[0]  = rgbs[rgb_load.index('WV_062')] - rgbs[rgb_load.index('IR_108')] # cd 1 also us 6
              ind[1]  = rgbs[rgb_load.index('WV_062')] - rgbs[rgb_load.index('WV_073')] # cd 2 also us 1 & 4
              ind[2]  = rgbs[rgb_load.index('IR_108')]                                    # cd 3 also us 2 & 3
              ind[3]  = rgbs[rgb_load.index('WV_073')] - rgbs[rgb_load.index('IR_134')] # cd 4
              ind[4]  = rgbs[rgb_load.index('WV_062')] - rgbs[rgb_load.index('IR_097')] # cd 5
              ind[5]  = rgbs[rgb_load.index('IR_087')] - rgbs[rgb_load.index('IR_120')] # cd 6
          
              ind[6]  = rgbs[rgb_load.index('IR_087')] - rgbs[rgb_load.index('IR_108')]- rgbs[rgb_load.index('IR_108')] + rgbs[rgb_load.index('IR_120')] #gi 2
              ind[7]  = rgbs[rgb_load.index('IR_087')] - rgbs[rgb_load.index('IR_108')] # gi 4
              ind[8]  = rgbs[rgb_load.index('IR_120')] - rgbs[rgb_load.index('IR_108')] # gi 7
              
              ind[9]  = rgbs[rgb_load.index('IR_097')] - rgbs[rgb_load.index('IR_134')] # us 5
              ind[10] = rgbs[rgb_load.index('WV_062')] - rgbs[rgb_load.index('IR_120')] # us 7
              
              #ind[11] = rgbs[rgb_load.index('CTP')]
              #ind[12] = rgbs[rgb_load.index('CTT')]        
        t_end = deepcopy(time1)

        
        n_timestep = rgbs.shape[0]
        
        t_start = t_end - timedelta(minutes = 5*n_timestep)
        
        
        t_min = t_start - timedelta(minutes = 5)
        t_max = t_end + timedelta(minutes = 5)    

        displ_array = np.zeros((len(displacement),2))
        for dis in range(len(displacement)):
            displ_array[dis,:]=displacement[dis]
        
  
        time_save = []
        recs = []
        classes = ['split and merge','split','merge','no split or merge']
        class_colours = ['r','y','g','b']    

        t = deepcopy(t_end)
        for gg in range(ind.shape[0]):
            time_save.append(t)
            if backward:
                t -= timedelta(minutes = 5)
            else:
                t += timedelta(minutes = 5)

        if backward and False:
                for i in range(0,len(class_colours)):
                    recs.append(mpatches.Rectangle((0,0),1,1,fc=class_colours[i]))
                
                for i in range(ind.shape[1]):
                    t = deepcopy(t_end)
                    fig = plt.figure()
                    ax = plt.subplot(211)
                    #plt.xlabel("%s %s %s"%(str(t.day),str(t.month),str(t.year)))
                    plt.ylabel(names[i])  
                    for gg in range(ind.shape[0]):
                       
                       ax.plot_date(t, ind[gg,i], fmt='o', xdate = True, ydate=False, c = color_list[gg])#, s = 40)
                       #if i == 2:
                       #    time_save.append(t)
                       t -= timedelta(minutes = 5)
                    
                    ax.set_xlim([t_min, t_max])
                    xfmt = dates.DateFormatter('%H:%M')
                    ax.xaxis.set_major_formatter(xfmt)
                    plt.xticks([])
            
            #        plt.xticks(rotation='vertical')
                    lgd = ax.legend(recs,classes,loc='center left',bbox_to_anchor=(1,0.5))
                    t = deepcopy(t_end)
                    ax = plt.subplot(212)
                    plt.xlabel("%s/%s/%s"%(str(t.day),str(t.month),str(t.year)))
                    plt.ylabel("Area")  
                    for gg in range(ind.shape[0]):
                            ax.plot_date(t, area[gg], fmt='o', xdate = True, ydate=False, c = color_list[gg])#, s = 40)
                            
                            t -= timedelta(minutes = 5)
                    ax.set_xlim([t_min, t_max])
                    xfmt = dates.DateFormatter('%H:%M')
                    ax.xaxis.set_major_formatter(xfmt)
                    plt.xticks(rotation='vertical')
                    lgd = ax.legend(recs,classes,loc='center left',bbox_to_anchor=(1,0.5))        
                    
                    #/data/COALITION2/PicturesSatellite/LEL_results_wind/cell_properties
                    #outputDir = "/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/cell_properties/"+interesting_cell+"/properties/"
                    outputDir = yearS+"-"+monthS+"-"+dayS+"/cell_properties/"+interesting_cell+"/properties/"
                    fig.savefig(create_dir(outputDir)+names[i]+".png",bbox_extra_artists=(lgd,), bbox_inches = 'tight')
                    plt.close(fig)
                
        
                if False:       
                    #pickle.dump( time_save, open("TimeCell1h.p", "wb" ) )
                    #pickle.dump( area, open("AreaCell1h.p", "wb" ) )
                    #pickle.dump( displ_array, open("DxDyCell1h.p", "wb" ) )
                    t = deepcopy(t_end)
                    fig = plt.figure()
                    ax = plt.subplot(311)
                    #plt.xlabel("%s %s %s"%(str(t.day),str(t.month),str(t.year)))
                    plt.ylabel("displacement dx")  
                    for gg in range(len(displacement)):
                       ax.plot_date(t, displacement[gg][0], fmt='o', xdate = True, ydate=False, c = color_list[gg])#, s = 40)
                       t -= timedelta(minutes = 5)
                    
                    ax.set_xlim([t_min, t_max])
                    xfmt = dates.DateFormatter('%H:%M')
                    ax.xaxis.set_major_formatter(xfmt)
                    plt.xticks([])
                
                #        plt.xticks(rotation='vertical')
                    #lgd = ax.legend(recs,classes,loc='center left',bbox_to_anchor=(1,0.5))
                    t = deepcopy(t_end)
                    ax = plt.subplot(312)
                    #plt.xlabel("%s %s %s"%(str(t.day),str(t.month),str(t.year)))
                    plt.ylabel("displacement dy")  
                    for gg in range(len(displacement)):
                       ax.plot_date(t, displacement[gg][1], fmt='o', xdate = True, ydate=False, c = color_list[gg])#, s = 40)
                       t -= timedelta(minutes = 5)
                    
                    ax.set_xlim([t_min, t_max])
                    xfmt = dates.DateFormatter('%H:%M')
                    ax.xaxis.set_major_formatter(xfmt)
                    plt.xticks([])
                
                #        plt.xticks(rotation='vertical')
                    #lgd = ax.legend(recs,classes,loc='center left',bbox_to_anchor=(1,0.5))    
                    
                    t = deepcopy(t_end)
                    ax = plt.subplot(313)
                    plt.xlabel("%s/%s/%s"%(str(t.day),str(t.month),str(t.year)))
                    plt.ylabel("Area")  
                    for gg in range(ind.shape[0]):
                            ax.plot_date(t, area[gg], fmt='o', xdate = True, ydate=False, c = color_list[gg])#, s = 40)
                            
                            t -= timedelta(minutes = 5)
                    ax.set_xlim([t_min, t_max])
                    xfmt = dates.DateFormatter('%H:%M')
                    ax.xaxis.set_major_formatter(xfmt)
                    plt.xticks(rotation='vertical')
                    #lgd = ax.legend(recs,classes,loc='center left',bbox_to_anchor=(1,0.5))        
                    
                    #/data/COALITION2/PicturesSatellite/LEL_results_wind/cell_properties
                    fig.savefig(outputDir +"Displacement.png",bbox_extra_artists=(lgd,), bbox_inches = 'tight')
                    plt.close(fig)

        return ind, area, displ_array, time_save, center

def plot_results_history(t1, value1, label1, t2, value2, label2, t3, value3, label3, 
                         time1, variable, interesting_cell, 
                         times = None, split = None, merge = None):
    
    if times is not None:
        minimum_data = min(min(value1),min(value2),min(value3))
        val_to_subtract = (max(max(value1),max(value2),max(value3)) - minimum_data)/15
        min_value_split = [minimum_data - val_to_subtract]
        min_value_merge = [minimum_data - (val_to_subtract/2)]
        
        times = np.array(times)
        split = np.array(split)
        merge = np.array(merge)
        
        t_split = times[split>0]
        t_merge = times[merge>0]
    
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.plot_date(t1,value1, "*", markeredgewidth=1,markeredgecolor='red',markerfacecolor = 'None',label=label1)           
    ax.plot_date(t2,value2, "^", markeredgewidth=1,markeredgecolor='magenta',markerfacecolor = 'None',label=label2)  
    ax.plot_date(t3, value3, 'o',markeredgewidth=1,markeredgecolor='black', markerfacecolor = 'None',label=label3)           
    if times is not None:
        ax.plot_date(t_split, min_value_split*t_split.size, 'o',markersize = 4, color = "cyan",label="Split")
        ax.plot_date(t_merge, min_value_merge*t_merge.size, 'o',markersize = 4, color = "blue",label="Merge")
    
    if variable != "dx" and variable != "dy":
        ax.plot_date(t1[0],value1[0], color = "green", label = "Starting point")
    plt.xlim(t1[-1]-timedelta(minutes = 5), t1[0]+timedelta(minutes = 5))
    ax.legend(loc='best'); # upper left ##"best");
    
    yearS, monthS, dayS, hourS, minS = string_date(time1)
    
    filename="plot_history_back/"+variable+yearS+monthS+dayS+"_"+hourS+minS+"_ID"+str(id_interesting_cell)+'.png'
    #print (filename)
    plt.xlabel("time")
    if variable == "area":
        ylabel = "Area [km2]"
    elif variable == "IR108":
        ylabel = "Brightness temperature IR10.8 [K]"
    elif variable == "dx":
        ylabel = "South-North displacement [km]"
    elif variable == "dy":
        ylabel = "East-West displacement [km]"    
    elif variable == "COM":
        ylabel = "Coordinates Center of Mass"
    else:
        ylabel = "unknown variable"
    plt.title("ID"+str(interesting_cell)+" "+dayS+"."+monthS+"."+yearS)
    plt.ylabel(ylabel)
    plt.show()
    fig.savefig(filename)
    plt.close(fig)    #plt.plot(time_save, area, color = "red")

def find_split_and_merge(id_cell, times,labels_dir):
    data_container = {}
    data_container['all_connections'] = {}
    data_container['all_cell_properties'] = {}
    data_container['all_labels'] = {}
    times.sort()
    split = []
    merge = []
    
    for time in times:
        string_id, data_container = get_info_current_time(time, data_container, labels_dir)
        string_id_before, data_container = get_info_current_time(time-timedelta(minutes=5), data_container, labels_dir)
        
        connections = data_container['all_connections'][string_id_before]
        
        #find ancestors of cell at time-5min
        ancestors = data_container['all_cell_properties'][string_id][id_cell].id_prev
        
        if len(ancestors)==0:
            #no ancestors, new cell
            split.append(0)
            merge.append(0)
        else:
            if len(ancestors)==1: 
                merge.append(0) #if only one ancestors, there was no merge
                #ancestors = [ancestors] #allow to loop over ancestors even if only one (avoid looping over the letters of "IDXX")
            else:
                merge.append(1) #if more than one ancestors, there was a merge
            
            split_tmp = 0
            for ancestor in ancestors:
                if split_tmp == 0:
                    for con in range(len(connections)): 
                        if connections[con][0] == id_cell:
                            
                            children = connections[con][1:]
                            
                            if len(children)>1:
                                split_tmp = 1 #if one of the ancestors has more than one children, is a split
                                split.append(1) #as soon as there is one split just count and break
                                
                else:
                    break
            if split_tmp == 0:
                split.append(0)
        if len(split)!=len(merge):
            print(len(split))
            print(split)
            print(len(merge))
            print("len different")
            quit()
        
    if len(split)!=len(times) or len(merge)!=len(times):
        print(len(split))
        print(split)
        print(len(merge))
        print(len(times))
        print("Quitting because something went wrong with the splitting and merging count,history_backward line 1132")
        quit()
    else:
        return times, split, merge

            

if __name__=="__main__":

    import seaborn
       
    #id_interesting_cell = 54
    id_interesting_cell = 233
    backward = True

    #input_file = sys.argv[1]
    #if input_file[-3:] == '.py': 
    #    input_file=input_file[:-3]
    #in_msg = get_input_msg(input_file)
    #print ("input imported: ", input_file)
    #
    #if len(sys.argv)<6:
    #    print ("*** Warning, default call:")
    #    print (current_file+" 2015 6 7 15 10")
    #    time1 = datetime(2015,6,7,15,10) 
    #else:
    #    print("time frame to process: ",sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])
    #    year = int(sys.argv[2])
    #    month = int(sys.argv[3])
    #    day = int(sys.argv[4])
    #    hour = int(sys.argv[5])
    #    minutes =  int(sys.argv[6])
    #    #time1 = datetime(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])
    #    time1 = datetime(year, month, day, hour, minutes)

    from get_input_msg import get_date_and_inputfile_from_commandline
    in_msg = get_date_and_inputfile_from_commandline()
    time1 = in_msg.datetime

    if len(sys.argv)>7:
        id_interesting_cell = int(sys.argv[7])

    t_Stop = time1-timedelta(minutes = 65) #None #

    history_correction = False
    ind, area, displ_array, time_save, center = history_backward(time1, id_interesting_cell, backward, in_msg, t_stop = t_Stop, 
                                                                 labels_dir = '/opt/users/'+getpass.getuser()+'/PyTroll/scripts/labels/', history_correction = history_correction)
    history_correction = True
    ind_corr, area_corr, displ_array_corr, time_save_corr, center_corr = history_backward(time1, id_interesting_cell, backward, in_msg, t_stop = t_Stop , 
                                                                 labels_dir = '/opt/users/'+getpass.getuser()+'/PyTroll/scripts/labels/', history_correction = history_correction)
    history_correction = "follow_id"
    ind_id, area_id, displ_array_id, time_save_id, center_id = history_backward(time1, id_interesting_cell, backward, in_msg, t_stop = t_Stop, 
                                                                 labels_dir = '/opt/users/'+getpass.getuser()+'/PyTroll/scripts/labels/', history_correction = history_correction)
    
    times, split, merge = find_split_and_merge("ID"+str(id_interesting_cell), deepcopy(time_save), '/opt/users/'+getpass.getuser()+'/PyTroll/scripts/labels/')

    print("start plotting")
    plot_results_history(time_save,    area,            "Direct ancestors",time_save_id,     area_id,             "Follow ID",time_save_corr,     area_corr,    
                         "Corrected", time1, "area",  id_interesting_cell, times,      split,      merge)
    plot_results_history(time_save,ind[:,2],            "Direct ancestors",time_save_id,     ind_id[:,2],         "Follow ID",time_save_corr,     ind_corr[:,2],
                         "Corrected", time1, "IR108", id_interesting_cell, times,      split,      merge)
    plot_results_history(time_save[1:],displ_array[:,0],"Direct ancestors",time_save_id[1:], displ_array_id[:,0], "Follow ID",time_save_corr[1:], displ_array_corr[:,0],
                         "Corrected", time1, "dx",    id_interesting_cell, times[:-1], split[:-1], merge[:-1])
    plot_results_history(time_save[1:],displ_array[:,1],"Direct ancestors",time_save_id[1:], displ_array_id[:,1], "Follow ID",time_save_corr[1:], displ_array_corr[:,1],
                         "Corrected", time1, "dy",    id_interesting_cell, times[:-1], split[:-1], merge[:-1])
    
    #plot_results_history(time_save,area,"Not corrected",time_save_id, area_id, "Not corrected, follow ID",time_save_corr,area_corr,"Corrected",time1,"COM")
    
    
    
    
    
    
