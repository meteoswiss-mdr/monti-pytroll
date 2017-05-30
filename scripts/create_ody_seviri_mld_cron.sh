#!/bin/bash

# go to operational pytroll folder  
export dir1=/opt/users/hau/PyTroll/scripts/
echo ''
cd ${dir1}
. /opt/users/$LOGNAME/PyTroll/setup/bashrc
export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

echo "*** Start to make seviri pictures (loop until all data is there)"
$python ${dir1}/create_ody_seviri_mld_cron.py # > /tmp/loop_msg.txt 2>&1
