import numpy as np
import matplotlib.pyplot as plt 

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / N 

year="2014"
y2=str(int(year)-2000)
month="09"
day="20"
date1=year+"-"+month+"-"+day
date2=y2+month+day

folder="./"+date1+"/THX/"
file=folder+'/THX_densCG-ccs4_'+date2+'_0005min_005km.txt'

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
ssum = d[:,10]
area = d[:,11]

print "size(year) ", type(year), year.shape

file2=folder+'/THX_dens-ccs4_'+date2+'_0005min_005km.txt'
d_both = np.loadtxt(file2) #, skiprows=2
ssum_both = d_both[:,10]
print "size(ssum_both) ", type(ssum_both), ssum_both.shape


from pylab import *
#import matplotlib.pyplot as plt

plot_stats=True
plot_both=False

t_start =  0
t_end   = 24
#figuresize=(15,4)
figuresize=(19,3)
pos_x=0.04
pos_y=0.14
size_x=0.925
size_y=0.77

t = hour + minute / 60.
print "size(time) ", size(t)

if plot_stats:
    fig=figure(figsize=figuresize)
    axe = fig.add_axes([pos_x,pos_y,size_x,size_y])

    s = ssum_both
    print "size(sum)", size(s)
    plot(t, s, 'g.')
    s2 = running_mean(ssum_both, 10)
    plot(t[4:t.size-5], s2, 'g-', label="total lightnings")

    s = ssum
    plot(t, s, 'b.')
    s2 = running_mean(ssum, 10)
    plot(t[4:t.size-5], s2,'b-', label="cloud to ground")

    s = ssum_both-ssum
    plot(t, s, 'r.')
    s2 = running_mean(ssum_both-ssum, 10)
    plot(t[4:t.size-5], s2,'r-', label="intra clouds")



    #s = p75
    #plot(t, s, label="p75")
    #s = p90
    #plot(t, s, label="p90")
    
    legend(loc='upper right',prop={'size':10})
    xlim(t_start, t_end)

    xlabel('time (UTC)')
    ylabel('lightning rate / flashs/5min')
    title('lightning rate in Tecino')
    grid(True)
    savefig(folder+"/THX_rate_ccs4_"+date2+".png")
    print "display "+folder+"/THX_rate_ccs4_"+date2+".png &"
    #show()

if plot_both:
    fig, ax1 = plt.subplots(figsize=figuresize)
    grid(True)

    #pos1 = ax1.get_position() # get the original position
    #print pos1
    pos2 = [pos_x,pos_y,size_x,size_y] 
    ax1.set_position(pos2) # set a new position

    s1 = ssum
    ax1.plot(t, s1, 'b.')
    s1m = running_mean(ssum, 19) 
    ax1.plot(t[9:t.size-9], s1m, 'b-')
    ax1.set_xlabel('time (UTC)')
    # Make the y-axis label and tick labels match the line color.
    ax1.set_ylabel('flashs in the last 5min', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    #ax2 = ax1.twinx()
    #s2 = area / 1000.
    #ax2.plot(t, s2, 'g.')
    #s2 = running_mean(area / 1000., 10)
    #ax2.plot(t[4:t.size-5], s2, 'g-')
    #ax2.set_ylabel('area(min 1flash/km2) / 10**3 km**2', color='g')
    #for tl in ax2.get_yticklabels():
    #    tl.set_color('g')

    title('number of flashs and lightning area')
    xlim(t_start, t_end)
    grid(True)
    savefig(folder+"/THX_DENS_ccs4_"+date2+"_both.png")
    #plt.show()
