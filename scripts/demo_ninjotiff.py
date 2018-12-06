from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
import datetime
from PIL import Image

#from mpop.utils import debug_on
#debug_on()

from my_msg_module import get_last_SEVIRI_date

#sat="Meteosat-9"
sat="Meteosat-10"
if sat=="Meteosat-9":
    rapid_scan=True
else:
    rapid_scan=False

time_slot = get_last_SEVIRI_date(rapid_scan, delay=5)
#time_slot = datetime.datetime(2015, 11, 26, 19, 30)
print str(time_slot)

chn="IR_108"
global_data = GeostationaryFactory.create_scene(sat, "", "seviri", time_slot)
global_data.load([10.8])  #, reader_level="seviri-level2"
area="EuropeCanaryS95"  # only 'PLAT', 'MERC', stere (in Ninjo called 'NPOL', 'SPOL') possible
area="ccs4"             # only 'PLAT', 'MERC', stere (in Ninjo called 'NPOL', 'SPOL') possible
#area="EuroMercator"
area="germ"
chan_id=9600015
#chan_id=8800015

local_data = global_data.project(area)

channel_image=False
if channel_image:
    img = local_data.image.channel_image(chn)
    filesave = time_slot.strftime("MET9-RSS_COALITION2_germ-NPOL-COAL_%y%m%d%H%M.tif") # %Y%m%d%H%M
else:
    from trollimage.image import Image as trollimage
    from trollimage.colormap import rainbow
    colormap = rainbow
    min_data = local_data[chn].data.min()
    max_data = local_data[chn].data.max()
    colormap.set_range(min_data, max_data)
    img = trollimage(local_data[chn].data, mode="L", fill_value=[1,1,1]) # fill_value=[0,0,0]
    img.colorize(colormap)
    #PIL_image=img.pil_image()
    filesave = time_slot.strftime("MET9-RSS_COAL2TROLL_germ-NPOL-COAL_%y%m%d%H%M.tif")
    
print "... type(img)", type(img)
print "... save file ", filesave
img.save(filesave, fformat='mpop.imageo.formats.ninjotiff', ninjo_product_name="IR_108",
         chan_id=chan_id, data_source="MeteoSwiss COALITION2 algorithm", data_cat="GPRN", image_dt=time_slot)


"""
        cmap : tuple/list of 3 lists of uint16's
            Individual RGB arrays describing the color value for the
            corresponding data value.  For example, image data with a data
            type of unsigned 8-bit integers have 256 possible values (0-255).
            So each list in cmap will have 256 values ranging from 0 to
            65535 (2**16 - 1). (default linear B&W colormap)
        sat_id : int
            DWD NinJo Satellite ID number
        chan_id : int
            DWD NinJo Satellite Channel ID number
        data_source : str
            String describing where the data came from (SSEC, EUMCAST)
        tile_width : int
            Width of tiles on disk (default 512)
        tile_length : int
            Length of tiles on disk (default 512)
        data_cat : str
            NinJo specific data category
                - data_cat[0] = P (polar) or G (geostat)
                - data_cat[1] = O (original) or P (product)
                - data_cat[2:4] = RN or RB or RA or RN or AN
                                  (Raster, Bufr, ASCII, NIL)

            Example: 'PORN' or 'GORN' or 'GPRN' or 'PPRN'
        pixel_xres : float
            Nadir view pixel resolution in degrees longitude
        pixel_yres : float
            Nadir view pixel resolution in degrees latitude
        origin_lat : float
            Top left corner latitude
        origin_lon : float
            Top left corner longitude
        image_dt : datetime object
            Python datetime object describing the date and time of the image
            data provided in UTC
        projection : str
            NinJo compatible projection name (NPOL,PLAT,etc.)
        meridian_west : float
            Western image border (default 0.0)
        meridian_east : float
            Eastern image border (default 0.0)
        radius_a : float
            Large/equatorial radius of the earth (default <not written>)
        radius_b : float
            Small/polar radius of the earth (default <not written>)
        ref_lat1 : float
            Reference latitude 1 (default <not written>)
        ref_lat2 : float
            Reference latitude 2 (default <not written>)
        central_meridian : float
            Central Meridian (default <not written>)
        physic_value : str
            Physical value type. Examples:
                - Temperature = 'T'
                - Albedo = 'ALBEDO'
        physic_unit : str
            Physical value units. Examples:
                - 'CELSIUS'
                - '%'
        min_gray_val : int
            Minimum gray value (default 0)
        max_gray_val : int
            Maximum gray value (default 255)
        gradient : float
            Gradient/Slope
        axis_intercept : float
            Axis Intercept
        altitude : float
            Altitude of the data provided (default 0.0)
        is_atmo_corrected : bool
            Is the data atmosphere corrected? (True/1 for yes) (default False/0)
        is_calibrated : bool
            Is the data calibrated? (True/1 for yes) (default False/0)
        is_normalized : bool
            Is the data normalized (True/1 for yes) (default False/0)
        description : str
            Description string to be placed in the output TIFF (optional)
        transparent_pix : int
            Transparent pixel value (default -1)
        compression : int
            zlib compression level (default 6)
        inv_def_temperature_cmap : bool (default True)
            Invert the default colormap if physical value type is 'T'
        omit_filename_path : bool (default False)
            Do not store path in NTD_FileName tag
"""
