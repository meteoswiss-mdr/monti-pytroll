
def input(in_msg):

    print "*** read input from input_coalition2.py"

    #------------------------------------------------------------------------
    # if not specified (False), current (last) observation time is chosen  
    # chosse specification, if you want a default time without command line arguments 
    # (the specified time is overwritten by the command line arguments of plot_msg.py)
    #------------------------------------------------------------------------
    if False:
        year=2015
        month=2
        day=10
        hour=11
        minute=45
        in_msg.update_datetime(year, month, day, hour, minute)
        # !!!  if archive is used, adjust meteosat09.cfg accordingly !!!

    # specify an delay (in minutes), when you like to process a time some minutes ago
    # e.g. current time               2015-05-31 12:33 UTC
    # delay 5 min                     2015-05-31 12:28 UTC
    # last Rapid Scan Service picture 2015-05-31 12:25 UTC (Scan start) 
    in_msg.delay=0

    #----------------
    # chose area
    #----------------
    #in_msg.areas.append('ccs4')             # CCS4 Swiss projection 710x640
    #in_msg.areas.append('alps95')          # area around Switzerland processed by NWCSAF software 349x151 
    #in_msg.areas.append('ticino')          # stereographic proj of Ticino 342x311
    #in_msg.areas.append('germ')            # Germany 1024x1024
    #in_msg.areas.append('EuropeCanary')    # upper third of MSG disk, satellite at 0.0 deg East, full resolution 
    #in_msg.areas.append('EuropeCanary95')  # upper third of MSG disk, satellite at 9.5 deg East, full resolution 
    #in_msg.areas.append('EuropeCanaryS95') # upper third of MSG disk, satellite at 9.5 deg East, reduced resolution 1000x400
    #in_msg.areas.append('euro4')           # Europe 4km, 1024x1024
    #in_msg.areas.append('MSGHRVN')         # High resolution northern quarter 11136x2784
    #in_msg.areas.append('fullearth')       # full earth 600x300                    # does not yet work
    #in_msg.areas.append('met09globe')      # Cropped globe MSG image 3620x3620     # does not yet work
    #in_msg.areas.append('met09globeFull')  # Full    globe MSG image 3712x3712     # does not yet work
    #in_msg.areas.append('odysseyS25')      # Area of Odyssey composite (factor 2.5 smaller)
    #in_msg.area = 'ccs4'
    in_msg.area = "EuropeCanaryS95" # "ccs4" "blitzortung" #"eurotv" # "eurotv"

    # set cloud mask 
    #-------------------------
    #in_msg.show_clouds = 'all'
    #in_msg.show_clouds = 'developing'
    #in_msg.show_clouds = 'mature'
    in_msg.show_clouds = 'developing_and_mature'

    in_msg.use_TB_forecast = True    # use forecasted brightness temperatures (wind data required)
    in_msg.use_TB_forecast = False   # use brightness temperatures without lagrangian displacement 

    # directory containing the forecasted brightness temperatures
    in_msg.nowcastDir="/data/cinesat/out/"
    #in_msg.nowcastDir="/data/COALITION2/PicturesSatellite/LEL_results_wind//"+yearS+"-"+monthS+"-"+dayS+"/channels/" 
    #in_msg.nowcastDir="/opt/users/lel/PyTroll/scripts/channels_new//" 

    in_msg.mode_downscaling = 'gaussian_225_125'
    #in_msg.mode_downscaling = 'convolve_405_300'
    #in_msg.mode_downscaling = 'gaussian_150_100'
    #in_msg.mode_downscaling = 'no_downscaling'

    in_msg.mask_labelsSmall_lowUS = True   # ???
    in_msg.mask_labelsSmall_lowUS = False  # ???

    in_msg.clean_mask = 'skimage' 
    #in_msg.clean_mask = 'scipy' 
    #in_msg.clean_mask = 'both' 
    #in_msg.clean_mask = 'no_cleaning'

    in_msg.rapid_scan_mode = False   # use 15 and 30min for estimating the updraft
    #in_msg.rapid_scan_mode = True   # use  5 and 10min for estimating the updraft (useful if no wind data is available)


    in_msg.forced_mask = 'no_mask'              
    #in_msg.forced_mask = 'IR_039_minus_IR_108'  # force to include any pixel (in mature_mask) regardless of the other thresholds
    #in_msg.forced_mask = 'CloudType'

    #-----------------------------
    # choose production of results
    #-----------------------------
    in_msg.results = ['C2rgb']
    # --------------------------------------
    # choose production of auxiliary results
    # --------------------------------------
    # mask that removed the thin cirrus
    in_msg.aux_results=[]
    in_msg.aux_results.append('mask_cirrus')
    in_msg.aux_results.append('tests_glationation')
    in_msg.aux_results.append('tests_optical_thickness')
    in_msg.aux_results.append('tests_updraft')
    in_msg.aux_results.append('tests_small_ice')
    in_msg.aux_results.append('indicator_glationation')
    in_msg.aux_results.append('indicator_optical_thickness')
    in_msg.aux_results.append('indicator_updraft')
    in_msg.aux_results.append('indicator_small_ice')
    in_msg.aux_results.append('labelled_objects')
    in_msg.aux_results.append('final_mask')
    in_msg.aux_results.append('forced_mask')
    in_msg.aux_results.append('mature_mask')
    in_msg.aux_results.append('developing_mask')
    in_msg.aux_results.append('IR_108')
  

    # please download the shape file 
    in_msg.mapDir='/data/OWARNA/hau/maps_pytroll/'
    in_msg.mapResolution='i'       ## f  full resolution: Original (full) data resolution.          
                                   ## h  high resolution: About 80 % reduction in size and quality. 
                                   ## i  intermediate resolution: Another ~80 % reduction.          
                                   ## l  low resolution: Another ~80 % reduction.                   
                                   ## c  crude resolution: Another ~80 % reduction. 
                                   ## None -> automatic choise

    #in_msg.sat = "meteosat"  # default "meteosat"
    # 8=MSG1, 9=MSG2, 10=MSG3
    #in_msg.sat_nr=8
    #in_msg.RSS=False 
    in_msg.sat_nr=9
    in_msg.RSS=True
    #in_msg.sat_nr=10
    #in_msg.RSS=False 

    in_msg.reader_level="seviri-level2"
    #in_msg.reader_level="seviri-level4" 

    #in_msg.outputDir='./pics/'
    #in_msg.outputDir = "./%Y-%m-%d/%Y-%m-%d_%(rgb)s-%(area)s/"
    #in_msg.outputDir = '/data/cinesat/out/'
    in_msg.outputDir = '/data/COALITION2/PicturesSatellite/%Y-%m-%d/%Y-%m-%d_%(rgb)s_%(area)s/'
    #if in_msg.only_obs_noForecast == True:
    #    in_msg.outputDir = "/opt/users/lel/PyTroll/scripts//Mecikalski_obs/"
    #elif in_msg.RSS == True:
    #    in_msg.outputDir = "/opt/users/lel/PyTroll/scripts//Mecikalski_RapidScan/"
    #else:
    #    in_msg.outputDir = "/opt/users/lel/PyTroll/scripts//Mecikalski/"

    #in_msg.postprocessing_areas=['ccs4']
    in_msg.postprocessing_composite=["C2rgb-IR_108","C2rgb-HRV"]    

    in_msg.scpOutput = True
    #default: in_msg.scpOutputDir="las@lomux240:/www/proj/OTL/WOL/cll/satimages"
    #default: in_msg.scpID="-i /home/cinesat/.ssh/id_dsa_las"

    # switch off Rapid scan, if large areas are wanted 
    if ('fullearth' in in_msg.areas) or ('met09globe' in in_msg.areas) or ('met09globeFull' in in_msg.areas): 
       in_msg.RSS=False 

    # make some automatic adjustments to the input 
    europe_areas = ["eurotv","blitzortung","EuropeCanaryS95"]
    if in_msg.area not in europe_areas:
        scale = "local"
    else:
        scale = "europe"

    if scale == "europe":
        print "*** activated Europe version"
        print "    activate rapid scan mode, no downscaling, "
        print "    no TB forecasts, no cleaning and mask_labelsSmall_lowUS ???"
        in_msg.rapid_scan_mode = True
        in_msg.mode_downscaling = 'no_downscaling'
        in_msg.use_TB_forecast = False
        in_msg.clean_mask = 'no_cleaning'
        in_msg.mask_labelsSmall_lowUS = False

    # -------------   
    # input checks 
    # -------------   
    if in_msg.area in europe_areas:
        if in_msg.use_TB_forecast == True:
            print "*** Error in plot_coalition2.py"
            print "    currently no brightness temperature forecast"
            print "    implemented for areas outside Switzerland"
            quit()

    # -------------   
    # input checks 
    # -------------   
    if in_msg.verbose:
        print "*** Given input:"
        print "    in_msg.sat: ", in_msg.sat, in_msg.sat_nr
        print "    in_msg.area: ", in_msg.area
        print "    in_msg.delay: ", in_msg.delay
        print "    in_msg.show_clouds: ", in_msg.show_clouds
        print "    in_msg.use_TB_forecast: ", in_msg.use_TB_forecast
        if in_msg.use_TB_forecast:
            print "    in_msg.nowcastDir: ", in_msg.nowcastDir
        print "    in_msg.rapid_scan_mode: ", in_msg.rapid_scan_mode
        print "    in_msg.results: ", in_msg.results
        print "    in_msg.aux_results: ", in_msg.aux_results
        print "    in_msg.outputDir: ", in_msg.outputDir
        print "    in_msg.postprocessing_areas: ", in_msg.postprocessing_areas
        print "    in_msg.postprocessing_composite: ", in_msg.postprocessing_composite

    #in_msg.check_input = False

    #in_msg.make_plots=True
    #in_msg.fill_value=(0,0,0)  # black (0,0,0) / white (1,1,1) / transparent None  
    #in_msg.add_title = True
    #in_msg.add_borders = True
    #in_msg.border_color = 'red'
    #in_msg.add_rivers = False
    #in_msg.river_color = 'blue'
    #in_msg.add_logos = False
    #in_msg.add_colorscale = False
    #in_msg.HRV_enhancement = False

    #in_msg.outputFile = 'MSG_%(rgb)s-%(area)s_%y%m%d%H%M.png'

    #in_msg.compress_to_8bit=False
    
