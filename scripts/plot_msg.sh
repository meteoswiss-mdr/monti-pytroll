#### 
### ### #!/bin/bash

# go to operational pytroll folder  
#export PYTHONPATH=/opt/users/common/packages/anaconda2/bin:/opt/users/hau/PyTroll//scripts
#export XRIT_DECOMPRESS_PATH=/opt/users/common/bin/xRITDecompress
#export PPP_CONFIG_DIR=/opt/users/hau/PyTroll//etc/
#echo ''
. /opt/users/hau/PyTroll/setup/bashrc
#export python=/usr/bin/python
export python=/opt/users/common/packages/anaconda2/envs/PyTroll_hau/bin/python


export dir1=/opt/users/hau/PyTroll/scripts
cd ${dir1}

echo "*** Start to make seviri pictures (loop until all data is there)"
echo 
$python ${dir1}/plot_msg.py input_c2_background # > /tmp/loop_msg.txt 2>&1
#$python ${dir1}/loop_msg.py input_c2_background # > /tmp/loop_msg.txt 2>&1
#$python ${dir1}/loop_msg.py input_nwc_pngfiles 

## execute plot_msg pytroll script once (to create nc files)
#export PPP_CONFIG_DIR=/data/OWARNA/hau/pytroll/cfg_offline
#$python ${dir1}/plot_msg.py input_rad_ncfiles # > /tmp/plot_msg.txt 2>&1
#$python ${dir1}/plot_msg.py input_nwc_ncfiles

## remove result files older than 1 hour
#echo "*** Remove all result files older than 1 hour"
#find /data/cinesat/out/* -type f -mmin +60 -exec rm {} \;
