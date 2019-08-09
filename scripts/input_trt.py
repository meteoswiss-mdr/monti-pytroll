
def input(in_msg):

    import inspect
    in_msg.input_file = inspect.getfile(inspect.currentframe()) 
    print "*** read input from ", in_msg.input_file

    in_msg.sat    = "swisstrt"
    in_msg.sat_nr = "04"
    in_msg.instrument = "radar"
    in_msg.RSS = True 
    
    # specify an delay (in minutes), when you like to process a time some minutes ago
    # e.g. current time               2015-05-31 12:33 UTC
    # delay 5 min                     2015-05-31 12:28 UTC
    # last Rapid Scan Service picture 2015-05-31 12:25 UTC (Scan start) 
    in_msg.delay=5

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
    in_msg.RGBs.append('TRTcells')       # black and white'TRTcells'
    #in_msg.TRT_cell='2014072316550030'
    
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
    #in_msg.mapDir='/data/OWARNA/hau/maps_pytroll/'
    in_msg.mapDir='/opt/users/common/shapes/'
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
    in_msg.add_colorscale = False
    in_msg.HRV_enhancement = False

    in_msg.outputFormats = ['png'] 
    #in_msg.outputFormats = ['png','ninjotif'] 
    in_msg.outputFile = 'MSG_%(rgb)s-%(area)s_%y%m%d%H%M.png'
    in_msg.outputDir='./pics/'
    #in_msg.outputDir = "./%Y-%m-%d/%Y-%m-%d_%(rgb)s-%(area)s/"
    #in_msg.outputDir = '/data/cinesat/out/'
    #in_msg.outputDir = '/data/COALITION2/PicturesSatellite/%Y-%m-%d/%Y-%m-%d_%(rgb)s_%(area)s/'
    in_msg.compress_to_8bit=False

    
    in_msg.ninjotifFilename = 'MET%(sat_nr)s_%(RSS)s_%(rgb)s_%(area)s_%Y%m%d%H%M.tif' 
    in_msg.upload_ninjotif = False

    #in_msg.postprocessing_areas=['ccs4']
    #in_msg.postprocessing_areas=['EuropeCanaryS95']
    #in_msg.postprocessing_areas=["EuroMercator"]

    #in_msg.postprocessing_composite=["h03-ir108"]
    #in_msg.postprocessing_composite=["hrwdp-ir108"]
    #in_msg.postprocessing_composite=["CTT-ir108","CTH-ir108"]
    #in_msg.postprocessing_composite=["hrwdp-ir108", "hrwdc-ir108","streamd-ir108","hrwdr-ir108", "hrwdcnwp-ir108", "hrwdcnnwp-ir108"]
    #in_msg.postprocessing_composite=["hrwdr-ir108", "hrwdcnwp-ir108", "hrwdcnnwp-ir108", "streamd-ir108"]
    #in_msg.postprocessing_composite=["TRT-streamd-ir108", "TRT-streamd-HRV"] #"hrwdCT-ir108", "hrwdCT-HRV"
    #in_msg.postprocessing_composite=["TRT-radar-ir108pc"] #"hrwdCT-ir108", "hrwdCT-HRV"
    #in_msg.postprocessing_composite=["THX-IR_108","radar-convection","THX-radar-convection"]    
    #in_msg.postprocessing_composite=["THX-IR_108"] #"hrwdCT-ir108", "hrwdCT-HRV"
    #in_msg.postprocessing_composite=["THX-HRV"] #"hrwdCT-ir108", "hrwdCT-HRV"
    #in_msg.postprocessing_composite=["THX-HRVpc"] #"hrwdCT-ir108", "hrwdCT-HRV"
    #in_msg.postprocessing_composite=["TRT-radar-ir108pc","THX-HRVpc"]
    #in_msg.postprocessing_composite=["C2rgb-IR_108","C2rgb-ir108"]
    #in_msg.postprocessing_composite=["C2rgb-IR_108pc"]
    #in_msg.postprocessing_composite=["C2rgb-IR_108"]
    #in_msg.postprocessing_composite=["C2rgb-ir108"]
    #in_msg.postprocessing_composite=["hrwdpH-streamdH-HRV", "hrwdpM-streamdM-HRV", "hrwdpL-streamdL-HRV"] #"hrwdCT-ir108", "hrwdCT-HRV"
    #in_msg.postprocessing_composite=["hrwdp-streamd-HRV", "hrwdp-streamd-ir108"] #"hrwdCT-ir108", "hrwdCT-HRV"
    #in_msg.postprocessing_composite=["hrwdpL-streamdL-HRV","hrwdpL-streamdL-ir108"]
    #in_msg.postprocessing_composite=["hrwdpH-streamdH-HRV","hrwdpH-streamdH-ir108"]
    #in_msg.postprocessing_composite=["hrwdp-streamd-ir108","TRT-streamd-ir108"]
    #in_msg.postprocessing_composite=["TRT-radar-convection"] # "radar-convection",

    #in_msg.postprocessing_montage = [["MSG_radar-ir108","MSG_h03-ir108"],["MSG_radar-HRV","MSG_h03-HRV"],["MSG_RATE-ir108","MSG_h03-ir108"],["MSG_RATE-HRV","MSG_h03-HRV"]]
    #in_msg.postprocessing_montage = [["MSG_h03-ir108","MSG_HRV"],["MSG_h03-ir108","MSG_test"]]
    #in_msg.postprocessing_montage = [["MSG_C2rgb-IR-108","MSG_CT","MSG_HRoverview","MSG_TRT-radar-convection","MSG_radar-convection","MSG_THX-radar-convection"]]
    #in_msg.postprocessing_montage = [["MSG_C2rgb-Forecast-IR_108","MSG_CT","MSG_HRoverview","MSG_TRT-radar-convection","MSG_radar-convection","MSG_THX-radar-convection"]]
    #in_msg.postprocessing_montage = [["MSG_C2rgb-IR-108","MSG_CT","MSG_HRoverview","MSG_TRT-radar-ir108","MSG_radar-ir108","MSG_THX-ir108"]]
    #in_msg.postprocessing_montage = [["MSG_C2rgb-IR-108","MSG_CT","MSG_HRoverview","MSG_TRT-radar-ir108","MSG_radar-ir108","MSG_THX-ir108"]]
    #in_msg.postprocessing_montage = [["MSG_C2rgb-IR-108","MSG_CT","MSG_HRoverview","MSG_TRT-radar-convection","MSG_radar-convection","MSG_THX-HRV"]]
    #in_msg.postprocessing_montage = [["MSG_C2rgb-IR-108","MSG_CT","MSG_HRoverview","MSG_TRT-radar-ir108","MSG_radar-ir108","MSG_THX-HRV"]]
    #in_msg.postprocessing_montage = [["MSG_C2rgb-IR-108","MSG_CT","MSG_overview","MSG_convection","MSG_RATE-convection","MSG_THX-IR-108"]]
    #in_msg.postprocessing_montage = [["MSG_C2rgb-IR-108","MSG_CT","MSG_HRoverview","MSG_TRT-radar-ir108","MSG_radar-ir108","MSG_THX-ir108"]]
    #in_msg.postprocessing_montage = [["MSG_C2rgb-IR-108","MSG_CTpc","MSG_HRoverviewpc","MSG_TRT-radar-ir108pc","MSG_radar-ir108pc","MSG_THX-HRVpc"]]

    #in_msg.resize_montage = 70
    #in_msg.resize_composite = 100

    #in_msg.scpOutput = True
    #default: in_msg.scpOutputDir="las@lomux240:/www/proj/OTL/WOL/cll/satimages"
    #default: in_msg.scpID="-i /home/cinesat/.ssh/id_dsa_las"
    #default: in_msg.scpProducts = ['all']
    #in_msg.scpProducts = ['IR_108c', "radar-convection"] # list of rgb, composite and montage strings
