
from get_input_msg_py3 import input_msg_class
in_msg = input_msg_class()

def input(in_msg, timeslot=None):

    if timeslot is not None:
        in_msg.update_datetime(timeslot.year, timeslot.month, timeslot.day, timeslot.hour, timeslot.minute)

    #in_msg.sat="Meteosat"
    #in_msg.sat_nr=9
    #in_msg.RSS=True
    #in_msg.sat_nr=10
    #in_msg.RSS=True
    in_msg.sat_nr=11
    in_msg.RSS=False
       
    #in_msg.outputDir="./images/"
    in_msg.outputDir="/data/cinesat/out/"

    in_msg.areas.append("ccs4")
    #in_msg.areas.append('EuropeCenter')
    #in_msg.areas.append('SeviriDiskFull00S4')

    # in_msg.mapDir='/data/OWARNA/hau/maps_pytroll/'
    in_msg.mapResolution='l'       ## f  full resolution: Original (full) data resolution.          
                                   ## h  high resolution: About 80 % reduction in size and quality. 
                                   ## i  intermediate resolution: Another ~80 % reduction.          
                                   ## l  low resolution: Another ~80 % reduction.                   
                                   ## c  crude resolution: Another ~80 % reduction. 
                                   ## None -> automatic choise
    
    ##############################################################
    #### channels of SEVIRI
    #in_msg.RGBs.append("HRV")
    #in_msg.RGBs.append("VIS006")
    #in_msg.RGBs.append("VIS008")
    #in_msg.RGBs.append("IR_016")
    #in_msg.RGBs.append("IR_039")
    #in_msg.RGBs.append("WV_062")
    #in_msg.RGBs.append("WV_073")
    #in_msg.RGBs.append("IR_097")
    #in_msg.RGBs.append("IR_108")
    #in_msg.RGBs.append("IR_120")
    #in_msg.RGBs.append("IR_134")
    #### modified channels of SEVIRI, see satpy/satpy/etc/composites/seviri.yaml 
    #in_msg.RGBs.append("_vis06")                 # SZA corrected VIS006
    #in_msg.RGBs.append("_hrv")                    # SZA corrected HRV  
    #in_msg.RGBs.append("_vis06_filled_hrv")        
    #in_msg.RGBs.append("_ir108")                  # inverted IR_108
    #in_msg.RGBs.append("_vis_with_ir")            # replacement for HRVir108
    #### modified channels for VISIR, see satpy/satpy/etc/composites/visir.yaml
    #in_msg.RGBs.append("ir108_3d")
    #in_msg.RGBs.append("ir_cloud_day")
    #### backgrounds, see satpy/satpy/etc/composites/visir.yaml
    #in_msg.RGBs.append("_night_background")
    #in_msg.RGBs.append("_night_background_hires")
    # composites for SEVIRI, see, see satpy/satpy/etc/composites/seviri.yaml)
    #in_msg.RGBs.append("ct_masked_ir")
    #in_msg.RGBs.append("nwc_geo_ct_masked_ir")
    #in_msg.RGBs.append("cloudtop")
    #in_msg.RGBs.append("cloudtop_daytime")
    #in_msg.RGBs.append("convection")              # need to be switchoff later / need to be Luminicence sharpened
    #in_msg.RGBs.append("HRconvection")
    #in_msg.RGBs.append("LSconvection")            
    #in_msg.RGBs.append("night_fog")
    #in_msg.RGBs.append("snow")
    #in_msg.RGBs.append("day_microphysics")
    #in_msg.RGBs.append("day_microphysics_winter")
    #in_msg.RGBs.append("natural_color_raw")
    #in_msg.RGBs.append("natural_color")           # cannot be Luminicence/SW sharpened, too much colour change 
    #in_msg.RGBs.append("natural_color_nocorr")
    #in_msg.RGBs.append("DayNaturalColorNightIRoverview")
    #in_msg.RGBs.append("fog")
    #in_msg.RGBs.append("cloudmask")
    #in_msg.RGBs.append("cloudtype")
    #in_msg.RGBs.append("cloud_top_height")
    #in_msg.RGBs.append("cloud_top_pressure")
    #in_msg.RGBs.append("cloud_top_temperature")
    #in_msg.RGBs.append("cloud_top_phase")
    #in_msg.RGBs.append("cloud_drop_effective_radius")
    #in_msg.RGBs.append("cloud_optical_thickness")
    #in_msg.RGBs.append("cloud_liquid_water_path")
    #in_msg.RGBs.append("cloud_ice_water_path")
    #in_msg.RGBs.append("precipitation_probability")
    #in_msg.RGBs.append("convective_rain_rate")
    #in_msg.RGBs.append("convective_precipitation_hourly_accumulation")
    #in_msg.RGBs.append("total_precipitable_water")
    #in_msg.RGBs.append("showalter_index")
    #in_msg.RGBs.append("lifted_index")
    #in_msg.RGBs.append("convection_initiation_prob30")
    #in_msg.RGBs.append("convection_initiation_prob60")
    #in_msg.RGBs.append("convection_initiation_prob90")
    #in_msg.RGBs.append("asii_prob")
    #in_msg.RGBs.append("rdt_cell_type")
    #in_msg.RGBs.append("realistic_colors")
    #in_msg.RGBs.append("ir_overview")            ## need to be switchoff later / replacement for night_overview 
    #in_msg.RGBs.append("overview_raw")
    #in_msg.RGBs.append("overview")
    #in_msg.RGBs.append("green_snow")
    #in_msg.RGBs.append("HRgreen_snow")
    #in_msg.RGBs.append("colorized_ir_clouds")
    #in_msg.RGBs.append("vis_sharpened_ir")
    #in_msg.RGBs.append("ir_sandwich")
    #in_msg.RGBs.append("natural_enh")
    #in_msg.RGBs.append("hrv_clouds")
    #in_msg.RGBs.append("hrvvis_clouds")           
    #in_msg.RGBs.append("hrv_fog")
    #in_msg.RGBs.append("hrv_severe_storms")
    #in_msg.RGBs.append("hrv_severe_storms_masked")
    #in_msg.RGBs.append("natural_with_night_fog")
    #in_msg.RGBs.append("natural_color_with_night_ir")
    #in_msg.RGBs.append("natural_color_raw_with_night_ir")
    #in_msg.RGBs.append("natural_color_with_night_ir_hires")
    #in_msg.RGBs.append("natural_enh_with_night_ir")
    #in_msg.RGBs.append("natural_color_with_night_ir_hires")
    #in_msg.RGBs.append("natural_enh_with_night_ir")
    #in_msg.RGBs.append("natural_enh_with_night_ir_hires")
    #in_msg.RGBs.append("night_ir_alpha")
    #in_msg.RGBs.append("night_ir_with_background")
    #in_msg.RGBs.append("night_ir_with_background_hires")
    #in_msg.RGBs.append("vis_with_ir_cloud_overlay")
    # general VISIR composites, see satpy/satpy/etc/composites/visir.yaml
    #in_msg.RGBs.append("airmass")
    #in_msg.RGBs.append("ash")
    #in_msg.RGBs.append("cloudtop")
    #in_msg.RGBs.append("convection")
    #in_msg.RGBs.append("snow")
    #in_msg.RGBs.append("day_microphysics")
    #in_msg.RGBs.append("dust")
    #in_msg.RGBs.append("fog")
    ## in_msg.RGBs.append("green_snow")  # also defined above    # no replacement for red snow    
    #in_msg.RGBs.append("natural_enh")
    #in_msg.RGBs.append("natural_color_raw")
    #in_msg.RGBs.append("natural_color")
    ##in_msg.RGBs.append("night_fog")             # also in seviri
    ##in_msg.RGBs.append("overview")              # also in seviri
    ##in_msg.RGBs.append("true_color_raw")        # needs wavelength=0.45
    #in_msg.RGBs.append("natural_with_night_fog")
    #in_msg.RGBs.append("precipitation_probability")
    #in_msg.RGBs.append("cloudmask_extended")
    #in_msg.RGBs.append("cloudmask_probability")
    #in_msg.RGBs.append("cloud_drop_effective_radius")
    #in_msg.RGBs.append("cloud_optical_thickness")
    #in_msg.RGBs.append("night_microphysics")
    ##in_msg.RGBs.append("cloud_phase_distinction")       # requires Raylight scattinering and to download some pyspectral aux files 
    ##in_msg.RGBs.append("cloud_phase_distinction_raw")   # requires Raylight scattinering and to download some pyspectral aux files 
    ###### CMIC products 
    #in_msg.RGBs.append("cloud_water_path")
    #in_msg.RGBs.append("ice_water_path")
    #in_msg.RGBs.append("liquid_water_path")
    #in_msg.RGBs.append("cloud_phase")          # needs 1.6, 2.2, 0.67
    #in_msg.RGBs.append("cloud_phase_raw")      # needs 1.6, 2.2, 0.67
    #in_msg.RGBs.append("cimss_cloud_type")     # needs 1.4, 04, 1.6
    #in_msg.RGBs.append("cimss_cloud_type_raw") # needs 1.4, 04, 1.6
    #### self specified composites (need a modified satpy/satpy/etc/composites/seviri.yaml)
    #in_msg.RGBs.append("DayNightMicrophysics")
    #in_msg.RGBs.append("DayNightFog")
    #in_msg.RGBs.append("DayConvectionNightMicrophysics")
    #in_msg.RGBs.append("DayNightOverview")
    #in_msg.RGBs.append("SWconvection")
    #in_msg.RGBs.append("DayLSConvectionNightMicrophysics")
    #in_msg.RGBs.append("DaySWconvectionNightMicrophysics")
    #in_msg.RGBs.append("DayHRVVIScloudsNightIRoverview")
    
    ###############################################################

    #composites=["day_microphysics","_hrv"]  # does not work with to_image, only with show!!!
    #composites=["convection","_hrv"]  # does not work with to_image, only with show!!!
    #composites=["overview_raw","_hrv"]
    #composites=["overview","_hrv"]
    #composites=["vis_with_ir_cloud_overlay"]
    #composites=["cloud_top_height"]
    #composites=["DayNightMicrophysics"]
    #composites=["DayNightFog"]
    #composites=["DayConvectionNightMicrophysics"]
    #composites=["HRoverview"]        # more yellowish than LuminanceSharpened overview_raw ???
    #composites=["DayNightOverview"]
    #composites=["SWconvection"]
    #composites=["DaySWconvectionNightMicrophysics"]
    #composites=["natural_enh"]          # similar to natural, but only white clouds
    #composites=["hrv_severe_storms"]    # mainly blue, only storms are visible in white      
    #composites=["VIS006pc"]
    #composites=["IR_108pc"]
    #composites=["DayNightFog","DayNightMicrophysics"]
    
    #in_msg.RGBs=composites

    in_msg.mapDir='/opt/users/common/shapes/'

    in_msg.postprocessing_areas=['ccs4']
    in_msg.postprocessing_composite = ["radar-HRVir108","CRR-HRVir108","h03b-HRVir108","CRPh-HRVir108"]
    in_msg.postprocessing_montage = [["MSG_rrMlp-HRVir108","MSG_radar-HRVir108","MSG_CRR-HRVir108","MSG_rrMlpPm-HRVir108","MSG_h03b-HRVir108","MSG_CRPh-HRVir108"]]
    
    in_msg.scpOutput=True
    in_msg.scpProducts=[["MSG_rrMlp-HRVir108","MSG_radar-HRVir108","MSG_CRR-HRVir108","MSG_rrMlpPm-HRVir108","MSG_h03b-HRVir108","MSG_CRPh-HRVir108"]]
