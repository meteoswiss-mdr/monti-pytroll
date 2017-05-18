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

RGBs_user = ['HRoverview','sandwich','HRVir108','HRVir108','ndvi',\
             'WV_062_minus_WV_073','WV_062_minus_IR_108','IR_087_minus_IR_108','IR_087_minus_IR_120',\
             'IR_120_minus_IR_108','WV_073_minus_IR_134','trichannel','clouddepth']

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

Radar = ['precip','poh','mesh','vil', 'maxecho','echotop15','echotop20','echotop45','echotop50']
HSAF  = ['h03']

SEVIRI_viewing_geometry = ['vza','vaa','lat','lon']

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
