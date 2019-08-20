#!/bin/bash

# go to operational pytroll folder  
#echo ''
if [ -d "/opt/users/$LOGNAME/monti-pytroll/" ]; then
    . /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
else
    . /opt/users/$LOGNAME/PyTroll/setup/bashrc no_virtual_environment
fi
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

cd $PYTROLLHOME/scripts

echo "*** Start to make seviri pictures (loop until all data is there)"
echo 
python loop_msg.py input_trt_cronjob
