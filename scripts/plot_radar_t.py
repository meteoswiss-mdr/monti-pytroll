from __future__ import division
from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt 

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / N 

year="2013"
y2=str(int(year)-2000)
month="09"
day="08"
date1=year+"-"+month+"-"+day
date2=y2+month+day

folder="./"+date1+"/radar/"
file=folder+"RAD_RZC-ccs4_"+date2+".txt"

# f = open(file, 'r')

d = np.loadtxt(file) #, skiprows=2

year   = d[:, 0]
month  = d[:, 1]
day    = d[:, 2]
hour   = d[:, 3]
minute = d[:, 4]
mmean = d[:, 5]
p50  = d[:, 6]
p75  = d[:, 7]
p90  = d[:, 8]
mmax = d[:, 9]
area = d[:,10]

from pylab import *
#import matplotlib.pyplot as plt

plot_stats=True
plot_both=True
plot_total=False
plot_area=False

t_start =  6
t_end   = 24
#figuresize=(15,4)
figuresize=(19,3)
pos_x=0.04
pos_y=0.14
size_x=0.925
size_y=0.77

t = hour + minute / 60.

if plot_stats:
    fig=figure(figsize=figuresize)
    axe = fig.add_axes([pos_x,pos_y,size_x,size_y])

    s = mmean
    plot(t, s, 'b.')
    s2 = running_mean(mmean, 10)
    plot(t[4:t.size-5], s2,'b-', label="mean precip")

    s = p50
    plot(t, s, 'g.')
    s2 = running_mean(p50, 10)
    plot(t[4:t.size-5], s2, 'g-', label="median precip")

    #s = p75
    #plot(t, s, label="p75")
    #s = p90
    #plot(t, s, label="p90")
    
    legend(loc='upper right',prop={'size':10})
    xlim(t_start, t_end)

    xlabel('time (UTC)')
    ylabel('precipiation rate / mm/h')
    title('mean precipitation rate')
    grid(True)
    print("final image: display "+folder+"/RAD_RZC_ccs4_"+date2+"_stats.png &")
    savefig(folder+"/RAD_RZC_ccs4_"+date2+"_stats.png")
    #show()

if plot_both:
    fig, ax1 = plt.subplots(figsize=figuresize)
    grid(True)

    #pos1 = ax1.get_position() # get the original position
    #print pos1
    pos2 = [pos_x,pos_y,size_x,size_y] 
    ax1.set_position(pos2) # set a new position

    s1 = mmean * area / 1000.
    ax1.plot(t, s1, 'b.')
    s1m = running_mean(mmean * area / 1000., 10) 
    ax1.plot(t[4:t.size-5], s1m, 'b-')
    ax1.set_xlabel('time (UTC)')
    # Make the y-axis label and tick labels match the line color.
    ax1.set_ylabel('total precip / 10**9 l/h', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    s2 = area / 1000.
    ax2.plot(t, s2, 'g.')
    s2 = running_mean(area / 1000., 10)
    ax2.plot(t[4:t.size-5], s2, 'g-')
    ax2.set_ylabel('area(>0.1mm/h) / 10**3 km**2', color='g')
    for tl in ax2.get_yticklabels():
        tl.set_color('g')
    title('total precipitation and precipitation area')
    xlim(t_start, t_end)
    grid(True)
    print("final image: display "+folder+"/RAD_RZC_ccs4_"+date2+"_both.png &")
    savefig(folder+"/RAD_RZC_ccs4_"+date2+"_both.png")
    #plt.show()









if plot_total:
    fig=figure(figsize=figuresize)
    axe = fig.add_axes([pos_x,pos_y,size_x,size_y])

    s = mmean * area / 1000.
    plot(t, s, label="total precip")
   
    legend(loc='upper right',prop={'size':10})
    xlim(t_start, t_end)

    xlabel('time (UTC)')
    ylabel('total precip / 10**9 l/h')
    title('temporal evolution of the precipitation in Tecino')
    grid(True)
    print("final image: display "+folder+"/RAD_RZC_ccs4_"+date2+"_total.png &")
    savefig(folder+"/RAD_RZC_ccs4_"+date2+"_total.png")

if plot_area:
    fig=figure(figsize=figuresize)
    axe = fig.add_axes([pos_x,pos_y,size_x,size_y])

    s = area / 1000
    plot(t, s, label="area")
   
    legend(loc='upper right',prop={'size':10})
    xlim(t_start, t_end)

    xlabel('time (UTC)')
    ylabel('area with prep>0.1mm/h / 10**3 km**2')
    title('temporal evolution precipitation area')
    grid(True)
    print("final image: display "+folder+"/RAD_RZC_ccs4_"+date2+"_area.png &")
    savefig(folder+"/RAD_RZC_ccs4_"+date2+"_area.png")
