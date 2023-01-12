#!/bin/bash

echo '***'
echo '*** start virtual environment'
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc3 no_virtual_environment
#. /opt/users/$LOGNAME/PyTroll/setup/bashrc3 no_virtual_environment
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

cd $PYTROLLHOME/source

echo "*** Start to produce images for SATLive"
## execute plot_lightning pytroll script 
python  satlive_geo.py input_satlive.py    # > /tmp/demo_satpy_fog.txt 2>&1

## remove result files older than 1 hour (done in plot_ms.sh)
#echo "*** Remove all result files older than 1 hour"
#find /data/cinesat/out/* -type f -mmin +60 -exec rm {} \;
