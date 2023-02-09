"""
   List of all products that can be ploted.
"""


MSG       = ['VIS006', 'VIS008', 'IR_016', 'IR_039', 'WV_062', 'WV_073',\
                      'IR_087', 'IR_097', 'IR_108', 'IR_120', 'IR_134', 'HRV']
MSG_color = ['VIS006c','VIS008c','IR_016c','IR_039c','WV_062c','WV_073c',\
                    'IR_087c','IR_097c','IR_108c','IR_120c','IR_134c','HRVc']


RGBs_buildin = ['airmass','ash','cloudtop','convection','convection_co2',\
                 'day_microphysics','dust','fog','green_snow','ir108',\
                 'natural','night_fog','night_microphysics','night_overview',\
                 'overview','overview_sun','red_snow','refl39_chan','snow',\
                 'vis06','wv_high','wv_low']

RGBs_user = ['HRoverview','hr_natural','hr_airmass','sandwich','HRVFog','DayNightFog',\
             'HRVir108c','HRVir108','hrvIR108','VIS006ir108c','VIS006ir108','vis006IR108','sza','ndvi','IR_039c_CO2',\
             'VIS006-IR_016','IR_039-IR_108','WV_062-WV_073','WV_062-IR_108','IR_087-IR_108',\
             'IR_087-IR_120','IR_120-IR_108','WV_073-IR_134','trichannel','clouddepth','fls','streamplot',\
             'streamplot-100hPa','streamplot-200hPa','streamplot-300hPa','streamplot-400hPa','streamplot-500hPa',\
             'streamplot-600hPa','streamplot-700hPa','streamplot-800hPa','streamplot-900hPa','streamplot-1000hPa']


CMa =['CMa', 'CMa_DUST', 'CMa_QUALITY', 'CMa_VOLCANIC']  # PGE 1
CT = ['CT', 'CT_PHASE', 'CT_QUALITY']                    # PGE 2
CTTH = ['CTH', 'CTT', 'CTP']                             # PGE 3
PC = ['PC']                                              # PGE 4
CRR = ['CRR']                                            # PGE 5

old_sphr_format=False
if old_sphr_format:                                      # PGE 13
   SPhR = ['SPhR_BL','SPhR_CAPE','SPhR_HL','SPhR_KI','SPhR_LI','SPhR_ML','SPhR_QUALITY','SPhR_SHW','SPhR_TPW']
else:
   SPhR = ['sphr_bl','sphr_cape','sphr_diffbl','sphr_diffhl','sphr_diffki','sphr_diffli','sphr_diffml',\
           'sphr_diffshw','sphr_difftpw','sphr_hl','sphr_ki','sphr_li','sphr_ml','sphr_quality',\
           'sphr_sflag','sphr_shw','sphr_tpw']
PPh = ["PCPh", "CRPh"]                                   # PGE 14 

NWCSAF = CMa + CT + CTTH + PC + CRR + SPhR + PPh

Clear_sky = ['RII', 'GII']

CPP=['azidiff','cth','cldmask','cot','cph','ctt','cwp','dcld','dcot','dcwp','dndv','dreff',\
     'precip','precip_ir','qa','reff','satz','sds','sds_cs','sds_diff','sds_diff_cs',\
     'sunz','lat','lon','time_offset']

MSG_all = MSG + MSG_color + RGBs_buildin + RGBs_user + NWCSAF

SEVIRI_viewing_geometry = ['vza','vaa','lat','lon']

HSAF  = ['h03','h03b']

MSG_OT = ['ir_brightness_temperature',
               'ot_rating_ir',
               'ot_id_number',
               'ot_anvilmean_brightness_temperature_difference',
               'ir_anvil_detection',
               'visible_reflectance',
               'ot_rating_visible',
               'ot_rating_shadow',
               'ot_probability',
               'surface_based_cape',
               'most_unstable_cape',
               'most_unstable_equilibrium_level_temperature',
               'tropopause_temperature',
               'surface_1km_wind_shear',
               'surface_3km_wind_shear',
               'surface_6km_wind_shear',
               'ot_potential_temperature',
               'ot_height',
               'ot_pressure',
               'parallax_correction_latitude',
               'parallax_correction_longitude']

#################

swissradar = ['PRECIP','POH','MESHS','VIL', 'MaxEcho','EchoTOP15','EchoTOP20','EchoTOP45','EchoTOP50']

#################

swisstrt = ['TRT']

#################

cosmo_vars_const=["SOILTYP"]
cosmo_vars_2d=["lon_1", "lat_1",\
               "TWATER", "tropopause_height", "tropopause_temperature", "tropopause_pressure", \
               "FF_10M", "VMAX_10M", "CAPE_MU", "CAPE_ML", "CAPE_3KM", "CIN_MU", "CIN_ML", \
               "SLI", "LCL_ML", "LFC_ML", "T_2M", "TD_2M", "GLOB", "PS", \
               "PMSL", "PMSLr", "HZEROCL", "WSHEAR_0-3km", "WSHEAR_0-6km", "SYNMSG_BT_CL_IR10.8","IR_108-COSMO-minus-MSG", \
               "SDI_2", "SWISS12"]
cosmo_vars_3d=["POT_VORTIC", "THETAE", "MCONV", "geopotential_height", "RELHUM", "T_SO", "W_SO", "OMEGA",\
               "U", "U-100hPa", "U-200hPa", "U-300hPa", "U-400hPa", "U-500hPa", "U-600hPa", "U-700hPa", "U-800hPa", "U-900hPa", "U-1000hPa",\
               "V", "V-100hPa", "V-200hPa", "V-300hPa", "V-400hPa", "V-500hPa", "V-600hPa", "V-700hPa", "V-800hPa", "V-900hPa", "V-1000hPa"]
cosmo_lightninghail=["LPI","DHAIL_AV","DHAIL_SD","DHAIL_MX"]

cosmo = cosmo_vars_2d+cosmo_vars_3d+cosmo_lightninghail

#################

ninjo_chan_id = {'THX-ic_nrEURO1km':     8300015,
                 'THX-cg_nrEURO1km':     8400015,
                 'THX-tot_nrEURO1km':    8500015,
                 'HRoverview_nrEURO1km': 8600015,
                 'COALITION2_nrEURO1km': 8800015, 
                 'h03_nrEURO3km':        8900015,
                 'ref_nrEURO1km':        9000015,
                 'cot_nrEURO1km':        9100015,
                 'PCPh_nrEURO1km':       9200015,
                 'CRR_nrEURO1km':        9300015,
                 'CI_nrEURO1km':         9400015,
                 'OT_nrEURO1km':         9500015,
                 'COALITION2_nrEURO3km': 9600015, 
                 'IR-108_nrEURO3km':     9700015,
                 'IR-108_nrEURO1km':     9800015, 
                 'TRT_nrEURO1km':        9900015}

#7900015=COALITION
#### New satellite products MCH (Ulrich Hamann - APR 2016)
#8300015 = Lightning rate (IC)
#8400015 = Lightning rate (CG)
#8500015 = Lightning rate (TOT)
#8600015 = HRoverview
#8700015 = HRW (streamlines)
#8800015 = COALITION2                            # MET9_RSS_COALITION2_nrEURO1km_201707170945.tif  
#8900015 = H-SAF RR-int. (calibrated with Pol)
#9000015 = cloud effective radius
#9100015 = cloud optical depth
###### NWCSAF products (Ulrich Hamann - APR 2016)           
#9200015 = Prob. of prec. (PCPh)
#9300015 = CRR (PCPh)
#9400015 = CI (Convective Initiation)
#9500015 = Overshooting Tops
#9600015 = PyTroll1                             #MET9_RSS_COALITION2_nrEURO3km_201707170945.tif 
#9700015 = PyTroll2                             #MET9_RSS_IR108_nrEURO3km_201707170945.tif 
#9800015 = PyTroll3                             
#9900015 = PyTroll4



