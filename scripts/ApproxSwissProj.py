# Source: http://www.swisstopo.admin.ch/internet/swisstopo/en/home/topics/survey/sys/refsys/projections.html (see PDFs under "Documentation")
# converted to python with https://www.varycode.com/

## usage for 
## location close to Locarno 
# from ApproxSwissProj import ApproxSwissProj 
# ccs4 = ApproxSwissProj()
# lon =  8.+ 43/60.+ 49.79/3600.
# lat = 46.+  2/60.+ 38.87/3600.
# h = 650.60
# print ccs4.WGStoCHx(lat,lon), ccs4.WGStoCHy(lat,lon), ccs4.WGStoCHh(lat,lon,h) 
## 99999.973095 699999.763621 600.04947591
#
## zuerich 47 deg 22 sec N 8 deg 33 sec E
# lon =  8.+ 33/60.
# lat = 47.+ 22/60.
# print ccs4.WGStoCHx(lat,lon), ccs4.WGStoCHy(lat,lon)
## 248032.023897 683929.425073
#
## Bern 46 deg 57 sec N 7 deg 27 sec E
# lon =  7.+ 27/60.
# lat = 46.+ 57/60.
# print ccs4.WGStoCHx(lat,lon), ccs4.WGStoCHy(lat,lon)
## 199879.867332 601711.226851
#
## Genf 46 deg 12 sec N  06 deg 09 sec E
# lon =  6.+  9/60.
# lat = 46.+ 12/60.
# print ccs4.WGStoCHx(lat,lon), ccs4.WGStoCHy(lat,lon)
## 118544.263404 501410.609108

#from System import *
import math
from numpy import floor, power

class ApproxSwissProj(object):
	""" <summary>
	 Summary description for ApproxSwissProj.
	 </summary>
	"""
	def __init__(self):
		pass
	def LV03toWGS84(east, north, height, latitude, longitude, ellHeight):
		latitude = ApproxSwissProj.CHtoWGSlat(east, north)
		longitude = ApproxSwissProj.CHtoWGSlng(east, north)
		ellHeight = ApproxSwissProj.CHtoWGSheight(east, north, height)
		return 

	LV03toWGS84 = staticmethod(LV03toWGS84)

	def WGS84toLV03(latitude, longitude, ellHeight, east, north, height):
		east = ApproxSwissProj.WGStoCHy(latitude, longitude)
		north = ApproxSwissProj.WGStoCHx(latitude, longitude)
		height = ApproxSwissProj.WGStoCHh(latitude, longitude, ellHeight)
		return 

	WGS84toLV03 = staticmethod(WGS84toLV03)

	# Convert WGS lat/long (degree) to CH y
	def WGStoCHy(lat, lng):
		# Converts degrees dec to sex
		lat = ApproxSwissProj.DecToSexAngle(lat)
		lng = ApproxSwissProj.DecToSexAngle(lng)
		# Converts degrees to seconds (sex)
		lat = ApproxSwissProj.SexAngleToSeconds(lat)
		lng = ApproxSwissProj.SexAngleToSeconds(lng)
		# Axiliary values (% Bern)
		lat_aux = (lat - 169028.66) / 10000
		lng_aux = (lng - 26782.5) / 10000
		# Process Y
		y = 600072.37 + 211455.93 * lng_aux - 10938.51 * lng_aux * lat_aux - 0.36 * lng_aux * power(lat_aux, 2) - 44.54 * power(lng_aux, 3)
		return y

	WGStoCHy = staticmethod(WGStoCHy)
	
	# Convert WGS lat/long (degree) to CH x
	def WGStoCHx(lat, lng):
		# Converts degrees dec to sex
		lat = ApproxSwissProj.DecToSexAngle(lat)
		lng = ApproxSwissProj.DecToSexAngle(lng)
		# Converts degrees to seconds (sex)
		lat = ApproxSwissProj.SexAngleToSeconds(lat)
		lng = ApproxSwissProj.SexAngleToSeconds(lng)
		# Axiliary values (% Bern)
		lat_aux = (lat - 169028.66) / 10000
		lng_aux = (lng - 26782.5) / 10000
		# Process X
		x = 200147.07 + 308807.95 * lat_aux + 3745.25 * power(lng_aux, 2) + 76.63 * power(lat_aux, 2) - 194.56 * power(lng_aux, 2) * lat_aux + 119.79 * power(lat_aux, 3)
		return x

	WGStoCHx = staticmethod(WGStoCHx)
	
		# Convert WGS lat/long (degree) and height to CH h
	def WGStoCHh(lat, lng, h):
		# Converts degrees dec to sex
		lat = ApproxSwissProj.DecToSexAngle(lat)
		lng = ApproxSwissProj.DecToSexAngle(lng)
		# Converts degrees to seconds (sex)
		lat = ApproxSwissProj.SexAngleToSeconds(lat)
		lng = ApproxSwissProj.SexAngleToSeconds(lng)
		# Axiliary values (% Bern)
		lat_aux = (lat - 169028.66) / 10000
		lng_aux = (lng - 26782.5) / 10000
		# Process h
		h = h - 49.55 + 2.73 * lng_aux + 6.94 * lat_aux
		return h

	WGStoCHh = staticmethod(WGStoCHh)
	
		# Convert CH y/x to WGS lat
	def CHtoWGSlat(y, x):
		# Converts militar to civil and  to unit = 1000km
		# Axiliary values (% Bern)
		y_aux = (y - 600000) / 1000000
		x_aux = (x - 200000) / 1000000
		# Process lat
		lat = 16.9023892 + 3.238272 * x_aux - 0.270978 * power(y_aux, 2) - 0.002528 * power(x_aux, 2) - 0.0447 * power(y_aux, 2) * x_aux - 0.0140 * power(x_aux, 3)
		# Unit 10000" to 1 " and converts seconds to degrees (dec)
		lat = lat * 100 / 36
		return lat

	CHtoWGSlat = staticmethod(CHtoWGSlat)
	
		# Convert CH y/x to WGS long
	def CHtoWGSlng(y, x):
		# Converts militar to civil and  to unit = 1000km
		# Axiliary values (% Bern)
		y_aux = (y - 600000) / 1000000
		x_aux = (x - 200000) / 1000000
		# Process long
		lng = 2.6779094 + 4.728982 * y_aux + 0.791484 * y_aux * x_aux + 0.1306 * y_aux * power(x_aux, 2) - 0.0436 * power(y_aux, 3)
		# Unit 10000" to 1 " and converts seconds to degrees (dec)
		lng = lng * 100 / 36
		return lng

	CHtoWGSlng = staticmethod(CHtoWGSlng)
	
		# Convert CH y/x/h to WGS height
	def CHtoWGSheight(y, x, h):
		# Converts militar to civil and  to unit = 1000km
		# Axiliary values (% Bern)
		y_aux = (y - 600000) / 1000000
		x_aux = (x - 200000) / 1000000
		# Process height
		h = h + 49.55 - 12.60 * y_aux - 22.64 * x_aux
		return h

	CHtoWGSheight = staticmethod(CHtoWGSheight)
	
		# Convert sexagesimal angle (degrees, minutes and seconds "dd.mmss") to decimal angle (degrees)
	def SexToDecAngle(dms):
		# Extract DMS
		# Input: dd.mmss(,)ss
		deg = 0
		min = 0
		sec = 0
		deg = floor(dms)
		min = floor((dms - deg) * 100)
		sec = (((dms - deg) * 100) - min) * 100
		# Result in degrees dec (dd.dddd)
		return deg + min / 60 + sec / 3600

	SexToDecAngle = staticmethod(SexToDecAngle)
	
		# Convert decimal angle (degrees) to sexagesimal angle (degrees, minutes and seconds dd.mmss,ss)
	def DecToSexAngle(dec):
		deg = floor(dec)
		min = floor((dec - deg) * 60)
		sec = (((dec - deg) * 60) - min) * 60
		# Output: dd.mmss(,)ss
		return deg + min / 100 + sec / 10000

	DecToSexAngle = staticmethod(DecToSexAngle)

	# Convert sexagesimal angle (degrees, minutes and seconds dd.mmss,ss) to seconds
	def SexAngleToSeconds(dms):
		deg = 0
		min = 0
		sec = 0
		deg = floor(dms)
		min = floor((dms - deg) * 100)
		sec = (((dms - deg) * 100) - min) * 100
		# Result in degrees sex (dd.mmss)
		return sec + min * 60 + deg * 3600

	SexAngleToSeconds = staticmethod(SexAngleToSeconds)

if __name__ == '__main__':
	from ApproxSwissProj import ApproxSwissProj 
	ccs4 = ApproxSwissProj()

	print ""
	print "dir(ccs4)"
	print dir(ccs4)
	# 'WGS84toLV03', 'WGStoCHh', 'WGStoCHx', 'WGStoCHy'
	# 'CHtoWGSheight', 'CHtoWGSlat', 'CHtoWGSlng'

	# example Bern
	lat = 46.9167 
	lng =  7.4667
	xCH = ccs4.WGStoCHx(lat,lng)
	yCH = ccs4.WGStoCHy(lat,lng)
	print "*** Bern    is located at ", xCH, yCH, "in the ccs4 grid"

	# example Locarno
	lat = 46.1667
	lng =  8.8
	xCH = ccs4.WGStoCHx(lat,lng)
	yCH = ccs4.WGStoCHy(lat,lng)
	print "... Locarno is located at ", xCH, yCH, "in the ccs4 grid"

	print ""

	# lower left corner
	lat = ccs4.CHtoWGSlat(255000.0, -160000.0)  # y, x
	lng = ccs4.CHtoWGSlng(255000.0, -160000.0)  # y, x
	print "*** lower left corner of ccs4 is (ApproxSwissProj): ", lat, lng

	# alternative way
	from pyproj import Proj
	p = Proj(proj="somerc", lat_0=46.9524055555556, lon_0=7.43958333333333, ellps="bessel", x_0=600000, y_0=200000, k_0=1)
	lng1, lat1 = p(255000.0, -160000.0, inverse=True)
	print "    lower left corner of ccs4 is          (pyproj): ", lat1, lng1
	lng2, lat2 = p(255000.0,  480000.0, inverse=True)
	print "    upper left corner of ccs4 is          (pyproj): ", lat2, lng2
	lng3, lat3 = p(965000.0, -160000.0, inverse=True)
	print "    lower right corner of ccs4 is          (pyproj): ", lat3, lng3
	lng4, lat4 = p(965000.0,  480000.0, inverse=True)
	print "    upper right corner of ccs4 is          (pyproj): ", lat4, lng4
	print ""
	print "python coord2area_def_stere.py nrCOAL1km stere ", min([lat1,lat2,lat3,lat4]),max([lat1,lat2,lat3,lat4]), \
	                                                         min([lng1,lng2,lng3,lng4]), max([lng1,lng2,lng3,lng4]), 1.0

	print ""    
