from __future__ import division
from __future__ import print_function

import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
import pickle
from copy import deepcopy


x_axis = [0,5,10,15,20,25,30,35,40,45,50,55,60]


#pickle.dump(val_median, open('Median_'+variable+'_History'+str(history_correction)+'.p','wb'))

all = {}

versions = ["True", "False", "follow_id"]
names = ["Corrected history", "Not corrected history", "Nor corrected history,\nfollowing ID"]
colors_version = ["black", "magenta", "red"]
variables = ['area','IR108','CenterOfMass'] #,'dx','dy',

for variable in variables:
    all[variable]={}
    for version in versions:
        f = open('Median_'+variable+'_History'+version+'.p','rb')
        all[variable][version] = pickle.load(f)
        f.close()

f, axarr = plt.subplots(len(variables), sharex=True)
      
plt.xlim([0,65])  
plt.xlabel('lead time [min]')    

i = 0
k = 0
for variable in variables:
    for version,name,color in zip(versions,names,colors_version):
        if k == 0:
            axarr[i].plot(x_axis, all[variable][version],  '*',color = color,label=name)
            k=1
        else:
            axarr[i].plot(x_axis, all[variable][version], color = color,label=name)
    i+=1

print("ok so far")
axarr[0].set_ylabel('Er area [%]')
axarr[1].set_ylabel('Er IR10.8 [K]')
#axarr[2].set_ylabel('Er North-South [km]')
#axarr[3].set_ylabel('Er West-East [km]')
axarr[2].set_ylabel('Er centers [km]')
print("seems still ok")
#plt.show()
#f.subplots_adjust(right=0.6)
#plt.legend()   
box = axarr[0].get_position()
axarr[0].set_position([box.x0, box.y0, box.width * 0.8, box.height])
box = axarr[2].get_position()
axarr[2].set_position([box.x0, box.y0, box.width * 0.8, box.height])
box = axarr[1].get_position()
axarr[1].set_position([box.x0, box.y0, box.width * 0.8, box.height])
# Put a legend to the right of the current axis
axarr[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))

#plt.show()
f.savefig("validation/Medians.eps") 
f.savefig("validation/Medians.png") 
plt.close(f)     

fig = plt.figure()
variable = variables[0]
for version,name,color in zip(versions,names,colors_version):
    if k == 0:
        plt.plot(x_axis, all[variable][version],  '*',color = color,label=name)
        k=1
    else:
        plt.plot(x_axis, all[variable][version], color = color,label=name)

fig.savefig("AREA_MEdians.png")
