from __future__ import division
from __future__ import print_function

def input(in_msg, timeslot=None):

    import inspect
    in_msg.input_file = inspect.getfile(inspect.currentframe()) 
    print("*** read input from ", in_msg.input_file)
    import getpass

    #in_msg.sat = "meteosat"  # default "meteosat"
    in_msg.sat = "meteosat"
    #in_msg.sat = "Meteosat"
    # 8=MSG1, 9=MSG2, 10=MSG3
    #in_msg.sat_nr=8
    #in_msg.RSS=False 
    in_msg.sat_nr=9
    in_msg.RSS=True
    #in_msg.sat_nr=10
    #in_msg.RSS=True
    #in_msg.sat_nr=11
    #in_msg.RSS=False

    # specify an delay (in minutes), when you like to process a time some minutes ago
    # e.g. current time               2015-05-31 12:33 UTC
    # delay 5 min                     2015-05-31 12:28 UTC
    # last Rapid Scan Service picture 2015-05-31 12:25 UTC (Scan start) 
    in_msg.delay=6   # start 3, 8, 13, 18 ...

    #------------------------------------------------------------------------
    # if not specified (False), current (last) observation time is chosen  
    # choose specification, if you want a default time without command line arguments 
    # (the specified time is overwritten by the command line arguments of plot_msg.py)
    #------------------------------------------------------------------------
    if False:
        # offline mode (always a fixed time) # ignores command line arguments
        year=2015
        month=2
        day=10
        hour=11
        minute=45
        in_msg.update_datetime(year, month, day, hour, minute)
        # !!!  if archive is used, adjust meteosat09.cfg accordingly !!!
        
    if timeslot is not None:
        in_msg.update_datetime(timeslot.year, timeslot.month, timeslot.day, timeslot.hour, timeslot.minute)
    
    in_msg.no_NWCSAF = False

    #----------------
    # chose area
    #----------------
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
    in_msg.areas.append('ccs4')             # CCS4 Swiss projection 710x640 (should be second after Europe)
    #in_msg.areas.append('EuropeCanaryS95') # "ccs4" "blitzortung" #"eurotv" # "eurotv"
    #in_msg.areas.append("EuroMercator")    # same projection as blitzortung.org

    in_msg.check_RSS_coverage()

    in_msg.properties_cells = False
    in_msg.plot_forecast = False
    
    #model which will be used to fit the history of the cells and extrapolate the future area
    #in_msg.model_fit_area = "linear_exp"    # reccomended
    in_msg.model_fit_area = "linear_exp_exp" # reccomended
    #in_msg.model_fit_area = "linear"
    
    in_msg.stop_history_when_smallForward = False
    in_msg.stop_history_when_smallBackward = False
    in_msg.threshold_stop_history_when_small = 0.4

    in_msg.px_cut = 70 #set to 0 in validation (want to track cells wherever they are?); else reccomended 70

    in_msg.area_forecast = "ccs4c2" #reccomended: this way extra borders that allow to always have values within ccs4 area (but slower)
    #in_msg.area_forecast = "ccs4" 
             
    in_msg.integration_method_velocity = "euler"
    #in_msg.integration_method_velocity = "rk4" 
    
    #in_msg.wind_source = "HRV"
    in_msg.wind_source = "cosmo"
    in_msg.zlevel = 'pressure' 
    #in_msg.zlevel = 'modellevel'

    # bounaries for cloud layers in hPa when extrapolating the cloud positions in 3 layers (with different winds)
    in_msg.pressure_limits = [440,680] #[400,700] #[]#[150,250,350,450,550,650,750,850]# #[250,400] #[300,500]#
    
    in_msg.broad_areas = ['eurotv','blitzortung','EuropeCanaryS95','EuropeCanary95','germ','EuropeCanary','euro4','fullearth','met09globe','met09globeFull','odysseyS25']
    
    in_msg.areasNoRapidScan = ['fullearth','met09globe','met09globeFull'] #should also be changed to coordinates check!!!!
      
    in_msg.settings = "default" # the settings will be automatically defined depending on the area chosen
    #in_msg.settings == "manual"

    
    # set cloud mask 
    #-------------------------
    #in_msg.show_clouds = 'all'
    #in_msg.show_clouds = 'developing'
    #in_msg.show_clouds = 'mature'
    in_msg.show_clouds = 'developing_and_mature'

    if in_msg.nrt:
        in_msg.base_dir_sat  = "/data/cinesat/in/eumetcast1/"
        in_msg.base_dir_ctth = "/data/cinesat/in/safnwc/"
        in_msg.base_dir_ct   = "/data/cinesat/in/safnwc/"
        in_msg.nowcastDir    = "/data/cinesat/out/C2-BT-forecasts/"                                                          # directory containing the forecasted brightness temperatures
        in_msg.labelsDir     = '/data/cinesat/out/labels/'
    else:
        #base_dir_sat  = in_msg.datetime.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/%Y/%m/%d/")
        in_msg.base_dir_sat  = in_msg.datetime.strftime("/data/COALITION2/database/meteosat/radiance_HRIT/case-studies/%Y/%m/%d/")
        in_msg.base_dir_ctth = in_msg.datetime.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/CTTH/")    # NWCSAF produced by MeteoSwiss with RSS
        in_msg.base_dir_ct   = in_msg.datetime.strftime("/data/COALITION2/database/meteosat/SAFNWC_v2016/%Y/%m/%d/CT/")      # NWCSAF produced by MeteoSwiss with RSS
        #base_dir_ctth = in_msg.datetime.strftime("/data/OWARNA/hau/database/meteosat/SAFNWC/%Y/%m/%d/CTTH/")                # NWCSAF produced by EUMETSAT   with FDS
        in_msg.nowcastDir    = '/data/COALITION2/database/meteosat/rad_forecast/%Y-%m-%d/channels/'                          # directory containing the forecasted brightness temperatures
        in_msg.labelsDir     = '/data/COALITION2/PicturesSatellite/%Y-%m-%d/%Y-%m-%d_labels_%(area)s/'
        #in_msg.labelsDir     = '/opt/users/'+in_msg.user+'/PyTroll/scripts/labels/'
        
    # channels needed to produce the coalition2 product
    in_msg.RGBs=[]
    in_msg.RGBs.append('IR_039')
    in_msg.RGBs.append('WV_062')
    in_msg.RGBs.append('WV_073')
    in_msg.RGBs.append('IR_087')
    in_msg.RGBs.append('IR_097')
    in_msg.RGBs.append('IR_108')
    in_msg.RGBs.append('IR_120')
    in_msg.RGBs.append('IR_134')
    #in_msg.RGBs.append('HRV')      # for luminance
    in_msg.nwcsaf_calibrate=True
    #in_msg.RGBs.append('CTH')

    #-----------------------------
    # choose production of results
    #-----------------------------
    in_msg.results = ['C2rgb']
    in_msg.outputFormats = ['png']  # only for 'C2rgb'
    #in_msg.outputFormats = ['png','ninjotif']  # only for 'C2rgb'
    in_msg.ninjotifFilename = 'MET%(sat_nr)s_%(RSS)s_COALITION2_%(area)s_%Y%m%d%H%M.tif' 
    in_msg.upload_ninjotif = False
    in_msg.results.append('C2rgbHRV')
    # --------------------------------------
    # choose production of auxiliary results
    # --------------------------------------
    # mask that removed the thin cirrus
    in_msg.aux_results=[]
    #in_msg.aux_results.append('mask_cirrus')
    in_msg.aux_results.append('tests_glationation')
    in_msg.aux_results.append('tests_optical_thickness')
    in_msg.aux_results.append('tests_updraft')
    in_msg.aux_results.append('tests_small_ice')
    in_msg.aux_results.append('indicator_glationation')
    in_msg.aux_results.append('indicator_optical_thickness')
    in_msg.aux_results.append('indicator_updraft')
    in_msg.aux_results.append('indicator_small_ice')
    #in_msg.aux_results.append('CloudType')
    #in_msg.aux_results.append('fourth_mask')
    #in_msg.aux_results.append('developing_mask')
    #in_msg.aux_results.append('mature_mask')
    #in_msg.aux_results.append('final_mask')
    #in_msg.aux_results.append('forced_mask')
    #in_msg.aux_results.append('labelled_objects')
    #in_msg.aux_results.append('IR_108')
    #in_msg.aux_results.append('labels_tracked')
    #in_msg.aux_results.append('forecast_channels')
    #in_msg.aux_results.append('IR_108')
    #in_msg.aux_results.append('IR_108_t1')
    #in_msg.aux_results.append('IR_108_t2')
    #in_msg.aux_results.append('mask_downscale')


    # please download the shape file 
    #in_msg.mapDir='/data/OWARNA/hau/maps_pytroll/'
    in_msg.mapResolution='i'       ## f  full resolution: Original (full) data resolution.          
                                   ## h  high resolution: About 80 % reduction in size and quality. 
                                   ## i  intermediate resolution: Another ~80 % reduction.          
                                   ## l  low resolution: Another ~80 % reduction.                   
                                   ## c  crude resolution: Another ~80 % reduction. 
                                   ## None -> automatic choise

    # switch off Rapid scan, if large areas are wanted 
    if ('fullearth' in in_msg.areas) or ('met09globe' in in_msg.areas) or ('met09globeFull' in in_msg.areas): 
       in_msg.RSS=False 

    in_msg.forecasts_in_rapid_scan_mode = False #reccomended: easier to see development in 30-15-0 minutes comparisons   # for MSG3 the only possible
    #in_msg.forecasts_in_rapid_scan_mode = True

    if in_msg.RSS==False:
        print("*** Warning: use TB forecast in 15min mode, as they are only available every 15min")
        in_msg.forecasts_in_rapid_scan_mode = False
    
    in_msg.choose_forecast_times()

    in_msg.standardOutputName = 'MSG_%(rgb)s-%(area)s_%y%m%d%H%M.png'
    if in_msg.nrt:
        #in_msg.outputDir = '/data/COALITION2/tmp/'
        #in_msg.outputDir = '/data/cinesat/out/'
        in_msg.outputDir='./pics/'
    else:
        #in_msg.outputDir='./pics/'
        in_msg.outputDir = '/data/COALITION2/PicturesSatellite/%Y-%m-%d/%Y-%m-%d_%(rgb)s_%(area)s/'

    if in_msg.nrt:
        in_msg.outputDirForecasts = "/data/cinesat/out/" #'/opt/users/'+in_msg.user+'/PyTroll/scripts/nrt_test/' #
    else:
        in_msg.outputDirForecasts = '/data/COALITION2/PicturesSatellite/%Y-%m-%d/%Y-%m-%d_forecasts_%(area)s/'
   
    in_msg.scpOutput = False
    #default: in_msg.scpOutputDir="las@lomux240:/www/proj/OTL/WOL/cll/satimages"
    #default: in_msg.scpID="-i /home/cinesat/.ssh/id_dsa_las"

    #import ftp_DACH_MWO
    #in_msg.ftpUpload   = ftp_DACH_MWO.ftpUpload
    #in_msg.ftpProducts = ftp_DACH_MWO.ftpProducts
    #in_msg.ftpServer   = ftp_DACH_MWO.ftpServer
    #in_msg.ftpUser     = ftp_DACH_MWO.ftpUser
    #in_msg.ftpPassword = ftp_DACH_MWO.ftpPassword
    
    in_msg.chosen_settings={}
    #settings: set to None for automatic choice
    if in_msg.settings == "manual":
        
        check_overwriting = 0; current_setting = 'use_TB_forecast'
        
        #1) SETTING: choose one
        in_msg.chosen_settings['use_TB_forecast'] = True; check_overwriting+=1    # use forecasted brightness temperatures (wind data required) [suggested for CH]
        #in_msg.chosen_settings['use_TB_forecast'] = False; check_overwriting+=1   # use brightness temperatures without lagrangian displacement [required for area not covered by NWCSAF and cosmo]
        #in_msg.chosen_settings['use_TB_forecast'] = None; check_overwriting+=1 
        
        if check_overwriting > 1:
            print("you are overwriting your settings!!!! Check: ", current_setting)
            quit()
            
        
        check_overwriting = 0; current_setting = 'mode_downscaling'
        
        #2) SETTING: choose one
        in_msg.chosen_settings['mode_downscaling'] = 'gaussian_225_125'; check_overwriting+=1 #[suggested for CH]
        #in_msg.chosen_settings['mode_downscaling'] = 'convolve_405_300'; check_overwriting+=1
        #in_msg.chosen_settings['mode_downscaling'] = 'gaussian_150_100'; check_overwriting+=1
        #in_msg.chosen_settings['mode_downscaling'] = 'no_downscaling'; check_overwriting+=1 #[suggested for non local areas]
        #in_msg.chosen_settings['mode_downscaling'] = None; check_overwriting+=1
        
        if check_overwriting > 1:
            print("you are overwriting your settings!!!! Check: ", current_setting)
            quit()
                    
        
        check_overwriting = 0; current_setting = 'mask_labelsSmall_lowUS'
        
        #3) SETTING: choose one
        in_msg.chosen_settings['mask_labelsSmall_lowUS'] = True; check_overwriting+=1   # mask that removes the small clouds with low US
        #in_msg.chosen_settings['mask_labelsSmall_lowUS'] = False; check_overwriting+=1  # [suggested if clean_mask = 'no_cleaning'; suggested for non local]
        #in_msg.chosen_settings['mask_labelsSmall_lowUS'] = None; check_overwriting+=1
        
        if check_overwriting > 1:
            print("you are overwriting your settings!!!! Check: ", current_setting)
            quit()
                    
        
        check_overwriting = 0; current_setting = 'clean_mask'
        
        #4) SETTING: choose one
        in_msg.chosen_settings['clean_mask'] = 'skimage'; check_overwriting+=1 #[suggested for local]
        #in_msg.chosen_settings['clean_mask'] = 'scipy'; check_overwriting+=1 
        #in_msg.chosen_settings['clean_mask'] = 'both'; check_overwriting+=1 
        #in_msg.chosen_settings['clean_mask'] = 'no_cleaning'; check_overwriting+=1 #[suggested for non local]
        #in_msg.chosen_settings['clean_mask'] = None; check_overwriting+=1
        
        if check_overwriting > 1:
            print("you are overwriting your settings!!!! Check: ", current_setting)
            quit()
                
        
        check_overwriting = 0; current_setting = 'rapid_scan_mode'
        
        #5) SETTING: choose one
        in_msg.chosen_settings['rapid_scan_mode'] = False; check_overwriting+=1   # use 15 and 30min for estimating the updraft #[suggested for local]
        #in_msg.chosen_settings['rapid_scan_mode'] = True; check_overwriting+=1   # use  5 and 10min for estimating the updraft (useful if no wind data is available) #[suggested for non local]
        #in_msg.chosen_settings['rapid_scan_mode'] = None; check_overwriting+=1
        
        if check_overwriting > 1:
            print("you are overwriting your settings!!!! Check: ", current_setting)
            quit()
                    
        
        check_overwriting = 0; current_setting = 'forth_mask'
        # the forth mask will add an additional criteria that the pixel is accepted as COALITION2 result, e.g. it has to be a specific cloud type        
        #6) SETTING: choose one
        in_msg.chosen_settings['forth_mask'] = 'IR_039_minus_IR_108_day_only'; check_overwriting+=1              
        #in_msg.chosen_settings['forth_mask'] = 'IR_039_minus_IR_108'; check_overwriting+=1              
        #in_msg.chosen_settings['forth_mask'] = 'CloudType'; check_overwriting+=1 #at the moment this is not possible (problems loading CT)
        #in_msg.chosen_settings['forth_mask'] = 'no_mask'; check_overwriting+=1 
        #in_msg.chosen_settings['forth_mask'] = 'combined'; check_overwriting+=1   # for SZA>72 CT, otherwise IR_039_minus_IR_108
        #in_msg.chosen_settings['forth_mask'] = None; check_overwriting+=1
        
        if check_overwriting > 1:
            print("you are overwriting your settings!!!! Check: ", current_setting)
            quit()
        
        
        check_overwriting = 0; current_setting = 'forced_mask'
        # the forced_mask will add additional pixels to the COALITION2 result, independend of the cloud updraft, glaciation and optical thickness test                
        #7) SETTING: choose one
        in_msg.chosen_settings['forced_mask'] = 'no_mask'; check_overwriting+=1              
        #in_msg.chosen_settings['forced_mask'] = 'IR_039_minus_IR_108'; check_overwriting+=1  # force to include any pixel (in mature_mask) regardless of the other thresholds
        #in_msg.chosen_settings['forced_mask'] = 'CloudType'; check_overwriting+=1
        #in_msg.chosen_settings['forced_mask'] = None; check_overwriting+=1
        if check_overwriting > 1:
            print("you are overwriting your settings!!!! Check: ", current_setting)
            quit()
                    
        
        check_overwriting = 0; current_setting = 'mask_cirrus'
        
        #8) SETTING: choose one
        in_msg.chosen_settings['mask_cirrus'] = True; check_overwriting+=1
        #in_msg.chosen_settings['mask_cirrus'] = False; check_overwriting+=1
        #in_msg.chosen_settings['mask_cirrus'] = None; check_overwriting+=1
        
        if check_overwriting > 1:
            print("you are overwriting your settings!!!! Check: ", current_setting)
            quit()
                    
        
        #check_overwriting = 0; current_setting = 'reader_level'
        
        #9) SETTING: choose one
        #in_msg.chosen_settings['reader_level']="seviri-level2"; check_overwriting+=1
        #in_msg.chosen_settings['reader_level']="seviri-level4" ; check_overwriting+=1
        #in_msg.chosen_settings['reader_level']= None; check_overwriting+=1
        
        #if check_overwriting > 1:
        #    print "you are overwriting your settings!!!! Check: ", current_setting
        #    quit()
            
    else:
        in_msg.chosen_settings['use_TB_forecast'] = None
        in_msg.chosen_settings['mode_downscaling'] = None
        in_msg.chosen_settings['mask_labelsSmall_lowUS'] = None
        in_msg.chosen_settings['clean_mask'] = None
        in_msg.chosen_settings['rapid_scan_mode'] = None
        in_msg.chosen_settings['forth_mask'] = None            
        in_msg.chosen_settings['forced_mask'] = None
        in_msg.chosen_settings['mask_cirrus'] = None
        #in_msg.chosen_settings['reader_level']= None    
        #in_msg.chosen_settings['reader_level']="seviri-level4"

    ## !!! BAD FIX !!!
    in_msg.reader_level="seviri-level8"
    #in_msg.reader_level="seviri-level4"


    #PLOTTING SETTINGS. Not used??
    #in_msg.layer = ''
    #in_msg.layer = ' 2nd layer'
    in_msg.layer = '3rd layer'
    in_msg.add_rivers = False
    in_msg.add_borders = False
    in_msg.legend = True

    #saving output labels as pickle or shelve
    #in_msg.pickle_labels = True; in_msg.shelve_labels = False
    #in_msg.pickle_labels = False; in_msg.shelve_labels = True
    in_msg.pickle_labels = False; in_msg.shelve_labels = False

    in_msg.postprocessing_areas= []
    in_msg.postprocessing_areas.append('EuropeCanaryS95')
    #in_msg.postprocessing_areas.append('EuroMercator')
    in_msg.postprocessing_areas.append("ccs4")
    
    #in_msg.postprocessing_composite1=["C2rgb-ir108"]
    #in_msg.postprocessing_composite2=["C2rgb-Forecast-ir108"]  
    in_msg.postprocessing_composite1=["C2rgb-IR_108"]                   # used by plot_coalition2
    #in_msg.postprocessing_composite1=["C2rgbPC-IR_108"]                # used by plot_coalition2
    #in_msg.postprocessing_composite1=["C2rgb-overview"]                # used by plot_coalition2
    #in_msg.postprocessing_composite2=["C2rgb-Forecast-IR_108"]       # used by plot_coalition2
    #in_msg.postprocessing_composite=["C2rgb-IR_108","C2rgb-HRV"]    


    # load a few standard things 
    #in_msg.outputFile = 'WS_%(rgb)s-%(area)s_%y%m%d%H%M'
    #in_msg.fill_value = [0,0,0] # black
    
    #in_msg.fill_value = None    # transparent

    #INPUT NEEDED FOR PRODUCE_FORECASTS!!!!!!!!!!!
    #in_msg.ntimes = 2 #in_windshift.ntimes
    #print "... aggregate winddata for ", ntimes, " timesteps" 
    #min_correlation = 85 #in_windshift.min_correlation
    #min_conf_nwp = 80 #in_windshift.min_conf_nwp
    #min_conf_no_nwp = 80 #in_windshift.min_conf_no_nwp
    #cloud_type = [5,6,7,8,9,10,11,12,13,14] #in_windshift.cloud_type

    # satellite for HRW winds
    ##sat_nr = "08" #in_windshift.sat_nr
    
    in_msg.channels15 = ['WV_062','WV_073','IR_039','IR_087','IR_097','IR_108','IR_120','IR_134']
    in_msg.channels30 = ['WV_062','WV_073','IR_097','IR_108','IR_134']

    nrt = True # !HAU! ???
        
    # -------------   
    # input checks 
    # -------------   
    """
    if in_msg.area in broad_areas:
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
    """
    #in_msg.check_input = False
    in_msg.parallax_correction = False
    #in_msg.parallax_correction = True
    in_msg.parallax_gapfilling = 'nearest' # 'False' (default), 'nearest', 'bilinear'

    #in_msg.make_plots=True
    #in_msg.fill_value=(0,0,0)  # black (0,0,0) / white (1,1,1) / transparent None  
    in_msg.add_title = True 
    in_msg.title_color = (255,255,255)
    #in_msg.title = "COALITION-2, %Y-%m-%d %H:%MUTC, %(area)s"
    in_msg.title = "COALITION-2"
    in_msg.title_y_line_nr = 3  # (INT) at which line should the title start (automatically overwriten with 2 for ccs4)
    #in_msg.add_borders = True
    #in_msg.border_color = 'red'
    #in_msg.add_rivers = False
    #in_msg.river_color = 'blue'
    #in_msg.add_logos = False
    #in_msg.add_colorscale = False
    #in_msg.HRV_enhancement = True
    in_msg.HRV_enhancement = False

    #in_msg.outputFile = 'MSG_%(rgb)s-%(area)s_%y%m%d%H%M.png'

    #in_msg.compress_to_8bit=False
    
