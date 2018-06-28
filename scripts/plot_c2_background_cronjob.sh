#### 
### ### #!/bin/bash

# go to operational pytroll folder  
#export PYTHONPATH=/opt/users/common/packages/anaconda2/bin:/opt/users/hau/PyTroll//scripts
#export XRIT_DECOMPRESS_PATH=/opt/users/common/bin/xRITDecompress
#export PPP_CONFIG_DIR=/opt/users/hau/PyTroll//etc/
echo '***'
echo '*** start plot_c2_background.sh'
. /opt/users/hau/PyTroll/setup/bashrc
#export python=/usr/bin/python
export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

export dir1=/opt/users/hau/PyTroll/scripts
cd ${dir1}

echo "*** Start to make seviri pictures (loop until all data is there)"
echo 
#$python ${dir1}/plot_msg.py input_c2_background # > /tmp/loop_msg.txt 2>&1
$python ${dir1}/loop_msg.py input_c2_background # > /tmp/loop_msg.txt 2>&1
#$python ${dir1}/loop_msg.py input_nwc_pngfiles 

## execute plot_msg pytroll script once (to create nc files)
#export PPP_CONFIG_DIR=/data/OWARNA/hau/pytroll/cfg_offline
#$python ${dir1}/plot_msg.py input_rad_ncfiles # > /tmp/plot_msg.txt 2>&1
#$python ${dir1}/plot_msg.py input_nwc_ncfiles

# remove result files older than 45min
echo "*** Remove all result files older than 45min"
find /data/cinesat/out/*png -type f -mmin +45 -delete \;

# remove uncompressed data older than 10min
echo "*** Remove uncompressed data files older than 12min"
#find /tmp/?-000-MSG?__-MSG?_???____-*_-*___-*-__ -type f -mmin +15 -exec rm {} \;
find /tmp/?-000-MSG?__-MSG?_???____-*_-*___-*-__  -type f -mmin +12 -delete \;
find /tmp/SEVIRI_DECOMPRESSED_$LOGNAME/?-000-MSG?__-MSG?_???____-*_-*___-*-__  -type f -mmin +12 -delete \;
