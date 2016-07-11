# depiction options
# -----------------

# choose color combination
#rgb_display = 'us-cd-gi'
rgb_display = 'cd-us-gi'

# choose saturation enhancement 
#colour_enhancement_factor = 1   # 1 gives the original colour
colour_enhancement_factor = 2   # 1 gives the original colour
# colour_enhancement_factor = 3 # ??? 2 seems to be more colorful than 3 ???

# choose saturation for each indictor
cmax_cd =  255   
cmin_cd =  -80   
cmax_us =  255
cmin_us =    0
cmax_gi =   85  # 140 for 5 tests
cmin_gi =    0  

# backgroundcolor 
background_color = [255,255,255]   # white
background_color = [  0,  0,  0]   # black

# foregroud and background opacity (== 1 - transparency)
#foregroud_alpha  = 200      # pretty opaque
foregroud_alpha  = 255      # opaque
background_alpha =   50      # transparent
#background_alpha = 255     # opaque

# threshold of the interest field tests 
# -------------------------------------
vmin_cd =    [-50.,    -20.,    210.,    -14.,    -32.,    - 3.]
vmax_cd =    [ 1.,      2.,    300.,      3.,      6.,     15.]

th_cd   =    [-16.,    - 7.5,   250.,    - 2.,    -12.5,    2.2]

vmin_gi =    [- 6.,    - 8.,    - 5.,    - 3.,   - 6.,     -32.,    -10.]
vmax_gi =    [ 10.,      4.,      8.,      6.,     6.,      32.,      2.]

th_gi   =    [  2.,    - 1.5,    1.5,    - 1.,   - 1.,       0.,    - 1.]

vmin_us =    [-12.,    -50.,    -60.,    -15.,   - 8.,     -40.,    -40.,    -12.]
vmax_us =    [ 20.,     50.,     60.,     20.,    10.,      50.,     40.,     12.]

th_us   =    [  2.5,   -12.,    -10.,      2.5,    2.,      13.,     10.,    - 7.]    


# settings of the forth_mask (test to pass in addition to cloud depth, updraft strength and glaciation)
# -----------------------------------------------------------------------------------------------------
# if forth_mask == 'IR_039_minus_IR_108', check if IR_039_minus_IR_108 >= thresholds below 
mature_th_chDiff     = 25.0
developing_th_chDiff = 8.0

# if forth_mask == 'CloudType', then only a few cloud types 
mature_ct            = [17,14,12]
developing_ct        = [8,9,10,17,14,12]

# settings of the forced_mask (force to include any pixel (in mature_mask) regardless of the other thresholds)
# ------------------------------------------------------------------------------------------------------------
# threshold for forced_mask 
force_th_chDiff      = 40.0
cloud_type_forced    = [17,14]

#additional threshold for mask_cirrus (cd6 > th)
# -----------------------------------
th_cirrus            = 4.0


# additional parameters for cleaning (if skimage) 
# -----------------------------------------------
# [removes small holes within clouds (max_holes = max number of px to fill with clouds) and small clouds (min_cloud = number px minimum to keep a cloud)]
min_cloud = 20.0 #100.0 #
max_holes = 500.0


# additional parameters for cleaning (if mask_labelsSmall_lowUS) 
# -----------------------------------------------
# [removes cells with mean_us <= 3 and area<=500 (move this also to coalition2_settings)]
mask_labelsSmall_lowUS_maxUS = 3.0 
mask_labelsSmall_lowUS_maxArea = 500.0
