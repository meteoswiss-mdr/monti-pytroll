#!/bin/bash

# go to operational pytroll folder  
#echo ''
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

cd $PYTROLLHOME/scripts

echo "*** Start to make NWCSAF pictures (loop until all data is there)"
echo 
python loop_msg.py input_nwc_palette_cronjob     $1 $2 $3 $4 $5
python loop_msg.py input_nwc_CRR-CRPh_cronjob    $1 $2 $3 $4 $5
python loop_msg.py input_nwc_colortable_cronjob  $1 $2 $3 $4 $5
