#!/bin/bash

# shell variables
#----------------

export dir1=/data/OWARNA/hau/pytroll/programs/
export PPP_CONFIG_DIR=/data/OWARNA/hau/pytroll/cfg_nrt
export PYTHONPATH=/home/cinesat/python/lib/python2.7/site-packages
echo ''
echo 'PPP_CONFIG_DIR' $PPP_CONFIG_DIR

cd $dir1

echo "*** Start to make seviri pictures"
## execute plot_radar pytroll script 
/usr/bin/python $dir1/plot_radar_cronjob.py # > /tmp/plot_msg.txt 2>&1

## remove result files older than 1 hour (done in plot_ms.sh)
#echo "*** Remove all result files older than 1 hour"
#find /data/cinesat/out/* -type f -mmin +60 -exec rm {} \;