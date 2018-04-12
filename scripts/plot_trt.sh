#!/bin/bash

echo '***'
echo '*** start plot_trt.sh'
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

cd $PYTROLLHOME/scripts

echo "*** Start to plot lightning images"
## execute plot_lightning pytroll script 
python plot_trt_cronjob.py           # > /tmp/plot_trt_cronjob.txt 2>&1

## remove result files older than 1 hour (done in plot_ms.sh)
#echo "*** Remove all result files older than 1 hour"
#find /data/cinesat/out/* -type f -mmin +60 -exec rm {} \;
