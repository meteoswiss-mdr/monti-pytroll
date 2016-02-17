#!/bin/bash

# shell variables
#----------------
. ./set_python_paths.sh
export dir1=/data/OWARNA/hau/pytroll/programs/
export PPP_CONFIG_DIR=/data/OWARNA/hau/pytroll/cfg_nrt
export PYTHONPATH=/home/cinesat/python/lib/python2.7/site-packages
echo ''

echo 'PPP_CONFIG_DIR' $PPP_CONFIG_DIR

echo "*** Start to make seviri pictures"
## execute plot_msg pytroll script once 
#/usr/bin/python ${dir1}/plot_msg.py input_MSG # > /tmp/plot_msg.txt 2>&1
## execute plot_msg pytroll script in a loop until everything is processed 
#/usr/bin/python ${dir1}/loop_msg.py input_MSG # > /tmp/plot_msg.txt 2>&1
## execute plot_lightning pytroll script 
/usr/bin/python ${dir1}/plot_lightning_cronjob.py # > /tmp/plot_msg.txt 2>&1


## remove result files older than 1 hour (done in plot_ms.sh)
#echo "*** Remove all result files older than 1 hour"
#find /data/cinesat/out/* -mmin +60 -exec rm {} \;