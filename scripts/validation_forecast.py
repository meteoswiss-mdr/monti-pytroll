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

def validation_forecast(cell, t, t_end, t_stop_history, labels_dir):
    
    verbose = False
    model = "linear_exp_exp"
    all_errors_area = []
    all_errors_center = []
    all_errors_108 = []
    all_errors_dx = []
    all_errors_dy = []
    length_history = []
    
    while t <= t_end + timedelta(hours = 1):
    
        print "starting history backward"
        
        ind, area, displacement, time, center = history_backward(t.day,t.month,t.year,t.hour,t.minute,cell, True, t-timedelta(hours = 1),labels_dir = labels_dir)
        
        length_history.append(len(area)-1)
        
        names = ["WV_062 - IR_108", "WV_062 - WV_073", "IR_108", "WV_073 - IR_134", "WV_062 - IR_097",\
                 "IR_087 - IR_120", "IR_087 - 2IR_108plusIR_120", "IR_087 - IR_108",\
                 "IR_120 - IR_108", "IR_097 - IR_134", "WV_062 - IR_120", "CloudTopPressure", "CloudTopTemperature"]    
        history108 = []
        
        for i108 in range(ind.shape[0]):
            history108.append(ind[i108,2])
    
        if area == None or len(area)<=1:  
            print "The cell is outside of the area of interest or the history is not long enough (less than 1 timestep)"
        print "starting forecasts"    
        if len(area)<=3:
            t_forecast, y_forecast = future_properties(time, area, 'area', "linear")
            t_forecast, forecast108 = future_properties(time, history108, 'IR_108', "linear")
            
        else:
            t_forecast, y_forecast = future_properties(time, area, 'area', model)
            t_forecast, forecast108 = future_properties(time,history108,'IR_108',model)
        print "starting history forward, ", t     
        t_temp_stop = min ((t+timedelta(hours = 1)+timedelta(minutes = 5)), (t_stop_history+timedelta(minutes = 5)))    
        ind1, area1, displacement1, time1, center1 = history_backward(t.day,t.month,t.year,t.hour,t.minute,cell, False, t_temp_stop,labels_dir = labels_dir)
        print "history forward Done"        
        t2 = time1 #[::-1]
        y2 = area1 #[::-1]
        ir108_2 = []
        
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
                try:
                    dx =  int(round(displacement[:-1,0].mean())) #exclude last line because it's always 0,0 (new cell has no displacement)
                    dy = int(round(displacement[:-1,1].mean())) #exclude last line because it's always 0,0 (new cell has no displacement)
                    
                except ValueError:
                    print("VALUE ERROR")
                    print(displacement)
                    quit()
            print dx, dy
    
        else:
            print("wrong displacement")
            quit()
    
        index_stop = 12
    
    
        for i in range(12):
    
          dt += 5
          if verbose:
              print("... for time ", dt ,", index ", indx + i)
          if indx+i >= len(y_forecast):
              index_stop = deepcopy(i)
              break
          else:    
              area_new = y_forecast[indx+i]
              area_prev = y_forecast[indx+i-1]
          if verbose:
              print("area px that will be grown ", area_current)
      
              print("area forecasted ", area_new)
      
              print("area forecasted prev ", area_prev)
          #growth = sqrt(float(area_new)/float(area_current))
      
          if area_new < 0 or len(area_new)==0 or len(area_prev)==0:
              if verbose:
                  print("the cell is predicted to disappear")
              index_stop = deepcopy(i)
              break
      
          growth = sqrt(float(area_new)/float(area_prev))
          if verbose:
              print("growing by ", growth)
              print("dx ", dx)
              print("dy ", dy)
      
          #figure_labels(label_cell, outputFile, ttt, dt, area_plot="ccs4", add_name = "before")
      
          shifted_label = resize_array(label_cell,dx,dy, nx, ny)
      
          #figure_labels(shifted_label, outputFile, ttt, dt, area_plot="ccs4", add_name = "before_shifted")
          #quit()
          if verbose:
              print("   after shift ", sum(sum(shifted_label)))
      
          if sum(sum(shifted_label))==0:#the cell is outside the domain
              break
      
          #center of mass before resizing
          center_before = ndimage.measurements.center_of_mass(shifted_label)
          center_before = np.rint(center_before)    
          
          forecasted_center.append(center_before)
              
          if verbose:
              print("   after shift ", sum(sum(shifted_label)))
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
              print(np.unique(temp_label))
              print("   after resize ", sum(sum(temp_label)))
          #figure_labels(resized_label, outputFile, ttt, dt, area_plot="ccs4", add_name = "before_shifted_resized")
      
          #center of mass after resizing
          center_after = ndimage.measurements.center_of_mass(temp_label)
          center_after = np.rint(center_after)         
      
          dx_new,dy_new = center_before - center_after
      
          shifted_label = resize_array(temp_label,dx_new,dy_new, nx, ny)
          if verbose:
              print("   after shift2 ", sum(sum(shifted_label)))
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
              print("end ", area_current)
          forecasted_areas.append(area_current)
          #add check to make sure the area you produced is more or less correct
          if verbose:
              print(len(area1))
              print("indx1, i:",indx1,i)
          if indx1+i < len(area1): #if in reality the cell disappeared... not very nice that you just "kill" entire thing, but else what is distance centers??
              error_area.append((float((-area1[indx1+i] + area_current))/area1[indx1+i])*100)
              distance_centers = sqrt( (-center1[indx1+i][0]+center_before[0])*(-center1[indx1+i][0]+center_before[0]) + (-center1[indx1+i][1]+center_before[1])*(-center1[indx1+i][1]+center_before[1]) )
              center_dx = -center1[indx1+i][0]+center_before[0]
              center_dy = -center1[indx1+i][1]+center_before[1]
              error_center.append(distance_centers)
              error_dx.append(center_dx)
              error_dy.append(center_dy)
              error_108.append((float(-ir108_2[indx1+i] + forecast108[indx+i])/ir108_2[indx1+i])*100)    

         
        all_errors_area.append(error_area)
        all_errors_center.append(error_center)
        all_errors_108.append(error_108) 
        all_errors_dx.append(error_dx)
        all_errors_dy.append(error_dy)
        t += timedelta(minutes = 5)
        print "updating index"
    print "returning values"
    return all_errors_area,all_errors_center,all_errors_108,all_errors_dx, all_errors_dy, length_history

def plot_histogram(errors, str_cells, variable, th_history, longer_than_th):
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
        time_plot = all_errors.keys() 
        time_plot = map(int,time_plot)
        time_plot.sort()  
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
        #tmp_hist_values = hist_values[1:]
        blues = plt.get_cmap('Blues')
        cNorm = mpl.colors.Normalize(vmin = 0, vmax = max([item for sublist in hist_values[1:] for item in sublist]))
        scalarMap = mpl.cm.ScalarMappable(norm=cNorm, cmap = blues)      
        
        
        import matplotlib.patches as patches
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim(0,max(time_plot)+10)
        ax.set_ylim(axis_min, axis_max)
        ax.set_xlabel("Lead Time [min]")
        
        for i in range(len(time_plot)):
            #print hist_values
            #print "i", i
            #print len(hist_values)
            #print "values", hist_values[i]
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
        
        fig.savefig("validation/"+name_out+'%s_LeadTime.png'%variable, dpi=90, bbox_inches='tight')
        plt.close(fig)
        
    
    
if __name__ == "__main__":
    labels_dir = '/opt/users/lel/PyTroll/scripts/labels/'

    interesting_cell = []
    t_start = []
    t_end = []
    t_stop_history = []
    
    #cells to be included: respectively id_number, time start and end at which compute history and forecast every 5 min; time at which to stop (forecast and validation won't go further than that)
    interesting_cell.append(54);  t_start.append(datetime(2015,7,7,11,55)); t_end.append(datetime(2015,7,7,11,50)); t_stop_history.append(datetime(2015,7,7,13,0))
    interesting_cell.append(69);  t_start.append(datetime(2015,7,7,12,5)) ; t_end.append(datetime(2015,7,7,11,50)); t_stop_history.append(datetime(2015,7,7,13,0))
    interesting_cell.append(175); t_start.append(datetime(2015,7,7,13,45)); t_end.append(datetime(2015,7,7,12,50)); t_stop_history.append(datetime(2015,7,7,14,0))#t_end.append(datetime(2015,7,7,13,55))
    interesting_cell.append(147); t_start.append(datetime(2015,7,7,13,15)); t_end.append(datetime(2015,7,7,12,50)); t_stop_history.append(datetime(2015,7,7,14,0))#t_end.append(datetime(2015,7,7,15,35))
    interesting_cell.append(240); t_start.append(datetime(2015,7,7,15,10)); t_end.append(datetime(2015,7,7,15,0));  t_stop_history.append(datetime(2015,7,7,16,0))#t_start.append(datetime(2015,7,7,14,30)) t_end.append(datetime(2015,7,7,15,15))
    
    errors_area={}
    errors_COM = {}
    errors_108 = {}
    errors_dx = {}
    errors_dy = {}
    length_history = {}

    for cell,t,t_end,t_stop in zip(interesting_cell,t_start,t_end,t_stop_history):
        str_cell = "ID"+str(cell)
        errors_area[str_cell],errors_COM[str_cell],errors_108[str_cell],errors_dx[str_cell], errors_dy[str_cell], length_history[str_cell] = validation_forecast(cell, t, t_end, t_stop, labels_dir)
    x_axis = [0,5,10,15,20,25,30,35,40,45,50,55,60]
    str_cells = length_history.keys()
    
    #scatter plot of error on area (%), BT based on 10.8 (%) and position center for the forecast as a function of lead time. Colorscale dependent on length of history
    plot_scatter_errors = True 
    plot_scatter_errors_all = True #if set to true all chosen cells combined in one plot, if False one plot for each cell id
    
    plot_hist_AllLengthHistory = True
    plot_hist_ShortLongHistory = True
    
    plot_dx_dy = True
    
    plot_hexbin = True
    
    th_long_history = 30 # minutes of cell existence threshold between short and long history
                  
    #th_long_history += 5 # correction because at index 0 there is the starting point, observation = forecast, so actual length of history is 5 min less (example if length_history = 2 the cell existed for (2-1)*5 = 5 min)    
    
    if plot_scatter_errors:
        
        if plot_scatter_errors_all:
            vmax = 60 #max(max(length_history.values()))*5
            blues = plt.get_cmap('Blues')
            cNorm = mpl.colors.Normalize(vmin = 0, vmax = vmax)
            scalarMap0 = mpl.cm.ScalarMappable(norm=cNorm, cmap = blues)
            f, axarr = plt.subplots(3, sharex=True)
                  
            for id_cells in str_cells:
                  for i in range(len(length_history[id_cells])):
                    colorVal = scalarMap0.to_rgba(length_history[id_cells][i]*5)
                    color_current = [colorVal]*len(errors_area[id_cells][i])
                    axarr[0].scatter(x_axis[0:len(errors_area[id_cells][i])], errors_area[id_cells][i], color = color_current,marker='o')
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
            f.savefig("validation/ScatterErrors.png")          
        
        else:
          for id_cells in str_cells:
              vmax = 60 #max(max(length_history.values()))*5
              blues = plt.get_cmap('Blues')
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
              axarr[1].set_ylabel('Er IR10.8 [%]')

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
              f.savefig("validation/%s_ScatterErrors.png"%id_cells)  
                      
    if plot_hist_AllLengthHistory == True or plot_hist_ShortLongHistory == True:
            
            if plot_hist_AllLengthHistory:
                plot_histogram(errors_area, str_cells, "area", None, None)
                plot_histogram(errors_COM, str_cells, "CenterOfMass", None, None)
                plot_histogram(errors_108, str_cells, "IR108", None, None)
                plot_histogram(errors_dx, str_cells, "dx", None, None)
                plot_histogram(errors_dy, str_cells, "dy", None, None)
            if plot_hist_ShortLongHistory:
                plot_histogram(errors_area, str_cells, "area", th_long_history, True)
                plot_histogram(errors_COM, str_cells, "CenterOfMass", th_long_history, True)
                plot_histogram(errors_108, str_cells, "IR108", th_long_history, True)
                plot_histogram(errors_dx, str_cells, "dx", th_long_history, True)
                plot_histogram(errors_dy, str_cells, "dy", th_long_history, True)
                
                plot_histogram(errors_area, str_cells, "area", th_long_history, False)
                plot_histogram(errors_COM, str_cells, "CenterOfMass", th_long_history, False)
                plot_histogram(errors_108, str_cells, "IR108", th_long_history, False)
                plot_histogram(errors_dx, str_cells, "dx", th_long_history, False)
                plot_histogram(errors_dy, str_cells, "dy", th_long_history, False)                  
                  
    if plot_dx_dy:
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
          #print "short history"
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
          #print "long history"                
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
          f.savefig('validation/Validation_dx_dy.png')
          plt.close(f)
          
    if plot_hexbin:
        all_dx = []
        all_dy = []
        for ind in range(1,len(x_axis)):
            for id_cell in str_cells:
                  for ind_each_cell in range(len(errors_dx[id_cell])):
                      if len(errors_area[id_cell][ind_each_cell])>ind :
                          all_dx.append(errors_dx[id_cell][ind_each_cell][ind]*(-1))   
                          all_dy.append(errors_dy[id_cell][ind_each_cell][ind]) 
        fig = plt.figure()
        plt.hexbin(all_dy,all_dx)
        fig.savefig("validation/test_hexbin.png")
                  
                
                
        
