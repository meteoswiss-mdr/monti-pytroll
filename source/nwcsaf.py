product = {}
product['CMA']     = [ 'cloudmask' ]
product['CT']      = [ 'cloudtype' ]
product["CTTH"]    = [ 'cloud_top_height', 'cloud_top_pressure', 'cloud_top_temperature' ]
product["CMIC"]    = [ 'cloud_top_phase', 'cloud_drop_effective_radius', 'cloud_optical_thickness', 'cloud_liquid_water_path', 'cloud_ice_water_path' ]
product["PC"]      = [ 'precipitation_probability' ]
product["PC-Ph"]   = [ 'precipitation_probability_physical' ] # ???
product["CRR"]     = [ 'convective_rain_rate', 'convective_precipitation_hourly_accumulation' ]
product["CRR-Ph"]  = [ 'convective_rain_rate_physical' ] # ???
product["iSHAI"]   = [ 'total_precipitable_water', 'boundary_layer', 'medium_layer', 'high_layer', 'showalter_index', 'lifted_index' ]
product["CI"]      = [ 'convection_initiation_prob30' ]     # , 'convection_initiation_prob60', 'convection_initiation_prob90']
product["RDT-CW"]  = [ 'rdt_cell_type' ]
product["ASII-NG"] = [ 'asii_prob' ]
product["HRW"]     = [ 'wind_hrvis', 'wind_vis06', 'wind_vis08', 'wind_ir108', 'wind_ir120', 'wind_wv062', 'wind_wv073' ]

datasets = {}
datasets['CMA']     = [ 'cma', 'cma_cloudsnow', 'cma_cloudsnow_pal', 'cma_conditions', 'cma_dust', 'cma_dust_pal', 'cma_pal', 'cma_status_flag', 'cma_volcanic', 'cma_volcanic_pal' ]
datasets['CT']      = [ 'ct', 'ct_pal', 'ct_conditions', 'ct_cumuliform', 'ct_cumuliform_pal', 'ct_quality' ]
datasets["CTTH"]    = [ 'ctth_alti', 'ctth_alti_pal', 'ctth_conditions', 'ctth_effectiv', 'ctth_effectiv_pal', 'ctth_method', \
                        'ctth_pres', 'ctth_pres_pal', 'ctth_quality', 'ctth_status_flag', 'ctth_tempe', 'ctth_tempe_pal']
datasets["CMIC"]    = [ 'cmic_cot', 'cmic_cot_pal', 'cmic_iwp', 'cmic_iwp_pal', 'cmic_lwp', 'cmic_lwp_pal', \
                        'cmic_phase', 'cmic_phase_pal', 'cmic_quality', 'cmic_reff', 'cmic_reff_pal', 'cmic_status_flag' ]
datasets["PC"]      = [ 'pc', 'pc_conditions', 'pc_pal', 'pc_quality' ]
datasets["PC-Ph"]   = [ 'ppp' ] # ???
datasets["CRR"]     = [ 'crr', 'crr_accum', 'crr_accum_pal', 'crr_conditions', 'crr_intensity', 'crr_intensity_pal', 'crr_pal', 'crr_quality', 'crr_status_flag' ]
datasets["CRR-Ph"]  = [ 'crrp' ] # ???
datasets["iSHAI"]   = [ 'ihsai_status_flag', 'ishai_bl', 'ishai_bl_pal', 'ishai_conditions',
                        'ishai_diffbl', 'ishai_diffbl_pal', 'ishai_diffhl', 'ishai_diffhl_pal', 'ishai_diffml', 'ishai_diffml_pal',\
                        'ishai_diffki', 'ishai_diffki_pal', 'ishai_diffli', 'ishai_diffli_pal', 'ishai_diffshw', 'ishai_diffshw_pal',\
                        'ishai_diffskt', 'ishai_diffskt_pal', 'ishai_difftoz', 'ishai_difftoz_pal', 'ishai_difftpw', 'ishai_difftpw_pal',\
                        'ishai_hl', 'ishai_hl_pal', 'ishai_ki', 'ishai_ki_pal', 'ishai_li', 'ishai_li_pal', 'ishai_ml', 'ishai_ml_pal',\
                        'ishai_quality', 'ishai_residual', 'ishai_residual_pal', 'ishai_shw', 'ishai_shw_pal', 'ishai_skt', 'ishai_skt_pal',\
                        'ishai_toz', 'ishai_toz_pal', 'ishai_tpw', 'ishai_tpw_pal']
datasets["CI"]      = [ 'ci_conditions', 'ci_pal', 'ci_prob30', 'ci_prob60', 'ci_prob90', 'ci_prob_pal', 'ci_quality', 'ci_status_flag' ]
datasets["RDT-CW"]  = [ 'MapCellCatType', 'MapCellCatType_pal', 'MapCell_conditions', 'MapCell_quality' ]
datasets["ASII-NG"] = [ 'asii_turb_prob_pal', 'asii_turb_trop_prob', 'asii_turb_trop_prob_status_flag',\
                        'asii_turb_wave_prob', 'asii_turb_wave_prob_status_flag',\
                        'asiigw_conditions', 'asiigw_quality', 'asiitf_conditions', 'asiitf_quality' ]
datasets["HRW"]     = [ 'wind_hrvis', 'wind_vis06', 'wind_vis08', 'wind_ir108', 'wind_ir120', 'wind_wv062', 'wind_wv073' ] # ???


pge_id={}
pge_id[ 'cloudmask' ]                          = ["CMA"]
pge_id[ 'cloudtype' ]                          = ["CT"]
pge_id[ 'cloud_top_height' ]                   = ["CTTH"]
pge_id[ 'cloud_pressure' ]                     = ["CTTH"]
pge_id[ 'cloud_top_temperature' ]              = ["CTTH"]
pge_id[ 'cloud_top_phase' ]                    = ["CMIC"]
pge_id[ 'cloud_drop_effective_radius' ]        = ["CMIC"]
pge_id[ 'cloud_optical_thickness' ]            = ["CMIC"]
pge_id[ 'cloud_liquid_water_path' ]            = ["CMIC"]
pge_id[ 'cloud_ice_water_path' ]               = ["CMIC"]
pge_id[ 'precipitation_probability' ]          = ["PC"]
pge_id[ 'precipitation_probability_physical' ] = ["PC-Ph"]
pge_id[ 'convective_rain_rate' ]               = ["CRR"]
pge_id[ 'convective_precipitation_hourly_accumulation' ] = ["CRR"]
pge_id[ 'convective_rain_rate_physical' ]       = ["CRR-Ph"]
pge_id[ 'total_precipitable_water' ]    = ["iSHAI"]
pge_id[ 'boundary_layer' ]              = ["iSHAI"]
pge_id[ 'medium_layer' ]                = ["iSHAI"]
pge_id[ 'high_layer' ]                  = ["iSHAI"]
pge_id[ 'showalter_index' ]             = ["iSHAI"]
pge_id[ 'lifted_index' ]                = ["iSHAI"]
pge_id[ 'cape' ]                        = ["iSHAI"]
pge_id[ 'convection_initiation_prob30' ] = ["CI"]
pge_id[ 'rdt_cell_type' ]                = ["RDT-CW"]
pge_id[ 'asii_prob' ]        = ['asii_prob']
pge_id[ 'wind_hrvis' ]        = [ "HRW"]
pge_id[ 'wind_vis06' ]        = [ "HRW"]
pge_id[ 'wind_vis08' ]        = [ "HRW"]
pge_id[ 'wind_ir108' ]        = [ "HRW"]
pge_id[ 'wind_ir120' ]        = [ "HRW"]
pge_id[ 'wind_wv062' ]        = [ "HRW"]
pge_id[ 'wind_wv073' ]        = [ "HRW"]


ninjo_suffix = 'METEOSATNOWCSAF_EUROPA_ZENTRAL'
ninjo_def = {}
ninjo_def['cloudmask']  = ['CC', 'msg_cloudmask']
ninjo_def['cloudtype']  = ['CT', 'msg_cloudtype']
ninjo_def['cloud_top_height']  = ['CTH', 'msg_cloudtop_height']
ninjo_def['cloud_top_temperature']  = ['CTT', 'msg_cloudtop_temp']
ninjo_def['convective_rain_rate']  = ['CRR', 'msg_convective_rain_rate']

keywords_CMA = ['GEO-CMA quality', 'GEO-CMA completness', 'Clear FOVS', ' Cloudy ', 
                'Thin Cloud over snow FOVS', 'Snow or Ice FOVS'] 
keywords_CT = ['GEO-CT quality', 'GEO-CT completness', 'clear_land', 'clear_sea', 'snowice_land', '  vlow', '  low', '  mid-level  ', 
               ' hi_opaq', ' vq_opaq', ' fractional', 'semitr_thin', 'semitr_mean', 'semitr_thick', 'semitr_above_low', 'semitr_above_snow'] 
keywords_CTTH = ['GEO-CTTH quality', 'GEO-CTTH completness', 'Very low & low clouds', 
                 'mid-level clouds', 'high clouds', 'semi-transparent clouds'] 
keywords_CMIC = ['GEO-CMIC quality', 'GEO-CMIC completness',  '  liquid', '  ice', '  mixed', 
                 '  undefined', 'For water cloud  reff', 'For ice cloud  reff'] 
