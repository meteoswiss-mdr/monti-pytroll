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

def string_date(t):
    yearS  = str(t.year)
    monthS = "%02d" % t.month
    dayS   = "%02d" % t.day
    hourS  = "%02d" % t.hour
    minS   = "%02d" % t.minute
    
    return yearS, monthS, dayS, hourS, minS

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
        from Cells import Cells
        

def make_figureLabels(values, all_cells, obj_area, outputFile, colorbar = True, vmin = False, vmax = False, center = None):

    
    if vmin == False:
        vmin = values.min()
    if vmax == False:
        vmax = values.max()
    
    #obj_area = get_area_def(area)
    
    fig, ax = prepare_figure(obj_area) 
    
    mappable = plt.imshow(np.flipud(values), vmin = vmin, vmax = vmax, origin="lower")
    if center!=None:
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


def add_history(history_cell, t, id_prev, num_mean108): 
                          
    year0S  = str(t.year)
    month0S = "%02d" % t.month
    day0S   = "%02d" % t.day
    hour0S  = "%02d" % t.hour
    min0S   = "%02d" % t.minute    
    
    filename = '/opt/users/lel/PyTroll/scripts/labels/Labels_%s.shelve'%(year0S+month0S+day0S+hour0S+min0S)
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

def add_history1(history_cell, cell_id, cells_to_correct, cells_known, t_to_correct, t_known, num_rgb, interesting_cell, backward, data_container): #(ancestors).(children)
    verbose = False
    year2S, month2S, day2S, hour2S, min2S = string_date(t_known)
    year1S, month1S, day1S, hour1S, min1S = string_date(t_to_correct)
    
    string_id1, data_container = get_info_current_time(t_to_correct, data_container)
    string_id2, data_container = get_info_current_time(t_known, data_container)
        
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
        quit()
    labelsKnown = deepcopy(data_container['all_labels'][string_id2]) #deepcopy(myShelve2['labels'])
    
    labels_out_to_correct = np.zeros(labels_to_correct.shape)
    labels_outKnown = np.zeros(labelsKnown.shape)
    
    for ids in cells_to_correct:
        label = int(ids[2:])
        labels_out_to_correct[labels_to_correct==label] = label
        Atot_to_correct += data_container['all_cell_properties'][string_id1][ids].area_px
        for i in range(num_rgb):
            AT_to_correct[i] += data_container['all_cell_properties'][string_id1][ids].mean108[i] * data_container['all_cell_properties'][string_id1][ids].area_px
                    
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
    
   
    history_cell.colors.append('k')
    history_cell.area_px.append(A1) 
    history_cell.mean108 = np.vstack([history_cell.mean108, Temp_to_correct])
    
    
    labels_outKnownPlus1 = deepcopy(labels_outKnown)
    
    labels_out_to_correctPlus1 = deepcopy(labels_out_to_correct)
    
    labels_out_to_correctPlus1[labels_out_to_correctPlus1>0] = 1

    if backward:
        t = deepcopy(t_to_correct)
    else:
        t = deepcopy(t_known)

    t_interestPlus1 = t + timedelta(minutes=5)
    t_interestMinus1 = t - timedelta(minutes=5)
    
    test_KnownHistory = 0
    
    #displacement between tInterest (t) and tInterest - 5 min
    labels_outKnownPlus1 = np.zeros(labels_out_to_correctPlus1.shape)
    cells_to_use, data_container = find_ancestors(cells_to_correct,t,data_container)

    if cells_to_use == []:
        test_KnownHistory = 1 #there are no cells_to_correct of the current cells_to_correct! Displacement will be 0 and no image cells_to_correct
        
    else:
        string_idMinus1, data_container = get_info_current_time(t_interestMinus1, data_container)
        labels = deepcopy(data_container['all_labels'][string_idMinus1]) #deepcopy(myShelveMinus1['labels'])
            
    
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
        history_cell.center.append(center_to_correct-centerKnown)
    else:
        centerKnown = [0,0]    
        history_cell.center.append([0,0])
    
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


def find_ancestors(cell, t, data_container):
    
    verbose = False
    if verbose:
        print("**** finding ancestors \n", cell, t)
    ancestors = []
    
    string_id, data_container = get_info_current_time(t, data_container)
    
    if cell[0] == "I":
        cell1 = []
        cell1.append(cell)
        cell = deepcopy(cell1)
    
    for cell_curr in cell:
    
        try:
            ancestors.append(data_container['all_cell_properties'][string_id][cell_curr].id_prev)
            
        except KeyError: 
            print("current cells", cell_curr)
            print("all cells available:, ",data_container['all_cell_properties'][string_id].keys()) #myShelve['cells'].keys())
            quit()
        
    
    ancestors = [item for sublist in ancestors for item in sublist]
    ancestors = list(set(ancestors))
    
    ancestors = list(np.unique(ancestors))
    
    if verbose:
        print("the ancestors are: ", ancestors)
    return ancestors, data_container  
    
    
    
def find_children(cell,t,data_container) :
    verbose = False
    if verbose:
        print("**** finding children \n", cell, t)
    children = []   
    string_id, data_container = get_info_current_time(t, data_container)
    
    connections = data_container['all_connections'][string_id]
    
    if cell[0] == "I":
        cell1 = []
        cell1.append(cell)
        cell = deepcopy(cell1)
    for cell_curr in cell: 
        
        for con in range(len(connections)):
            if connections[con][0] == cell_curr:
                  children.append(deepcopy(connections[con][1:]))
    children = [item for sublist in children for item in sublist]
    children = list(set(children))
    children = list(np.unique(children))
    
    return children, data_container
    
def find_relatives(cellInterest, t1, t2, data_container): # tHistory, tInterest):
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
            ancestors, data_container = find_ancestors(children, t, data_container)
            
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
                children, data_container = find_children(children,t_prev, data_container)
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
     
def get_info_current_time(time, data_container): # all_connections = None, all_cell_properties = None, all_labels = None)
    
    yearS, monthS, dayS, hourS, minS = string_date(time)
    string_id = yearS+monthS+dayS+hourS+minS
    
    if string_id not in data_container['all_connections'].keys():
        filename = '/opt/users/lel/PyTroll/scripts/labels/Labels_%s.shelve'%(yearS+monthS+dayS+hourS+minS)
        myShelve = shelve.open(filename)
        try:
            data_container['all_connections'][string_id]     = myShelve['connections'] 
        except KeyError:
            1+2
            #if you try to read the current timestep it won't find the connections yet!!! COULD BE DANGEROUS, could give error later
        
        data_container['all_cell_properties'][string_id] = myShelve['cells']
        data_container['all_labels'][string_id]          = myShelve['labels']   
    # !!!!!!!!! some can be returned as NONE if None as input ---> should always have all as output even if not needed/used/known !!!!!!!!!!    
    return string_id, data_container

def check_if_CenterOfMass_outside(labels_tmp):
    x, y = ndimage.measurements.center_of_mass(labels_tmp)
    print("x", x)
    print("y", y)
    px_cut = 70
    if x <= px_cut or x >= (640-px_cut) or y <= px_cut or y >= (710-px_cut):
        return True
    else:
        return False
        
def history_backward(day,month,year,hour,minute,id_interesting_cell, backward, t_stop = None):

        """                                          
        --------------------------------------------------
        """
        #from Cells import Cells
        print("history backward of cell ID",id_interesting_cell)
        verbose = False        
        t1 = datetime(year, month, day, hour, minute)
        
        data_container = {}
        data_container['all_connections'] = {}
        data_container['all_cell_properties'] = {}
        data_container['all_labels'] = {}
        
        interesting_cell = "ID"+str(id_interesting_cell)
        t_requestHist = deepcopy(t1)
        
        if backward:
            if t_stop != None:
                t_startDay = t_stop
            elif day == 6 and month == 6:
                t_startDay = datetime(2015,6,6,11,25)
            elif day == 7 and month == 7:
                t_startDay = datetime(2015,7,7,11,50)
            t_stopDay = deepcopy(t1) + timedelta(minutes = 5)
        else:
            t_startDay = deepcopy(t1) - timedelta(minutes = 5)
            
            if t_stop != None:
                  t_stopDay = t_stop
            else:
                  t_stopDay = datetime(2015,7,7,16,30)
                        
        yearS  = str(t1.year)
        monthS = "%02d" % t1.month
        dayS   = "%02d" % t1.day
        hourS  = "%02d" % t1.hour
        minS   = "%02d" % t1.minute
    
        string_id, data_container = get_info_current_time(t1, data_container)
        
        labels_id = np.unique(data_container['all_labels'][string_id])
        
        if verbose:
          print("labels_id including 0",labels_id)
        
        labels_id = labels_id[labels_id>0]
        
        if verbose:
            print("labels_id",labels_id)
        
        history_cell ={}
    
        rgb_load = ['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134','CTP','CTT']
            
        names = ["WV_062minusIR_108","WV_062minusWV_073","IR_108","WV_073minusIR_134","WV_062minusIR_097","IR_087minusIR_120","IR_087minus2IR_108plusIR_120","IR_087minusIR_108","IR_120minusIR_108","IR_097minusIR_134","WV_062minusIR_120","CloudTopPressure","CloudTopTemperature"]
        
        labels_tmp = np.where(data_container['all_labels'][string_id]==id_interesting_cell,1,0)
        
        if check_if_CenterOfMass_outside(labels_tmp):
            return None, None, None, None
        
        for i in range(len(labels_id)):
            if verbose:
                print("history for cell: ", "ID"+str(labels_id[i]))
                print(labels_id[i])
            if "ID"+str(labels_id[i]) == interesting_cell:
                if verbose:
                    print("processing interesting cell")
                
                t = deepcopy(t1)
                
                cell_id = labels_id[i]
                if verbose:
                    print("----cell ID",cell_id)
                
                current_cell = data_container['all_cell_properties'][string_id]["ID"+str(cell_id)]
                history_cell["ID"+str(cell_id)] = deepcopy(current_cell)
                history_cell["ID"+str(cell_id)].mean108 = np.array(history_cell["ID"+str(cell_id)].mean108)
                history_cell["ID"+str(cell_id)].area_px = [history_cell["ID"+str(cell_id)].area_px]
                history_cell["ID"+str(cell_id)].colors.append('b')
                history_cell["ID"+str(cell_id)].center = []
                
                #id_prev = current_cell.id_prev
                
                while t > t_startDay and t < t_stopDay: # and len(id_prev) > 0: 
                
                    children = "ID"+str(cell_id)
                    if verbose:
                        print("children ", children)
                    #print "inside cycle"
                    if backward:
                         t = t - timedelta (minutes = 5)
                    else:
                         t = t + timedelta (minutes = 5)
                         t_temp = deepcopy(t1)
                         while t_temp < t:
                            children, data_container = find_children(children, t_temp, data_container)
                            t_temp += timedelta(minutes = 5) 
                    
                    if verbose:
                        print("TIMESTEP ", t)

                    
                    if backward:
                              children, ancestors, data_container = find_relatives(children, t, t_requestHist, data_container)
                    else:
                              children, ancestors, data_container = find_relatives(children, t_requestHist, t, data_container) 
                    
                    if len(children)>0 and len(ancestors)>0:
                              if verbose:
                                  print("after finding relatives \n Children",children, "\n Ancestors", ancestors)
                              if backward:
                                    history_cell["ID"+str(cell_id)], data_container = add_history1(history_cell["ID"+str(cell_id)], cell_id, ancestors, children, t, t_requestHist, len(rgb_load), interesting_cell, backward, data_container)
                              else:
                                    history_cell["ID"+str(cell_id)], data_container = add_history1(history_cell["ID"+str(cell_id)], cell_id, children, ancestors, t, t_requestHist, len(rgb_load), interesting_cell, backward, data_container)
                              
                              if verbose:
                                  print("history written for: ","ID",str(cell_id))
                    else:
                              if verbose:
                                  print("no ancestors or children")
                              break                                                          
                if verbose:
                    print("----is now a new cell", t, t_startDay)
            else:
                if verbose:
                    print("no match chosen ", interesting_cell, "and ID",str(labels_id[i]))
        if verbose:
            print("----beginning plotting")
            
            print("*** cell chosen: ",interesting_cell)
        
        rgbs = history_cell[interesting_cell].mean108
        
        area = history_cell[interesting_cell].area_px
        
        color_list = history_cell[interesting_cell].colors
        
        displacement = history_cell[interesting_cell].center
    
        if rgbs.ndim >1:
            ind = np.zeros((rgbs.shape[0],13))
        else:
            ind = np.zeros((13))
        

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
              
              ind[:,11] = rgbs[:,rgb_load.index('CTP')]
              ind[:,12] = rgbs[:,rgb_load.index('CTT')]
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
              
              ind[11] = rgbs[rgb_load.index('CTP')]
              ind[12] = rgbs[rgb_load.index('CTT')]        
        t_end = deepcopy(t1)

        
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

        return ind, area, displ_array, time_save






