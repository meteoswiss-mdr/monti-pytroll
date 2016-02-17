import numpy as np

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / N 


import datetime
from sys import argv
#from mpop.projector import get_area_def
#from mpop.utils import debug_on
#from pyresample import plot
#from trollimage.colormap import rainbow, purples, prgn, pubugn, brbg, piyg, spectral, greens, greens2
#from trollimage.image import Image as trollimage
#from pydecorate import DecoratorAGG
#import aggdraw
#from PIL import ImageFont, ImageDraw 
from os.path import exists
from os import makedirs
from os import stat
import subprocess
from ApproxSwissProj import ApproxSwissProj  
from pylab import *

import scp_settings
scpOutputDir = scp_settings.scpOutputDir
scpID = scp_settings.scpID 

#debug_on()

save_statistics=True
plot_diagram=False

add_colorscale=False
add_title=True
#layer=' 2nd layer'
layer=' 3rd layer'

scpOutput = False

dt = 5 # every five minutes 

props = ['dens','densCG']

if len(sys.argv) > 1:
    if len(sys.argv) < 4:
        print "***           "
        print "*** Warning, please specify date and time completely, e.g."
        print "***          python plot_lightning.py 2014 07 23 16 10 "
        print "***          arguments given by you:"
        for i in range(len(sys.argv)):
            print sys.argv[i]
        print "***           "
        quit() # quit at this point
    else:
        year   = int(sys.argv[1])
        month  = int(sys.argv[2])
        day    = int(sys.argv[3])
else:
    if False:  # automatic choise of last 5min 
        from my_msg_module import get_last_SEVIRI_date
        datetime1 = get_last_SEVIRI_date(True)
        year  = datetime1.year
        month = datetime1.month
        day   = datetime1.day
    else: # fixed date for text reasons
        year=2014          # 2014 09 15 21 35
        month= 7           # 2014 07 23 18 30
        day= 23

yearS = str(year)
y2    = yearS[2:]
monthS = "%02d" % month
dayS   = "%02d" % day
#hourS  = "%02d" % hour
#minS   = "%02d" % minute
dateS=yearS+'-'+monthS+'-'+dayS
date2=y2+monthS+dayS


# start at the beginning of the day
time_slot = datetime.datetime(year, month, day, 0, 0)

file_wildcards = "/data/lom/WOL/foudre/data/THX/THX%y%j0000.prd"
file = time_slot.strftime(file_wildcards)

print "... read", file


ni=640
nj=710

# empty masked array
dens     = np.ma.asarray(np.zeros(shape=(ni,nj)))
densCG   = np.ma.asarray(np.zeros(shape=(ni,nj)))

#print "*** dens.shape ", dens.shape

# define class for reprojection to ccs4 grid 
ccs4 = ApproxSwissProj()

# read data from file
if file != "" and stat(file).st_size != 0:

    print "... open file"
    NEAR_REAL_TIME=False

    if NEAR_REAL_TIME:
        # lat        lon    time           intra  current
        # 43.2540    9.9290 20150201033521 IC     35.2
        #                   12345678901234
        data = np.genfromtxt(file, dtype=None, names=('lat', 'lon', 'time', 'intra', 'current'))  # automatic specification of the format
        years  = [str(date)[ 0: 4] for date in data['time']]
        months = [str(date)[ 4: 6] for date in data['time']]
        days   = [str(date)[ 6: 8] for date in data['time']]
        hours  = [str(date)[ 8:10] for date in data['time']]
        mins   = [str(date)[10:12] for date in data['time']]
        secs   = [str(date)[12:14] for date in data['time']]
        #intra_cloud = np.zeros(len(data['type']), dtype=bool) # first initialize all with False == cloud to ground lightning  
    else: 
        # date                     |  lon   |  lat   |  curr|nS|mode|intra|    Ax |   Ki2|   Exc|      Incl|    Arc|  empty|  empty|  empty|  empty|
        # 01.09.2013 12:19:39.0 UTC|  12.824|  46.506| -16.0| 1|   6|    0|    0.1|   0.4|   1.0|       145|    1.0|    0.0|    0.0|    0.0|    0.0|
        data = np.genfromtxt(file, dtype=None, names=('date', 'lon', 'lat','current','nS','mode','intra','Ax','Ki2','Exc','Incl','Arc','d1','d2','d3','d4','d5'), delimiter="|") # automatic specification of the format
        days   = [str(date)[ 0: 2] for date in data['date']]
        months = [str(date)[ 3: 5] for date in data['date']]
        years  = [str(date)[ 6:10] for date in data['date']]
        hours  = [str(date)[11:13] for date in data['date']]
        mins   = [str(date)[14:16] for date in data['date']]
        secs   = [str(date)[17:21] for date in data['date']]


    # position in km (x->[-160:480], y->[255,965]
    xCH = ccs4.WGStoCHx(data['lat'],data['lon']) # and x in the vertical
    yCH = ccs4.WGStoCHy(data['lat'],data['lon']) # y is in horizontal direction

    ## convert to index (i->[0,640], j->[0,710]
    #iCH = np.floor(yCH/1000.)-255  # y is in horizontal direction
    #jCH = 710-(480-np.floor(xCH/1000.))  # and x in the vertical ## 
    # convert to index (i->[0,640], j->[0,710]
    iCH = np.floor(yCH/1000.)-255  # y is in horizontal direction
    jCH = 710-(480-np.floor(xCH/1000.))  # and x in the vertical ## 

    # considered time period 
    dtime = datetime.timedelta(minutes=dt)
    t_start = time_slot
    #t_start = datetime.datetime(year, month, day, 14, 10)
    t_loop = t_start

    #n_min = 15
    #n_min = 780
    n_min = 60*24  # one day 
    time_end = t_loop + datetime.timedelta(minutes=n_min)

    nt = n_min / dt
    sum_li = np.zeros(nt)
    sum_cg = np.zeros(nt)


    print "start, end: ", str(t_loop), str(time_end)
    print "... dt: ", dt, " min, nt: ", nt

    tt=0

    #for i, j, YYYY, MM, DD, hh, mm, ss in zip(iCH, jCH, years, months, days, hours, mins, secs, data['intra'], data['current']):
    #    if int(hh)==14 and int(mm)<20:
    #        print int(i), int(j), YYYY,MM,DD,hh,mm,ss
    #quit()


    #print "lightning between ", str(t_loop), " and ", str(t_loop+dtime), tt
    for i, j, YYYY, MM, DD, hh, mm, ss, ltype, curr in zip(iCH, jCH, years, months, days, hours, mins, secs, data['intra'], data['current']):
        secs=int(float(ss))
        microsecs=int((float(ss)-secs)*1000000)
        t_light = datetime.datetime(int(YYYY), int(MM), int(DD), int(hh), int(mm), secs, microsecond=microsecs) 

        #if int(hh)==14 and int(mm)<20:        
        #    print 'A', YYYY,MM,DD,hh,mm,ss

        if t_light < t_start:
            continue

        # search for the correct time slot
        while t_loop < time_end:
            # print int(i), int(j), str(t_light), ltype, curr
            if ( t_loop <= t_light and t_light-t_loop < dtime ):
                #print "count this lightning"
                #print 'B',int(i), int(j), str(t_light), ltype, curr
                if i<640 and j<710:
                    #print "***", int(i), int(j), str(t_light), ltype, curr
                    #dens[i,j]+=1
                    sum_li[tt]+=1
                    if ltype=='CG' or ltype==0:
                        #add_lightning(densCG, i, j, dx, form)
                        #densCG[i,j]+=1
                        sum_cg[tt]+=1
                break
            else:
                #print "lightning later", str(t_light), t_loop <= t_light, t_light-t_loop < dtime
                #sum_li[tt] = np.sum(dens.data)
                #sum_cg[tt] = np.sum(densCG.data)
                #print sum_l, "lightnings, of them ", sum_cg, " cloud to ground"
                #if sum_li[tt] > 0:
                #    print sum_li[tt], "lightnings, of them ", sum_cg[tt], " cloud to ground"

                ## plot lightnings
                #dens=np.rot90(dens)   
                #densCG=np.rot90(densCG) 
                ##ploting ...
   
                # renew arrays
                #dens     = np.ma.asarray(np.zeros(shape=(ni,nj)))
                #densCG   = np.ma.asarray(np.zeros(shape=(ni,nj)))
                t_loop+=dtime
                tt+=1
                #print "search lightnings between ", str(t_loop), " and ", str(t_loop+dtime), tt

        if t_light > time_end:
            break

    #if sum_li[tt] > 0:
    #    print sum_li[tt], "lightnings, of them ", sum_cg[tt], " cloud to ground"

    #print ""
    #print sum_li 
    #print sum_cg

    t = np.arange(nt)*dt / 60. # time in hours

    plot_stats=True
    if plot_stats:

        output_dir='./'+yearS+'-'+monthS+'-'+dayS+'/THX/'
        if not exists(output_dir):
            print '... create output directory: ' + output_dir
            makedirs(output_dir)

        #figuresize=(15,4)
        figuresize=(19,3)
        pos_x=0.04
        pos_y=0.14
        size_x=0.925
        size_y=0.77
        fig=figure(figsize=figuresize)
        axe = fig.add_axes([pos_x,pos_y,size_x,size_y])
        
        s = sum_li
        #print "size(sum)", size(s)
        plot(t, s, 'g.')
        s2 = running_mean(sum_li, 10)
        plot(t[4:t.size-5], s2, 'g-', label="total lightnings")
        
        s = sum_cg
        plot(t, s, 'b.')
        s2 = running_mean(sum_cg, 10)
        plot(t[4:t.size-5], s2,'b-', label="cloud to ground")
        
        s = sum_li - sum_cg
        plot(t, s, 'r.')
        s2 = running_mean(sum_li - sum_cg, 10)
        plot(t[4:t.size-5], s2,'r-', label="intra clouds")

        legend(loc='upper right',prop={'size':10})
        xlabel('time (UTC)')
        ylabel('lightning rate / flashs/5min')

        title('number of flashs, '+dateS)

        fig_t_start =  6
        fig_t_end   = 24
        xlim(fig_t_start, fig_t_end)

        fig_n_start =   0
        fig_n_end   = 250
        ylim(fig_n_start, fig_n_end)

        grid(True)
        #file_basename2 = 'THX_dens2-'+'ccs4'+'_'+yearS[2:]+monthS+dayS+'_'+dt_str+'_'+dx_str
        print "save plot: display "+output_dir+"/THX_dens_ccs4_"+date2+"_ALL.png"
        print " "
        savefig(output_dir+"/THX_dens_ccs4_"+date2+"_ALL.png")

