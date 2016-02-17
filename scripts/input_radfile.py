
def input(in_msg):

    print "*** read input from input_MSG.py"

    #------------------------------------------------------------------------
    # choose (default) observation time 
    # (this time is overwritten by the command line arguments of plot_msg.py)
    # (if no date is given in command line neither, 
    # then last MSG observation date is chosen)
    #------------------------------------------------------------------------
    if False:
        year=2014
        month=7
        day=23
        hour=16
        minute=10
        in_msg.update_datetime(year, month, day, hour, minute)
        # !!!  if archive is used, adjust meteosat09.cfg accordingly !!!

    #----------------------
    # choose RGBs 
    #----------------------
    #-------------------
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
    #in_msg.RGBs.append('IR_108')       # black and white
    ##in_msg.RGBs.append('IR_120')       # black and white
    ##in_msg.RGBs.append('IR_134')       # black and white
    ##in_msg.RGBs.append('HRV')          # black and white
    in_msg.RGBs.append('VIS006c')      # colored version
    in_msg.RGBs.append('VIS008c')      # colored version
    in_msg.RGBs.append('IR_016c')      # colored version
    in_msg.RGBs.append('IR_039c')      # colored version
    in_msg.RGBs.append('WV_062c')      # colored version
    in_msg.RGBs.append('WV_073c')      # colored version
    in_msg.RGBs.append('IR_087c')      # colored version
    in_msg.RGBs.append('IR_097c')      # colored version
    in_msg.RGBs.append('IR_108c')      # colored version
    in_msg.RGBs.append('IR_120c')      # colored version
    in_msg.RGBs.append('IR_134c')      # colored version
    in_msg.RGBs.append('HRVc')         # colored version
    #-------------------
    # satellite channel differences
    #in_msg.RGBs.append('WV_062-WV_073')
    #in_msg.RGBs.append('WV_062-IR_108')
    #in_msg.RGBs.append('WV_073-IR_134')
    #in_msg.RGBs.append('IR_087-IR_108')      
    #in_msg.RGBs.append('IR_087-IR_120')      
    #in_msg.RGBs.append('IR_120-IR_108')   
    #in_msg.RGBs.append('trichannel')
    #-------------------
    # buil in RGBs, see http://mpop.readthedocs.org/en/latest/pp.html
    #                or  http://oiswww.eumetsat.int/~idds/html/doc/best_practices.pdf
    #-------------------      # RED            GREEN          BLUE
    #in_msg.RGBs.append('airmass')           # WV_062-WV_073  IR_097-IR_108  -WV_062
    #in_msg.RGBs.append('ash')               
    #in_msg.RGBs.append('cloudtop')
    #in_msg.RGBs.append('convection')         # WV_062-WV_073  IR_039-IR_108  IR_016-VIS006
    ##in_msg.RGBs.append('convection_co2')
    #in_msg.RGBs.append('day_microphysics')   # VIS008         IR_039(solar)  IR_108     # requires the pyspectral modul 
    #in_msg.RGBs.append('dust')               # IR_120-IR_108  IR_108-IR_087  IR_108
    #in_msg.RGBs.append('fog')
    #in_msg.RGBs.append('green_snow')
    ##in_msg.RGBs.append('ir108')
    #in_msg.RGBs.append('natural')            # IR_016         VIS008         VIS006
    #in_msg.RGBs.append('night_fog')          
    #in_msg.RGBs.append('night_microphysics') # IR_120-IR_108  IR_108-IR_039  IR_108
    #in_msg.RGBs.append('night_overview')
    #in_msg.RGBs.append('overview')
    #in_msg.RGBs.append('overview_sun')
    #in_msg.RGBs.append('red_snow')
    #in_msg.RGBs.append('refl39_chan')        # requires the pyspectral modul
    #in_msg.RGBs.append('snow')               # requires the pyspectral modul
    #in_msg.RGBs.append('vis06')
    #in_msg.RGBs.append('wv_high')
    #in_msg.RGBs.append('wv_low')
    #-------------------
    # user defined RGBs
    #in_msg.RGBs.append('HRoverview')
    ##in_msg.RGBs.append('sandwich')
    ##in_msg.RGBs.append('ndvi')
    #-------------------
    # NWC SAF
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
    #in_msg.RGBs.append('CTT')
    #in_msg.RGBs.append('CTH')
    #in_msg.RGBs.append('CTP')
    ## NWC SAF PEG 13 
    #in_msg.RGBs.append('sphr_bl')
    #in_msg.RGBs.append('sphr_cape')
    ##in_msg.RGBs.append('sphr_diffbl')
    ##in_msg.RGBs.append('sphr_diffhl')
    ##in_msg.RGBs.append('sphr_diffki')
    ##in_msg.RGBs.append('sphr_diffli')
    ##in_msg.RGBs.append('sphr_diffml')
    ##in_msg.RGBs.append('sphr_diffshw')
    ##in_msg.RGBs.append('sphr_difftpw')
    #in_msg.RGBs.append('sphr_hl')
    #in_msg.RGBs.append('sphr_ki')
    #in_msg.RGBs.append('sphr_li')
    #in_msg.RGBs.append('sphr_ml')
    #in_msg.RGBs.append('sphr_quality')
    ##in_msg.RGBs.append('sphr_sflag')
    #in_msg.RGBs.append('sphr_shw')
    #in_msg.RGBs.append('sphr_tpw')

    #-------------------
    # experimental
    #in_msg.RGBs.append('clouddepth')     # test according to Mecikalski, 2010
    ##in_msg.RGBs.append('CMa')           # no reader exists
    ##in_msg.RGBs.append('CMa_DUST')      # no reader exists
    ##in_msg.RGBs.append('CMa_VOLCANIC')  # no reader exists
    ##in_msg.RGBs.append('RII')
    
    #----------------
    # chose area
    #----------------
    #in_msg.areas.append('EuropeCanary')
    #in_msg.areas.append('EuropeCanary95')
    #in_msg.areas.append('EuropeCanaryS95')
    #in_msg.areas.append('germ')            # Germany 1024x1024
    #in_msg.areas.append('euro4')           # Europe 4km, 1024x1024
    in_msg.areas.append('ccs4')            # CCS4 Swiss projection 710x640
    #in_msg.areas.append('alps')            # CCS4 Swiss projection 710x640
    #in_msg.areas.append('ticino')            # CCS4 Swiss projection 710x640
    #in_msg.areas.append('MSGHRVN')         # High resolution northern quarter 11136x2784
    #in_msg.areas.append('fullearth')       # full earth 600x300                    # does not yet work
    #in_msg.areas.append('met09globe')      # Cropped globe MSG image 3620x3620     # does not yet work
    #in_msg.areas.append('met09globeFull')  # Full    globe MSG image 3712x3712     # does not yet work
    
    # 8=MSG1, 9=MSG2, 10=MSG3
    #in_msg.sat_nr=0
    #in_msg.RSS=True 
    #in_msg.sat_nr=8
    #in_msg.RSS=False 
    in_msg.sat_nr=9
    in_msg.RSS=True 
    #in_msg.sat_nr=10
    #in_msg.RSS=False 
    
    # switch off Rapid scan, if large areas are wanted 
    if ('fullearth' in in_msg.areas) or ('met09globe' in in_msg.areas) or ('met09globeFull' in in_msg.areas): 
       in_msg.RSS=False 
    
    # please download the spape file of 
    in_msg.mapDir='/data/OWARNA/hau/maps_pytroll/'
    # in_msg.add_borders=False
    # in_msg.add_rivers=True
        
    #in_msg.check_input = True    # for radiances check always PRO and EPI files
    in_msg.check_input = False    # for radiances check always PRO and EPI files
    #in_msg.save_reprojected_data=['EuropeCanaryS95','ccs4']
    in_msg.save_reprojected_data=['ccs4']
    in_msg.reprojected_data_filename='%(msg)s_%(area)s_%Y%m%d%H%M_rad.nc'
    in_msg.reprojected_data_dir='/data/COALITION2/database/meteosat/ccs4/%Y/%m/%d/'
    #in_msg.reprojected_data_filename='MSG_test_%Y%m%d%H%M.nc'
    #in_msg.save_statistics=True
    in_msg.HRV_enhancement=False
    in_msg.make_plots=False
    #in_msg.make_plots=True

    in_msg.outputFile = 'MSG_%(rgb)s-%(area)s_%y%m%d%H%M.png'
    in_msg.outputDir='./pics/'
    in_msg.outputDir = "./%Y-%m-%d/%Y-%m-%d_%(rgb)s-%(area)s/"
    #in_msg.outputDir = '/data/cinesat/out/'

    in_msg.compress_to_8bit=False

    #in_msg.scpOutput = True
    #default see scp_settings.py: e.g. in_msg.scpOutputDir="las@lomux240:/www/proj/OTL/WOL/cll/satimages"
    #default see scp_settings.py: e.g. in_msg.scpID="-i /home/cinesat/.ssh/id_dsa_las"

    # please download the shape file 
    in_msg.mapDir='/data/OWARNA/hau/maps_pytroll/'

    in_msg.add_title = True
    in_msg.add_borders = True
    in_msg.add_rivers = False
    in_msg.add_logos = False
    in_msg.add_colorscale = True
    in_msg.fixed_minmax = True
    
    
