#!/bin/bash

# go to operational pytroll folder  
export dir1=/data/OWARNA/hau/pytroll/programs/
export PYTHONPATH=/home/cinesat/python/lib/python2.7/site-packages
export XRIT_DECOMPRESS_PATH=/data/OWARNA/hau/pytroll/bin/xRITDecompress
echo ''

cd ${dir1}

echo "*** Start to make seviri pictures (loop until all data is there)"
export PPP_CONFIG_DIR=/data/OWARNA/hau/pytroll/cfg_nrt
/usr/bin/python ${dir1}/loop_msg.py input_hsaf_cronjob # > /tmp/loop_msg.txt 2>&1

## execute plot_msg pytroll script once (to create nc files)
#export PPP_CONFIG_DIR=/data/OWARNA/hau/pytroll/cfg_offline
#/usr/bin/python ${dir1}/plot_msg.py input_rad_ncfiles # > /tmp/plot_msg.txt 2>&1
#/usr/bin/python ${dir1}/plot_msg.py input_nwc_ncfiles

## remove result files older than 1 hour (done in plot_ms.sh)
#echo "*** Remove all result files older than 1 hour"
#find /data/cinesat/out/* -type f -mmin +60 -exec rm {} \;