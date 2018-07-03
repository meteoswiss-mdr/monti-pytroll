from mpop.imageo.geo_image import GeoImage
from copy import deepcopy
from trollimage.colormap import rdbu, greys, rainbow, spectral
import numpy as np

def hr_visual(self):
    """Make a High Resolution visual BW image composite from Seviri
    channel.
    """
    self.check_channels("HRV")

    img = GeoImage(self["HRV"].data, self.area, self.time_slot,
                   fill_value=0, mode="L")
    img.enhance(stretch="crude")
    return img 

hr_visual.prerequisites = set(["HRV"])


def hr_overview(self):
    """Make a High Resolution Overview RGB image composite from Seviri
    channels.
    """
    self.check_channels(0.635, 0.85, 10.8, "HRV")

    ch1 = self[0.635].check_range()
    ch2 = self[0.85].check_range()
    ch3 = -self[10.8].data

    img = GeoImage((ch1, ch2, ch3), self.area, self.time_slot,
                   fill_value=(0, 0, 0), mode="RGB")

    img.enhance(stretch="crude")
    img.enhance(gamma=[1.6, 1.6, 1.1])

    luminance = GeoImage((self["HRV"].data), self.area, self.time_slot,
                         crange=(0, 100), mode="L")

    luminance.enhance(gamma=2.0)

    img.replace_luminance(luminance.channels[0])

    return img

hr_overview.prerequisites = set(["HRV", 0.635, 0.85, 10.8])


def hr_natural(self, stretch=None, gamma=1.8):
    """Make a Natural Colors RGB image composite.

    +--------------------+--------------------+--------------------+
    | Channels           | Range (reflectance)| Gamma (default)    |
    +====================+====================+====================+
    | IR1.6              | 0 - 90             | gamma 1.8          |
    +--------------------+--------------------+--------------------+
    | VIS0.8             | 0 - 90             | gamma 1.8          |
    +--------------------+--------------------+--------------------+
    | VIS0.6             | 0 - 90             | gamma 1.8          |
    +--------------------+--------------------+--------------------+
    """
    self.check_channels(0.635, 0.85, 1.63)

    ch1 = self[1.63].check_range()
    ch2 = self[0.85].check_range()
    ch3 = self[0.635].check_range()

    img = GeoImage((ch1, ch2, ch3),
                      self.area,
                      self.time_slot,
                      fill_value=(0, 0, 0),
                      mode="RGB",
                      crange=((0, 90),
                              (0, 90),
                              (0, 90)))

    if stretch:
        img.enhance(stretch=stretch)
    if gamma:
        img.enhance(gamma=gamma)

    luminance = GeoImage((self["HRV"].data), self.area, self.time_slot,
                         crange=(0, 100), mode="L")

    luminance.enhance(gamma=2.0)

    img.replace_luminance(luminance.channels[0])

    return img

hr_natural.prerequisites = set(["HRV", 0.635, 0.85, 1.63])


def hr_airmass(self):
    """Make an airmass RGB image composite.

    +--------------------+--------------------+--------------------+
    | Channels           | Temp               | Gamma              |
    +====================+====================+====================+
    | WV6.2 - WV7.3      |     -25 to 0 K     | gamma 1            |
    +--------------------+--------------------+--------------------+
    | IR9.7 - IR10.8     |     -40 to 5 K     | gamma 1            |
    +--------------------+--------------------+--------------------+
    | WV6.2              |   243 to 208 K     | gamma 1            |
    +--------------------+--------------------+--------------------+
    """
    self.check_channels(6.7, 7.3, 9.7, 10.8)

    ch1 = self[6.7].data - self[7.3].data
    ch2 = self[9.7].data - self[10.8].data
    ch3 = self[6.7].data

    img = GeoImage((ch1, ch2, ch3),
                   self.area,
                   self.time_slot,
                   fill_value=(0, 0, 0),
                   mode="RGB",
                   crange=((-25, 0),
                           (-40, 5),
                           (243, 208)))

    luminance = GeoImage((self["HRV"].data), self.area, self.time_slot,
                         crange=(0, 100), mode="L")

    luminance.enhance(gamma=2.0)

    img.replace_luminance(luminance.channels[0])

    return img

hr_airmass.prerequisites = set(["HRV", 6.7, 7.3, 9.7, 10.8])


def sandwich(self):
    """Make a colored 10.8 RGB image with HRV resolution enhacement 
    from Seviri channels.
    """
    from trollimage.image import Image as trollimage

    self.check_channels(10.8, "HRV")

    ## use trollimage to create black white image
    #img = trollimage(self['IR_108'].data, mode="L")
    img = GeoImage(self["IR_108"].data, self.area, self.time_slot, mode="L") #, fill_value=0

    # use trollimage to create a color map
    greys.set_range(-30 + 273.15, 30 + 273.15)
    cm2 = deepcopy(rainbow)
    cm2.set_range( -73 + 273.15, -30.00001 + 273.15)
    cm2.reverse()
    my_cm = cm2 + greys

    #luminance = GeoImage((self["HRV"].data), self.area, self.time_slot,
    #                     crange=(0, 100), mode="L")
    #luminance.enhance(gamma=2.0)
    #img.replace_luminance(luminance.channels[0])

    ## colorize the image
    img.colorize(my_cm)

    return img

sandwich.prerequisites = set(["HRV", 10.8])
#sandwich.prerequisites = set([10.8])   


def HRVFog(self, downscale=False, return_data=False):
    """Make an HRV RGB image composite.
    +--------------------+--------------------+--------------------+
    | Channels           | Temp               | Gamma              |
    +====================+====================+====================+
    | NIR1.6             |        0 -  70     | gamma 1            |
    +--------------------+--------------------+--------------------+
    | HRV                |        0 - 100     | gamma 1            |
    +--------------------+--------------------+--------------------+
    | HRV                |        0 - 100     | gamma 1            |
    +--------------------+--------------------+--------------------+
    """
    self.check_channels(1.6, "HRV")

    from pyorbital.astronomy import sun_zenith_angle
    lonlats = self["HRV"].area.get_lonlats()
    sza = sun_zenith_angle(self.time_slot, lonlats[0], lonlats[1])
    cos_sza = np.cos(np.radians(sza)) + 0.05
        
    ch1 = self[1.6].data   / cos_sza
    ch2 = self["HRV"].data / cos_sza
    ch3 = self["HRV"].data / cos_sza

    # this area exception is not nice!
    if downscale or (self["HRV"].area.name=='ccs4' or self["HRV"].area.name=='Switzerland_stereographic_500m'):
        print '... downscale NIR1.6'
        from plot_coalition2 import downscale_array
        ch1 = downscale_array(ch1)

    if return_data:
        return ch1, ch2, ch3
        
    img = GeoImage((ch1, ch2, ch3),
                   self.area,
                   self.time_slot,
                   fill_value=(0, 0, 0),
                   mode="RGB",
                   crange=((0,  70),
                           (0, 100),
                           (0, 100)))

    return img

HRVFog.prerequisites = set(["HRV", "IR_016"])


def get_sza_mask(self, sza_max=80 ):

    # calculate longitude/latitude and solar zenith angle 
    from pyorbital.astronomy import sun_zenith_angle
    lonlats = self.area.get_lonlats()
    sza = sun_zenith_angle(self.time_slot, lonlats[0], lonlats[1])

    mask = np.array(sza > sza_max)
    return mask

def get_box_mask(self, lon_min=-180, lon_max=180, lat_min=-90, lat_max=90):

    # calculate longitude/latitude and solar zenith angle 
    from pyorbital.astronomy import sun_zenith_angle
    lonlats = self.area.get_lonlats()
    print dir(self.area)

    mask = np.array(lonlats[0] > lon_min)
    mask[lon_max < lonlats[0]] = False
    mask[lonlats[1] < lat_min] = False
    mask[lat_max < lonlats[1]] = False

    return mask


def DayNightFog(self, downscale=False, sza_max=88):
    """Make an RGB image composite.
    during day:   HRVFog
    during night: night microphysics
    """
    self.check_channels(1.6, 3.9, 10.8, 12.0, "HRV")

    # HRVFog recipe
    # --------------
    from pyorbital.astronomy import sun_zenith_angle
    lonlats = self["HRV"].area.get_lonlats()
    sza = sun_zenith_angle(self.time_slot, lonlats[0], lonlats[1])
    import numpy as np
    cos_sza = np.cos(np.radians(sza)) + 0.05
        
    ch1a = self[1.6].data   / cos_sza
    ch2a = self["HRV"].data / cos_sza
    ch3a = self["HRV"].data / cos_sza

    # this area exception is not nice!
    if downscale or (self["HRV"].area.name=='ccs4' or self["HRV"].area.name=='Switzerland_stereographic_500m'):
        print '... downscale NIR1.6'
        from plot_coalition2 import downscale_array
        ch1a = downscale_array(ch1a)

    # night microphysics recipe
    # --------------------------       
    ch1b = self[12.0].data - self[10.8].data
    ch2b = self[10.8].data - self[3.9].data
    ch3b = self[10.8].data

    # this area exception is not nice!
    if downscale or (self["HRV"].area.name=='ccs4' or self["HRV"].area.name=='Switzerland_stereographic_500m'):
        print '... downscale night microphysics - red/green/blue'
        ch1b = downscale_array(ch1b)
        ch2b = downscale_array(ch2b)
        ch3b = downscale_array(ch3b)
    
    # re-adjust range so that both are in in the same range
    # ch1b [-4,2] -> [0,70]
    ch1b = (ch1b+4.)*70./6.
    # ch2b [0,10] -> [0,100]
    ch2b = (ch2b)*10.
    # ch3b [243, 293] -> [0,100]
    ch3b = (ch3b-243.0)*100.0/(293.0-243.0)
    
    mask = np.array(sza > sza_max)
    
    # add two images:
    ch1 = (1-mask)*ch1a + mask*ch1b
    ch2 = (1-mask)*ch2a + mask*ch2b
    ch3 = (1-mask)*ch3a + mask*ch3b

    img = GeoImage((ch1, ch2, ch3),
                   self.area,
                   self.time_slot,
                   fill_value=(0, 0, 0),
                   mode="RGB",
                   crange=((0,  70),
                           (0, 100),
                           (0, 100)))

    #img = GeoImage((ch1, ch2, ch3),
    #               self.area,
    #               self.time_slot,
    #               fill_value=(0, 0, 0),
    #               mode="RGB",
    #               crange=((-4, 2),
    #                       (0, 10),
    #                       (243, 293)))
    
    return img

DayNightFog.prerequisites = set(["HRV","IR_016",'IR_039','IR_108','IR_120'])


#def daynight_blackground(self, cos_scaled=True, use_HRV=False, smooth=False, stretch=(0.005, 0.005), colorscale='greys'):
def daynight_blackground(self, cos_scaled=True, use_HRV=False, smooth=False, stretch=False, colorscale='greys', fixed_minmax=False, white_clouds=True):

    import numpy as np

    # threshold sza
    sza1 = 80.
    
    # calculate longitude/latitude and solar zenith angle 
    from pyorbital.astronomy import sun_zenith_angle
    lonlats = self["IR_108"].area.get_lonlats()
    sza = sun_zenith_angle(self.time_slot, lonlats[0], lonlats[1])

    if not smooth:
        mask = np.array(sza > sza1)
    else:
        mask = np.zeros(ir108.shape)
        mask[np.where( sza > sza1 )] = 1

    # select, if you want HRV or VIS006
    if use_HRV:
        vis   = self["HRV"].data
    else:
        vis   = self["VIS006"].data

    # sceen out data at night/day part of the disk 
    ir108 = self["IR_108"].data * mask
    
    # ... and apply cos scaling to mitigate effect of solar zenith angle
    if not cos_scaled:
        vis = vis * (1-mask) 
    else:
        vis = vis * (1-mask) / (np.cos(np.radians(sza))+0.05)

    # normilize vis reflectivity and ir brightness temperature
    # to comparable range between 0 and 1
    if fixed_minmax:
        # minimum and maximum for ir108
        ir1 = 190.
        ir2 = 290.
        # minimum and maximum for HRV (or VIS006) scale
        vis1 =  0.
        if not cos_scaled:
            vis2 = 75. #for pure vis/hrv
        else:
            vis2 = 110. #for scaling with cos(sza)
    else:
        # linear stretch from p1 percentile to p2 percentile
        
        #import matplotlib.pyplot as plt
        #plt.hist(ir108[np.where(ir108 > 100)], bins='auto')
        #plt.title("Histogram with 'auto' bins")
        #plt.show()
        
        #print "    min/max(1) IR:", ir108.min(), ir108.max() 
        #print "    min/max(1) VIS:", vis.min(), vis.max()
        # percentile limits 
        p1= 5
        p2=95
        #
        ind_ir108 = np.where(ir108 > 100)
        if len(ind_ir108) > 5:
            ir1  = np.percentile( ir108[ind_ir108], p1 )
            ir2  = np.percentile( ir108[ind_ir108], p2 )
        else:
            ir1 = 190.
            ir2 = 290.
        ind_vis=np.where(vis > 0)
        if len(ind_vis) > 5:        
            vis1 = np.percentile( vis[np.where(vis > 0)], p1 )
            vis2 = np.percentile( vis[np.where(vis > 0)], p2 )
        else:
            vis1 =  5.
            if not cos_scaled:
                vis2 = 75.
            else:
                vis2 = 110.
        #print "    min/max(2) IR:", ir1, ir2
        #print "    min/max(2) VIS:", vis1, vis2
        
    # scale the vis and ir channel to the range [0,1] # multiply with mask to keep the zeros for day/night area
    ir108 = (ir108 - ir1) / ( ir2- ir1) *  mask
    vis   = (vis  - vis1) / (vis2-vis1) * (1-mask)
    
    #print "    min/max scaled ir: ", ir108.min(), ir108.max()
    #print "    min/max scaled vis:", vis.min(), vis.max()

    # invert ir108
    ir108 = (1 - ir108) *  mask
        
    img = GeoImage(vis + ir108, self.area, self.time_slot, fill_value=(0,0,0), mode="L")

    if colorscale=='rainbow':
        from trollimage.colormap import rainbow
        cm = deepcopy(rainbow)
    elif colorscale=='greys':
        from trollimage.colormap import greys
        cm = deepcopy(greys)
        if white_clouds:
            cm = cm.reverse()

    cm.set_range(0, 1)
    img.colorize(cm)

    #if stretch:
    #    img.enhance(stretch=stretch)

    return img

def HRVir108c(self, smooth=False):
    self.check_channels("HRV", "IR_108")
    return daynight_blackground(self, cos_scaled=True, use_HRV=True, smooth=smooth, colorscale='rainbow')

HRVir108c.prerequisites = set(["HRV", 10.8])

def HRVir108(self, smooth=False):
    self.check_channels("HRV", "IR_108")
    return daynight_blackground(self, cos_scaled=True, use_HRV=True, smooth=smooth, colorscale='greys')

HRVir108.prerequisites = set(["HRV", 10.8])

def hrvIR108(self, smooth=False):
    self.check_channels("HRV", "IR_108")
    return daynight_blackground(self, cos_scaled=True, use_HRV=True, smooth=smooth, colorscale='greys', white_clouds=False)

hrvIR108.prerequisites = set(["HRV", 10.8])

def VIS006ir108c(self, smooth=False):
    self.check_channels("VIS006", "IR_108")
    return daynight_blackground(self, cos_scaled=True, use_HRV=False, smooth=smooth, colorscale='rainbow')

VIS006ir108c.prerequisites = set(["VIS006", 10.8])

def VIS006ir108(self, smooth=False):
    self.check_channels("VIS006", "IR_108")
    return daynight_blackground(self, cos_scaled=True, use_HRV=False, smooth=smooth, colorscale='greys')

VIS006ir108.prerequisites = set(["VIS006", 10.8])

def vis006IR108(self, smooth=False):
    self.check_channels("VIS006", "IR_108")
    return daynight_blackground(self, cos_scaled=True, use_HRV=False, smooth=smooth, colorscale='greys', white_clouds=False)

vis006IR108.prerequisites = set(["VIS006", 10.8])

def sza(self):

    #self.check_channels("VIS006", "HRV", "IR_108")
    import numpy as np

    # calculate longitude/latitude and solar zenith angle 
    from pyorbital.astronomy import sun_zenith_angle
    lonlats = self.area.get_lonlats()
    #lonlats = self["IR_108"].area.get_lonlats()
    sza = sun_zenith_angle(self.time_slot, lonlats[0], lonlats[1])
    ### stupid numbers for outside disk!!!
    #import numpy.ma as ma
    #sza=ma.masked_equal(sza, 8.24905797976)
    #sza=ma.masked_equal(sza, 8.25871138053)
    
    img = GeoImage(sza, self.area, self.time_slot, fill_value=(0,0,0), mode="L")

    from trollimage.colormap import rainbow
    cm = deepcopy(rainbow)
    cm.set_range(0, 90)
    img.colorize(cm)

    return img

sza.prerequisites = set([])

def ndvi(self):
    """Make a normalized vegitation index image 
    from Seviri channels.
    """
    from trollimage.image import Image as trollimage
    from trollimage.colormap import rdylgn

    self.check_channels('VIS006', 'VIS008')

    colorize=True

    ndvi = (self['VIS008']-self['VIS006']) / (self['VIS008']+self['VIS006'])

    ## use trollimage to create black white image
    ## black and white version 
    img = GeoImage(ndvi.data, self.area, self.time_slot, fill_value=(0,0,0), mode="L")

    if colorize:
        # use trollimage to create a color map
        rdylgn.set_range( -1., +1.)
        # colorize the image
        img.colorize(rdylgn)

    return img

ndvi.prerequisites = set(['VIS006', 'VIS008'])


def IR_039c_CO2(self):
    """
    IR_039 channel, but compensated for the CO2 absorption
    """

    from trollimage.image import Image as trollimage

    self.co2corr_chan()
    self.check_channels("_IR39Corr")

    img = GeoImage(self["_IR39Corr"].data, self.area, self.time_slot, fill_value=(0,0,0), mode="L")

    #min_data = prop.min()
    #max_data = prop.max()
    min_data = 210  # same as for IR_039 in get_input_msg.py 
    max_data = 340  # same as for IR_039 in get_input_msg.py 

    colorize = True
    if colorize:
        # use trollimage to create a color map
        cm = deepcopy(rainbow)
        cm.set_range( min_data, max_data)
        # colorize the image
        img.colorize(cm)

    return img

IR_039c_CO2.prerequisites = set([3.75, 10.8, 13.4])


def VIS006_minus_IR_016(self):
    """Make a colored image of the difference of two Seviri channels.
    """

    from trollimage.image import Image as trollimage

    self.check_channels('VIS006','IR_016')

    ch_diff = self['VIS006']-self['IR_016']

    min_data = ch_diff.data.min()
    max_data = ch_diff.data.max()
    print "    min/max", min_data, max_data

    img = trollimage(ch_diff.data, mode="L", fill_value=(0,0,0))

    cm = deepcopy(rainbow)
    #cm.set_range(min_data, max_data)
    cm.set_range(-15, 40)
    img.colorize(cm)

    #from trollimage.colormap import rdbu
    #rdbu.set_range(min_data, max_data)
    #rdbu.set_range(-50, +50)
    #rdbu.reverse()
    #img.colorize(rdbu)

    #greys.set_range(-70, -25)
    #greys.reverse()
    #cm2 = deepcopy(rainbow)
    #cm2.set_range(-25, 5)
    #my_cm = greys + cm2
    #img.colorize(my_cm)

    return img

VIS006_minus_IR_016.prerequisites = set(['VIS006','IR_016'])


def IR_039_minus_IR_108(self):
    """Make a colored image of the difference of two Seviri channels.
    """

    from trollimage.image import Image as trollimage

    self.check_channels('IR_039','IR_108')

    ch_diff = self['IR_039']-self['IR_108']

    min_data = ch_diff.data.min()
    max_data = ch_diff.data.max()
    print "min/max", min_data, max_data

    img = trollimage(ch_diff.data, mode="L", fill_value=(0,0,0))

    from trollimage.colormap import rainbow
    colormap = deepcopy(rainbow)
    #colormap.set_range(min_data, max_data)
    colormap.set_range(-5, 55)
    img.colorize(colormap)

    #rdbu.set_range(min_data, max_data)
    #rdbu.set_range(-50, +50)
    #rdbu.reverse()
    #img.colorize(rdbu)

    #greys.set_range(-70, -25)
    #greys.reverse()
    #cm2 = deepcopy(rainbow)
    #cm2.set_range(-25, 5)
    #my_cm = greys + cm2
    #img.colorize(my_cm)

    return img

IR_039_minus_IR_108.prerequisites = set(['IR_039','IR_108'])

def WV_062_minus_WV_073(self):
    """Make a colored image of the difference of two Seviri channels.
    """

    self.check_channels('WV_062','WV_073')

    from trollimage.image import Image as trollimage

    ch_diff = self['WV_062']-self['WV_073']

    min_data = ch_diff.data.min()
    max_data = ch_diff.data.max()
    print "min/max", min_data, max_data

    img = trollimage(ch_diff.data, mode="L", fill_value=(0,0,0))

    #from trollimage.colormap import rdbu
    #rdbu.set_range(min_data, max_data)
    #rdbu.set_range(-20, +20)
    #rdbu.reverse()
    #img.colorize(rdbu)

    greys.set_range(-25, -15)
    greys.reverse()
    cm2 = deepcopy(rainbow)
    cm2.set_range(-15, 5)
    my_cm = greys + cm2
    img.colorize(my_cm)

    return img

WV_062_minus_WV_073.prerequisites = set(['WV_062','WV_073'])


def WV_062_minus_IR_108(self):
    """Make a colored image of the difference of two Seviri channels.
    """

    from trollimage.image import Image as trollimage

    self.check_channels('WV_062','IR_108')

    ch_diff = self['WV_062']-self['IR_108']

    min_data = ch_diff.data.min()
    max_data = ch_diff.data.max()
    print "min/max", min_data, max_data

    img = trollimage(ch_diff.data, mode="L", fill_value=(0,0,0))

    #from trollimage.colormap import rdbu
    #rdbu.set_range(min_data, max_data)
    #rdbu.set_range(-50, +50)
    #rdbu.reverse()
    #img.colorize(rdbu)

    greys.set_range(-70, -25)
    greys.reverse()
    cm2 = deepcopy(rainbow)
    cm2.set_range(-25, 5)
    my_cm = greys + cm2
    img.colorize(my_cm)

    return img

WV_062_minus_IR_108.prerequisites = set(['WV_062','IR_108'])


def WV_073_minus_IR_134(self):
    """Make a colored image of the difference of two Seviri channels.
    """

    from trollimage.image import Image as trollimage

    self.check_channels('WV_073','IR_134')

    ch_diff = self['WV_073']-self['IR_134']

    min_data = ch_diff.data.min()
    max_data = ch_diff.data.max()
    print "min/max", min_data, max_data

    img = trollimage(ch_diff.data, mode="L", fill_value=(0,0,0))

    cm2 = deepcopy(rainbow)
    #rainbow.set_range(min_data, max_data)
    cm2.set_range(-15, +5)
    cm2.reverse()
    img.colorize(cm2)

    #greys.set_range(-4, -1.5)
    #greys.reverse()
    #cm2 = deepcopy(rainbow)
    #cm2.set_range(-1.5, 1.5)
    #my_cm = greys + cm2
    #rdpu.set_range(1.5, 4)
    #my_cm2 = my_cm + rdpu
    #img.colorize(my_cm2)

    return img

WV_073_minus_IR_134.prerequisites = set(['WV_073','IR_134'])


def IR_087_minus_IR_108(self):
    """Make a colored image of the difference of two Seviri channels.
    """

    from trollimage.image import Image as trollimage

    self.check_channels('IR_087','IR_108')

    ch_diff = self['IR_087']-self['IR_108']
  
    min_data = ch_diff.data.min()
    max_data = ch_diff.data.max()
    print "min/max", min_data, max_data

    img = trollimage(ch_diff.data, mode="L", fill_value=(0,0,0))

    #from trollimage.colormap import rdbu
    #rdbu.set_range(min_data, max_data)
    #rdbu.set_range(-5, +5)
    #rdbu.reverse()
    #img.colorize(rdbu)

    greys.set_range(-4, -1.5)
    greys.reverse()
    cm2 = deepcopy(rainbow)
    cm2.set_range(-1.5, 1.5)
    my_cm = greys + cm2
    rdpu.set_range(1.5, 4)
    my_cm2 = my_cm + rdpu
    img.colorize(my_cm2)

    return img

IR_087_minus_IR_108.prerequisites = set(['IR_087','IR_108'])

def IR_087_minus_IR_120(self):
    """Make a colored image of the difference of two Seviri channels.
    """

    from trollimage.image import Image as trollimage

    self.check_channels('IR_087','IR_120')

    ch_diff = self['IR_087']-self['IR_120']
  
    min_data = ch_diff.data.min()
    max_data = ch_diff.data.max()
    print "min/max", min_data, max_data

    img = trollimage(ch_diff.data, mode="L", fill_value=(0,0,0))

    cm2 = deepcopy(rainbow)
    cm2.set_range(min_data, max_data)
    cm2.set_range(-4, +4)
    cm2.reverse()
    img.colorize(cm2)

    #greys.set_range(-4, -1.5)
    #greys.reverse()
    #cm2 = deepcopy(rainbow)
    #cm2.set_range(-1.5, 1.5)
    #my_cm = greys + cm2
    #rdpu.set_range(1.5, 4)
    #my_cm2 = my_cm + rdpu
    #img.colorize(my_cm2)

    return img

IR_087_minus_IR_120.prerequisites = set(['IR_087','IR_120'])


def IR_120_minus_IR_108(self):
    """Make a colored image of the difference of two Seviri channels.
    """

    from trollimage.image import Image as trollimage

    self.check_channels('IR_108','IR_120')

    ch_diff = self['IR_120']-self['IR_108']

    min_data = ch_diff.data.min()
    max_data = ch_diff.data.max()
    print "min/max", min_data, max_data

    img = trollimage(ch_diff.data, mode="L", fill_value=(0,0,0))

    #from trollimage.colormap import rdbu
    #rdbu.set_range(min_data, max_data)
    #rdbu.set_range(-5, +5)
    #rdbu.reverse()
    #img.colorize(rdbu)

    colormap = deepcopy(rainbow)
    #colormap.set_range(min_data, max_data)
    colormap.set_range(-5, +2)
    colormap.reverse()
    img.colorize(colormap)

    #greys.set_range(-6, -1.6)
    #greys.reverse()
    #cm2 = deepcopy(rainbow)
    #cm2.set_range(-1.6, 0.6)
    #my_cm = greys + cm2
    #greys.set_range(0.6, 2)
    #my_cm2 = my_cm + greys
    #img.colorize(my_cm2)

    return img

IR_120_minus_IR_108.prerequisites = set(['IR_108','IR_120'])


def trichannel(self):
    """Make a colored image of the difference of three Seviri channels.
    """

    self.check_channels('IR_087','IR_108','IR_120')

    from trollimage.image import Image as trollimage

    ch_diff = self['IR_087'] - 2*self['IR_108'] + self['IR_120']

    min_data = ch_diff.data.min()
    max_data = ch_diff.data.max()
    print "min/max", min_data, max_data

    img = trollimage(ch_diff.data, mode="L", fill_value=(0,0,0))

    #from trollimage.colormap import rdbu
    #rdbu.set_range(min_data, max_data)
    #rdbu.set_range(-5, +5)
    #rdbu.reverse()
    #img.colorize(rdbu)

    greys.set_range(-9, -2.5)    # 2.5 according to Mecikalski, 2.2 maybe better?
    greys.reverse()
    cm2 = deepcopy(rainbow)
    cm2.set_range(-2.5, 1.34)
    my_cm = greys + cm2
    greys.set_range(1.34, 6)
    my_cm2 = my_cm + greys
    img.colorize(my_cm2)

    return img

trichannel.prerequisites = set(['IR_087','IR_108','IR_120'])

def mask_clouddepth(self):

    import numpy as np

    self.check_channels('WV_062','WV_073','IR_087','IR_108','IR_120','IR_134')

    mask = self['IR_108'].data*0

    ch_diff = self['WV_062']-self['IR_108']
    index = np.where( ch_diff.data > -25 )
    mask[index] = mask[index]+1

    ch_diff = self['WV_062']-self['WV_073']
    index = np.where( ch_diff.data > -12.5 )
    mask[index] = mask[index]+1

    index = np.where( self['IR_108'].data < 250. )
    mask[index] = mask[index]+1

    ch_diff = self['WV_073']-self['IR_134']
    index = np.where( ch_diff.data > -2. )
    mask[index] = mask[index]+1

    ch_diff = self['WV_062']-self['WV_073']
    index = np.where( ch_diff.data > -12.5 )
    mask[index] = mask[index]+1

    ch_diff = self['IR_087']-self['IR_120']
    index = np.where( np.logical_and( -1.6 < ch_diff.data, ch_diff.data < 2.2 ) )
    mask[index] = mask[index]+1 

    return mask


def clouddepth(self):
    """Six tests for cloud depth according to Mecikalski 2010.
    Mecikalski et al. 2010, J. Appl. Meteo. Climatology
    Cloud Top Properties of Growing Cumulus prior to Convective Initiation
    as Measured by MeteoSat Second Generation, Part I: Infrared Fields 
    """

    from trollimage.image import Image as trollimage
    from my_composites import mask_clouddepth
    
    mask = mask_clouddepth(self)

    img = trollimage(mask, mode="L")
    min_data= mask.min()
    max_data= mask.max()

    print "    use trollimage.image.image for colorized pictures (min="+str(min_data)+", max="+str(max_data)+")"
    cm2 = deepcopy(rainbow)
    cm2.set_range(min_data, max_data)
    img.colorize(cm2)

    return img

#clouddepth.prerequisites = set(['WV_062','WV_073','IR_087','IR_097','IR_108','IR_120','IR_134'])
clouddepth.prerequisites = set(['WV_062','WV_073','IR_087','IR_108','IR_120','IR_134'])


#def channel_difference(self, rgb):
#    """Make a colored image of the difference of two Seviri channels.
#    """
#
#    from trollimage.image import Image as trollimage
#
#    ch1=rgb[0:6]
#    ch2=rgb[7:13]
#
#    ch_diff = self[ch1]-self[ch2]
#
#    min_data = ch_diff.data.min()
#    max_data = ch_diff.data.max()
#
#    img = trollimage(data_diff.data, mode="L")
#    #rdbu.set_range(min_data, max_data)
#    rdbu.set_range(-25, +25)                                    # !!! HERE is the problem !!!
#    rdbu.reverse()
#    img.colorize(rdbu)
#
#    return img
#
#channel_difference.prerequisites = set([rgb[0:6], rgb[7:13]])   # !!! HERE is the problem !!!



seviri = [hr_visual, hr_overview, hr_natural, hr_airmass, sandwich, HRVFog, DayNightFog, \
          HRVir108c, HRVir108, hrvIR108, VIS006ir108c, VIS006ir108, vis006IR108, sza, ndvi, IR_039c_CO2, \
          VIS006_minus_IR_016, IR_039_minus_IR_108, WV_062_minus_WV_073, WV_062_minus_IR_108,\
          WV_073_minus_IR_134, IR_120_minus_IR_108, IR_087_minus_IR_108, IR_087_minus_IR_120, \
          trichannel, clouddepth, mask_clouddepth]


def get_image(data, rgb): 

    if rgb=="airmass":
        obj_image = data.image.airmass
    elif rgb=='ash':
        obj_image = data.image.ash
    elif rgb=='cloudtop':
        obj_image = data.image.cloudtop
    elif rgb=='convection':
        obj_image = data.image.convection
    elif rgb=='convection_co2':
        obj_image = data.image.convection_co2
    elif rgb=='day_microphysics':    # requires the pyspectral modul, in composite code in /mpop/mpop/instruments/seviri.py
        obj_image = data.image.day_microphysics
    elif rgb=='dust':
        obj_image = data.image.dust
    elif rgb=='fog':
        obj_image = data.image.fog
    elif rgb=='green_snow':
        obj_image = data.image.green_snow
    elif rgb=='ir108':
        obj_image = data.image.ir108
    elif rgb=='natural':
        obj_image = data.image.natural
    elif rgb=='night_fog':
        obj_image = data.image.night_fog
    elif rgb=='night_microphysics':
        obj_image = data.image.night_microphysics
    elif rgb=='night_overview':
        obj_image = data.image.night_overview
    elif rgb=='overview':
        obj_image = data.image.overview
    elif rgb=='overview_sun':
        obj_image = data.image.overview_sun
    elif rgb=='red_snow':
        obj_image = data.image.red_snow
    elif rgb=='refl39_chan':
        obj_image = data.image.refl39_chan
    elif rgb=='snow':
        obj_image = data.image.snow
    elif rgb=='vis06':
        obj_image = data.image.vis06
    elif rgb=='wv_high':
        obj_image = data.image.wv_high
    elif rgb=='wv_low':
        obj_image = data.image.wv_low
    elif rgb=='HRoverview':
        obj_image = data.image.hr_overview
    elif rgb=='hr_natural':
        obj_image = data.image.hr_natural
    elif rgb=='hr_airmass':
        obj_image = data.image.hr_airmass
    elif rgb=='sandwich':
        obj_image = data.image.sandwich
    elif rgb=='HRVFog':
        obj_image = data.image.HRVFog
    elif rgb=='DayNightFog':
        obj_image = data.image.DayNightFog
    elif rgb=='HRVir108c':
        obj_image = data.image.HRVir108c
    elif rgb=='HRVir108':
        obj_image = data.image.HRVir108
    elif rgb=='hrvIR108':
        obj_image = data.image.hrvIR108
    elif rgb=='VIS006ir108c':
        obj_image = data.image.VIS006ir108c
    elif rgb=='VIS006ir108':
        obj_image = data.image.VIS006ir108
    elif rgb=='vis006IR108':
        obj_image = data.image.vis006IR108
    elif rgb=='ndvi':
        obj_image = data.image.ndvi
    elif rgb=='sza':
        obj_image = data.image.sza
    elif rgb=='IR_039c_CO2':
        obj_image = data.image.IR_039c_CO2
    elif rgb=='VIS006-IR_016':
        obj_image = data.image.VIS006_minus_IR_016
    elif rgb=='IR_039-IR_108':
        obj_image = data.image.IR_039_minus_IR_108
    elif rgb=='WV_062-WV_073':
        obj_image = data.image.WV_062_minus_WV_073
    elif rgb=='WV_062-IR_108':
        obj_image = data.image.WV_062_minus_IR_108
    elif rgb=='WV_073-IR_134':
        obj_image = data.image.WV_073_minus_IR_134
    elif rgb=='IR_087-IR_108':
        obj_image = data.image.IR_087_minus_IR_108
    elif rgb=='IR_087-IR_120':
        obj_image = data.image.IR_087_minus_IR_120
    elif rgb=='IR_120-IR_108':
        obj_image = data.image.IR_120_minus_IR_108
    elif rgb=='trichannel':
        obj_image = data.image.trichannel
    elif rgb=='clouddepth':
        obj_image = data.image.clouddepth
    elif rgb == 'VIS006' or rgb == 'VIS008' or rgb == 'IR_016' or rgb == 'IR_039' or rgb == 'WV_062' or rgb == 'WV_073' or \
            rgb == 'IR_087' or rgb == 'IR_097' or rgb == 'IR_108' or rgb == 'IR_120' or rgb == 'IR_134' or rgb == 'HRV':
        obj_image = data.image.channel_image
    elif rgb == 'CT' or rgb == 'CTTH' or 'ctt' or 'cph' or 'cot':
        obj_image = 0
    else:
        print "*** ERROR, undefined rgb mode"
        print "*** ERROR, undefined rgb mode"

    return obj_image
