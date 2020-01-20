from __future__ import division
from __future__ import print_function

import numpy as np
from datetime import datetime, timedelta
from produce_forecasts_develop import string_date
from scipy.misc import imread
import matplotlib.pyplot as plt
import pickle
import sys
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from plot_msg import load_products
#import seaborn
from copy import deepcopy


def to_grayscale(arr): 
    "If arr is a color image (3D array), convert it to grayscale (2D array)." 
    from scipy import average
    if len(arr.shape) == 3: 
        return average(arr, -1)  # average over the last axis (color channels) 
    else: 
        return arr         

def compare_images(img_obs, img_mod): 
      from scipy import sum
      import numpy as np
      from scipy.linalg import norm 
      diff = img_mod - img_obs  # elementwise for scipy arrays 
      m_norm = sum(abs(diff))  # Manhattan norm 
      z_norm = norm(diff.ravel(), 0)  # Zero norm 
      err = (np.sum(diff ** 2))
      err/=float(img1.shape[0] * img2.shape[1])
      std=diff.std()
      count=sum(sum(1 for i in range(diff.shape[0]) if abs(diff[i,col])<1) for col in range(diff.shape[1]))
      median = np.median(diff)
      return (m_norm, z_norm,diff,err,std,count,median) #, corr)  

def plot_diff(img_obs,img_mod,label_mod, lead_time):
    diff = img_mod - img_obs
    fig = plt.figure()
    plt.imshow(diff) #forecasts_out[channel_nr[rgb],ind_time,:,:]>0)
    plt.axis('off')
    plt.colorbar()
    plt.show()
    plt.savefig("Difference_ObsMod_"+label_mod+"_"+lead_time+".png")
    plt.close(fig)

def setBoxColors(bp,ind,color):
    #inspired from answer to: http://stackoverflow.com/questions/16592222/matplotlib-group-boxplots
    
    print("index_model: ", ind)
    print("index single: ", ind)
    print("index double: ", ind*2)
    print("shape double: ", len(bp['fliers']))
    
    plt.setp(bp['boxes'][ind], color=color)
    plt.setp(bp['caps'][ind], color=color)
    plt.setp(bp['caps'][ind+1], color=color)
    plt.setp(bp['whiskers'][ind], color=color)
    plt.setp(bp['whiskers'][ind+1], color=color)
    plt.setp(bp['fliers'][ind], color=color)
    #plt.setp(bp['fliers'][ind+1], color=color)
    plt.setp(bp['medians'][ind], color=color)
    

def set_colors(bp):
    setBoxColors(bp,0,'blue')
    setBoxColors(bp,1,'red')
    #setBoxColors(bp,2,'cyan')
    #setBoxColors(bp,3,'magenta')    

def compute_stats(obs,mod):
    
    obs = np.ndarray.flatten(obs)
    mod = np.ndarray.flatten(mod)

    keep = np.ones(obs.shape)

    keep[np.logical_or(np.isnan(obs), np.isnan(mod))] = 0 #!!!
    keep[np.logical_or(obs.mask == True, mod.mask==True)] = 0 

    obs = obs[keep==1]
    mod = mod[keep==1]
    
    diff = mod-obs

    corr_coeff = np.corrcoef(obs,mod)[0,1]
    
    mean = diff.mean()
    std = diff.std()
    count = sum(keep)
    median = np.ma.median(diff.flatten())
    
    mean1 = diff[diff!=0].mean()
    std1 = diff[diff!=0].std()
    count1 = sum(keep[diff!=0])
    median1 = np.ma.median(diff[diff!=0].flatten())

    return corr_coeff, mean, std, median, count, mean1, std1, median1, count1

def plot_stat(time,var1layer,var3layer,y_label):
    fig = plt.figure()
    plt.scatter(time1, var1layer, color = "blue", label = '1 p layer, forced mask')
    plt.scatter(time1, var3layer, color = "red", label = '3 p layer, forced mask')
    plt.ylabel(y_label)
    plt.legend(loc="best")    
    plt.savefig("Comparison_Advections_Stats_"+y_label+".png")
    plt.close()

#==========================================================================================================
#==========================================================================================================

if __name__ == "__main__":

    from get_input_msg import get_date_and_inputfile_from_commandline
    in_msg = get_date_and_inputfile_from_commandline(print_usage=print_usage)

    #from get_input_msg import get_input_msg    
    #input_file = sys.argv[1]
    #if input_file[-3:] == '.py': 
    #    input_file=input_file[:-3]
    #in_msg = get_input_msg(input_file)
    #time_slot0 = datetime(2015,10,15,5,0)

    in_msg.update_datetime(2015,10,15,5,0)
    time_slot0 = in_msg.datetime

    year0S, month0S, day0S, hour0S, min0S = string_date(time_slot0)
    path = "/data/COALITION2/PicturesSatellite/LEL_results_wind//"+year0S+"-"+month0S+"-"+day0S+"/channels_fig//"
    
    #fig = plt.figure()
    #ax = plt.axes()
    #plt.hold(True)
    
    means1 = []
    stds1 = []
    means2 = []
    stds2 = []    
    corrcoeffs1 = []
    corrcoeffs2 = []
    medians1 = []
    medians2 = []
    count1 = []
    count2 = []
    
    
    means1NonZero  = []
    stds1NonZero  = []
    means2NonZero  = []
    stds2NonZero  = []    
    medians1NonZero  = []
    medians2NonZero  = []
    count1NonZero  = []
    count2NonZero  = []
    
    
    
    time1=[]

    for i in range(5,65,5):
        leadS = "%02d" % i
        #diff["t"+leadS] = {}
        diff = []
        diff1 = []
        yearS, monthS, dayS, hourS, minS = string_date(time_slot0+timedelta(minutes = i))

        #print ("*** read data for ", in_msg.sat_str(),in_msg.sat_nr_str(), "seviri", time_slot0+timedelta(minutes = i))
        
        global_data = GeostationaryFactory.create_scene(in_msg.sat_str(),in_msg.sat_nr_str(), "seviri",  time_slot0+timedelta(minutes = i))
        area_loaded = get_area_def("EuropeCanary95")  #(in_windshift.areaExtraction)  
        area_loaded = load_products(global_data, ['CTT'], in_msg, area_loaded)
        data = global_data.project("ccs4")        

        img_obs = deepcopy(data['CTT'].data)
        img_obs.mask[:,:] = False
        
        if True:
            print("pickles/"+year0S+month0S+day0S+"_"+hour0S+min0S+"_CTT_t"+leadS+"_1layer.p")
            tmp = pickle.load(open( "pickles/"+year0S+month0S+day0S+"_"+hour0S+min0S+"_CTT_t"+leadS+"_1layer.p","rb"))
            tmp = (tmp[0]-img_obs)
            diff1.append(tmp)
            tmp = tmp.flatten()
            print("0 before")
            print("max: ", tmp.max())
            print("mean: ", tmp.mean())
            print("number points: ", tmp.size)
            #print "median: ", tmp.median()

            tmp1 = []
            for err in tmp:
                if abs(err) <= 50:
                    tmp1.append(err)
            tmp1 = np.array(tmp1)
            print("0 after")
            print("max: ", tmp1.max())
            print("mean: ", tmp1.mean())
            print("number points: ", tmp1.size)
            #print "median: ", tmp1.mmedian()        
            
            diff.append(tmp1)    
            #diff.append(tmp[0]-img_obs) #diff.append((tmp[0]-img_obs).flatten()) #pickles/20151015_0500_CTT_t05_1layer.p
            tmp = pickle.load(open( "pickles/"+year0S+month0S+day0S+"_"+hour0S+min0S+"_CTT_t"+leadS+"_3layer.p","rb"))
            tmp = (tmp[0]-img_obs)
            diff1.append(tmp)
            tmp = tmp.flatten()
            tmp1 = []
            print("1 before")
            print("max: ", tmp.max())
            print("mean: ", tmp.mean())
            print("number points: ", tmp.size)
            #print "median: ", tmp.median()
            for err in tmp:
                if abs(err) <= 50:
                    tmp1.append(err)
            tmp1 = np.array(tmp1)
            print("1 after")
            print("max: ", tmp1.max())
            print("mean: ", tmp1.mean())
            print("number points: ", tmp1.size)
            #print "median: ", tmp1.median() 
            diff.append(tmp1) 
            #diff.append(tmp[0]-img_obs)
        tmp = pickle.load(open( "pickles/forced/"+year0S+month0S+day0S+"_"+hour0S+min0S+"_CTT_t"+leadS+"_1layerForced_mask.p","rb"))  #pickles/forced/20151015_0500_CTT_t05_1layerForced_mask.p
        tmp.mask[:,:] = False
        
        print("1 layer")
        print("corr_coeff, mean, std, median, count, meanNonZero, stdNonZero, medianNonZero, countNonZero")
        corr_coeff, mean, std, median, count, meanNonZero, stdNonZero, medianNonZero, countNonZero = compute_stats(deepcopy(data['CTT'].data), tmp)
        print(corr_coeff, mean, std, median, count, meanNonZero, stdNonZero, medianNonZero, countNonZero)
        
        diff1.append(tmp-img_obs)
        
        flat = (tmp-img_obs).flatten()
        flat = flat[~np.isnan(flat)]
        #tmp = tmp.flatten()[~np.isnan(flat)]
        #obs_tmp = img_obs.flatten()[~np.isnan(flat)]
        
        means1.append(mean)
        stds1.append(std)
        medians1.append(median)
        count1.append(count)
        
        means1NonZero.append(meanNonZero)
        stds1NonZero.append(stdNonZero)
        medians1NonZero.append(medianNonZero)
        count1NonZero.append(countNonZero)
        #k = corr_coeff_(img_obs,tmp)
        
        corrcoeffs1.append(corr_coeff) #np.corrcoef(flat, obs_tmp)[0,1])
        time1.append(i)
        #medians1.append(flat.data.median())

        
        diff.append(flat) #diff.append(tmp-img_obs)
        

        tmp = pickle.load(open( "pickles/forced/"+year0S+month0S+day0S+"_"+hour0S+min0S+"_CTT_t"+leadS+"_3layerForced_mask.p","rb"))
        tmp.mask[:,:] = False
        
        print("3 layers")
        print("corr_coeff, mean, std, median, count, meanNonZero, stdNonZero, medianNonZero, countNonZero")
        corr_coeff, mean, std, median, count, meanNonZero, stdNonZero, medianNonZero, countNonZero = compute_stats(deepcopy(data['CTT'].data), tmp)
        print(corr_coeff, mean, std, median, count, meanNonZero, stdNonZero, medianNonZero, countNonZero)
        
        diff1.append(tmp-img_obs)
        flat = (tmp-img_obs).flatten()
        
        flat = flat[~np.isnan(flat)]
        
        #tmp = tmp.flatten()[~np.isnan(flat)]
        #obs_tmp = img_obs.flatten()[~np.isnan(flat)]
        
        means2.append(mean)
        stds2.append(std)
        medians2.append(median)
        count2.append(count)
        
        means2NonZero.append(meanNonZero)
        stds2NonZero.append(stdNonZero)
        medians2NonZero.append(medianNonZero)
        count2NonZero.append(countNonZero)
        #k = corr_coeff_(img_obs,tmp)
        
        corrcoeffs2.append(corr_coeff) #corrcoeffs2.append(np.corrcoef(flat, obs_tmp)[0,1])
        #medians2.append(flat.median())
        
        
        diff.append(flat) #diff.append(tmp-img_obs)
        #diff.append((tmp-img_obs).flatten())

        
        #diff.append(tmp-img_obs)
        
        for diff_count in diff:
            print(len(diff_count))
           
        
        if True:
            model_ind_plot = 0
            for diff_one in diff1:
                #print diff_one
                #diff_one = np.reshape(diff_one, img_obs.shape)
                #diff_one
                fig = plt.figure()
                plt.imshow(diff_one)
                plt.axis('off')
                plt.colorbar()
                plt.savefig("Difference_t%s_%s.png"%(leadS, model_ind_plot))
                plt.close()
                model_ind_plot += 1
        
        #bp = plt.boxplot(diff, positions = [i-1,i-.5,i+.5,i+1], widths = .6)
        #diff = diff [2:]
        #bp = plt.boxplot(diff, positions = [i-1,i+1], widths = .6)
     
        #set_colors(bp)
    
    """
    plt.xlim(0,65)  
    plt.ylim(-20,20)
    ax.set_xticklabels(['5', '10', '15','20','25','30','35','40','45','50','55','60'])
    ax.set_xticks([5,10,15,20,25,30,35,40,45,50,55,60])
    
    hB, = plt.plot([1,1],'b-')
    hR, = plt.plot([1,1],'r-')
    plt.legend((hB, hR),('1 p layer, forced mask', '3 p layers, forced mask'), loc = 'upper left' )
    hB.set_visible(False)
    hR.set_visible(False)
    
    plt.savefig("Comparison_Advections.png")
    plt.close()
    
    fig = plt.figure()
    plt.subplot(311)
    print time1
    plt.scatter(time1, means1,color = "blue", label = '1 p layer, forced mask')
    print time1
    plt.scatter(time1, means2, color = "red", label = '3 p layer, forced mask')
    print time1
    plt.ylabel("Mean")
    plt.legend(loc="best")
    plt.subplot(312)
    plt.scatter(time1, stds1,color = "blue", label = '1 p layer, forced mask')
    plt.scatter(time1, stds2,color = "red", label = '3 p layer, forced mask')
    plt.ylabel("Std")
    plt.legend(loc="best")    
    plt.subplot(313)
    plt.scatter(time1, corrcoeffs1, color = "blue", label = '1 p layer, forced mask')
    plt.scatter(time1, corrcoeffs2, color = "red", label = '3 p layer, forced mask')
    plt.ylabel("Corr. forc-obs")
    plt.legend(loc="best")    
    plt.savefig("Comparison_Advections_Stats.png")
    plt.close()
    
    plot_stat(time1,means1,means2,"mean")
    plot_stat(time1,medians1,medians2,"median")
    plot_stat(time1,count1,count2,"Pixels")
    plot_stat(time1,corrcoeffs1,corrcoeffs2,"Correlation")
    plot_stat(time1,stds1,stds2,"std")
    
    plot_stat(time1,means1NonZero,means2NonZero,"mean[NonZero]")
    plot_stat(time1,medians1NonZero,medians2NonZero,"median[NonZero]")
    plot_stat(time1,count1NonZero,count2NonZero,"pixels[NonZero]")
    
    plot_stat(time1,stds1NonZero,stds2NonZero,"std")    
    """
    """
    img_obs = imread(path+"CTT_"+yearS+monthS+dayS+hourS+minS+"_ObsDownscaled.png").astype(float)
        
        tmp = imread(path+"CTT_"+year0S+month0S+day0S+hour0S+min0S+"_t"+leadS+"_1layer.png")#.astype(float) #- img_obs #CTT_2015150500_t05_1layer_ForcedMask
        diff.append(tmp) #.flatten())
        tmp = imread(path+"CTT_"+year0S+month0S+day0S+hour0S+min0S+"_t"+leadS+"_3layer.png")#.astype(float) #- img_obs
        diff.append(tmp) #diff.append(tmp.flatten())
        tmp = imread(path+"CTT_"+year0S+month0S+day0S+hour0S+min0S+"_t"+leadS+"_1layer_ForcedMask.png")#.astype(float) #- img_obs
        diff.append(tmp) #diff.append(tmp.flatten())
        tmp = imread(path+"CTT_"+year0S+month0S+day0S+hour0S+min0S+"_t"+leadS+"_3layer_ForcedMask.png")#.astype(float) #- img_obs
        diff.append(tmp) #diff.append(tmp.flatten())   
    
    diff["t"+leadS]['1layer'] = imread(path+"CTT_"+yearS+monthS+dayS+hourS+minS+"_t"+leadS+"1_layer.png").astype(float) - img_obs #CTT_2015150500_t05_1layer_ForcedMask
    diff["t"+leadS]['3_layer'] = imread(path+"CTT_"+yearS+monthS+dayS+hourS+minS+"_t"+leadS+"3_layer.png").astype(float) - img_obs
    diff["t"+leadS]['1_layer_Forced'] = imread(path+"CTT_"+yearS+monthS+dayS+hourS+minS+"_t"+leadS+"1_layer_ForcedMask.png").astype(float) - img_obs
    diff["t"+leadS]['3_layer_Forced'] = imread(path+"CTT_"+yearS+monthS+dayS+hourS+minS+"_t"+leadS+"3_layer_ForcedMask.png").astype(float) - img_obs
    
    
    
    
    from pylab import plot, show, savefig, xlim, figure, \
                hold, ylim, legend, boxplot, setp, axes


    
    
    
    
    
    img_obs_t15 = imread("CTT_201510150515_ObsDownscaled.png".astype(float)
    img_obs_t30 = imread("CTT_201510150530_ObsDownscaled.png".astype(float)
    
    img_mod['t15_1layer'] = imread("CTT_2015150500_t15_1layer.png").astype(float)
    img_mod['t30_1layer'] = imread("CTT_2015150500_t30_1layer.png".astype(float)
    img_mod['t15_3layer'] = imread("CTT_2015150500_t15_3layer.png".astype(float)
    img_mod['t30_3layer'] = imread("CTT_2015150500_t30_3layer.png".astype(float)
    img_mod['t15_3layer_ForcedMask'] = imread("CTT_201510150500_t15_ForcedMask".astype(float)
    img_mod['t30_3layer_ForcedMask'] = imread("CTT_201510150500_t30_ForcedMask".astype(float)
    
    wanted_plot_diff = True
    
    wanted_stats = True
    
    models = img_mod.keys()
    
    if wanted_plot_diff:
        for model in models:
            if model[:3]=="t15":
                plot_diff(img_obs_t15,img_mod[model], model[4:],model[:3])
            elif model[:3]=="t30":
                plot_diff(img_obs_t30,img_mod[model], model[4:],model[:3])
            else:
                print("quitting because lead time different from 15 and 30")
                quit()
                  
    if wanted_stats:
        m_norms = []
        y_norms = []
        diffs =[]
        errs =[]
        sts =[]
        counts =[]
        medians =[]
        m_norm, z_norm,diff,err,std,count,median = compare_images(img_obs_t15,img_mod1_t15)
    
    
    file_obs = '/opt/users/lel/PyTroll/scripts/obs/MSG_CTT-ccs4_%s.png'%(yearS[2:]+monthS+dayS+hourS+minS)
    if t==0:
        file_mod = '/opt/users/lel/PyTroll/scripts/mod/CTT_t0.png'
    else:
        file_mod = '/opt/users/lel/PyTroll/scripts/mod/CTT_t%s_euler_DisplMeter_cosmo.png'%(tS)

    img_obs = to_grayscale(imread(file_obs).astype(float)) 
    img_mod = to_grayscale(imread(file_mod).astype(float))

    norm_mahn[c], norm_zero[c], diff[c], err[c], std[c], count[c]= compare_images(img_obs,img_mod)
    
    corr_coeff[c]=np.corrcoef(np.ndarray.flatten(mod),np.ndarray.flatten(obs))
    """
