from __future__ import division
from __future__ import print_function


def input(in_msg, timeslot=None):

    import inspect
    in_msg.input_file = inspect.getfile(inspect.currentframe()) 
    print("*** read input from ", in_msg.input_file)

    # 8=MSG1, 9=MSG2, 10=MSG3
    in_msg.sat = "Meteosat"
    #in_msg.sat = "meteosat"
    #in_msg.sat_nr=8
    #in_msg.RSS=False 
    #in_msg.sat_nr=9
    #in_msg.RSS=True
    #in_msg.sat_nr=10
    #in_msg.RSS=False
    in_msg.sat_nr=11
    in_msg.RSS=False

    # specify an delay (in minutes), when you like to process a time some minutes ago
    # e.g. current time               2015-05-31 12:33 UTC
    # delay 5 min                     2015-05-31 12:28 UTC
    # last Rapid Scan Service picture 2015-05-31 12:25 UTC (Scan start) 
    #in_msg.delay=5

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
    #in_msg.RGBs.append('IR_108')       # black and white
    ##in_msg.RGBs.append('IR_120')       # black and white
    ##in_msg.RGBs.append('IR_134')       # black and white
    #in_msg.RGBs.append('HRV')          # black and white
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
    in_msg.RGBs.append('day_microphysics')   # VIS008         IR_039(solar)  IR_108     # requires the pyspectral modul 
    #in_msg.RGBs.append('dust')               # IR_120-IR_108  IR_108-IR_087  IR_108
    #in_msg.RGBs.append('fog')
    #in_msg.RGBs.append('green_snow')
    #in_msg.RGBs.append('ir108')
    #in_msg.RGBs.append('natural')            # IR_016         VIS008         VIS006
    #in_msg.RGBs.append('night_fog')          
    #in_msg.RGBs.append('night_microphysics') # IR_120-IR_108  IR_108-IR_039  IR_108
    #in_msg.RGBs.append('night_overview')
    #in_msg.RGBs.append('overview')
    ##in_msg.RGBs.append('overview_sun')
    #in_msg.RGBs.append('red_snow')
    ##in_msg.RGBs.append('refl39_chan')        # requires the pyspectral modul
    #in_msg.RGBs.append('snow')               # requires the pyspectral modul
    ##in_msg.RGBs.append('vis06')
    ##in_msg.RGBs.append('wv_high')
    #in_msg.RGBs.append('wv_low')
    #-------------------
    # user defined RGBs
    #in_msg.RGBs.append('HRoverview')
    ##in_msg.RGBs.append('sandwich')
    ##in_msg.RGBs.append('ndvi')
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
    #in_msg.RGBs.append('CTT')
    #in_msg.RGBs.append('CTH')
    #in_msg.RGBs.append('CTP')
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
    #-------------------
    # H-SAF
    #-------------------
    #in_msg.sat = "HSAF"
    #in_msg.sat_nr=""
    #in_msg.RSS=False 
    #in_msg.RGBs.append('h03')
    #-------------------
    # experimental
    #in_msg.RGBs.append('clouddepth')     # test according to Mecikalski, 2010
    ##in_msg.RGBs.append('RII')
    
    #----------------
    # chose area
    #----------------
    #in_msg.areas.append('EuropeCanary')    # upper third of MSG disk, satellite at 0.0 deg East, full resolution 
    #in_msg.areas.append('EuropeCanary95')  # upper third of MSG disk, satellite at 9.5 deg East, full resolution 
    #in_msg.areas.append('EuropeCanaryS95') # upper third of MSG disk, satellite at 9.5 deg East, reduced resolution 1000x400
    #in_msg.areas.append('EuroMercator') # 
    #in_msg.areas.append('germ')            # Germany 1024x1024
    #in_msg.areas.append('euro4')           # Europe 4km, 1024x1024
    #in_msg.areas.append('ccs4')             # CCS4 Swiss projection 710x640
    #in_msg.areas.append('alps95')          # area around Switzerland processed by NWCSAF software 349x151 
    #in_msg.areas.append('ticino')          # stereographic proj of Ticino 342x311
    #in_msg.areas.append('MSGHRVN')         # High resolution northern quarter 11136x2784
    #in_msg.areas.append('fullearth')       # full earth 600x300                    # does not yet work
    #in_msg.areas.append('SeviriDisk95')      # Cropped globe MSG image 3620x3620     
    #in_msg.areas.append('SeviriDiskFull95')  # Full    globe MSG image 3712x3712     
    #in_msg.areas.append('SeviriDiskFull00')  # Full    globe MSG image 3712x3712     
    in_msg.areas.append('SeviriDiskFull00S4')  # Full   globe MSG image  742x 742
    #in_msg.areas.append('SouthArabia')
    #in_msg.areas.append('opera_odyssey')
    in_msg.check_RSS_coverage()

    in_msg.check_input = False
    #in_msg.reader_level="seviri-level4" 
    #in_msg.save_reprojected_data=['ccs4']
    in_msg.reprojected_data_filename='%(msg)s_%(area)s_%Y%m%d%H%M_nwcsaf.nc'
    in_msg.reprojected_data_dir='/data/COALITION2/database/meteosat/ccs4/%Y/%m/%d/'
    in_msg.save_statistics=False

    in_msg.make_plots = True
    in_msg.fill_value = (0,0,0)  # black (0,0,0) / white (1,1,1) / transparent None  
    in_msg.add_title = True
    in_msg.add_borders = True
    in_msg.add_rivers = False
    in_msg.add_logos = False
    in_msg.add_colorscale = True
    in_msg.HRV_enhancement = False

    in_msg.outputFile = 'MSG_%(rgb)s-%(area)s_%y%m%d%H%M.png'
    #in_msg.outputDir='./pics/'
    #in_msg.outputDir = "./%Y-%m-%d/%Y-%m-%d_%(rgb)s-%(area)s/"
    in_msg.outputDir = '/data/cinesat/out/'
    #in_msg.outputDir = '/data/COALITION2/PicturesSatellite/%Y-%m-%d/%Y-%m-%d_%(rgb)s_%(area)s/'

    in_msg.compress_to_8bit=False

    in_msg.scpOutput = True
    in_msg.scpOutputDir="las@lomux240:/www/proj/OTL/WOL/cll/satimages/SeviriDiskFull00S4"
    #default: in_msg.scpOutputDir="las@lomux240:/www/proj/OTL/WOL/cll/satimages"
    #default: in_msg.scpID="-i /home/cinesat/.ssh/id_dsa_las"

    # please download the shape file 
    # in_msg.mapDir='/opt/users/common/shapes/'

    #in_msg.postprocessing_areas=["ccs4"]
    #in_msg.postprocessing_areas=['EuropeCanaryS95']
    #in_msg.postprocessing_composite=["h03b-ir108"] 
    #in_msg.postprocessing_composite=["hrwdp-ir108"] 
    #in_msg.postprocessing_composite=["CTT-ir108","CTH-ir108"] 
    #in_msg.postprocessing_composite=["hrwdp-ir108", "hrwdc-ir108","streamd-ir108","hrwdr-ir108", "hrwdcnwp-ir108", "hrwdcnnwp-ir108"]    
    #in_msg.postprocessing_composite=["hrwdr-ir108", "hrwdcnwp-ir108", "hrwdcnnwp-ir108", "streamd-ir108"]    
    #in_msg.postprocessing_composite=["TRT-streamd-ir108", "TRT-streamd-HRV"] #"hrwdCT-ir108", "hrwdCT-HRV"
    #in_msg.postprocessing_composite=["hrwdpH-streamdH-HRV", "hrwdpM-streamdM-HRV", "hrwdpL-streamdL-HRV"] #"hrwdCT-ir108", "hrwdCT-HRV"
    #in_msg.postprocessing_composite=["hrwdp-streamd-HRV", "hrwdp-streamd-ir108"] #"hrwdCT-ir108", "hrwdCT-HRV"
    #in_msg.postprocessing_composite=["hrwdpL-streamdL-HRV","hrwdpL-streamdL-ir108"] 
    #in_msg.postprocessing_composite=["hrwdpH-streamdH-HRV","hrwdpH-streamdH-ir108"] 
    in_msg.postprocessing_composite=["hrwdp-streamd-ir108","TRT-streamd-ir108"] 
