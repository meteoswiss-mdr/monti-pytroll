from __future__ import division
from __future__ import print_function


def input(in_msg):

    import inspect
    in_msg.input_file = inspect.getfile(inspect.currentframe()) 
    print("*** read input from ", in_msg.input_file)

    in_msg.sat = "cosmo"
    in_msg.instrument = "cosmo"
    in_msg.sat_nr="1"
    in_msg.RSS=False  # better determine RSS automatically

    # if forecast is not yet ready, the model run before is used 
    in_msg.delay=0

    if False:
        # offline mode (always a fixed time) # ignores command line arguments
        year=2015
        month=2
        day=10
        hour=11
        minute=45
        in_msg.update_datetime(year, month, day, hour, minute)
        # !!!  if archive is used, adjust meteosat09.cfg accordingly !!!

    #----------------------
    # choose RGBs 
    #----------------------
    #----------------
    # chose RGB mode
    #-------------------
    ## satellite channels
    ##in_msg.RGBs.append('VIS006')       # black and white
    ##in_msg.RGBs.append('VIS008')       # black and white
    ##in_msg.RGBs.append('IR_016')       # black and white
    ##in_msg.RGBs.append('IR_039')       # black and white
    ##in_msg.RGBs.append('WV_062')       # black and white
    ##in_msg.RGBs.append('WV_073')       # black and white
    ##in_msg.RGBs.append('IR_087')       # black and white
    ##in_msg.RGBs.append('IR_097')       # black and white
    ##in_msg.RGBs.append('IR_108')       # black and white
    ##in_msg.RGBs.append('IR_120')       # black and white
    ##in_msg.RGBs.append('IR_134')       # black and white
    ##in_msg.RGBs.append('HRV')          # black and white
    #in_msg.RGBs.append('VIS006c')      # colored version
    #in_msg.RGBs.append('VIS008c')      # colored version
    #in_msg.RGBs.append('IR_016c')      # colored version
    #in_msg.RGBs.append('IR_039c')      # colored version
    #in_msg.RGBs.append('WV_062c')      # colored version
    #in_msg.RGBs.append('WV_073c')      # colored version
    #in_msg.RGBs.append('IR_087c')      # colored version
    #in_msg.RGBs.append('IR_097c')      # colored version
    #in_msg.RGBs.append('IR_108c')      # colored version
    #in_msg.RGBs.append('IR_120c')      # colored version
    #in_msg.RGBs.append('IR_134c')      # colored version
    #in_msg.RGBs.append('HRVc')         # colored version
    #-------------------
    # viewing geometry
    #-------------------
    #in_msg.sat = "vza"
    #in_msg.sat = "vaa"

    # satellite channel differences
    #in_msg.RGBs.append('WV_062-WV_073')
    #in_msg.RGBs.append('WV_062-IR_108')
    #in_msg.RGBs.append('WV_073-IR_134')
    #in_msg.RGBs.append('IR_087-IR_108')      
    #in_msg.RGBs.append('IR_039-IR_108')      
    #in_msg.RGBs.append('IR_120-IR_108')      
    #in_msg.RGBs.append('IR_087-IR_120')      
    #in_msg.RGBs.append('IR_120-IR_108')
    #in_msg.RGBs.append('trichannel')
    #-------------------
    # viewing geometry
    #-------------------
    #in_msg.RGBs.append('vza')   # known bug: cant be displayed for original projection, e.g. met09globeFull
    #in_msg.RGBs.append('vaa')
    #in_msg.RGBs.append('lat')
    #in_msg.RGBs.append('lon')
    #-------------------    
    # buil in RGBs, see http://mpop.readthedocs.org/en/latest/pp.html
    #                or  http://oiswww.eumetsat.int/~idds/html/doc/best_practices.pdf
    #-------------------      # RED            GREEN          BLUE
    #in_msg.RGBs.append('airmass')           # WV_062-WV_073  IR_097-IR_108  -WV_062
    #in_msg.RGBs.append('ash')               
    #in_msg.RGBs.append('cloudtop')
    #in_msg.RGBs.append('convection')         # WV_062-WV_073  IR_039-IR_108  IR_016-VIS006
    ##in_msg.RGBs.append('convection_co2')
    ##in_msg.RGBs.append('day_microphysics')   # VIS008         IR_039(solar)  IR_108     # requires the pyspectral modul 
    #in_msg.RGBs.append('dust')               # IR_120-IR_108  IR_108-IR_087  IR_108
    #in_msg.RGBs.append('fog')
    #in_msg.RGBs.append('green_snow')
    ##in_msg.RGBs.append('ir108')
    #in_msg.RGBs.append('natural')            # IR_016         VIS008         VIS006
    #in_msg.RGBs.append('night_fog')          
    #in_msg.RGBs.append('night_microphysics') # IR_120-IR_108  IR_108-IR_039  IR_108
    #in_msg.RGBs.append('night_overview')
    #in_msg.RGBs.append('overview')
    ##in_msg.RGBs.append('overview_sun')
    #in_msg.RGBs.append('red_snow')
    ##in_msg.RGBs.append('refl39_chan')        # requires the pyspectral modul
    ##in_msg.RGBs.append('snow')               # requires the pyspectral modul
    ##in_msg.RGBs.append('vis06')
    ##in_msg.RGBs.append('wv_high')
    ##in_msg.RGBs.append('wv_low')
    #-------------------
    # user defined RGBs
    #in_msg.RGBs.append('HRoverview')
    ##in_msg.RGBs.append('sandwich')
    ##in_msg.RGBs.append('ndvi')
    #in_msg.RGBs.append('sza')
    #in_msg.RGBs.append('HRVFog')
    #in_msg.RGBs.append('DayNightFog')
    ##-------------------
    ## NWC SAF
    ##-------------------
    ## NWC SAF PEG 1
    #in_msg.RGBs.append('CMa')
    #in_msg.RGBs.append('CMa_DUST')
    #in_msg.RGBs.append('CMa_VOLCANIC')
    #in_msg.RGBs.append('CMa_QUALITY')
    ## NWC SAF PEG 2
    #in_msg.RGBs.append('CT')
    #in_msg.RGBs.append('CT_PHASE')
    #in_msg.RGBs.append('CT_QUALITY')
    ## NWC SAF PEG 3 
    in_msg.nwcsaf_calibrate=True
    #in_msg.RGBs.append('CTT')
    #in_msg.RGBs.append('CTH')
    #in_msg.RGBs.append('CTP')
    ## NWC SAF PEG 4
    #in_msg.RGBs.append('CRR')
    ## NWC SAF PEG 5
    #in_msg.RGBs.append('PC')
    ## NWC SAF PEG 13 
    #in_msg.nwcsaf_calibrate=False
    #in_msg.RGBs.append('sphr_bl')
    #in_msg.RGBs.append('sphr_cape')
    #in_msg.RGBs.append('sphr_diffbl')
    #in_msg.RGBs.append('sphr_diffhl')
    #in_msg.RGBs.append('sphr_diffki')
    #in_msg.RGBs.append('sphr_diffli')
    #in_msg.RGBs.append('sphr_diffml')
    #in_msg.RGBs.append('sphr_diffshw')
    #in_msg.RGBs.append('sphr_difftpw')
    #in_msg.RGBs.append('sphr_hl')
    #in_msg.RGBs.append('sphr_ki')
    #in_msg.RGBs.append('sphr_li')
    #in_msg.RGBs.append('sphr_ml')
    #in_msg.RGBs.append('sphr_quality')
    #in_msg.RGBs.append('sphr_sflag')
    #in_msg.RGBs.append('sphr_shw')
    #in_msg.RGBs.append('sphr_tpw')
    #in_msg.RGBs.append('SPhR_BL')      # old format
    #in_msg.RGBs.append('SPhR_CAPE')    # old format
    #in_msg.RGBs.append('SPhR_HL')      # old format
    #in_msg.RGBs.append('SPhR_KI')      # old format
    #in_msg.RGBs.append('SPhR_LI')      # old format
    #in_msg.RGBs.append('SPhR_ML')      # old format
    #in_msg.RGBs.append('SPhR_QUALITY') # old format
    #in_msg.RGBs.append('SPhR_SHW')     # old format
    #in_msg.RGBs.append('SPhR_TPW')     # old format
    ## NWC SAF PEG 14
    #in_msg.RGBs.append('PCPh')
    #in_msg.RGBs.append('CRPh')
    #-------------------
    # H-SAF
    #-------------------
    #in_msg.sat = "HSAF"
    #in_msg.sat_nr=""
    #in_msg.RSS=False 
    #in_msg.RGBs.append('h03')
    #-------------------
    # CPP (cloud physical products from KNMI)
    #-------------------
    #in_msg.sat = "cpp"
    #in_msg.RGBs.append('azidiff')
    #in_msg.RGBs.append('cth')
    #in_msg.RGBs.append('cldmask')
    #in_msg.RGBs.append('cot')
    #in_msg.RGBs.append('cph')
    #in_msg.RGBs.append('ctt')
    #in_msg.RGBs.append('cwp')
    #in_msg.RGBs.append('dcld')
    #in_msg.RGBs.append('dcot')
    #in_msg.RGBs.append('dcwp')
    #in_msg.RGBs.append('dndv')
    #in_msg.RGBs.append('dreff')
    #in_msg.RGBs.append('precip')
    #in_msg.RGBs.append('precip_ir')
    #in_msg.RGBs.append('qa')
    #in_msg.RGBs.append('reff')
    #in_msg.RGBs.append('satz')
    #in_msg.RGBs.append('sds')
    #in_msg.RGBs.append('sds_cs')
    #in_msg.RGBs.append('sds_diff')
    #in_msg.RGBs.append('sds_diff_cs')
    #in_msg.RGBs.append('sunz')
    #in_msg.RGBs.append('lat')
    #in_msg.RGBs.append('lon')
    #in_msg.RGBs.append('time_offset')
    #-------------------
    # msg-ot (Overshooting tops from Bedka 2016)
    #-------------------
    #in_msg.RGBs.append('ir_brightness_temperature')
    #in_msg.RGBs.append('ot_rating_ir')
    #in_msg.RGBs.append('ot_id_number')
    #in_msg.RGBs.append('ot_anvilmean_brightness_temperature_difference')
    #in_msg.RGBs.append('ir_anvil_detection')
    #in_msg.RGBs.append('visible_reflectance')
    #in_msg.RGBs.append('ot_rating_visible')
    #in_msg.RGBs.append('ot_rating_shadow')
    #in_msg.RGBs.append('ot_probability')
    #in_msg.RGBs.append('surface_based_cape')
    #in_msg.RGBs.append('most_unstable_cape')
    #in_msg.RGBs.append('most_unstable_equilibrium_level_temperature')
    #in_msg.RGBs.append('tropopause_temperature')
    #in_msg.RGBs.append('surface_1km_wind_shear')
    #in_msg.RGBs.append('surface_3km_wind_shear')
    #in_msg.RGBs.append('surface_6km_wind_shear')
    #in_msg.RGBs.append('ot_potential_temperature')
    #in_msg.RGBs.append('ot_height')
    #in_msg.RGBs.append('ot_pressure')
    #in_msg.RGBs.append('parallax_correction_latitude')
    #in_msg.RGBs.append('parallax_correction_longitude')
    #-------------------
    # COSMO (cosmo1)
    #-------------------
    in_msg.sat = "cosmo"
    in_msg.instrument = "cosmo"
    in_msg.sat_nr="1"
    in_msg.pressure_levels={}
    #in_msg.RGBs.append('lon_1')
    #in_msg.RGBs.append('lat_1')
    #in_msg.RGBs.append('TWATER')
    #in_msg.RGBs.append('tropopause_height')
    #in_msg.RGBs.append('tropopause_temperature')
    #in_msg.RGBs.append('tropopause_pressure')
    #in_msg.RGBs.append('FF_10M')
    #in_msg.RGBs.append('VMAX_10M')
    #in_msg.RGBs.append('CAPE_MU')
    #in_msg.RGBs.append('CAPE_ML')
    #in_msg.RGBs.append('CIN_MU')
    #in_msg.RGBs.append('CIN_ML')
    #in_msg.RGBs.append('SLI')
    #in_msg.RGBs.append('LCL_ML')
    #in_msg.RGBs.append('LFC_ML')
    #in_msg.RGBs.append('T_SO')
    #in_msg.RGBs.append('T_2M')
    #in_msg.RGBs.append('TD_2M')
    #in_msg.RGBs.append('GLOB')
    #in_msg.RGBs.append('PS')
    #in_msg.RGBs.append('PMSL')
    #in_msg.RGBs.append('PMSLr')
    #in_msg.RGBs.append('HZEROCL')
    #in_msg.RGBs.append('WSHEAR_0-3km')
    #in_msg.RGBs.append('WSHEAR_0-6km')
    #in_msg.RGBs.append('SYNMSG_BT_CL_IR10.8')
    in_msg.RGBs.append('SDI_2')
    #in_msg.RGBs.append('SWISS12')
    in_msg.RGBs.append('SOILTYP')
               
    #in_msg.pressure_levels["POT_VORTIC"]=[700,500,300]    
    #in_msg.RGBs.append('POT_VORTIC')
    #in_msg.pressure_levels["THETAE"]=[700,500,300]    
    #in_msg.RGBs.append('THETAE')
    #in_msg.pressure_levels["MCONV"]=[700,500,300]
    #in_msg.RGBs.append('MCONV')
    #in_msg.pressure_levels["geopotential_height"]=[700,500,300]
    #in_msg.RGBs.append('geopotential_height')
    #in_msg.pressure_levels["RELHUM"]=[850,750]
    #in_msg.RGBs.append('RELHUM')
    in_msg.pressure_levels["OMEGA"]=[700]
    in_msg.RGBs.append('OMEGA')
    #in_msg.pressure_levels["W_SO"]=[0]
    #in_msg.RGBs.append('W_SO')

    #in_msg.RGBs.append('U')
    #in_msg.RGBs.append('U-100hPa')
    #in_msg.pressure_levels["U"]=[800,500,300]
    #in_msg.RGBs.append('V')
    #in_msg.pressure_levels["V"]=[800,500,300]
    #in_msg.RGBs.append('streamplot')
    #in_msg.RGBs.append('streamplot-300hPa')
    #in_msg.RGBs.append('streamplot-500hPa')
    #in_msg.RGBs.append('streamplot-800hPa')
    
    # experimental
    #in_msg.RGBs.append('clouddepth')     # test according to Mecikalski, 2010
    ##in_msg.RGBs.append('RII')
    
    #----------------
    # chose area
    #----------------
    in_msg.areas.append('ccs4')             # CCS4 Swiss projection 710x640
    #in_msg.areas.append('alps95')          # area around Switzerland processed by NWCSAF software 349x151 
    #in_msg.areas.append('ticino')          # stereographic proj of Ticino 342x311
    #in_msg.areas.append('germ')            # Germany 1024x1024
    #in_msg.areas.append('EuropeCanary')    # upper third of MSG disk, satellite at 0.0 deg East, full resolution 
    #in_msg.areas.append('EuropeCanary95')  # upper third of MSG disk, satellite at 9.5 deg East, full resolution 
    #in_msg.areas.append('EuropeCanaryS95') # upper third of MSG disk, satellite at 9.5 deg East, reduced resolution 1000x400
    #in_msg.areas.append('euro4')           # Europe 4km, 1024x1024
    #in_msg.areas.append('nrEURO1km')       # Switzerland 1.056km for COALTION
    #in_msg.areas.append('euroHDready')      # Europe in HD resolution 1280 x 720
    #in_msg.areas.append('MSGHRVN')         # High resolution northern quarter 11136x2784
    #in_msg.areas.append('fullearth')       # full earth 600x300                    # does not yet work
    #in_msg.areas.append('met09globe')      # Cropped globe MSG image 3620x3620     # does not yet work
    #in_msg.areas.append('met09globeFull')  # Full    globe MSG image 3712x3712     # does not yet work
    #in_msg.areas.append('odysseyS25')      # Area of Odyssey composite (factor 2.5 smaller)
    #in_msg.areas.append("nrEURO1km")
    #in_msg.areas.append("EuroMercator")    # same projection as blitzortung.org

    in_msg.check_RSS_coverage()

    # please download the shape file 
    # in_msg.mapDir='/data/OWARNA/hau/maps_pytroll/'
    in_msg.mapResolution=None      ## f  full resolution: Original (full) data resolution.          
                                   ## h  high resolution: About 80 % reduction in size and quality. 
                                   ## i  intermediate resolution: Another ~80 % reduction.          
                                   ## l  low resolution: Another ~80 % reduction.                   
                                   ## c  crude resolution: Another ~80 % reduction.   
    
    # switch off Rapid scan, if large areas are wanted 
    if ('fullearth' in in_msg.areas) or ('met09globe' in in_msg.areas) or ('met09globeFull' in in_msg.areas): 
       in_msg.RSS=False 

    in_msg.check_input = False
    #in_msg.reader_level="seviri-level4" 
    #in_msg.parallax_correction = True
    #in_msg.estimate_cth=True
    #in_msg.parallax_gapfilling = 'bilinear' # 'False' (default), 'nearest', 'bilinear'
    #in_msg.save_reprojected_data=['ccs4']
    in_msg.reprojected_data_filename='%(msg)s_%(area)s_%Y%m%d%H%M_nwcsaf.nc'
    in_msg.reprojected_data_dir='/data/COALITION2/database/meteosat/ccs4/%Y/%m/%d/'
    in_msg.save_statistics=False

    in_msg.make_plots=True
    in_msg.fill_value=(0,0,0)  # black (0,0,0) / white (1,1,1) / transparent None  
    in_msg.add_title = True
    in_msg.title = [" %(sat)s, %Y-%m-%d %H:%MUTC, %(area)s, %(rgb)s"]
    in_msg.title_y_line_nr = 1  # (INT) at which line should the title start
    in_msg.add_borders = True
    in_msg.border_color = 'red'
    in_msg.add_rivers = False
    in_msg.river_color = 'blue'
    in_msg.add_logos = False
    in_msg.logos_dir = "/opt/users/common/logos/"
    in_msg.add_colorscale = True
    in_msg.HRV_enhancement = False

    in_msg.outputFormats = ['png'] 
    #in_msg.outputFormats = ['png','ninjotif'] 
    in_msg.outputFile = 'COSMO_%(rgb)s-%(area)s_%y%m%d%H%M.png'
    in_msg.outputDir='./pics/'
    #in_msg.outputDir = "./%Y-%m-%d/%Y-%m-%d_%(rgb)s-%(area)s/"
    in_msg.outputDir = '/data/cinesat/out/'
    #in_msg.outputDir = '/data/COALITION2/PicturesSatellite/%Y-%m-%d/%Y-%m-%d_%(rgb)s_%(area)s/'
    in_msg.compress_to_8bit=False

    
    in_msg.ninjotifFilename = 'MET%(sat_nr)s_%(RSS)s_%(rgb)s_%(area)s_%Y%m%d%H%M.tif' 
    in_msg.upload_ninjotif = False

    #in_msg.postprocessing_areas=['ccs4']
    #in_msg.postprocessing_areas=['EuropeCanaryS95']
    #in_msg.postprocessing_areas=["EuroMercator"]

    #in_msg.postprocessing_montage = [["MSG_IR-108c","COSMO_SYNMSG-BT-CL-IR10.8"]]
    in_msg.postprocessing_montage = [["MSG_IR-108cpc","COSMO_SYNMSG-BT-CL-IR10.8"]]

    #in_msg.resize_montage = 70
    #in_msg.resize_composite = 100

    in_msg.scpOutput = False
    #in_msg.scpOutputDir="las@lomux240:/www/proj/OTL/WOL/cll/satimages"  # default in scp_settings.py
    #in_msg.scpID="-i /home/cinesat/.ssh/id_rsa_las"                     # default in scp_settings.py
    #default: in_msg.scpProducts = ['all']
    #in_msg.scpProducts = [["MSG_IR-108cpc","COSMO_SYNMSG-BT-CL-IR10.8"]]
    #in_msg.scpProducts = ["IR-108cpc-SYNMSG-BT-CL-IR10.8"]
    #in_msg.scpProducts = ['IR_108c', "radar-convection"] # list of rgb, composite and montage strings
