#!/bin/bash

# shell variables
#----------------

echo '***'
echo '*** start plot_hrw.sh'
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

cd $PYTROLLHOME/scripts

echo "*** Start to make high resolution wind images"
python plot_hrw_cronjob.py input_hrw_cronjob.py $1 $2 $3 $4 $5  # > /tmp/plot_msg.txt 2>&1

#python postprocessing.py --parea ccs4  input_hrw_cronjob.py

## remove result files older than 1 hour (done in plot_ms.sh)
#echo "*** Remove all result files older than 1 hour"
#find /data/cinesat/out/* -type f -mmin +60 -exec rm {} \;
