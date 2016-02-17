# 'small program to read lightning data, format lat,lon,time,type,current'

from numpy import genfromtxt, floor, zeros, arange, meshgrid, rot90
import matplotlib.pyplot as plt
from matplotlib.cm import jet
from matplotlib.pyplot import savefig
from os.path import basename
from ApproxSwissProj import ApproxSwissProj 
from datetime import datetime, timedelta, date 
import numpy.ma as ma
ccs4 = ApproxSwissProj()

file="/data/OWARNA/hau/database/lightnings/2014/258/THX142582135.prd.dat"
fname=basename(file)
year='20'+fname[3:5]
doy=fname[5:8]
hh=fname[8:10]
mm=fname[10:12]

date0 = date(int(year),1,1) + timedelta(int(doy)-1) 
#date1 = date0 + timedelta(seconds=(int(hh)*3600+int(mm)*60)) ## does not work, why?!?
date2=datetime(date0.year, date0.month, date0.day, int(hh), int(mm), 0)
print "... plot data for "+date2.strftime("%Y-%m-%d %H:%M UTC")

## file format
## lat       lon       time        type   current
# 43.1170    5.0120 20140915213443 IC     9.2

## data=np.loadtxt(file,usecols=(0,1,2,4))
## print "%f" % data[0,0], "%f" % data[0,1], "%i" % data[0,2], "%f" % data[0,3] ## only numbers


# a=np.loadtxt(file, dtype={'names': ('lat', 'lon', 'time', 'type', 'current'),'formats': (np.float, np.float, np.int, '|S15', np.float)})
data = genfromtxt(file, dtype=None, names=('lat', 'lon', 'time', 'type', 'current'))  # automatic specification of the format

xCH = ccs4.WGStoCHx(data['lat'],data['lon'])
yCH = ccs4.WGStoCHy(data['lat'],data['lon'])

iCH = floor(yCH/1000.)-255  # y is in horizontal direction
jCH = 480-floor(xCH/1000.)  # and x in the vertical


#for y, x, d in zip(yCH,xCH,data):
#    print "%7.3f" % d['lon'], "%7.3f" % d['lat'], d['time'], d['type'], "%6.1f" % d['current'] 
#    print "%8.2f" % (y/1000.), "%8.2f" % (x/1000.), d['time'], d['type'], "%6.1f" % d['current'] 

lightnings = ma.asarray(zeros(shape=(640,710)))

## mark single point
#for i, j in zip(iCH,jCH):
#    #print " %4i" % i, "%4i" % j, d['time'], d['type'], "%6.1f" % d['current'] 
#    lightnings[i,j]+=1

# mark a square 
dd=10
for i, j in zip(iCH,jCH):
    #print " %4i" % i, "%4i" % j, d['time'], d['type'], "%6.1f" % d['current'] 
    lightnings[i-dd:i+dd,j-dd:j+dd]+=1

#rr=20
#x = arange(0, 710)
#y = arange(0, 640)
#X, Y = meshgrid(x, y)

#for i, j in zip(iCH,jCH):
#    interior = (X-i**2) + (Y-j**2) < rr**2
#    lightnings+=1*interior
#    for i2 in (arange(-rr,rr+1)+i):
#        for j2 in (arange(-rr,rr+1)+j):
#            if (i-i2)**2 + (j-j2)**2 < rr**2:
#                lightnings[i,j]+=1

lightnings=rot90(lightnings)

lightnings.mask = (lightnings == 0)

#x=range(710)
#y=range(640)

#img_light = plt.contourf(lightnings[110:160,650:709], cmap=jet)
#img_light = plt.contourf(lightnings, cmap=jet)
#img_light = plt.imshow(lightnings[110:160,650:709],interpolation='none',origin='lower', cmap=jet)
img_light = plt.imshow(lightnings,interpolation='none',origin='lower', cmap=jet)
plt.colorbar(img_light)
#plt.show()
outputFile="lightning.png"
savefig(outputFile)
print '... save figure as ', outputFile
