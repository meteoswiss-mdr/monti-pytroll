from __future__ import division
from __future__ import print_function


def input(in_msg, timeslot=None):

    import inspect
    in_msg.input_file = inspect.getfile(inspect.currentframe()) 
    print("*** read input from ", in_msg.input_file)

    # 8=MSG1, 9=MSG2, 10=MSG3
    #in_msg.sat_nr=8
    #in_msg.RSS=False 
    #in_msg.sat_nr=9
    #in_msg.RSS=True
    in_msg.sat_nr=10
    in_msg.RSS=False 

    # specify an delay (in minutes), when you like to process a time some minutes ago
    # e.g. current time               2015-05-31 12:33 UTC
    # delay 5 min                     2015-05-31 12:28 UTC
    # last Rapid Scan Service picture 2015-05-31 12:25 UTC (Scan start) 
    in_msg.delay=15
    
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
    #in_msg.RGBs.append('WV_062_minus_WV_073')
    #in_msg.RGBs.append('WV_062_minus_IR_108')
    #in_msg.RGBs.append('WV_073_minus_IR_134')
    #in_msg.RGBs.append('IR_087_minus_IR_108')      
    #in_msg.RGBs.append('IR_087_minus_IR_120')      
    #in_msg.RGBs.append('IR_120_minus_IR_108')
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
    in_msg.sat = "cpp"
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
    in_msg.RGBs.append('precip')
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


    # experimental
    #in_msg.RGBs.append('clouddepth')     # test according to Mecikalski, 2010
    ##in_msg.RGBs.append('RII')
    
    #----------------
    # chose area
    #----------------
    #in_msg.areas.append('ccs4')             # CCS4 Swiss projection 710x640
    #in_msg.areas.append('germ')            # Germany 1024x1024
    #in_msg.areas.append('euro4')           # Europe 4km, 1024x1024
    #in_msg.areas.append('EuropeCanary')    # upper third of MSG disk, satellite at 0.0 deg East, full resolution 
    #in_msg.areas.append('EuropeCanary95')  # upper third of MSG disk, satellite at 9.5 deg East, full resolution 
    #in_msg.areas.append('EuropeCanaryS95') # upper third of MSG disk, satellite at 9.5 deg East, reduced resolution 1000x400
    #in_msg.areas.append('alps95')          # area around Switzerland processed by NWCSAF software 349x151 
    #in_msg.areas.append('ticino')          # stereographic proj of Ticino 342x311
    #in_msg.areas.append('MSGHRVN')         # High resolution northern quarter 11136x2784
    #in_msg.areas.append('fullearth')       # full earth 600x300                    # does not yet work
    #in_msg.areas.append('met09globe')      # Cropped globe MSG image 3620x3620     # does not yet work
    #in_msg.areas.append('met09globeFull')  # Full    globe MSG image 3712x3712     # does not yet work
    #in_msg.areas.append('SeviriDiskFull00S4')
    in_msg.areas.append('odysseyS25')

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
    #in_msg.save_reprojected_data=['ccs4']
    in_msg.reprojected_data_filename='%(msg)s_%(area)s_%Y%m%d%H%M_nwcsaf.nc'
    in_msg.reprojected_data_dir='/data/COALITION2/database/meteosat/ccs4/%Y/%m/%d/'
    in_msg.save_statistics=False

    in_msg.make_plots=True
    in_msg.fill_value=None  # black (0,0,0) / white (1,1,1) / transparent None  
    in_msg.add_title = True
    in_msg.add_borders = True
    in_msg.border_color = 'red'
    in_msg.add_rivers = False
    in_msg.river_color = 'blue'
    in_msg.add_logos = True
    in_msg.add_colorscale = False
    in_msg.HRV_enhancement = False

    in_msg.outputFile = '%(sat)s_%(rgb)s-%(area)s_%y%m%d%H%M.png'
    #in_msg.outputDir='./pics/'
    #in_msg.outputDir = "./%Y-%m-%d/%Y-%m-%d_%(rgb)s-%(area)s/"
    in_msg.outputDir = '/data/cinesat/out/'
    #in_msg.outputDir = '/data/COALITION2/PicturesSatellite/%Y-%m-%d/%Y-%m-%d_%(rgb)s_%(area)s/'

    in_msg.compress_to_8bit=False

    in_msg.scpOutput = True
    #default: in_msg.scpOutputDir="las@lomux240:/www/proj/OTL/WOL/cll/satimages"
    #default: in_msg.scpID="-i /home/cinesat/.ssh/id_dsa_las"
    
    #in_msg.postprocessing_areas=['odysseyS25','SeviriDiskFull00S4']
    in_msg.postprocessing_areas=['odysseyS25']
    in_msg.postprocessing_composite=['precip-ir108','precip-HRV']
    in_msg.postprocessing_montage = [["MSG_RATE-ir108","cpp_precip-ir108"],["MSG_RATE-HRV","cpp_precip-HRV"]]
    #in_msg.postprocessing_areas=['ccs4','EuropeCanaryS95']
    #in_msg.postprocessing_composite=['cth-ir108', 'cot-ir108', 'ctt-ir108','reff-ir108', 'precip-ir108','precip_ir-ir108']    
    #in_msg.postprocessing_composite=['reff-ir108','precip-ir108', 'cot-ir108']    
    #in_msg.postprocessing_composite=['cth-ir108']    
    #in_msg.postprocessing_composite=['cot-ir108']    
