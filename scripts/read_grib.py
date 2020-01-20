from __future__ import division
from __future__ import print_function

# example from website
# http://pygrib.googlecode.com/svn/trunk/docs/pygrib-module.html

import pygrib
from matplotlib import pyplot as plt

path="/data/OWARNA/hau/pytroll/test/"
file="test_cape.gr"

grbs = pygrib.open(path+file)
#print type(grbs)
#print dir(grbs)

print("-------------------------")
print("*** inventory of the file "+file)
grbs.seek(0)
for g in grbs:
    print("   ", g) 
    print("typeOfLevel: ", g.typeOfLevel)
    print("level: ", g.level)
    print("name: ", g.name)
    print("validDate: ", g.validDate)
    print("analDate: ", g.analDate)
    # print g.forecastTime
    print(dir(g))
print("-------------------------")
print(" ")

# grb = grbs.read(1)[0]  # read returns a list with the next N (N=1 in this case) messages.
# grbs.tell()

# find the first grib message with a matching name:
grb = grbs.select()[0]
data = grb.values
print("shape: ", data.shape)
print("min/max: ",  data.min(), data.max())

#print "open figure"
#fig = plt.figure(figsize=(5, 8))
# obj_quadmesh = plt.pcolormesh( data, cmap=plt.cm.gist_rainbow, vmin=0) 
print("contourf")
CS = plt.contourf( data )

#plt.show()
print("safefig")
plt.savefig('read_grib.png')
