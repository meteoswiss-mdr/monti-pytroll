#%matplotlib inline
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from copy import deepcopy
import matplotlib.dates as mdates
from datetime import timedelta
from Cells import Cells

def future_properties(time,property_values, property_name,model):
        verbose = False
        
        possible_models = ["example","linear","2nd_degree_polynom","3rd_degree_polynom","5th_degree_polynom","linear_exp","linear_exp_exp"]
        
        # rapid scan is 5min time steps
        dt=5 
        ## normal SEVIRI scan time
        #dt=15
        
        
        if property_name != None and model == None:
            if property_name == "area" or property_name == "channel":
                model = "linear_exp"
            elif property_name == "displacement_dx" or property_name == "displacement_dy":
                model = "linear"
         
        if model not in possible_models:
            print "test"
            print 'The chosen fitting model is not implemented'
            print model
            quit()
        
        # Getting back the objects:
        
        
        names = ["WV_062 - IR_108", "WV_062 - WV_073", "IR_108", "WV_073 - IR_134", "WV_062 - IR_097",\
                 "IR_087 - IR_120", "IR_087 - 2IR_108plusIR_120", "IR_087 - IR_108",\
                 "IR_120 - IR_108", "IR_097 - IR_134", "WV_062 - IR_120", "CloudTopPressure", "CloudTopTemperature"]
      
        
        # reverse order of everything  

        time = time[::-1]
        if property_name == "displacement":
            dx = property_values[:,0]
            dy = property_values[:,1]
            dx = dx[::-1]
            dy = dy[::-1]
        else:
            property_values = property_values[::-1]
        
        y_true = property_values
        ylabel = property_name
        
        npredict = len(y_true)
        
        nforecast = 13
        
        ntrue = npredict#len(area)
        nsample = ntrue  # all samples are known
        msample = min(len(property_values),12)     # take this number of last values for fitting
        
        
        x_true = np.linspace(0, ntrue-1, ntrue)
        t_true = time
        
        y = y_true[nsample-msample:nsample] 
        x1 = np.linspace(nsample-1-msample, nsample-1, msample)
        t1 = time[nsample-msample:nsample]
        #x1 = np.linspace(0, msample-1, msample)
        if verbose:
            print("... x1", x1)
        
        if len(x1) != len(y):
            if verbose:
                print ("different length of x1",len(x1)," and y", len(y))
                print("x1", x1)
                print("y1", y1)
            t1 = t1[1:npredict+1]
            quit()
        
        dtau1=5
        dtau2=10
        #dtau3=20
        
        
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
        
        else:
            print ("unknown fitting model")
            quit()
        if verbose:
            print ("X.shape", X.shape)
        X = sm.add_constant(X)
        if verbose:
            print ("X.shape", X.shape)
        
        if verbose:
            print (x1)
        #print (y.shape, y.size)
        #print (y)
        #print (X.shape)
        #print (X)
        
        # Estimation
        print ("*** Estimation")
        #print ("y.shape ",y.shape,", X.shape ", X.shape)
        olsmod = sm.OLS(y, X)
        olsres = olsmod.fit()
        if verbose:
            print (olsres.summary())
        ypred = olsres.predict(X)
        
        # Create a new sample of explanatory variables Xnew, predict and plot
        if verbose:
            print ("Create a new sample of explanatory variables Xnew, predict and plot")
        x1n = np.linspace(nsample,nsample+nforecast-1, nforecast)
        if verbose:
            print (x1n)
        
        t1n=np.array([time[nsample-1] for pointlessIndex in range(nforecast)]) # just initializing the time array
        for i in range(0,len(t1n)):
            if verbose:
                print ("time length",len(time))
                print ("n sample", nsample)
            t1n[i] = time[nsample-1]+(i+1)*timedelta(minutes = 5)
            if verbose:
                print t1n[i]
        
        if model=="example":
            Xnew = np.column_stack((x1n, np.sin(x1n), (x1n-5)**2))
        elif model=="linear":
            #Xnew = np.column_stack((x1n))
            Xnew = x1n
        elif model=="2nd_degree_polynom":
            Xnew = np.column_stack((x1n, x1n**2))
        elif model=="3rd_degree_polynom":
            Xnew = np.column_stack((x1n, x1n**2, x1n**3))
        elif model=="5th_degree_polynom":
            Xnew = np.column_stack((x1n, x1n**2, x1n**3, x1n**4, x1n**5))
        elif model=="linear_exp":
            Xnew = np.column_stack((x1n, np.exp(-x1n) ))
        #elif model=="linear_exp_exp":
        #    Xnew = np.column_stack((x1n, np.exp(-x1n), np.exp(-0.5*x1n) ))
        elif model=="linear_exp_exp":
            Xnew = np.column_stack((x1n*dt, np.exp(-x1n*dt/dtau1), np.exp(-x1n*dt/dtau2) ))

        elif model == "constant":
            Xnew = x1n 
        else:
            print ("unknown fitting model")
            quit()
        
        Xnew = sm.add_constant(Xnew)
        if verbose:
            print ("Xnew.shape", X.shape)
        
        ynewpred =  olsres.predict(Xnew) # predict out of sample
        if verbose:
            print(ynewpred)
        
        if False:
              # Plot comparison
              fig, ax = plt.subplots()
              if True:
                  ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                  ax.plot_date(t1, y, 'o', label="Data starting 12:30")           # noisy data
                  if verbose:
                      print ("t1 done")
                  ax.plot_date(time2, y2, '*', label="Data starting 13:50")           # noisy data time2[1:]
                  if verbose:
                      print ("t2 done")
                  ax.plot_date(t_true, y_true, 'b-', label="True")     # exact data calc with function t_true[1:]
                  if verbose:
                      print ("t_exact done")
                  #ax.plot_date(t1, ypred, 'r-', label="inline prediction")    # inline prediction
                  ax.plot_date(np.hstack((t1, t1n)), np.hstack((ypred, ynewpred)), 'r', label=model)
              else:
                  ax.plot(x1, y, 'o', label="Data")           # noisy data
                  ax.plot(x_true, y_true, 'b-', label="True")     # exact data calc with function
                  #ax.plot(x1, ypred, 'r-', label="inline prediction")    # inline prediction
                  ax.plot(np.hstack((x1, x1n)), np.hstack((ypred, ynewpred)), 'r', label="OLS prediction")
              
              ax.set_ylabel(ylabel)
              ax.legend(loc="best");
              
              #plt.show()
              filename=ylabel+'_'+model+'_'+str(nsample)+'.png'
              if verbose:
                    print (filename)
              fig.savefig(filename)
              plt.close(fig)
        
        t_save = np.hstack((t1, t1n))
        y_save = np.hstack((ypred, ynewpred))
        

        return t_save, y_save







