product = {}
product['CMA']     = [ 'cloudmask']
product['CT']      = [ 'cloudtype']
product["CTTH"]    = [ 'cloud_top_height', 'cloud_top_pressure', 'cloud_top_temperature']
product["CMIC"]    = [ 'cloud_top_phase', 'cloud_drop_effective_radius', 'cloud_optical_thickness', 'cloud_liquid_water_path', 'cloud_ice_water_path']
product["PC"]      = [ 'precipitation_probability']
product["PC-Ph"]   = [ ]
product["CRR"]     = [ 'convective_rain_rate', 'convective_precipitation_hourly_accumulation']
product["CRR-Ph"]  = [ ]
product["iSHAI"]   = [ 'total_precipitable_water', 'boundary_layer', 'medium_layer', 'high_layer', 'showalter_index', 'lifted_index']
product["CI"]      = [ 'convection_initiation_prob30']     # , 'convection_initiation_prob60', 'convection_initiation_prob90']
product["RDT-CW"]  = [ 'rdt_cell_type']
product["ASII-NG"] = [ 'asii_prob' ]
product["HRW"]     = [ ]

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
