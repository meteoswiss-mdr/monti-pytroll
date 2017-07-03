#!/opt/users/common/packages/anaconda3/envs/PyTroll_hau/bin/python
# -*- coding: utf-8 -*-
"""
ninjotiff_example

Created on Wed Dec  2 10:00:18 2015

@author: ras

This example is using a ninjotiff.cfg file. If you prefer to pass all
meta-data by arguments, they can be defined like:
The ninjotiff.cfg is saved in the PPP_CONFIG_DIR, i.g. $PYTROLLHOME/PyTroll/etc/

ninjotiff_config = {
      0.6: {'description': 'MSG Channel 1',
            'sat_id': 6200014,
            'chan_id': 100015,
            'data_cat': 'GORN',
            'data_source': 'EUMETCAST'}, 
     10.8: {'description': 'MSG Channel 9',
            'sat_id': 6200014,
            'chan_id': 900015,
            'data_cat': 'GORN',
            'data_source': 'EUMETCAST'},
    'HRV': {'description': 'MSG Channel 12',
            'sat_id': 6200014,
            'chan_id': 1200015,
            'data_cat': 'GORN',
            'data_source': 'EUMETCAST'},
}

Saving an image for 'chn' will then go like:

    image.save(filename,
               fformat='mpop.imageo.formats.ninjotiff',
               physic_unit=physic_unit,
               ch_min_measurement_unit=min_value,
               ch_max_measurement_unit=max_value,
               **ninjotiff_config[chn])
"""

from PIL import Image as Pimage
import numpy as np
from mpop.imageo.geo_image import GeoImage

def _image2array(im):
    '''
    Utility function that converts an image file in 3 or 4 np arrays
    that can be fed into 'geo_image.GeoImage' in order to generate
    a PyTROLL GeoImage object.
    '''
    #im = Pimage.open(filepath).convert('RGB')
    (width, height) = im.size
    if im.mode == 'RGB' or im.mode == 'RGBA':
        _r = np.array(list(im.getdata(0)))/255.0
        _g = np.array(list(im.getdata(1)))/255.0
        _b = np.array(list(im.getdata(2)))/255.0
        _r = _r.reshape((height, width))
        _g = _g.reshape((height, width))
        _b = _b.reshape((height, width))
    else:
        "*** Error in pilimage2geoimage (ninjotiff_example)"
        "    unknown PIL_image mode: ", pimage.mode       
    if 'RGBA':
        _a = np.array(list(im.getdata(3)))/255.0
        _a = _a.reshape((height, width))
        
    if im.mode == 'RGB':        
        return _r, _g, _b
    elif im.mode == 'RGBA':
        return _r, _g, _b, _a

def pilimage2geoimage(pimage, area, timeslot):
    if pimage.mode == 'RGB':
        (r,g,b) = _image2array(pimage)
        gi = GeoImage((r,g,b), area, timeslot, mode=pimage.mode)
    elif pimage.mode == 'RGBA':
        (r,g,b,a) = _image2array(pimage)
        gi = GeoImage((r,g,b,a), area, timeslot, mode=pimage.mode)
    else:
        "*** Error in pilimage2geoimage (ninjotiff_example)"
        "    unknown PIL_image mode: ", pimage.mode
        quit
    return gi

if __name__ == '__main__':

    import sys
    import os
    from datetime import datetime, timedelta
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # Basic check.
    try:
        os.environ['PPP_CONFIG_DIR']
    except KeyError:
        print >>sys.stderr, "PPP_CONFIG_DIR is not defined"
        sys.exit(2)

    from mpop.satellites import GeostationaryFactory
    import mpop.utils

    LOG = mpop.utils.get_logger(__name__)
    if "DEBUG" in os.environ:
        mpop.utils.debug_on()

    # Handle argument.
    try:
        filename = sys.argv[1]
        i__ =  os.path.basename(filename).split('-')
        TIMESLOT = datetime.strptime(i__[6], '%Y%m%d%H%M')
        SATNO = "%02d" % (7 + int(i__[2][3]))
        print "... satellite number "+str(SATNO)
    except IndexError:
        #print >> sys.stderr, "usage: ninjotiff_example <MSG EPI filename>"
        #exit(2)
        from my_msg_module import get_last_SEVIRI_date
        SATNO = "09"
        SATNO = "10"
        if SATNO == "10":
            RSS = False
        else:
            RSS = True
        TIMESLOT = get_last_SEVIRI_date(RSS, delay=10)

    print "*** MSG ", SATNO, str(TIMESLOT)
        
    # Areas to be loaded into and to be projected onto.
    AREAS = (
        ('germ','germ','germ'),
        #('visir_full', 'MSGF', 'msg_pc'),
        #('hrv_north', 'MSGHRVN', 'msg_hrvn_pc')
        )

    CHANNEL_DICT = {
        #'visir_full': (0.6, 0.8, 1.6, 3.9, 6.2, 7.3, 8.7, 9.7, 10.8, 12.0, 13.4),
        'visir_full': (0.6, 10.8,),
        'germ': (0.6, 0.8, 1.6, 3.9, 6.2, 7.3, 8.7, 9.7, 10.8, 12.0, 13.4),
        'ccs4': (0.6, 0.8, 1.6, 3.9, 6.2, 7.3, 8.7, 9.7, 10.8, 12.0, 13.4),
        'hrv_north': ('HRV',)
        }

    BITS_PER_SAMPLE = 8
    DO_GEOIMAGE = False
    DO_CONVECTION = False
    DO_TROLLIMAGE = True

    if DO_GEOIMAGE:
        for area_name, area_in, area_out in AREAS:
            global_data = GeostationaryFactory.create_scene("meteosat",
                                                            SATNO, 
                                                            "seviri", 
                                                            #area=area_in,
                                                            time_slot=TIMESLOT)

            # Load channel by channel (to save memory).
            for chn in CHANNEL_DICT[area_name]:
                global_data.load([chn])
                chn_name = global_data[chn].name

                # Save 'unit' ... it seems to be lost somewhere.
                global_data[chn].unit = global_data[chn].info.get('units', 'None')

                # Resample to Plate Caree.
                scene = global_data.project(area_out, mode='quick', precompute=True)

                # Kelvin -> Celsius.
                physic_unit = scene[chn].unit.upper()
                if physic_unit in ('K', 'KELVIN'):
                    scene[chn].data -= 273.15
                    physic_unit = scene[chn].unit = 'C'

                # Value range as DWD
                if physic_unit in ('C', 'CELSIUS'):
                    # IR
                    value_range = (-88.5, 40.)
                else:
                    # VIS
                    value_range = (0., 125.)

                #
                # A GeoImage specifying a color range.
                #
                # If no color_range specified, MPOP will not scaled the data into the [0., 1.] range.
                # In that case set the data_is_scaled_01 option to False in img.save
                #
                img = scene.image(chn, mode="L", crange=[value_range])
                LOG.info("%s (%s, %s) %.2f %.2f %.2f" % (chn_name, physic_unit,
                                                         img.channels[0].dtype,
                                                         img.channels[0].min(),
                                                         img.channels[0].mean(),
                                                         img.channels[0].max()))

                #
                # Save it to Ninjo tif format, pass physics unit and Ninjo product name
                # (by "coincidence" product name correspond to MPOP's channel name :).
                #
                # If physics unit is not passed, we will expect to find it in ninjotiff's config file.
                #
                filename = ('MSG-' + TIMESLOT.strftime("%Y%m%d_%H%M") + '-' +
                            area_name.split('_')[-1] + '-' + chn_name + '-%db.tif' % BITS_PER_SAMPLE)
                LOG.info("Saving to Ninjo tif %s" % filename)
                img.save(filename,
                         fformat='mpop.imageo.formats.ninjotiff',
                         physic_unit=physic_unit,
                         ninjo_product_name=chn_name,
                         ch_min_measurement_unit=value_range[0],
                         ch_max_measurement_unit=value_range[1],
                         nbits=BITS_PER_SAMPLE)

                # Cleanup.
                scene.unload([chn])
                global_data.unload([chn])


    if DO_CONVECTION:
        #
        # RGB example, convection
        #
        # NOT ready for 16 bit
        BITS_PER_SAMPLE = 8

        product_name = 'convection'
        #area_name, area_in, area_out = ('visir_europe', 'MSGNH', 'msg_ninjo_europe_big')
        area_name, area_in, area_out = ('germ', 'germ', 'germ')    
        channels = [0.635, 1.63, 3.75, 6.7, 7.3, 10.8]

        global_data = GeostationaryFactory.create_scene("meteosat",
                                                        SATNO, 
                                                        "seviri", 
                                                        #area=area_in,
                                                        time_slot=TIMESLOT)

        # Load channels.
        global_data.load(channels)

        # Resample to Plate Caree.
        scene = global_data.project(area_out, mode='quick', precompute=True)
        img = scene.image.convection()
        print "type(img) ", type(img)
        #type(img)  <class 'mpop.imageo.geo_image.GeoImage'>

        filename = ('MSG-' + TIMESLOT.strftime("%Y%m%d_%H%M") + '-' +
                    area_name.split('_')[-1] + '-' + product_name + '-%db.tif' % BITS_PER_SAMPLE)
        LOG.info("Saving to Ninjo tif %s" % filename)
        img.save(filename,
                 fformat='mpop.imageo.formats.ninjotiff',
                 ninjo_product_name='msg_' + product_name,
                 nbits=BITS_PER_SAMPLE)


    if DO_TROLLIMAGE:

        BITS_PER_SAMPLE = 8

        product_name = 'convection'
        #area_name, area_in, area_out = ('visir_europe', 'MSGNH', 'msg_ninjo_europe_big')
        area_name, area_in, area_out = ('germ', 'germ', 'germ')    

        #chn = 10.8 ; product_name = 'IR108'; ninjo_product_name = 'IR_108'
        chn = 'CTH' ; product_name = 'CTH' ; ninjo_product_name = 'msg_cloudtop_height'
        
        global_data = GeostationaryFactory.create_scene("meteosat",
                                                        SATNO, 
                                                        "seviri", 
                                                        #area=area_in,
                                                        time_slot=TIMESLOT)

        # Load channels.
        import products 
        if chn in products.NWCSAF:
            from my_msg_module import get_NWC_pge_name, convert_NWCSAF_to_radiance_format
            pge = get_NWC_pge_name(chn)
            global_data.load([pge], calibrate=True, reader_level="seviri-level3") 
            convert_NWCSAF_to_radiance_format(global_data, None, chn, True, True)
        else:
            global_data.load([chn])
        
        # Resample to Plate Caree.
        local_data = global_data.project(area_out, mode='quick', precompute=True)

        from trollimage.image import Image as trollimage
        from trollimage.colormap import rainbow
        colormap = rainbow
        min_data = local_data[chn].data.min()
        max_data = local_data[chn].data.max()
        colormap.set_range(min_data, max_data)
        TROLL_imgage = trollimage(local_data[chn].data, mode="L", fill_value=None) # fill_value=[0,0,0]
        TROLL_imgage.colorize(colormap)
        PIL_image = TROLL_imgage.pil_image()
        from mpop.projector import get_area_def
        area_def = get_area_def(area_out)
        GEO_image = pilimage2geoimage(PIL_image, area_def, TIMESLOT)
        if True:
            filesave = TIMESLOT.strftime("MET"+SATNO+"_RSS_"+ product_name+"______"+area_out+"_%Y%m%d%H%M.tif")
            LOG.info("Saving %s as Ninjo tif" % filesave)
            GEO_image.save(filesave,
                           fformat='mpop.imageo.formats.ninjotiff',
                           ninjo_product_name=ninjo_product_name,
                           nbits=BITS_PER_SAMPLE)
        else:
            filesave = TIMESLOT.strftime("MET"+SATNO+"_RSS_"+ product_name+"______"+area_out+"_%Y%m%d%H%M.png")
            LOG.info("Saving %s as png" % filesave)
            PIL_image.save(filesave,
                            fformat='png')
