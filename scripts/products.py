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
                 'CT_nrEURO1km':         9800015, 
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



