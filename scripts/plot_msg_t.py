
year="2013"
y2="13"
month="09"
day="08"

date=year+"-"+month+"-"+day
folder="./"+date+"/"
in_file=folder+'/MSG_ccs4_'+y2+month+day+'b.txt'
out_file='/MSG_ccs4_'+y2+month+day+'_'

# f = open(file, 'r')

import numpy as np

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / N 

print '... read file ', in_file
d = np.loadtxt(in_file) #, skiprows=2

year   = d[:, 0]
month  = d[:, 1]
day    = d[:, 2]
hour   = d[:, 3]
minute = d[:, 4]
VIS006 = d[:, 5]
VIS008 = d[:, 6]
IR_016 = d[:, 7]
IR_039 = d[:, 8]
WV_062 = d[:, 9]
WV_073 = d[:,10]
IR_087 = d[:,11]
IR_097 = d[:,12]
IR_108 = d[:,13]
IR_120 = d[:,14]
IR_134 = d[:,15]
HRV = d[:,16]

from pylab import *
#import matplotlib.pyplot as plt

solar=False
thermal=True
dthermal_K=False
dthermal_2=False
dthermal_N=True


t_start =  6
t_end   = 24
#figuresize=(15,4)
figuresize=(19,3)
pos_x=0.04
pos_y=0.14
size_x=0.925
size_y=0.77

t = hour + minute / 60.

if solar:
    fig=figure(figsize=figuresize)
    axe = fig.add_axes([pos_x,pos_y,size_x,size_y])
    s = VIS006
    plot(t, s, label="VIS006")
    s = VIS008
    plot(t, s, label="VIS008")
    s = IR_016
    plot(t, s, label="IR_016")
    s = HRV
    plot(t, s, label="HRV")
    
    legend(loc='upper right',prop={'size':10})
    xlim(t_start, t_end)

    xlabel('time (UTC)')
    ylabel('solar channels')
    title('temporal evolution solar channels, ')
    grid(True)
    print "save figure: display "+folder+"/"+out_file+"t_solar.png &"
    savefig(folder+"/"+out_file+"t_solar.png")
    #show()

if thermal:
    fig=figure(figsize=figuresize)
    axe = fig.add_axes([pos_x,pos_y,size_x,size_y])
    #s = IR_039
    #plot(t, s,'--k', label="IR_039")
    s = WV_062
    plot(t, s,'g', label="WV_062")
    s = WV_073
    plot(t, s,'b', label="WV_073")
    s = IR_087
    plot(t, s,'c', label="IR_087")
    s = IR_097
    plot(t, s,'m', label="IR_097")
    s = IR_108
    plot(t, s,'y', label="IR_108")
    s = IR_120
    plot(t, s,'k', label="IR_120")
    s = IR_134
    plot(t, s, 'r', label="IR_134")
   
    legend(loc='upper right',prop={'size':10})
    xlim(t_start, t_end)

    xlabel('time (UTC)')
    ylabel('brightness temperature / K')
    title('thermal channels')
    grid(True)
    print "save figure: display "+folder+"/"+out_file+"t_thermal.png &"
    savefig(folder+"/"+out_file+"t_thermal.png")

if dthermal_K:
    fig=figure(figsize=figuresize)
    axe = fig.add_axes([pos_x,pos_y,size_x,size_y])
    s = WV_062-IR_108
    plot(t, s,'r', label="WV_062-IR_108 (cloud depth)")
    s = WV_062-WV_073
    plot(t, s,'g', label="WV_062-WV_073 (cloud depth)")
    s = WV_073-IR_134
    plot(t, s,'b', label="WV_073-IR_134 (cloud depth)")
    s = WV_062-IR_097
    plot(t, s,'c', label="WV_062-IR_097 (cloud depth)")
    s = IR_087-IR_120
    plot(t, s,'m', label="IR_087-IR_120 (cloud depth)")
    s = IR_087-IR_108
    plot(t, s,'y', label="IR_087-IR_108 (glaciation)")
    s = IR_120-IR_108
    plot(t, s,'k', label="IR_120-IR_108 (glaciation)")
   
    legend(loc='lower right',prop={'size':10})
    xlim(t_start, t_end)

    xlabel('time (UTC)')
    ylabel('brightness temperature / K')
    title('thermal channel differences')
    grid(True)
    print "save figure: display "+folder+"/"+out_file+"/t_thermal_diff_K.png &"
    savefig(folder+"/"+out_file+"/t_thermal_diff_K.png")

if dthermal_2:
    fig, ax1 = plt.subplots(figsize=figuresize)
    grid(True)

    #pos1 = ax1.get_position() # get the original position
    #print pos1
    pos2 = [pos_x,pos_y,size_x,size_y] 
    ax1.set_position(pos2) # set a new position
    s = WV_062-IR_108
    ax1.plot(t, s, 'r-', label="WV_062-IR_108 (cloud depth)")
    s = WV_062-IR_097
    ax1.plot(t, s, 'c-', label="WV_062-IR_097 (cloud depth)")
    s = WV_062-WV_073
    ax1.plot(t, s, 'g-', label="WV_062-IR_073 (cloud depth)")
    ax1.set_xlabel('time (UTC)')
    # Make the y-axis label and tick labels match the line color.
    ax1.set_ylabel('d brightness temperature / K', color='r')
    #for tl in ax1.get_yticklabels():
    #    tl.set_color('k')

    ax2 = ax1.twinx()
    s = IR_087-IR_120
    ax2.plot(t, s, 'm-')
    s = IR_087-IR_108
    ax2.plot(t, s, 'y-')
    s = IR_120-IR_108
    ax2.plot(t, s, 'k-')
    ax2.set_ylabel('d brightness temperature / K', color='k')
    #for tl in ax2.get_yticklabels():
    #    tl.set_color('g')
    title('thermal channel differences')
    xlim(t_start, t_end)
    grid(True)
    print "save figure: display "+folder+"/"+out_file+"/t_thermal_diff_2.png &"
    savefig(folder+"/"+out_file+"/t_thermal_diff_2.png")
    #plt.show()

if dthermal_N:
    fig=figure(figsize=figuresize)
    n=5
    ind = (t > 6)
    lll=1

    if n != 1:
        t=t[2:t.size-2]

    axe = fig.add_axes([pos_x,pos_y,size_x,size_y])
    s = WV_062-IR_108
    s = (s-s[ind].min())/(s[ind].max()-s[ind].min())
    if n != 1:
        s=running_mean(s, n)
    print s.size, t.size
    if lll==1:
        plot(t, s,'r', label="WV_062-IR_108 (cloud depth)")
    else:
        plot(t, s,'r')
    s = WV_062-WV_073
    s = (s-s[ind].min())/(s[ind].max()-s[ind].min())
    if n != 1:
        s=running_mean(s, n)
    if lll==1:
        plot(t, s,'g', label="WV_062-WV_073 (cloud depth)")
    else:
         plot(t, s,'g')
    s = WV_073-IR_134
    s = (s-s[ind].min())/(s[ind].max()-s[ind].min())
    if n != 1:
        s=running_mean(s, n)
    if lll==1:
        plot(t, s,'b', label="WV_073-IR_134 (cloud depth)")
    else:
        plot(t, s,'b')
    s = WV_062-IR_097
    s = (s-s[ind].min())/(s[ind].max()-s[ind].min())
    if n != 1:
        s=running_mean(s, n)
    if lll==1:
        plot(t, s,'c', label="WV_062-IR_097 (cloud depth)")
    else:
        plot(t, s,'c')
    s = IR_120-IR_087
    s = (s-s[ind].min())/(s[ind].max()-s[ind].min())
    if n != 1:
        s=running_mean(s, n)
    if lll==1:
        plot(t, s,'m')
    else:
        plot(t, s,'m', label="IR_120-IR_087 (cloud depth)")
    s = IR_108-IR_087
    s = (s-s[ind].min())/(s[ind].max()-s[ind].min())
    if n != 1:
        s=running_mean(s, n)
    if lll==1:
        plot(t, s,'y')
    else:
        plot(t, s,'y', label="IR_108-IR_087 (glaciation)")
    s = IR_120-IR_108
    s = (s-s[ind].min())/(s[ind].max()-s[ind].min())
    if n != 1:
        s=running_mean(s, n)
    if lll==1:
        plot(t, s,'k')
    else:
        plot(t, s,'k', label="IR_120-IR_108 (glaciation)")
   
    legend(loc='lower right',prop={'size':9})
    xlim(t_start, t_end)
    ylim(0, 1)

    xlabel('time (UTC)')
    ylabel(' d brightness temperature [0,1]')
    title('thermal channel differences')
    grid(True)
    print "save figure: display "+folder+"/"+out_file+"t_thermal_diff_N.png &"
    savefig(folder+"/"+out_file+"t_thermal_diff_N.png")
