from __future__ import division
from __future__ import print_function

import matplotlib.pyplot as plt
import numpy
import time
from datetime import datetime,timedelta
from Cells import Cells
from history_backward import history_backward, string_date, Cells #_withSAF
from properties_cells import create_dir
from future_properties import future_properties
from test_forecast import resize_array
from scipy import ndimage
import numpy as np
import matplotlib as mpl
import shelve
from copy import deepcopy
from math import sqrt
import scipy
from mpl_toolkits.mplot3d import Axes3D
from g_3dhist import plot_3d_histogram
#import colors
from get_input_msg import get_input_msg
import sys


def validation_forecast(cell, t, t_end, in_msg, history_correction):####LEL#validation_forecast(cell, t, t_end, t_stop_history, labels_dir):
    
    labels_dir = in_msg.labelsDir #'/opt/users/lel/PyTroll/scripts/labels/'
    verbose = False
    model = in_msg.model_fit_area
    all_errors_area = []
    all_errors_center = []
    all_errors_108 = []
    all_errors_dx = []
    all_errors_dy = []
    length_history = []
    
    while t <= t_end + timedelta(hours = 1):
    
        print(("starting history backward ", t))
        
        ind, area, displacement, time, center = history_backward(t, cell, True, in_msg, t-timedelta(hours=1), labels_dir=labels_dir,history_correction = history_correction)
        """
        if history_correction == True:
            history_correction_opposite = False
        else:
            history_correction_opposite = True
        #ind_True, area_True, displacement_True, time_True, center_True = history_backward(t, cell, True, in_msg, t-timedelta(hours=1), labels_dir=labels_dir,history_correction = history_correction_opposite)
        
        if len(area_True)!=len(area):
            print ("BACKWARD")
            print ("cell: ", cell)
            print ("time: ", t)
            print ("len False: ", len(area))
            print ("len True: ", len(area_True))
            quit()
        """    
        
        length_history.append(len(area)-1)
        
        names = ["WV_062 - IR_108", "WV_062 - WV_073", "IR_108", "WV_073 - IR_134", "WV_062 - IR_097",\
                 "IR_087 - IR_120", "IR_087 - 2IR_108plusIR_120", "IR_087 - IR_108",\
                 "IR_120 - IR_108", "IR_097 - IR_134", "WV_062 - IR_120", "CloudTopPressure", "CloudTopTemperature"]    
        history108 = []
        
        for i108 in range(ind.shape[0]):
            try:
                history108.append(ind[i108,2])
            except IndexError: #if the history is only 1 timestep long, ind is one list, therefore the value of the 108 is only one, the 3rd
                history108.append(ind[2])
                break
    
        if area is None or len(area)<=1:  
            print("The cell is outside of the area of interest or the history is not long enough (less than 1 timestep)")
        print("starting forecasts")    
        if len(area)<=3:
            t_forecast, y_forecast = future_properties(time, area, 'area', "linear")
            t_forecast, forecast108 = future_properties(time, history108, 'IR_108', "linear")
            
        else:
            t_forecast, y_forecast = future_properties(time, area, 'area', model)
            t_forecast, forecast108 = future_properties(time,history108,'IR_108',model)
        print("starting history forward, ", t)     
        ##LEL# t_temp_stop = min ((t+timedelta(hours = 1)+timedelta(minutes = 5)), (t_stop_history+timedelta(minutes = 5))) 
        t_temp_stop = t+timedelta(hours = 1)+timedelta(minutes = 5) 
        
        #history_correction = "follow_id" ##################### COMPARING ALL HISTORIES TO THE FOLLOW_ID VERSION!!!!!
        
        ind1, area1, displacement1, time1, center1 = history_backward(t, cell, False, in_msg, t_temp_stop, labels_dir=labels_dir,history_correction = history_correction)
        print("history forward Done") 
        
        """
        ind1_True, area1_True, displacement1_True, time1_True, center1_True = history_backward(t, cell, False, in_msg, t_temp_stop, labels_dir=labels_dir,history_correction = history_correction_opposite)
               
        
        if len(area1_True)!=len(area1) or displacement1.shape != displacement1_True.shape:
            print ("FORWARD")
            print ("cell: ", cell)
            print ("time: ", t)
            print ("len False: ", len(area1)," displacement False", displacement1.shape)
            print ("len True: ", len(area1_True)," displacement True", displacement1_True.shape)
            quit()
        """        
        t2 = time1 #[::-1]
        y2 = area1 #[::-1]
        ir108_2 = []
 
 
        if t==datetime(2015,7,7,15,20) and False:
                print("length history backward: ", len(time))
                print("length history forward: ", len(time1))
                print("length forecast: ", len(t_forecast))
                print("length forecast - index : ", len(t_forecast)- np.where(t_forecast==t)[0])
                print("length foreward - index : ", len(time1) - time1.index(t))
                print(time)
                print(time1)
                print(t_forecast)
                
                quit()
        
        if ind1.shape[0] == ind1.size:
            ir108_2.append(ind1[2])
        else:
            for i108 in range(ind1.shape[0]):
                
                ir108_2.append(ind1[i108,2])    
               
        forecasted_areas = []
        forecasted_center = []
        
        yearS, monthS, dayS, hourS, minS = string_date(t)
        filename = labels_dir+'Labels_%s.shelve'%(yearS+monthS+dayS+hourS+minS)
        myShelve = shelve.open(filename)
        labels_all = deepcopy(myShelve['labels'])          
        nx,ny = labels_all.shape  
        label_cell = np.zeros(labels_all.shape)
        label_cell[labels_all==cell] = 1
        dt = 0
          
        area_current = sum(sum(label_cell))
          
        forecasted_areas.append(area_current)
        
        forecasted_center.append(np.rint(ndimage.measurements.center_of_mass(label_cell)))
        
        error_area = [0]
        error_center = [0]
        error_108 = [0]
        error_dx = [0]
        error_dy = [0]
        
        myShelve.close()
          
        indx = np.where(t_forecast==t)[0] + 1
        
        indx1 = time1.index(t) + 1 #np.where(time1==t)[0] + 1
        
                 
        if displacement.shape[1]==2:
            if len(displacement) < 2:
                dx = 0
                dy = 0
            else:
                #try:
                    if displacement[-1,0]==0 and displacement[-1,1]==0 or np.isnan(displacement[-1,0]) or np.isnan(displacement[-1,1]):
                        dx = int(round(displacement[:-1,0].mean())) #exclude last line because it's always 0,0 (new cell has no displacement) CHECK IF THIS IS REQUIRED,not sure
                        dy = int(round(displacement[:-1,1].mean())) #exclude last line because it's always 0,0 (new cell has no displacement)
                    else:
                        dx = int(round(displacement[:,0].mean()))
                        dy = int(round(displacement[:,1].mean()))
                    
                #except ValueError:
                #    print("VALUE ERROR (line 168 in validation_forecast")
                #    print(displacement)
                #    quit()
            print(dx, dy)
    
        else:
            print("wrong displacement")
            quit()
    
        index_stop = 12
        
        max_forecast_time = min(12,len(t2)-indx1, len(t_forecast)-indx)
    
        for i in range(max_forecast_time):
    
          dt += 5
          if verbose:
              print(("... for time ", dt ,", index ", indx + i))
          if indx+i >= len(y_forecast):
              index_stop = deepcopy(i)
              break
          else:    
              area_new = y_forecast[indx+i]
              area_prev = y_forecast[indx+i-1]
          if verbose:
              print(("area px that will be grown ", area_current))
      
              print(("area forecasted ", area_new))
      
              print(("area forecasted prev ", area_prev))
          #growth = sqrt(float(area_new)/float(area_current))
      
          if area_new < 0 or len(area_new)==0 or len(area_prev)==0:
              if verbose:
                  print("the cell is predicted to disappear")
              index_stop = deepcopy(i)
              print("the cell is predicted to disappear")
              print(("stopping at: ", i, "instead of: ", list(range(max_forecast_time))))
              break
      
          growth = sqrt(float(area_new)/float(area_prev))
          if verbose:
              print(("growing by ", growth))
              print(("dx ", dx))
              print(("dy ", dy))
      
          #figure_labels(label_cell, outputFile, ttt, dt, area_plot="ccs4", add_name = "before")
      
          shifted_label = resize_array(label_cell,dx,dy, nx, ny)
      
          #figure_labels(shifted_label, outputFile, ttt, dt, area_plot="ccs4", add_name = "before_shifted")
          #quit()
          if verbose:
              print(("   after shift ", sum(sum(shifted_label))))
      
          if sum(sum(shifted_label))==0:#the cell is outside the domain
              break
      
          #center of mass before resizing
          center_before = ndimage.measurements.center_of_mass(shifted_label)
          center_before = np.rint(center_before)    
          
          forecasted_center.append(center_before)
              
          if verbose:
              print(("   after shift ", sum(sum(shifted_label))))
          resized_label = scipy.misc.imresize(shifted_label,float(growth),'nearest')
      
          resized_label[resized_label >0] = 1
      
          temp_label = np.zeros((nx,ny))
      
          #after resizing, the array is larger/smaller than nx,ny --> create new array that contains all the label region                  
          if resized_label.shape[0]<nx:
              temp_label[0:resized_label.shape[0],0:resized_label.shape[1]] = deepcopy(resized_label)
          else:
              x_start = max(min(np.nonzero(resized_label)[0])-1,0)
              y_start = max(min(np.nonzero(resized_label)[1])-1,0)      
              temp_label[0:min(nx,resized_label.shape[0]-x_start),0:min(ny,resized_label.shape[1]-y_start)] = deepcopy(resized_label[x_start:min(x_start+nx,resized_label.shape[0]),y_start:min(y_start+ny,resized_label.shape[1])])            
      
          if verbose:
              print((np.unique(temp_label)))
              print(("   after resize ", sum(sum(temp_label))))
          #figure_labels(resized_label, outputFile, ttt, dt, area_plot="ccs4", add_name = "before_shifted_resized")
      
          #center of mass after resizing
          center_after = ndimage.measurements.center_of_mass(temp_label)
          center_after = np.rint(center_after)         
      
          dx_new,dy_new = center_before - center_after
      
          shifted_label = resize_array(temp_label,dx_new,dy_new, nx, ny)
          if verbose:
              print(("   after shift2 ", sum(sum(shifted_label))))
          label_cell = np.zeros((nx,ny))
      
          label_cell[0:,0:] = shifted_label[0:nx,0:ny]
      
          if label_cell.shape[0] != nx or label_cell.shape[1] != ny:
                print("incorrect size")
                quit()
      
          #forecasted_labels["ID"+str(interesting_cell)].append(deepcopy(label_cell))
      
      
          #indx+=1
      
          label_cell = shifted_label #????????????????????????????????????
      
          area_current = sum(sum(label_cell))
          if verbose:
              print(("end ", area_current))
          forecasted_areas.append(area_current)
          #add check to make sure the area you produced is more or less correct
          if verbose:
              print((len(area1)))
              print(("indx1, i:",indx1,i))
          if indx1+i < len(area1): #if in reality the cell disappeared... not very nice that you just "kill" entire thing, but else what is distance centers??
              error_area.append((float((-area1[indx1+i] + area_current))/area1[indx1+i])*100)
              distance_centers = sqrt( (-center1[indx1+i][0]+center_before[0])*(-center1[indx1+i][0]+center_before[0]) + (-center1[indx1+i][1]+center_before[1])*(-center1[indx1+i][1]+center_before[1]) )
              center_dx = -center1[indx1+i][0]+center_before[0]
              center_dy = -center1[indx1+i][1]+center_before[1]
              error_center.append(distance_centers)
              error_dx.append(center_dx)
              error_dy.append(center_dy)
              error_108.append(-ir108_2[indx1+i] + forecast108[indx+i])    

         
        all_errors_area.append(error_area)
        all_errors_center.append(error_center)
        all_errors_108.append(error_108) 
        all_errors_dx.append(error_dx)
        all_errors_dy.append(error_dy)
        t += timedelta(minutes = 5)
        print("updating index")
    print("returning values")
    return all_errors_area,all_errors_center,all_errors_108,all_errors_dx, all_errors_dy, length_history

def plot_histogram(errors, length_history, str_cells, variable, th_history, longer_than_th, history_correction):
        if history_correction == True:
            add_name = "_CorrectHist"
        elif history_correction=="follow_id":
            add_name = "_NotCorrectHistFollowID"
        else:
            add_name = "_NotCorrectHist"
        hist_values = []
        hist_edges = []
        nbins = 6
        val_q1 = []
        val_q3 = []
        val_median = []
        axis_max = 0
        axis_min = 10000000 
        all_errors = {}
        name_out = "Histogram_"
        time_plot = [0,5,10,15,20,25,30,35,40,45,50,55,60]
        update_name = 0
        for ind in range(len(time_plot)):
              all_errors['%s'%time_plot[ind]]=[]
              for id_cell in str_cells:
                    for ind_each_cell in range(len(errors[id_cell])):
                        if len(errors[id_cell][ind_each_cell])>ind :
                            if th_history != None:
                                if longer_than_th:
                                    if update_name == 0:
                                        name_out+="HistoryMin%smin_"%str(th_history)
                                        update_name = 1
                                    if length_history[id_cell][ind_each_cell] >= th_long_history/5:
                                        all_errors['%s'%time_plot[ind]].append(errors[id_cell][ind_each_cell][ind]) 
                                else:
                                    if update_name == 0:
                                        name_out+="HistoryMax%smin_"%str(th_history)
                                        update_name = 1
                                    if length_history[id_cell][ind_each_cell] < th_long_history/5:    
                                        all_errors['%s'%time_plot[ind]].append(errors[id_cell][ind_each_cell][ind])                                    
                            else:
                                all_errors['%s'%time_plot[ind]].append(errors[id_cell][ind_each_cell][ind])            
              if all_errors['%s'%time_plot[ind]]==[]:
                    del all_errors['%s'%time_plot[ind]]              
        time_plot = list(all_errors.keys()) 
        time_plot = list(map(int,time_plot))
        time_plot.sort()  
        xtick_lables = []
        for ttime in time_plot:
            if ttime == 0:
                xtick_lables.append(str(ttime))
            else:
                xtick_lables.append(str(ttime)+"\n["+str(len(all_errors['%s'%ttime]))+"]")        

        for i in range(len(time_plot)): #c, z in zip(['r', 'g', 'b', 'y'], [5, 10, 15, 20]):
            hist_values_current, hist_edges_current = np.histogram(all_errors['%s'%str(time_plot[i])],nbins)
            hist_values.append(hist_values_current)
            hist_edges.append(hist_edges_current)
            if max(hist_edges_current)>axis_max:
                axis_max = max(hist_edges_current)
            if min(hist_edges_current)<axis_min:
                axis_min = min(hist_edges_current)
            val_q1.append(np.percentile(all_errors['%s'%str(time_plot[i])],25))
            val_q3.append(np.percentile(all_errors['%s'%str(time_plot[i])],75))
            val_median.append(np.median(all_errors['%s'%str(time_plot[i])]))
        
        pickle_median = True
        if pickle_median and th_history==None:
            import pickle
            pickle.dump(val_median, open('Median_'+variable+'_History'+str(history_correction)+'.p','wb'))
        
        #tmp_hist_values = hist_values[1:]
        blues = plt.get_cmap('Blues_r')
        cNorm = mpl.colors.Normalize(vmin = 0, vmax = max([item for sublist in hist_values[1:] for item in sublist]))
        scalarMap = mpl.cm.ScalarMappable(norm=cNorm, cmap = blues)      
        
        if variable == "area":
            ylabel_name = "percentage error area [%]"
        elif variable == "CenterOfMass":
            ylabel_name = "distance center of mass observed and forecasted"
        elif variable == "dx":
            ylabel_name = "error in South-North displacement [km]"
        elif variable == "dy":
            ylabel_name = "error in East-West displacement [km]"
        elif variable == "IR108":
            ylabel_name = "error IR10.8 brightness temperature [K]"
        
        import matplotlib.patches as patches
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim(0,max(time_plot)+5)
        ax.set_ylim(axis_min, axis_max)
        ax.set_xticks(time_plot)
        ax.set_xticklabels(xtick_lables)
        ax.set_xlabel("Lead Time [min]\n [number of events]")
        ax.set_ylabel(ylabel_name)
        
        for i in range(len(time_plot)):
            #print (hist_values)
            #print ("i", i)
            #print (len(hist_values))
            #print ("values", hist_values[i])
            for j in range(0,len(hist_values[i])): 
                colorVal = scalarMap.to_rgba(hist_values[i][j])
                Er_min = hist_edges[i][j]
                height = abs(hist_edges[i][j+1]-hist_edges[i][j])
                ax.add_patch(patches.Rectangle((int(time_plot[i])-1, Er_min), 2, height, facecolor=colorVal))
        plt.plot(time_plot,val_q1,'m', label = "Q1")
        plt.plot(time_plot,val_q3, 'r', label = "Q3")
        plt.plot(time_plot, val_median, 'g', label = "median")
        plt.legend(loc="best")            
        fig.subplots_adjust(right=0.8)
        cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.65])
        cb1 = mpl.colorbar.ColorbarBase(cbar_ax, cmap=blues,
                            norm=cNorm,
                            orientation='vertical')
        cb1.set_label('Count')
        
        fig.savefig("validation/"+name_out+'%s_LeadTime'%variable+add_name+'.eps', dpi=90, bbox_inches='tight')
        fig.savefig("validation/"+name_out+'%s_LeadTime'%variable+add_name+'.png', dpi=90, bbox_inches='tight')
        plt.close(fig)
        
def plot_boxplot(errors, length_history, str_cells, variable, th_history, longer_than_th, history_correction, graph_type = "boxplot"):
        if history_correction == True:
            add_name = "_CorrectHist"
        elif history_correction=="follow_id":
            add_name = "_NotCorrectHistFollowID"
        else:
            add_name = "_NotCorrectHist"    
        all_errors = {}
        name_out = "Boxplot_"
        time_plot = [0,5,10,15,20,25,30,35,40,45,50,55,60]
        update_name = 0
        for ind in range(len(time_plot)):
              all_errors['%s'%time_plot[ind]]=[]
              for id_cell in str_cells:
                    for ind_each_cell in range(len(errors[id_cell])):
                        if len(errors[id_cell][ind_each_cell])>ind :
                            if th_history != None:
                                if longer_than_th:
                                    if update_name == 0:
                                        name_out+="HistoryMin%smin_"%str(th_history)
                                        update_name = 1
                                    if length_history[id_cell][ind_each_cell] >= th_long_history/5:
                                        all_errors['%s'%time_plot[ind]].append(errors[id_cell][ind_each_cell][ind]) 
                                else:
                                    if update_name == 0:
                                        name_out+="HistoryMax%smin_"%str(th_history)
                                        update_name = 1
                                    if length_history[id_cell][ind_each_cell] < th_long_history/5:    
                                        all_errors['%s'%time_plot[ind]].append(errors[id_cell][ind_each_cell][ind])                                    
                            else:
                                all_errors['%s'%time_plot[ind]].append(errors[id_cell][ind_each_cell][ind])            
              if all_errors['%s'%time_plot[ind]]==[]:
                    del all_errors['%s'%time_plot[ind]]              
        time_plot = list(all_errors.keys()) 
        time_plot = list(map(int,time_plot))
        time_plot.sort()  
        
        xtick_lables = []
        
        for ttime in time_plot:
            if ttime == 0:
                xtick_lables.append(str(ttime))
            else:
                xtick_lables.append(str(ttime)+"\n["+str(len(all_errors['%s'%ttime]))+"]")
        
        error_plot = []
        for tttt in time_plot:
            error_plot.append(all_errors['%s'%tttt])
        
        if variable == "area":
            ylabel_name = "percentage error area [%]"
        elif variable == "CenterOfMass":
            ylabel_name = "distance center of mass observed and forecasted"
        elif variable == "dx":
            ylabel_name = "error in South-North displacement [km]"
        elif variable == "dy":
            ylabel_name = "error in East-West displacement [km]"
        elif variable == "IR108":
            ylabel_name = "error IR10.8 brightness temperature [K]"
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim(0,max(time_plot)+10)
        ##ax2 = ax.twiny()
        if variable == "area":
            ax.set_ylim(-100, 200)
        elif variable == "dx" or variable == "dy":
            ax.set_ylim(-40,30)
        elif variable == "CenterOfMass":
            ax.set_ylim(0,40)
        elif variable == "IR108":
            ax.set_ylim(-15,15)
        ax.set_xlabel("Lead Time [min]\n [number of events]")
        ax.set_ylabel(ylabel_name)
        if graph_type == "boxplot":
            plt.boxplot(error_plot)
            
            add = ""
        elif graph_type == "violin":
            ax = sns.violinplot(data = error_plot)
            add = "violin"
        ax.set_xticklabels(xtick_lables) #time_plot)
        
        ##new_tick_locations = np.array(time_plot[1:])
        #ax2.set_xlim(ax.get_xlim())
        ##ax2.set_xticks(new_tick_locations)
        ##ax2.set_xticklabels(number_events)
        ##ax2.set_xlabel("number of events")
        fig.savefig("validation/"+name_out+add+'%s_LeadTime'%variable+add_name+'.eps', dpi=90, bbox_inches='tight')
        fig.savefig("validation/"+name_out+add+'%s_LeadTime'%variable+add_name+'.png', dpi=90, bbox_inches='tight')
        plt.close(fig)    

def plot_Scatter(each_cell_separately, str_cells, length_history, errors_area, errors_108, errors_COM, history_correction):
    
    if history_correction == True:
        add_name = "_CorrectHist"
    elif history_correction=="follow_id":
        add_name = "_NotCorrectHistFollowID"
    else:
        add_name = "_NotCorrectHist"
    x_axis = [0,5,10,15,20,25,30,35,40,45,50,55,60]
    if each_cell_separately:
        for id_cells in str_cells:
            vmax = 60 #max(max(length_history.values()))*5
            blues = plt.get_cmap('Blues_r')
            cNorm = mpl.colors.Normalize(vmin = 0, vmax = vmax)
            scalarMap0 = mpl.cm.ScalarMappable(norm=cNorm, cmap = blues)
            f, axarr = plt.subplots(3, sharex=True)    
            for i in range(len(length_history[id_cells])):
                colorVal = scalarMap0.to_rgba(length_history[id_cells][i]*5)
                color_current = [colorVal]*len(errors_area[id_cells][i])
                axarr[0].scatter(x_axis[0:len(errors_area[id_cells][i])], errors_area[id_cells][i], color = color_current,marker='o')
                axarr[0].set_ylabel('Er area [%]')
                #plt.ylabel('Er area [px2]')
          
            for i in range(len(length_history[id_cells])):
                colorVal = scalarMap0.to_rgba(length_history[id_cells][i]*5)
                color_current = [colorVal]*len(errors_108[id_cells][i])
                axarr[1].scatter(x_axis[0:len(errors_108[id_cells][i])], errors_108[id_cells][i], color = color_current,marker='o')
                #plt.ylabel('Er IR10.8 [K]')    
                axarr[1].set_ylabel('Er IR10.8 [K]')

            for i in range(len(length_history[id_cells])):
                colorVal = scalarMap0.to_rgba(length_history[id_cells][i]*5)
                color_current = [colorVal]*len(errors_COM[id_cells][i])
                axarr[2].scatter(x_axis[0:len(errors_COM[id_cells][i])], errors_COM[id_cells][i], color = color_current,marker='o')
                plt.xlim([0,65])
                plt.xlabel('lead time [min]')
                axarr[2].set_ylabel('Er centers [px]')
                #plt.ylabel('Er centers [px]')  
                f.subplots_adjust(right=0.8)
  
                cbar_ax = f.add_axes([0.85, 0.2, 0.05, 0.6]) #left bottom width height
                cb1 = mpl.colorbar.ColorbarBase(cbar_ax, cmap=blues,
                                                norm=cNorm,
                                                orientation='vertical')
                cb1.set_label('Length History [min]')          
                f.savefig("validation/%s_ScatterErrors"+add_name+".eps"%id_cells)
                f.savefig("validation/%s_ScatterErrors"+add_name+".png"%id_cells) 
                plt.close(f)    
    else:
        vmax = 60 #max(max(length_history.values()))*5
        blues = plt.get_cmap('Blues')
        cNorm = mpl.colors.Normalize(vmin = 0, vmax = vmax)
        scalarMap0 = mpl.cm.ScalarMappable(norm=cNorm, cmap = blues)
        f, axarr = plt.subplots(3, sharex=True)
              
        for id_cells in str_cells:
              for i in range(len(length_history[id_cells])):
                colorVal = scalarMap0.to_rgba(length_history[id_cells][i]*5)
                color_current = [colorVal]*len(errors_area[id_cells][i])
                try:
                    axarr[0].scatter(x_axis[0:len(errors_area[id_cells][i])], errors_area[id_cells][i], color = color_current,marker='o')
                except ValueError:
                    print("shape_color_current", len(color_current))
                    print("color_current \n", color_current)
                    print("errors_area: ", errors_area[id_cells][i])
                    print("len errors_area: ", len(errors_area[id_cells][i]))
                    quit()
              for i in range(len(length_history[id_cells])):
                colorVal = scalarMap0.to_rgba(length_history[id_cells][i]*5)
                color_current = [colorVal]*len(errors_108[id_cells][i])
                axarr[1].scatter(x_axis[0:len(errors_108[id_cells][i])], errors_108[id_cells][i], color = color_current,marker='o')
              for i in range(len(length_history[id_cells])):
                colorVal = scalarMap0.to_rgba(length_history[id_cells][i]*5)
                color_current = [colorVal]*len(errors_COM[id_cells][i])
                axarr[2].scatter(x_axis[0:len(errors_COM[id_cells][i])], errors_COM[id_cells][i], color = color_current,marker='o')
              
        plt.xlim([0,65])  
        plt.xlabel('lead time [min]')    
        axarr[0].set_ylabel('Er area [%]')
        axarr[1].set_ylabel('Er IR10.8 [%]')
        axarr[2].set_ylabel('Er centers [px]')
        f.subplots_adjust(right=0.8)
        cbar_ax = f.add_axes([0.85, 0.2, 0.05, 0.6]) #left bottom width height
        cb1 = mpl.colorbar.ColorbarBase(cbar_ax, cmap=blues,
                                        norm=cNorm,
                                        orientation='vertical')
        cb1.set_label('Length History [min]')          
        f.savefig("validation/ScatterErrors"+add_name+".eps") 
        f.savefig("validation/ScatterErrors"+add_name+".png")
        plt.close(f)     

def plot_hexagonal2dHist(str_cell, errors_area, errors_dx, errors_dy, history_correction):
    if history_correction == True:
        add_name = "_CorrectHist_"
    elif history_correction==False:
        add_name = "_NotCorrectHist_"
    else:
        add_name = "_NotCorrectHistFollowID"
    x_axis = [0,5,10,15,20,25,30,35,40,45,50,55,60]
    print(("plotting hexbin, history correction = ", history_correction))
    all_dx = []
    all_dy = []
    for ind in range(1,len(x_axis)):
        for id_cell in str_cells:
              for ind_each_cell in range(len(errors_dx[id_cell])):
                  if len(errors_area[id_cell][ind_each_cell])>ind :
                      all_dx.append(errors_dx[id_cell][ind_each_cell][ind]*(-1))   
                      all_dy.append(errors_dy[id_cell][ind_each_cell][ind]) 
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.hexbin(all_dy,all_dx)
    ax.set_xlim([-40,40])
    ax.set_ylim([-40,40])
    fig.savefig("validation/Hexbin"+add_name+".eps")
    fig.savefig("validation/Hexbin"+add_name+".png")
    plt.close(fig)          

def plot_dx_dy(str_cells, errors_dx, errors_dy, errors_area, length_history, history_correction):
    if history_correction == True:
        add_name = "_CorrectHist"
    elif history_correction=="follow_id":
        add_name = "_NotCorrectHistFollowID"
    else:
        add_name = "_NotCorrectHist"
    print(("plotting dx dy history correction = ", history_correction))
    
    time_plot = [0,5,10,15,20,25,30,35,40,45,50,55,60]
    all_errors_dx_ShortHistory = {}
    all_errors_dx_LongHistory = {}
    all_errors_dy_ShortHistory = {}
    all_errors_dy_LongHistory = {}
    #plot with the errors on the area separated based on the length of the history (th_long_history)
    for ind in range(0,len(time_plot)):
        all_errors_dx_ShortHistory['%s'%time_plot[ind]]=[]
        all_errors_dx_LongHistory['%s'%time_plot[ind]]=[]
        all_errors_dy_ShortHistory['%s'%time_plot[ind]]=[]
        all_errors_dy_LongHistory['%s'%time_plot[ind]]=[]
        for id_cell in str_cells:
              for ind_each_cell in range(len(errors_dx[id_cell])):
                  if len(errors_area[id_cell][ind_each_cell])>ind :
                      if length_history[id_cell][ind_each_cell] < th_long_history/5:
                        all_errors_dx_ShortHistory['%s'%time_plot[ind]].append(errors_dx[id_cell][ind_each_cell][ind]*(-1))
                        all_errors_dy_ShortHistory['%s'%time_plot[ind]].append(errors_dy[id_cell][ind_each_cell][ind])
                      else:
                        all_errors_dx_LongHistory['%s'%time_plot[ind]].append(errors_dx[id_cell][ind_each_cell][ind]*(-1))   
                        all_errors_dy_LongHistory['%s'%time_plot[ind]].append(errors_dy[id_cell][ind_each_cell][ind]) 

    blues = plt.get_cmap('Blues_r')
    cNorm = mpl.colors.Normalize(vmin = 0, vmax = 60)
    scalarMap = mpl.cm.ScalarMappable(norm=cNorm, cmap = blues)

    f, axarr = plt.subplots(2, sharex=True, sharey=True) #fig = plt.figure()
    #plt.subplot(211)
    #"short history"
    for i in range(len(time_plot)-1,-1,-1):   
      colorVal = scalarMap.to_rgba(i*5)
      #plt.scatter(all_errors_dx_LongHistory ['%s'%time_plot[i]], all_errors_dy_LongHistory ['%s'%time_plot[i]], color = colorVal) 
      color_current = [colorVal]*len(all_errors_dx_ShortHistory['%s'%time_plot[i]])
      axarr[0].scatter(all_errors_dy_ShortHistory['%s'%time_plot[i]],all_errors_dx_ShortHistory['%s'%time_plot[i]], color = color_current)#, edgecolor = 'none')
      
    axarr[0].scatter(0,0,marker="*",color = 'r', s = 50)

    #plt.ylabel('South-North displacement [km]')  
    #plt.xlabel('West-East displacement [km]')  
    blues = plt.get_cmap('Blues_r')
    cNorm = mpl.colors.Normalize(vmin = 0, vmax = 60)
    scalarMap = mpl.cm.ScalarMappable(norm=cNorm, cmap = blues)            
    #"long history"                
    #plt.subplot(212)
    for i in range(len(time_plot)-1,-1,-1):
      colorVal = scalarMap.to_rgba(i*5)
      color_current = [colorVal]*len(all_errors_dx_LongHistory['%s'%time_plot[i]]) #necessary to do this because colorVal is 4 numbers, if all_errors_dx_LongHistory is also 4 numbers it makes them 4 colors!!
      axarr[1].scatter(all_errors_dy_LongHistory['%s'%time_plot[i]], all_errors_dx_LongHistory['%s'%time_plot[i]],color = color_current)#, edgecolor = 'none')        
      
    axarr[1].scatter(0,0,marker="*",color = 'r', s = 50) 
    #for ax in axarr:
    #  ax.set_ylabel('South-North displacement [km]')  
    #  ax.set_xlabel('West-East displacement [km]')              
    f.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.ylabel("South-North displacement [km]")
    plt.xlabel("West-East displacement [km]")

    f.subplots_adjust(right=0.8)

    cbar_ax = f.add_axes([0.85, 0.2, 0.05, 0.6]) #left bottom width height
    cb1 = mpl.colorbar.ColorbarBase(cbar_ax, cmap=blues,
                  norm=cNorm,
                  orientation='vertical')
    cb1.set_label('Lead Time [min]')
    #f.tight_layout()
    f.savefig('validation/Validation_dx_dy'+add_name+'.eps')
    f.savefig('validation/Validation_dx_dy'+add_name+'.png')
    plt.close(f)        

def plot_pdf(str_cells,errors_area,errors_dx, errors_dy, length_history, history_correction):
    if history_correction == True:
        add_name = "_CorrectHist"
    elif history_correction=="follow_id":
        add_name = "_NotCorrectHistFollowID"
    else:
        add_name = "_NotCorrectHist"
    x_axis = [0,5,10,15,20,25,30,35,40,45,50,55,60]
    all_dx = []
    all_dy = []
    all_lead_time = []
    for ind in range(1,len(x_axis)):
        for id_cell in str_cells:
              for ind_each_cell in range(len(errors_dx[id_cell])):
                  if len(errors_area[id_cell][ind_each_cell])>ind :
                      all_dx.append(errors_dx[id_cell][ind_each_cell][ind]*(-1))   
                      all_dy.append(errors_dy[id_cell][ind_each_cell][ind])
                      all_lead_time.append(ind*5)
    
    y1 = deepcopy(all_dx) # usual conversion between matrix and plotting convenction: in matrix x = north to south, y = west to east. In plotting x = west to east, y = south to north. (x matrix has already been multiplicated by -1)
    
    x1 = deepcopy(all_dy) #
    lead_times = deepcopy(all_lead_time)
    to_pickle = False
    if to_pickle:
        import pickle
        to_dump = []
        to_dump.append(x1)
        to_dump.append(y1)
        to_dump.append(all_lead_time)
        pickle.dump(to_dump, open('errors_x_y.p','wb'))
        
    vmax = 60 #max(max(length_history.values()))*5
    blues = plt.get_cmap('Blues_r')
    cNorm = mpl.colors.Normalize(vmin = 0, vmax = vmax)
    scalarMap = mpl.cm.ScalarMappable(norm=cNorm, cmap = blues)
    
    color_lead = []
    distances00 = []
    for lead_t, x, y in zip(lead_times, x1,y1):
        color_lead.append(scalarMap.to_rgba(lead_t))
        distances00.append(sqrt(x*x+y*y))
    
    print("20% percentile", np.percentile(distances00,20))
    print("40% percentile", np.percentile(distances00,40))
    print("60% percentile", np.percentile(distances00,60))
    print("80% percentile", np.percentile(distances00,80))
    print("100% percentile", np.percentile(distances00,100))
    print("max: ", max(distances00))
    
    fig, ax = plt.subplots(nrows=1,ncols=1)
    
    ax.scatter(x1,y1,color=color_lead)
    radius = []
    percentiles_wanted = [25,50,75]
    for percent in percentiles_wanted:
        radius.append(np.percentile(distances00,percent))        
    n_bin_x = int(float(max(x1)-min(x1))/size_bin)
    n_bin_y = int(float(max(y1)-min(y1))/size_bin)
    H, xedges, yedges = np.histogram2d(x1,y1,bins=[n_bin_x,n_bin_y])
    H0=deepcopy(H)
    extent = [xedges[0],xedges[-1],yedges[0],yedges[-1]]
    
    for i in range(H.shape[0]):
        for j in range(H.shape[1]):
            H[i,j] = float(H[i,j])/len(x1)*100
    cmap = plt.cm.get_cmap("autumn_r")
    cset1 = ax.contour(H.transpose(), extent = extent, cmap = cmap, linewidths= 3)
    
    for r_circle,percent in zip(radius,percentiles_wanted):
        circle_to_plot = plt.Circle((0,0),r_circle, color = "black", linewidth=2, fill=False)
        ax.add_artist(circle_to_plot)
        plt.text(r_circle,0,str(percent)+"%",fontsize=12,color = "black", fontweight = "bold")
    
    ax.set_xlim(xmin=-20.,xmax=+20.)
    ax.set_ylim(ymin=-20.,ymax=+20.) 
    ax.set_aspect('equal')
    #plt.clabel(cset1, inline=0, fontsize=12,fmt = '%r %%')
    for i in range(len(cset1.levels)):
        cset1.collections[i].set_label(str(cset1.levels[i])+"%")
    plt.ylabel("South-North displacement [km]")
    plt.xlabel("West-East displacement [km]")
    plt.legend(loc='upper left')       
    plt.title("Displacement error (33 cells, %s points)"%(str(len(x1))))
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.65])
    cb1 = mpl.colorbar.ColorbarBase(cbar_ax, cmap=blues,
                                    norm=cNorm,
                                    orientation='vertical')
    cb1.set_label('Length history [min]')
    fig.savefig("validation/dx_dy_Contour"+add_name+".eps")
    fig.savefig("validation/dx_dy_Contour"+add_name+".png")
    plt.close(fig)    

    
if __name__ == "__main__":

    import seaborn as sns    

    input_file = sys.argv[1]
    if input_file[-3:] == '.py': 
        input_file=input_file[:-3]
    in_msg = get_input_msg(input_file)
    print(("input imported: ", input_file))

    history_correction = True
    print(("history correction = ", history_correction))
    size_bin = 2.5 #kilometers in x and y dimension corresponding to desired size of the bins (in pdf of SN and WE displacement error)
    interesting_cell = []
    t_start = []
    t_end = []
    t_stop_history = []
    
    verbose = False
    
    #cells to be included: respectively id_number, time start and end at which compute history and forecast every 5 min; time at which to stop (forecast and validation won't go further than that)
    #if False:
    if True:
            interesting_cell.append(67);  t_start.append(datetime(2015,7,7,11,55)); t_end.append(datetime(2015,7,7,14,45))####LEL#54
            #interesting_cell.append(82);  t_start.append(datetime(2015,7,7,12,5)) ; t_end.append(datetime(2015,7,7,11,50))####LEL#69
            interesting_cell.append(180); t_start.append(datetime(2015,7,7,13,45)); t_end.append(datetime(2015,7,7,12,50))####LEL#175
            interesting_cell.append(165); t_start.append(datetime(2015,7,7,13,20)); t_end.append(datetime(2015,7,7,12,50))####LEL#147
            interesting_cell.append(240); t_start.append(datetime(2015,7,7,15,10)); t_end.append(datetime(2015,7,7,14,25))####LEL#240
    
    #if False:
    #if True:
            interesting_cell.append(39);  t_start.append(datetime(2015,6,6,11,15)); t_end.append(datetime(2015,6,6,12,05))
            interesting_cell.append(41);  t_start.append(datetime(2015,6,6,11,25)); t_end.append(datetime(2015,6,6,11,20))
            interesting_cell.append(57);  t_start.append(datetime(2015,6,6,11,40)); t_end.append(datetime(2015,6,6,14,10))
            interesting_cell.append(60);  t_start.append(datetime(2015,6,6,11,45)); t_end.append(datetime(2015,6,6,11,55))
            interesting_cell.append(87);  t_start.append(datetime(2015,6,6,12,30)); t_end.append(datetime(2015,6,6,14,35))
            #interesting_cell.append(134); t_start.append(datetime(2015,6,6,13,15)); t_end.append(datetime(2015,6,6,14,05)) #1315
    
    #if True:
    #if False:
            interesting_cell.append(13);  t_start.append(datetime(2015,6,7,9,55));  t_end.append(datetime(2015,6,7,12,20))
            interesting_cell.append(15);  t_start.append(datetime(2015,6,7,10,0));  t_end.append(datetime(2015,6,7,10,40))
            interesting_cell.append(18);  t_start.append(datetime(2015,6,7,10,10)); t_end.append(datetime(2015,6,7,11,25))
            interesting_cell.append(39);  t_start.append(datetime(2015,6,7,10,55)); t_end.append(datetime(2015,6,7,11,45))
            interesting_cell.append(72);  t_start.append(datetime(2015,6,7,11,55)); t_end.append(datetime(2015,6,7,12,55))
            interesting_cell.append(75);  t_start.append(datetime(2015,6,7,12,0));  t_end.append(datetime(2015,6,7,13,45))
            interesting_cell.append(162); t_start.append(datetime(2015,6,7,13,45)); t_end.append(datetime(2015,6,7,14,50))
            interesting_cell.append(233); t_start.append(datetime(2015,6,7,14,35)); t_end.append(datetime(2015,6,7,18,0))
            #interesting_cell.append(233); t_start.append(datetime(2015,6,7,17,35)); t_end.append(datetime(2015,6,7,16,50))
            #interesting_cell.append(15);  t_start.append(datetime(2015,6,7,10,0));  t_end.append(datetime(2015,6,7,10,40))
    
    #if True:
    #if False:
            interesting_cell.append(60);  t_start.append(datetime(2015,6,12,10,5));  t_end.append(datetime(2015,6,12,9,55))
            interesting_cell.append(63);  t_start.append(datetime(2015,6,12,10,5));  t_end.append(datetime(2015,6,12,10,15))
            interesting_cell.append(117); t_start.append(datetime(2015,6,12,11,5));  t_end.append(datetime(2015,6,12,11,5))
            interesting_cell.append(169); t_start.append(datetime(2015,6,12,11,5));  t_end.append(datetime(2015,6,12,11,20))
            interesting_cell.append(173); t_start.append(datetime(2015,6,12,11,5));  t_end.append(datetime(2015,6,12,12,15))
            interesting_cell.append(395); t_start.append(datetime(2015,6,12,12,45)); t_end.append(datetime(2015,6,12,12,40))
            interesting_cell.append(394); t_start.append(datetime(2015,6,12,12,45)); t_end.append(datetime(2015,6,12,12,25))
    
    #if False:
    #if True: 
            interesting_cell.append(4);   t_start.append(datetime(2015,8,7,11,35));  t_end.append(datetime(2015,8,7,13,0))
            interesting_cell.append(11);  t_start.append(datetime(2015,8,7,12,20));  t_end.append(datetime(2015,8,7,14,5))
            interesting_cell.append(58);  t_start.append(datetime(2015,8,7,13,35));  t_end.append(datetime(2015,8,7,16,10))
            interesting_cell.append(79);  t_start.append(datetime(2015,8,7,14,20));  t_end.append(datetime(2015,8,7,16,35))
            interesting_cell.append(107); t_start.append(datetime(2015,8,7,14,35));  t_end.append(datetime(2015,8,7,17,0))
            interesting_cell.append(118); t_start.append(datetime(2015,8,7,14,55));  t_end.append(datetime(2015,8,7,15,35))
            interesting_cell.append(167); t_start.append(datetime(2015,8,7,15,35));  t_end.append(datetime(2015,8,7,16,5))
            interesting_cell.append(236); t_start.append(datetime(2015,8,7,16,35));  t_end.append(datetime(2015,8,7,17,0))
            interesting_cell.append(251); t_start.append(datetime(2015,8,7,16,40));  t_end.append(datetime(2015,8,7,17,0))
    
    errors_area_False={}
    errors_COM_False = {}
    errors_108_False = {}
    errors_dx_False = {}
    errors_dy_False = {}
    length_history_False = {}
    
    errors_area_True={}
    errors_COM_True = {}
    errors_108_True = {}
    errors_dx_True = {}
    errors_dy_True = {}
    length_history_True = {}

    errors_area_follow_id={}
    errors_COM_follow_id = {}
    errors_108_follow_id = {}
    errors_dx_follow_id = {}
    errors_dy_follow_id = {}
    length_history_follow_id = {}
    
    ####LEL# for cell,t,t_end,t_stop in zip(interesting_cell,t_start,t_end,t_stop_history):
    for cell,t,t_end in zip(interesting_cell,t_start,t_end):
        str_cell = "ID"+str(cell)
        print(("begin validation for:", False))
        errors_area_False[str_cell],errors_COM_False[str_cell],errors_108_False[str_cell],errors_dx_False[str_cell], errors_dy_False[str_cell], length_history_False[str_cell] = validation_forecast(cell, t, t_end, in_msg, False)   ####LEL#(cell, t, t_end, t_stop, labels_dir)
        
        print(("begin validation for:", True))
        errors_area_True[str_cell],errors_COM_True[str_cell],errors_108_True[str_cell],errors_dx_True[str_cell], errors_dy_True[str_cell], length_history_True[str_cell] = validation_forecast(cell, t, t_end, in_msg, True)
        print(("begin validation for:", "follow_id"))
        errors_area_follow_id[str_cell],errors_COM_follow_id[str_cell],errors_108_follow_id[str_cell],errors_dx_follow_id[str_cell], errors_dy_follow_id[str_cell], length_history_follow_id[str_cell] = validation_forecast(cell, t, t_end, in_msg, "follow_id")
        
        if len(errors_area_False[str_cell])!=len(errors_area_True[str_cell]) or len(errors_area_False[str_cell])!=len(errors_area_follow_id[str_cell]):
            print("The number of timestep for the version with history correction and without it are different.")
            print("Quitting at line 585 of validation_forecasts.")
            quit()
    
        #make sure that the validation (in terms of number of points) are identical for the two versions. 
        #In fact it could be that according to one version the cell is forecasted to disappear (and the validation would be stopped) whereas it doesn't according to the other 
        for ind_correct_length in range(len(errors_area_True[str_cell])):
            errors_True = errors_area_True[str_cell][ind_correct_length]
            errors_False = errors_area_False[str_cell][ind_correct_length]
            errors_follow_id = errors_area_follow_id[str_cell][ind_correct_length]
            print(("checking if ", len(errors_True), "is the same as ", len(errors_False), " and ", len(errors_follow_id)))
            if len(errors_True)!=len(errors_False) or len(errors_True)!=len(errors_follow_id):
                #print ("all errors True: \n",errors_area[str_cell])
                #print ("all errors False: \n",errors_area_True[str_cell])
                print("WARNING: length of histories with and without correction are different!! Cutting the shorter")
                if verbose:
                    print("current errrors True: ", errors_True, "len: ", len(errors_True))
                    print("current errrors False: ", errors_False, "len: ", len(errors_False))
                    print("current errrors False: ", errors_follow_id, "len: ", len(errors_follow_id))
                    print("index", errors_area[str_cell].index(errors_True))
                    print("time", t+timedelta(minutes = 5*errors_area[str_cell].index(errors_True)))
                len_shorter = min(len(errors_True),len(errors_False),len(errors_follow_id))
                if verbose:
                    print("len shorter", len_shorter)
                    print("values: ", errors_area_False[str_cell][ind_correct_length][0:len_shorter])
                
                errors_area_False[str_cell][ind_correct_length] = errors_area_False[str_cell][ind_correct_length][0:len_shorter]
                errors_area_True[str_cell][ind_correct_length] = errors_area_True[str_cell][ind_correct_length][0:len_shorter]
                errors_COM_False[str_cell][ind_correct_length] = errors_COM_False[str_cell][ind_correct_length][0:len_shorter]
                errors_COM_True[str_cell][ind_correct_length] = errors_COM_True[str_cell][ind_correct_length][0:len_shorter]
                errors_108_False[str_cell][ind_correct_length] = errors_108_False[str_cell][ind_correct_length][0:len_shorter]
                errors_108_True[str_cell][ind_correct_length] = errors_108_True[str_cell][ind_correct_length][0:len_shorter]
                errors_dx_False[str_cell][ind_correct_length] = errors_dx_False[str_cell][ind_correct_length][0:len_shorter]
                errors_dx_True[str_cell][ind_correct_length] = errors_dx_True[str_cell][ind_correct_length][0:len_shorter]
                errors_dy_False[str_cell][ind_correct_length] = errors_dy_False[str_cell][ind_correct_length][0:len_shorter]
                errors_dy_True[str_cell][ind_correct_length] = errors_dy_True[str_cell][ind_correct_length][0:len_shorter]

                errors_area_follow_id[str_cell][ind_correct_length] = errors_area_follow_id[str_cell][ind_correct_length][0:len_shorter]
                errors_COM_follow_id[str_cell][ind_correct_length] = errors_COM_follow_id[str_cell][ind_correct_length][0:len_shorter]
                errors_108_follow_id[str_cell][ind_correct_length] = errors_108_follow_id[str_cell][ind_correct_length][0:len_shorter]
                errors_dx_follow_id[str_cell][ind_correct_length] = errors_dx_follow_id[str_cell][ind_correct_length][0:len_shorter]
                errors_dy_follow_id[str_cell][ind_correct_length] = errors_dy_follow_id[str_cell][ind_correct_length][0:len_shorter]
               
                #length_history_False[str_cell][ind_correct_length] = length_history_False[str_cell][ind_correct_length][0:len_shorter]
                #length_history_True[str_cell][ind_correct_length] = length_history_True[str_cell][ind_correct_length][0:len_shorter]

    
    #quit()
    str_cells = list(length_history_True.keys()) #could add a check to make sure the keys of _True and _False versions are the same
    
    #scatter plot of error on area (%), BT based on 10.8 (%) and position center for the forecast as a function of lead time. Colorscale dependent on length of history
    plot_scatter_errors = True
    plot_scatter_each_cell_separately = False #if set to true all chosen cells combined in one plot, if False one plot for each cell id
    
    plot_hist_AllLengthHistory = True
    plot_hist_ShortLongHistory = True
    
    plot_dx_dy_scatter = True
    plot_dx_dy_pdf = True
    
    plot_hexbin = True
    
    plot_boxplot_ShortLongHistory = True
    plot_boxplot_AllLengthHistoryHistory = True
    
    th_long_history = 30 # minutes of cell existence threshold between short and long history
    
    if plot_scatter_errors:
        print("plotting scatter errors")
        plot_Scatter(plot_scatter_each_cell_separately, str_cells, length_history_True, errors_area_True, errors_108_True, errors_COM_True, True)
        plot_Scatter(plot_scatter_each_cell_separately, str_cells, length_history_False, errors_area_False, errors_108_False, errors_COM_False, False)
        plot_Scatter(plot_scatter_each_cell_separately, str_cells, length_history_False, errors_area_False, errors_108_False, errors_COM_False, "follow_id")
             
    if plot_hist_AllLengthHistory == True or plot_hist_ShortLongHistory == True:
            print("plotting histograms")
            if plot_hist_AllLengthHistory:
                #with history correction
                plot_histogram(errors_area_True, length_history_True, str_cells, "area", None, None,True)
                plot_histogram(errors_COM_True, length_history_True, str_cells, "CenterOfMass", None, None,True)
                plot_histogram(errors_108_True, length_history_True, str_cells, "IR108", None, None,True)
                plot_histogram(errors_dx_True, length_history_True, str_cells, "dx", None, None,True)
                plot_histogram(errors_dy_True, length_history_True, str_cells, "dy", None, None,True)
                
                #without history correction  
                plot_histogram(errors_area_False, length_history_False, str_cells, "area", None, None,False)
                plot_histogram(errors_COM_False, length_history_False, str_cells, "CenterOfMass", None, None,False)
                plot_histogram(errors_108_False, length_history_False, str_cells, "IR108", None, None,False)
                plot_histogram(errors_dx_False, length_history_False, str_cells, "dx", None, None,False)
                plot_histogram(errors_dy_False, length_history_False, str_cells, "dy", None, None,False)

                #without history correction, following_id
                plot_histogram(errors_area_follow_id, length_history_follow_id, str_cells, "area", None, None,"follow_id")
                plot_histogram(errors_COM_follow_id, length_history_follow_id, str_cells, "CenterOfMass", None, None,"follow_id")
                plot_histogram(errors_108_follow_id, length_history_follow_id, str_cells, "IR108", None, None,"follow_id")
                plot_histogram(errors_dx_follow_id, length_history_follow_id, str_cells, "dx", None, None,"follow_id")
                plot_histogram(errors_dy_follow_id, length_history_follow_id, str_cells, "dy", None, None,"follow_id")                
            if plot_hist_ShortLongHistory:
                #with history correction
                plot_histogram(errors_area_True, length_history_True, str_cells, "area", th_long_history, True, True)
                plot_histogram(errors_COM_True, length_history_True, str_cells, "CenterOfMass", th_long_history, True, True)
                plot_histogram(errors_108_True, length_history_True, str_cells, "IR108", th_long_history, True, True)
                plot_histogram(errors_dx_True, length_history_True, str_cells, "dx", th_long_history, True, True)
                plot_histogram(errors_dy_True, length_history_True, str_cells, "dy", th_long_history, True, True)
                
                plot_histogram(errors_area_True, length_history_True, str_cells, "area", th_long_history, False, True)
                plot_histogram(errors_COM_True, length_history_True, str_cells, "CenterOfMass", th_long_history, False, True)
                plot_histogram(errors_108_True, length_history_True, str_cells, "IR108", th_long_history, False, True)
                plot_histogram(errors_dx_True, length_history_True, str_cells, "dx", th_long_history, False, True)
                plot_histogram(errors_dy_True, length_history_True, str_cells, "dy", th_long_history, False, True)                  
                
                #without history correction  
                plot_histogram(errors_area_False, length_history_False, str_cells, "area", th_long_history, True, False)
                plot_histogram(errors_COM_False, length_history_False, str_cells, "CenterOfMass", th_long_history, True, False)
                plot_histogram(errors_108_False, length_history_False, str_cells, "IR108", th_long_history, True, False)
                plot_histogram(errors_dx_False, length_history_False, str_cells, "dx", th_long_history, True, False)
                plot_histogram(errors_dy_False, length_history_False, str_cells, "dy", th_long_history, True, False)
                
                plot_histogram(errors_area_False, length_history_False, str_cells, "area", th_long_history, False, False)
                plot_histogram(errors_COM_False, length_history_False, str_cells, "CenterOfMass", th_long_history, False, False)
                plot_histogram(errors_108_False, length_history_False, str_cells, "IR108", th_long_history, False, False)
                plot_histogram(errors_dx_False, length_history_False, str_cells, "dx", th_long_history, False, False)
                plot_histogram(errors_dy_False, length_history_False, str_cells, "dy", th_long_history, False, False)  

                #without history correction, following id 
                plot_histogram(errors_area_follow_id, length_history_follow_id, str_cells, "area", th_long_history, True, "follow_id")
                plot_histogram(errors_COM_follow_id, length_history_follow_id, str_cells, "CenterOfMass", th_long_history, True, "follow_id")
                plot_histogram(errors_108_follow_id, length_history_follow_id, str_cells, "IR108", th_long_history, True, "follow_id")
                plot_histogram(errors_dx_follow_id, length_history_follow_id, str_cells, "dx", th_long_history, True, "follow_id")
                plot_histogram(errors_dy_follow_id, length_history_follow_id, str_cells, "dy", th_long_history, True, "follow_id")
                
                plot_histogram(errors_area_follow_id, length_history_follow_id, str_cells, "area", th_long_history, False, "follow_id")
                plot_histogram(errors_COM_follow_id, length_history_follow_id, str_cells, "CenterOfMass", th_long_history, False, "follow_id")
                plot_histogram(errors_108_follow_id, length_history_follow_id, str_cells, "IR108", th_long_history, False, "follow_id")
                plot_histogram(errors_dx_follow_id, length_history_follow_id, str_cells, "dx", th_long_history, False, "follow_id")
                plot_histogram(errors_dy_follow_id, length_history_follow_id, str_cells, "dy", th_long_history, False, "follow_id")                  
    if plot_hexbin:
        plot_hexagonal2dHist(str_cell, errors_area_True, errors_dx_True, errors_dy_True, True)
        plot_hexagonal2dHist(str_cell, errors_area_False, errors_dx_False, errors_dy_False, False)
        plot_hexagonal2dHist(str_cell, errors_area_follow_id, errors_dx_follow_id, errors_dy_follow_id, "follow_id")
    
    if plot_boxplot_ShortLongHistory:
        print("plotting boxplot 1/2")
        #with history correction  
        plot_boxplot(errors_area_True, length_history_True, str_cells, "area", th_long_history, True, True,graph_type = "boxplot") 
        plot_boxplot(errors_COM_True, length_history_True, str_cells, "CenterOfMass", th_long_history, True, True,graph_type = "boxplot")
        plot_boxplot(errors_108_True, length_history_True, str_cells, "IR108", th_long_history, True, True,graph_type = "boxplot")
        plot_boxplot(errors_dx_True, length_history_True, str_cells, "dx", th_long_history, True, True,graph_type = "boxplot")
        plot_boxplot(errors_dy_True, length_history_True, str_cells, "dy", th_long_history, True, True,graph_type = "boxplot")
        
        plot_boxplot(errors_area_True, length_history_True, str_cells, "area", th_long_history, False, True,graph_type = "boxplot")
        plot_boxplot(errors_COM_True, length_history_True, str_cells, "CenterOfMass", th_long_history, False, True,graph_type = "boxplot")
        plot_boxplot(errors_108_True, length_history_True, str_cells, "IR108", th_long_history, False, True,graph_type = "boxplot")
        plot_boxplot(errors_dx_True, length_history_True, str_cells, "dx", th_long_history, False, True,graph_type = "boxplot")
        plot_boxplot(errors_dy_True, length_history_True, str_cells, "dy", th_long_history, False, True,graph_type = "boxplot") 
        
        #without history correction  
        plot_boxplot(errors_area_False, length_history_False, str_cells, "area", th_long_history, True, False, graph_type = "boxplot") 
        plot_boxplot(errors_COM_False, length_history_False, str_cells, "CenterOfMass", th_long_history, True, False, graph_type = "boxplot")
        plot_boxplot(errors_108_False, length_history_False, str_cells, "IR108", th_long_history, True, False, graph_type = "boxplot")
        plot_boxplot(errors_dx_False, length_history_False, str_cells, "dx", th_long_history, True, False, graph_type = "boxplot")
        plot_boxplot(errors_dy_False, length_history_False, str_cells, "dy", th_long_history, True, False, graph_type = "boxplot")
        
        plot_boxplot(errors_area_False, length_history_False, str_cells, "area", th_long_history, False, False, graph_type = "boxplot")
        plot_boxplot(errors_COM_False, length_history_False, str_cells, "CenterOfMass", th_long_history, False, False, graph_type = "boxplot")
        plot_boxplot(errors_108_False, length_history_False, str_cells, "IR108", th_long_history, False, False, graph_type = "boxplot")
        plot_boxplot(errors_dx_False, length_history_False, str_cells, "dx", th_long_history, False, False, graph_type = "boxplot")
        plot_boxplot(errors_dy_False, length_history_False, str_cells, "dy", th_long_history, False, False, graph_type = "boxplot")    

        #without history correction, following_id 
        plot_boxplot(errors_area_follow_id, length_history_follow_id, str_cells, "area", th_long_history, True, "follow_id", graph_type = "boxplot") 
        plot_boxplot(errors_COM_follow_id, length_history_follow_id, str_cells, "CenterOfMass", th_long_history, True, "follow_id", graph_type = "boxplot")
        plot_boxplot(errors_108_follow_id, length_history_follow_id, str_cells, "IR108", th_long_history, True, "follow_id", graph_type = "boxplot")
        plot_boxplot(errors_dx_follow_id, length_history_follow_id, str_cells, "dx", th_long_history, True, "follow_id", graph_type = "boxplot")
        plot_boxplot(errors_dy_follow_id, length_history_follow_id, str_cells, "dy", th_long_history, True, "follow_id", graph_type = "boxplot")
        
        plot_boxplot(errors_area_follow_id, length_history_follow_id, str_cells, "area", th_long_history, False, "follow_id", graph_type = "boxplot")
        plot_boxplot(errors_COM_follow_id, length_history_follow_id, str_cells, "CenterOfMass", th_long_history, False, "follow_id", graph_type = "boxplot")
        plot_boxplot(errors_108_follow_id, length_history_follow_id, str_cells, "IR108", th_long_history, False, "follow_id", graph_type = "boxplot")
        plot_boxplot(errors_dx_follow_id, length_history_follow_id, str_cells, "dx", th_long_history, False, "follow_id", graph_type = "boxplot")
        plot_boxplot(errors_dy_follow_id, length_history_follow_id, str_cells, "dy", th_long_history, False, "follow_id", graph_type = "boxplot")   
        
    if plot_boxplot_AllLengthHistoryHistory:
        print("plotting boxplot 2/2")
        #with history correction
        plot_boxplot(errors_area_True, length_history_True, str_cells, "area", None, None, True)
        plot_boxplot(errors_COM_True, length_history_True, str_cells, "CenterOfMass", None, None, True)
        plot_boxplot(errors_108_True, length_history_True, str_cells, "IR108", None, None, True)
        plot_boxplot(errors_dx_True, length_history_True, str_cells, "dx", None, None, True)
        plot_boxplot(errors_dy_True, length_history_True, str_cells, "dy", None, None, True)   
        
        #without history correction  
        plot_boxplot(errors_area_False, length_history_False, str_cells, "area", None, None, False)
        plot_boxplot(errors_COM_False, length_history_False, str_cells, "CenterOfMass", None, None, False)
        plot_boxplot(errors_108_False, length_history_False, str_cells, "IR108", None, None, False)
        plot_boxplot(errors_dx_False, length_history_False, str_cells, "dx", None, None, False)
        plot_boxplot(errors_dy_False, length_history_False, str_cells, "dy", None, None, False)  

        #without history correction, following id
        plot_boxplot(errors_area_follow_id, length_history_follow_id, str_cells, "area", None, None, "follow_id")
        plot_boxplot(errors_COM_follow_id, length_history_follow_id, str_cells, "CenterOfMass", None, None, "follow_id")
        plot_boxplot(errors_108_follow_id, length_history_follow_id, str_cells, "IR108", None, None, "follow_id")
        plot_boxplot(errors_dx_follow_id, length_history_follow_id, str_cells, "dx", None, None, "follow_id")
        plot_boxplot(errors_dy_follow_id, length_history_follow_id, str_cells, "dy", None, None, "follow_id") 
    
    if plot_dx_dy_scatter:
        plot_dx_dy(str_cells, errors_dx_True, errors_dy_True, errors_area_True, length_history_True, True)
        plot_dx_dy(str_cells, errors_dx_False, errors_dy_False, errors_area_False, length_history_False, False)
        plot_dx_dy(str_cells, errors_dx_False, errors_dy_False, errors_area_False, length_history_False, "follow_id")
    
    if plot_dx_dy_pdf:      
        plot_pdf(str_cells,errors_area_True,errors_dx_True, errors_dy_True, length_history_True, True)
        plot_pdf(str_cells,errors_area_False,errors_dx_False, errors_dy_False, length_history_False, False)
        plot_pdf(str_cells,errors_area_False,errors_dx_False, errors_dy_False, length_history_False, "follow_id")
    
        
