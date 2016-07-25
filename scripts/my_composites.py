from mpop.imageo.geo_image import GeoImage
from copy import deepcopy

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

def sandwich(self):
    """Make a colored 10.8 RGB image with HRV resolution enhacement 
    from Seviri channels.
    """
    from trollimage.image import Image as trollimage
    from trollimage.colormap import rdbu, greys, rainbow, spectral

    self.check_channels(10.8, "HRV")

    ## use trollimage to create black white image
    #img = trollimage(self['IR_108'].data, mode="L")
    img = GeoImage(self["IR_108"].data, self.area, self.time_slot,
                   fill_value=0, mode="L")

    # use trollimage to create a color map
    greys.set_range(-30 + 273.15, 30 + 273.15)
    rainbow.set_range( -73 + 273.15, -30.00001 + 273.15)
    rainbow.reverse()
    my_cm = rainbow + greys

    luminance = GeoImage((self["HRV"].data), self.area, self.time_slot,
                         crange=(0, 100), mode="L")
    luminance.enhance(gamma=2.0)
    img.replace_luminance(luminance.channels[0])

    ## colorize the image
    #img.colorize(my_cm)

    return img

sandwich.prerequisites = set(["HRV", 10.8])
#sandwich.prerequisites = set([10.8])   

def HRVir108(self, cos_scaled=True, use_HRV=False, smooth=False):

    self.check_channels("VIS006", "HRV", "IR_108")
    import numpy as np

    # calculate longitude/latitude and solar zenith angle 
    from pyorbital.astronomy import sun_zenith_angle
    lonlats = self["IR_108"].area.get_lonlats()
    sza = sun_zenith_angle(self.time_slot, lonlats[0], lonlats[1])

    # threshold sza
    sza1 = 80.
    ir1 = 190.
    ir2 = 320.
    vis1 =  0.
    if not cos_scaled:
        vis2 = 75. #for pure vis/hrv
    else:
        vis2 = 110. #for scaling with cos(sza)

    # scale the vis and ir channel to appropriate min / max 
    ir108 = (self["IR_108"].data - ir1) / (ir2-ir1)
    if not use_HRV:
        vis   = (self["VIS006"].data - vis1) / (vis2-vis1) 
    else:
        vis   = (self["HRV"].data    - vis1) / (vis2-vis1)

    if not smooth:
        mask = np.array(sza > sza1)
    else:
        mask = np.zeros(ir108.shape)
        mask[np.where( sza1 > sza1 )] = 1


    print "*** AAA ", type(mask)
    print "*** AAA ", mask
    print "mask", mask.shape, type(mask)

    if not cos_scaled:
        ch1 = vis * (1-mask) 
    else:
        ch1 = vis * (1-mask) / (np.cos(np.radians(sza))+0.05)
    ch2 = (1 - ir108) * mask

    img = GeoImage(ch1+ch2, self.area, self.time_slot, fill_value=(0,0,0), mode="L")

    from trollimage.colormap import rainbow
    cm = deepcopy(rainbow)
    cm.set_range(0, 1)
    img.colorize(cm)

    return img

HRVir108.prerequisites = set(["VIS006", "HRV", 10.8])

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

def WV_062_minus_WV_073(self):
    """Make a colored image of the difference of two Seviri channels.
    """

    self.check_channels('WV_062','WV_073')

    from trollimage.image import Image as trollimage

    ch_diff = self['WV_062']-self['WV_073']

    min_data = ch_diff.data.min()
    max_data = ch_diff.data.max()
    print "min/max", min_data, max_data

    img = trollimage(ch_diff.data, mode="L")

    #from trollimage.colormap import rdbu
    #rdbu.set_range(min_data, max_data)
    #rdbu.set_range(-20, +20)
    #rdbu.reverse()
    #img.colorize(rdbu)

    from trollimage.colormap import rainbow, greys
    greys.set_range(-25, -15)
    greys.reverse()
    rainbow.set_range(-15, 5)
    my_cm = greys + rainbow
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

    img = trollimage(ch_diff.data, mode="L")

    #from trollimage.colormap import rdbu
    #rdbu.set_range(min_data, max_data)
    #rdbu.set_range(-50, +50)
    #rdbu.reverse()
    #img.colorize(rdbu)

    from trollimage.colormap import rainbow, greys
    greys.set_range(-70, -25)
    greys.reverse()
    rainbow.set_range(-25, 5)
    my_cm = greys + rainbow
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

    img = trollimage(ch_diff.data, mode="L")

    from trollimage.colormap import rainbow
    rainbow.set_range(min_data, max_data)
    rainbow.set_range(-15, +5)
    rainbow.reverse()
    img.colorize(rainbow)

    #from trollimage.colormap import rainbow, greys, rdpu
    #greys.set_range(-4, -1.5)
    #greys.reverse()
    #rainbow.set_range(-1.5, 1.5)
    #my_cm = greys + rainbow
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

    img = trollimage(ch_diff.data, mode="L")

    #from trollimage.colormap import rdbu
    #rdbu.set_range(min_data, max_data)
    #rdbu.set_range(-5, +5)
    #rdbu.reverse()
    #img.colorize(rdbu)

    from trollimage.colormap import rainbow, greys, rdpu
    greys.set_range(-4, -1.5)
    greys.reverse()
    rainbow.set_range(-1.5, 1.5)
    my_cm = greys + rainbow
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

    img = trollimage(ch_diff.data, mode="L")

    from trollimage.colormap import rainbow
    rainbow.set_range(min_data, max_data)
    rainbow.set_range(-4, +4)
    rainbow.reverse()
    img.colorize(rainbow)

    #from trollimage.colormap import rainbow, greys, rdpu
    #greys.set_range(-4, -1.5)
    #greys.reverse()
    #rainbow.set_range(-1.5, 1.5)
    #my_cm = greys + rainbow
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

    img = trollimage(ch_diff.data, mode="L")

    #from trollimage.colormap import rdbu
    #rdbu.set_range(min_data, max_data)
    #rdbu.set_range(-5, +5)
    #rdbu.reverse()
    #img.colorize(rdbu)

    from trollimage.colormap import rainbow, greys
    greys.set_range(-6, -1.6)
    greys.reverse()
    rainbow.set_range(-1.6, 0.6)
    my_cm = greys + rainbow
    greys.set_range(0.6, 2)
    my_cm2 = my_cm + greys
    img.colorize(my_cm2)

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

    img = trollimage(ch_diff.data, mode="L")

    #from trollimage.colormap import rdbu
    #rdbu.set_range(min_data, max_data)
    #rdbu.set_range(-5, +5)
    #rdbu.reverse()
    #img.colorize(rdbu)

    from trollimage.colormap import rainbow, greys
    greys.set_range(-9, -2.5)    # 2.5 according to Mecikalski, 2.2 maybe better?
    greys.reverse()
    rainbow.set_range(-2.5, 1.34)
    my_cm = greys + rainbow
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
    from trollimage.colormap import rainbow
    from my_composites import mask_clouddepth
    
    mask = mask_clouddepth(self)

    img = trollimage(mask, mode="L")
    min_data= mask.min()
    max_data= mask.max()

    print "    use trollimage.image.image for colorized pictures (min="+str(min_data)+", max="+str(max_data)+")"
    rainbow.set_range(min_data, max_data)
    img.colorize(rainbow)

    return img

#clouddepth.prerequisites = set(['WV_062','WV_073','IR_087','IR_097','IR_108','IR_120','IR_134'])
clouddepth.prerequisites = set(['WV_062','WV_073','IR_087','IR_108','IR_120','IR_134'])


#def channel_difference(self, rgb):
#    """Make a colored image of the difference of two Seviri channels.
#    """
#
#    from trollimage.image import Image as trollimage
#    from trollimage.colormap import rdbu, greys, rainbow, spectral
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



seviri = [hr_visual, hr_overview, sandwich, HRVir108, ndvi, WV_062_minus_WV_073, WV_062_minus_IR_108, WV_073_minus_IR_134, \
          IR_120_minus_IR_108, IR_087_minus_IR_108, IR_087_minus_IR_120, trichannel, clouddepth, mask_clouddepth]


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
    elif rgb=='sandwich':
        obj_image = data.image.sandwich
    elif rgb=='HRVir108':
        obj_image = data.image.HRVir108
    elif rgb=='ndvi':
        obj_image = data.image.ndvi
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
