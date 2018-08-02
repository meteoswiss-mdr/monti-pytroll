from datetime import datetime, timedelta
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from mpop.imageo.TRTimage import fig2img    
from mpop.imageo.HRWimage import prepare_figure
import history_backward
from history_backward import history_backward, string_date, Cells
from properties_cells import create_dir
from future_properties import future_properties
import scipy
from math import sqrt
from scipy import ndimage
from mpop.projector import get_area_def
import shelve
from copy import deepcopy
import numpy as np
import cPickle as pickle
from skimage.transform import resize
import scipy.misc as sm
import matplotlib.dates as mdates
import subprocess
import glob
#from Cells import Cells
import cProfile
import pstats
import time
from time import strftime
from matplotlib import colors, cm
from PIL import Image
from my_msg_module import format_name

#these were giving conflicts.Required for the part added (ir108 background if no background image available)
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from plot_msg import load_products
import pylab
import getpass

from my_msg_module import format_name
from postprocessing import postprocessing


def resize_array(array, dx, dy, nx, ny):

    temp_array=np.zeros_like(array)
    array_out = np.zeros_like(array)
    
    if dx>0:
        temp_array[dx:,:]  = deepcopy(array[0:-dx,:])
    elif dx < 0:
        temp_array[0:dx,:] = deepcopy(array[-dx:,:])
    else:
        temp_array[:,:]    = deepcopy(array[:,:])
    
    if dy>0:
        array_out[:,dy:]  = temp_array[:,0:-dy]
    elif dy < 0:
        array_out[:,0:dy] = temp_array[:,-dy:]
    else:
        array_out[:,:]    = temp_array[:,:]  

    return array_out

def figure_labels(labels, outputFile, timeObs, dt, area_plot="ccs4", add_name = None, verbose=True):

    if verbose:
        print("*** produce label figures")

    yearS, monthS, dayS, hourS, minS = string_date(timeObs)
    data_time = timeObs + timedelta(minutes = dt)
    yearSf, monthSf, daySf, hourSf, minSf = string_date(data_time)
    
    labels = np.flipud(labels)
    
    obj_area = get_area_def(area_plot)
    fig, ax = prepare_figure(obj_area) 
    plt.contour(labels,[0.5],colors='y')
    #plt.imshow(labels, origin="lower")
    PIL_image = fig2img ( fig )
    if add_name is not None:
          PIL_image.save(create_dir(outputFile)+"Forecast"+yearS+monthS+dayS+"_Obs"+hourS+minS+"_Forc"+hourSf+minSf+add_name+".png")
          path = (outputFile)+"Forecast"+yearS+monthS+dayS+"_Obs"+hourS+minS+"_Forc"+hourSf+minSf+add_name+".png"
    else:
          PIL_image.save(create_dir(outputFile)+"Forecast"+yearS+monthS+dayS+"_Obs"+hourS+minS+"_Forc"+hourSf+minSf+".png")
          path = (outputFile)+"Forecast"+yearS+monthS+dayS+"_Obs"+hourS+minS+"_Forc"+hourSf+minSf+".png"
    print "... display ",path," &"
    plt.close( fig)    
#savefig('demo.png', transparent=True)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------

#if __name__ == '__main__':
def plot_forecast_area(ttt, model, outputDir, current_labels = None, t_stop=None, BackgroundFile=None, ForeGroundRGBFile=None, labels_dir = '/opt/users/'+getpass.getuser()+'/PyTroll/scripts/labels/', in_msg = None):
    verbose = True
    if t_stop is None:
        t_stop = ttt
    
    ylabel = "area"

    while ttt <= t_stop:
        yearS, monthS, dayS, hourS, minS = string_date(ttt)
        if verbose:
            print("******** read cell properties from shelve")
        
        if current_labels is None:
              yearS, monthS, dayS, hourS, minS = string_date(ttt)
              filename = 'Labels_%s.shelve'%(yearS+monthS+dayS+hourS+minS)
              myShelve = shelve.open(filename)
              labels_all = deepcopy(myShelve['labels'])
        else:
              labels_all = deepcopy(current_labels)
        if verbose:
            print(labels_all)
        
        unique_labels = np.unique(labels_all[labels_all>0])
        if verbose:
            print("... cells with unique labels: ", unique_labels)
                
        forecasted_labels = {}
        forecasted_areas = []    
        at_least_one_cell = False        

        if verbose:
            print "*** computing history backward (", labels_dir, ")"

        for interesting_cell in unique_labels:

              forecasted_labels["ID"+str(interesting_cell)]=[]
              
              # calculate backward history for 1 hour and save it in labels_dir
              ind, area, displacement, time, center = history_backward(ttt,  interesting_cell, True, in_msg, ttt-timedelta(hours = 1), labels_dir=labels_dir) #-timedelta(minutes = 10))
              #                                                        current time, cell_id, backward?   time_stop
              if area is None or len(area)<=1:  
                  if verbose:
                        print "new cell or cell with COM outside domain"
                  continue
              at_least_one_cell = True 
                 
              if len(area)<=3:
                    # if history is too short, use linear extrapolation
                    t, y = future_properties(time, area, ylabel, "linear")
              else:
                    t, y = future_properties(time, area, ylabel, model)
              
              if False:
                    ind1, area1, displacement1, time1, center = history_backward(ttt, interesting_cell, False, ttt+timedelta(hours=1), labels_dir=labels_dir)
                    print "******** computed history forward"
            
                    t2 = time1 #[::-1]
                    y2 = area1 #[::-1]
            
            
              nx,ny = labels_all.shape
              #if verbose:
              #    print(nx,ny)
      
              label_cell = np.zeros(labels_all.shape)
              label_cell[labels_all==interesting_cell] = 1
              #pickle.dump(label_cell, open("test_label.p", "wb" ) )
              #quit()
              dt = 0
              if False:
                  figure_labels(label_cell, outputDir, ttt, dt, area_plot="ccs4", add_name = "_ID"+str(interesting_cell), verbose=verbose)
      
              area_current = sum(sum(label_cell))
      
              forecasted_areas.append(area_current)
      
              indx = np.where(t==ttt)[0] + 1
      
              if verbose:
                    print "*** compute displacement "

              if displacement.shape[1]==2:
                    if len(displacement) == 0:
                        dx = 0
                        dy = 0
                    else:
                        try:
                            dx = int(round(displacement[:,0].mean()))
                            dy = int(round(displacement[:,1].mean()))
                        except ValueError:
                            print("VALUE ERROR")
                            print(displacement)
                            quit()
                    print "    computed displacement dx, dy = ", dx, dy
      
              else:
                    print("wrong displacement")
                    quit()
      
              labels_in_time={}
              
              index_stop = 12
              
              
              print("*** calculate forecasts for cell ID"+str(interesting_cell))
              if verbose:
                  print("index   time    area  growth")
                  print("----------------------------")

              for i in range(13):
                  
                  dt += 5
                  #if verbose:
                  #    print("... for time ", dt ,", index ", indx + i)

                  if indx+i >= len(y):
                      index_stop = deepcopy(i)
                      break
                  else:    
                      area_new  = y[indx+i]
                      area_prev = y[indx+i-1]

                  #if verbose:
                  #    print("area px that will be grown ", area_current)
                  #    print("area forecasted ", area_new)
                  #    print("area forecasted prev ", area_prev)

                  ###growth = sqrt(float(area_new)/float(area_current))
                  
                  if area_new < 0 or len(area_new)==0 or len(area_prev)==0:
                      if verbose:
                          print("the cell is predicted to disappear")
                      index_stop = deepcopy(i)
                      break
                  
                  growth = sqrt(float(area_new)/float(area_prev))
                  #if verbose:
                  #    print("growing by ", growth)
                  #    print("dx ", dx)
                  #    print("dy ", dy)

                  if verbose:
                      print(indx + i, dt, area_new, growth) 

                  #figure_labels(label_cell, outputDir, ttt, dt, area_plot="ccs4", add_name = "before")

                  shifted_label = resize_array(label_cell, dx, dy, nx, ny)

                  #figure_labels(shifted_label, outputDir, ttt, dt, area_plot="ccs4", add_name = "before_shifted")
                  #quit()
                  if verbose:
                      print("   after shift ", sum(sum(shifted_label)))
                  
                  if sum(sum(shifted_label))==0: #the cell is outside the domain
                      break
                  
                  #center of mass before resizing
                  center_before = ndimage.measurements.center_of_mass(shifted_label)
                  center_before = np.rint(center_before)        
                  #if verbose:
                  #    print("   after shift ", sum(sum(shifted_label)))

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
                  
                  #if verbose:
                  #    print(np.unique(temp_label))
                  #    print("   after resize ", sum(sum(temp_label)))

                  #figure_labels(resized_label, outputDir, ttt, dt, area_plot="ccs4", add_name = "before_shifted_resized")
      
                  #center of mass after resizing
                  center_after = ndimage.measurements.center_of_mass(temp_label)
                  center_after = np.rint(center_after)         
      
                  dx_new,dy_new = center_before - center_after
      
                  shifted_label = resize_array(temp_label,dx_new,dy_new, nx, ny)
                  #if verbose:
                  #    print("   after shift2 ", sum(sum(shifted_label)))
                  label_cell = np.zeros((nx,ny))

                  label_cell[0:,0:] = shifted_label[0:nx,0:ny]
      
                  if label_cell.shape[0] != nx or label_cell.shape[1] != ny:
                        print("incorrect size")
                        quit()
                  
                  forecasted_labels["ID"+str(interesting_cell)].append(deepcopy(label_cell))
                  
                  
                  #indx+=1
      
                  label_cell = shifted_label #????????????????????????????????????
      
                  area_current = sum(sum(label_cell))
                  if verbose:
                      print("end ", area_current)
                  forecasted_areas.append(area_current)
                  #add check to make sure the area you produced is more or less correct
      
      
              t_temp = deepcopy(ttt)
              forecasted_time = []
      
              for gg in range(len(forecasted_areas)):
                  forecasted_time.append(t_temp)
                  t_temp+=timedelta(minutes = 5)
      
              """
              if verbose:
                print("******** produce images")

              if False:
                  t_composite = deepcopy(ttt)
                  for i in range(min(len(y),index_stop)):
          
                      yearSf, monthSf, daySf, hourSf, minSf = string_date(t_composite)
                      contour_file = outputDir + "Forecast"+yearS+monthS+dayS+"_Obs"+hourS+minS+"_Forc"+hourSf+minSf+"_ID"+str(interesting_cell)+".png"    
                      type_image = "_HRV"
                      #background_file = "/data/COALITION2/PicturesSatellite//"+yearS+"-"+monthS+"-"+dayS+"/"+yearS+"-"+monthS+"-"+dayS+type_image+"_"+"ccs4"+"/MSG"+type_image+"-"+"ccs4"+"_"+yearS[2:]+monthS+dayS+hourS+minS+".png"
                      background_file = "/data/COALITION2/PicturesSatellite/LEL_results_wind/"+yearS+"-"+monthS+"-"+dayS+"/RGB-HRV_dam/"+yearS+monthS+dayS+"_"+hourS+minS+"*.png"            
                      out_file1 = create_dir( outputDir+"/Contours/")+"Obs"+hourS+minS+"_Forc"+hourSf+minSf+"_ID"+str(interesting_cell)+".png"
                      if verbose:
                          print("... create composite "+contour_file+" "+background_file+" "+out_file1)
                      #subprocess.call("/usr/bin/composite "+contour_file+" "+background_file+" "+out_file1, shell=True)
                      if verbose:
                          print("... saved composite: display ", out_file1, " &")
                      t_composite+=timedelta(minutes=5)
              """
              """
              if False:
                  fig, ax = plt.subplots()
                  ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                  ax.plot_date(t, y, 'o',label="Fit and extrapolation")
                  ax.plot_date(forecasted_time, forecasted_areas, '*',label="forecasted")
                  ax.plot_date(t2, y2, '*', label="Observations")
                  #ax.set_xlim([t[0]-timedelta(minutes = 5), t2[-1]+timedelta(minutes = 5)])
                  ax.set_ylabel("area")
                  ax.legend(loc="best");
                  fig.savefig(yearS+monthS+dayS+"_"+hourS+minS+"_AreaInTime"+"ID"+str(interesting_cell)+".png")
                  plt.close( fig)    
              """      

        t_composite = deepcopy(ttt)
        
        # merge coalition2 file with 
        if ForeGroundRGBFile is None:
            currentRGB_im_filename = "/opt/users/"+getpass.getuser()+"/PyTroll/scripts/Mecikalski/cosmo/Channels/indicators_in_time/RGB_dam/"+yearS+monthS+dayS+"_"+hourS+minS+"*ccs4.png"
        else:
            currentRGB_im_filename = ForeGroundRGBFile
        
        currentRGB_im = glob.glob(currentRGB_im_filename)
        if len(currentRGB_im)<1:  
            print "No file found:", currentRGB_im_filename

        # get background file 
        if BackgroundFile is None:
            background_im_filename = '/data/COALITION2/PicturesSatellite/LEL_results_wind/'+yearS+'-'+monthS+'-'+dayS+'/RGB-HRV_dam/'+yearS+monthS+dayS+'_'+hourS+minS+'*.png'
        else:
            background_im_filename = BackgroundFile
        background_im = glob.glob(background_im_filename)

        if len(background_im)>0:
            im = plt.imread(background_im[0])
            back_exists = True
        else:
            back_exists = False
        #img1 = Image.imread(currentRGB_im[0])

        obj_area = get_area_def("ccs4")
        fig,ax = prepare_figure(obj_area)
        if in_msg.nrt == False:
              if back_exists:
                  plt.imshow(np.flipud(im))   
              else:
                  # now read the data we would like to forecast
                  global_data = GeostationaryFactory.create_scene(in_msg.sat_str(), in_msg.sat_nr_str(), "seviri", ttt)
                  #global_data_RGBforecast = GeostationaryFactory.create_scene(in_msg.sat, str(10), "seviri", time_slot)
      
                  # area we would like to read
                  area2load = "EuropeCanary95" #"ccs4" #c2"#"ccs4" #in_windshift.ObjArea
                  area_loaded = get_area_def(area2load )#(in_windshift.areaExtraction)  
  
                  # load product, global_data is changed in this step!
                  area_loaded = load_products(global_data, ['IR_108'], in_msg, area_loaded ) 
                  data = global_data.project("ccs4")                  
                  plt.imshow(np.flipud(data['IR_108'].data),cmap = pylab.gray())
        
        # background file form function argument or default
        if BackgroundFile is None:
            background_im_filename = '/data/COALITION2/PicturesSatellite/LEL_results_wind/'+yearS+'-'+monthS+'-'+dayS+'/RGB-HRV_dam/'+yearS+monthS+dayS+'_'+hourS+minS+'*.png'
        else:
            if verbose:
                print "... BackgroundFile ", BackgroundFile
            background_im_filename = BackgroundFile
            
        # searching background file (wildcards are possible)
        background_im = glob.glob(background_im_filename)
        if len(background_im) == 0:
            print "*** Error in plot_forecast_area (test_forecast.py)"
            print "    no background file found: ", background_im_filename
            quit()
        elif len(background_im) > 1:
            print "*** Warning in plot_forecast_area (test_forecast.py)"
            print "    several background files found: ", background_im

        # read background file
        im = plt.imread(background_im[0])
        
        #img1 = Image.imread(currentRGB_im[0])
        obj_area = get_area_def("ccs4")
        fig,ax = prepare_figure(obj_area)
        #plt.imshow(np.flipud(im))   

        # plot contour lines for all cells

        if at_least_one_cell:      
              time_wanted_minutes = [5,20,40,60] 
              time_wanted = []
              color_wanted = []
              vmax = 70
              
              for t_want in time_wanted_minutes:
                  time_wanted.append((t_want-5)/5)
                  tmp = (mpl.cm.Blues(float(t_want)/vmax))
                  tmp1 = [tmp]
                  color_wanted.append(tmp1)
              
              all_labels_in_time = np.zeros((nx,ny))
              
              for i in range(len(time_wanted)-1,-1,-1):
                  ind_time = time_wanted [i]
                  
                  for key, forc_labels in forecasted_labels.iteritems():  #forecasted_labels["ID"+str(interesting_cell)]=[]  
                      
                      if len(forc_labels)>ind_time:
                          #plt.contour(np.flipud(forc_labels[ind_time]),[0.5],colors = color_wanted_cont[i]) #colors='w') #
                          
                          all_labels_in_time[forc_labels[ind_time]>0] = time_wanted_minutes[i]                     
              
              forc_labels_tmp = np.ma.masked_where(all_labels_in_time==0,all_labels_in_time)
              plt.contourf(np.flipud(forc_labels_tmp), cmap="Blues", vmin=0, vmax=vmax)    
              
              
              if False:    
                    for i in range(len(time_wanted)):
                        
                        ind_time = time_wanted [i]
                        
                        for key, forc_labels in forecasted_labels.iteritems():  #forecasted_labels["ID"+str(interesting_cell)]=[]  
                            
                            if len(forc_labels)>ind_time:
                                plt.contour(np.flipud(forc_labels[ind_time]),[0.5],colors = color_wanted[i]) #colors='w') #
        else:
            print "*** Warning, no COALITION2 cell detected "
            print "    produce empty figure ..."
        
        
        PIL_image = fig2img ( fig )
        
        standardOutputName = in_msg.standardOutputName.replace('%y%m%d%H%M',strftime('%y%m%d%H%M',ttt.timetuple()))
        
        #PIL_image.paste(img1, (0, 0), img1)
        if in_msg is None:
            PIL_image.save(create_dir(outputDir)+"Forecast"+yearS+monthS+dayS+"_Obs"+hourS+minS+".png")
            path = (outputDir)+yearS+monthS+dayS+hourS+minS+"Forecast.png"
        else:

            # dic_figure={}
            # if in_msg.nrt == True:
            #     dic_figure['rgb']= 'Forecast' #'C2rgbForecastTMP-IR-108'
            # else:
            #     dic_figure['rgb']= 'Forecast-C2rgb'
            # dic_figure['area']='ccs4'
            # PIL_image.save(create_dir(outputFile)+standardOutputName%dic_figure)
            # path = (outputFile)+standardOutputName%dic_figure
            # if in_msg.nrt == False:
            #     dic_figure={}
            #     dic_figure['rgb']= 'C2rgb-Forecast-HRV' #'C2rgbForecastTMP-IR-108'
            #     dic_figure['area']='ccs4'
            #     path_output = (outputFile)+standardOutputName%dic_figure
            #     print "creating composite: ",currentRGB_im[0],"+",path
        #        subprocess.call("/usr/bin/composite "+currentRGB_im[0]+" "+path+" "+path_output, shell=True)
        
        #print "... display ",path_output," &"

            #dic_figure={}
            #dic_figure['rgb']= 'Forecast' #'C2rgbForecastTMP-IR-108'
            #dic_figure['area']='ccs4'
            outputFile = format_name(create_dir(outputDir)+in_msg.outputFile, ttt, rgb='Forecast', area='ccs4', sat_nr=int(in_msg.sat_nr))
            #PIL_image.save(create_dir(outputDir)+in_msg.outputFile%dic_figure)
            PIL_image.save(outputFile)
            #path = (outputDir)+in_msg.outputFile%dic_figure
            path = outputFile

        print "... display ",path," &"

        plt.close( fig)                             
        if True:
            if verbose:
                print "path foreground", currentRGB_im[0]
            
            if in_msg is None:
                path_composite = (outputFile)+yearS+monthS+dayS+"_Obs"+hourS+minS+"Forecast_composite.png"     
            else:
                # dic_figure={}
                # dic_figure['rgb']='C2rgb-Forecast-HRV'
                # dic_figure['area']='ccs4'
                # path_composite = (outputFile)+standardOutputName%dic_figure
                #dic_figure = {}
                #dic_figure['rgb'] = "_HRV" #'IR-108'
                #dic_figure['area']='ccs4'
                #path_IR108 = (outputFile)+standardOutputName%dic_figure

                #dic_figure={}
                #dic_figure['rgb'] = 'C2rgbForecast-IR-108'
                #dic_figure['area'] = 'ccs4'
                #path_composite = (outputDir) + in_msg.outputFile%dic_figure
                path_composite = format_name( outputDir+in_msg.outputFile, ttt, rgb='C2rgbForecast-IR-108', area='ccs4', sat_nr=int(in_msg.sat_nr))
                #dic_figure = {}
                #dic_figure['rgb'] = 'IR-108'
                #dic_figure['area']='ccs4'
                #path_IR108 = (outputDir) + in_msg.outputFile%dic_figure
                path_IR108 = format_name( outputDir+in_msg.outputFile, ttt, rgb='IR-108', area='ccs4', sat_nr=int(in_msg.sat_nr))

                
            if in_msg.nrt == True:
                if verbose:
                    print "---starting post processing"
                #if area in in_msg.postprocessing_areas:
                in_msg.postprocessing_composite = deepcopy(in_msg.postprocessing_composite2)

                postprocessing(in_msg, ttt, in_msg.sat_nr, "ccs4")
            #print "... display",path_composite,"&"
            if in_msg.scpOutput and in_msg.nrt == True and False: #not necessary because already done within postprocessing
                print "... secure copy "+path_composite+ " to "+in_msg.scpOutputDir #
                subprocess.call("scp "+in_msg.scpID+" "+path_composite  +" "+in_msg.scpOutputDir+" 2>&1 &", shell=True)    #BackgroundFile   #
        
        if False:
            for i in range(12):    
                  contour_files = glob.glob(outputDir + "Forecast"+yearS+monthS+dayS+"_Obs"+hourS+minS+"_Forc"+hourSf+minSf+"_ID*.png")
                  if verbose:
                            print("Files found: ",contour_files)
                  if len(contour_files)>0:
                      background_file = "/data/COALITION2/PicturesSatellite/LEL_results_wind/"+yearS+"-"+monthS+"-"+dayS+"/RGB-HRV_dam/"+yearS+monthS+dayS+"_"+hourS+minS+"*.png"
                      out_file1 = create_dir( outputDir+"/Contours/")+"Obs"+hourS+minS+"_Forc"+hourSf+minSf+".png"
                  t_composite+=timedelta(minutes=5)  
  
        ttt += timedelta(minutes = 5)
"""
norm = cm.colors.Normalize(vmax=abs(Z).max(), vmin=-abs(Z).max())
cmap = cm.PRGn

plt.figure()


plt.subplot(2, 2, 1)

cset1 = plt.contourf(X, Y, Z, levels,
                 cmap=cm.get_cmap(cmap, len(levels) - 1),
                 norm=norm,
                 )
        c(norm(15.0))
""" 
"""
    yearS, monthS, dayS, hourS, minS = string_date(timeObs)
    data_time = timeObs + timedelta(minutes = dt)
    yearSf, monthSf, daySf, hourSf, minSf = string_date(data_time)
    
    labels = np.flipud(labels)
    
    obj_area = get_area_def(area_plot)
    fig, ax = prepare_figure(obj_area) 
    plt.contour(labels,[0.5],colors='y')
    #plt.imshow(labels, origin="lower")
    PIL_image = fig2img ( fig )
    if add_name is not None:
          PIL_image.save(create_dir(outputDir)+"Forecast"+yearS+monthS+dayS+"_Obs"+hourS+minS+"_Forc"+hourSf+minSf+add_name+".png")
          path = (outputDir)+"Forecast"+yearS+monthS+dayS+"_Obs"+hourS+minS+"_Forc"+hourSf+minSf+add_name+".png"
    else:
          PIL_image.save(create_dir(outputDir)+"/Forecast"+yearS+monthS+dayS+"_Obs"+hourS+minS+"_Forc"+hourSf+minSf+".png")
          path = (outputDir)+"/Forecast"+yearS+monthS+dayS+"_Obs"+hourS+minS+"_Forc"+hourSf+minSf+".png"
    print "... display ",path," &"
    plt.close( fig)   
"""



if __name__ == '__main__':
    #filenames = []
    #for i in range(5):
    #    filename = 'test_forecastProf_%d.stats' % i
    #    cProfile.run('print %d, main()' % i, filename)
    # Read all 5 stats files into a single object
    verbose = False
    profiling = False
    
    ttt = datetime(2015,7,7,13,0)
    interesting_cell = 67
    outputFile = "/opt/users/"+getpass.getuser()+"/PyTroll/scripts/forecasting_labels/"    
                
    model = "linear_exp_exp"
    #model = "linear"; ylabel = "channel"
    #model = "linear"; ylabel = "displacement_dx"
    #model = "linear"; ylabel = "displacement_dy"       

    if profiling:
        cProfile.run('plot_forecast_area(ttt, model, outputFile, current_labels = None, t_stop=ttt)','test_forecastProf.prof')
    else:
        plot_forecast_area(ttt, model, outputFile, current_labels = None, t_stop=ttt)
 
    #stats = pstats.Stats('test_forecastProf_0.stats')
    #for i in range(1, 5):
    #    stats.add('test_forecastProf_%d.stats' % i)
    
    # Clean up filenames for the report
    #stats.strip_dirs()
    
    # Sort the statistics by the cumulative time spent in the function
    #stats.sort_stats('cumulative')
    
    #stats.print_stats()











