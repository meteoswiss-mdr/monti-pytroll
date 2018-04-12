#!/bin/bash

echo '***'
echo '*** start plot_radar.sh'
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

cd $PYTROLLHOME/scripts

echo "*** Start to radar iamges"
## execute plot_radar pytroll script 
python plot_radar_cronjob.py           # > /tmp/plot_radar_cronjob.txt 2>&1

## remove result files older than 1 hour (done in plot_ms.sh)
#echo "*** Remove all result files older than 1 hour"
#find /data/cinesat/out/* -type f -mmin +60 -exec rm {} \;
