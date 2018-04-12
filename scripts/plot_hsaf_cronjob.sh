#!/bin/bash

# go to operational pytroll folder  
#echo ''
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

cd $PYTROLLHOME/scripts

echo "*** Start to make seviri pictures (loop until all data is there)"
echo 
python loop_msg.py input_hsaf_cronjob
python loop_msg.py input_hsaf_EuropeCanaryS95_cronjob


# create composite 
python postprocessing.py --scp -a odysseyS25 -c 'h03-ir108'                  input_hsaf_cronjob.py
python postprocessing.py --scp --parea ccs4  -c ["h03-ir108","h03-HRV"] -m [["MSG_radar-ir108","MSG_h03-ir108"],["MSG_radar-HRV","MSG_h03-HRV"]] input_hsaf_cronjob.py
python postprocessing.py --scp --parea odysseyS25  -c '' -m [["MSG_RATE-ir108","MSG_h03-ir108"],["MSG_RATE-HRV","MSG_h03-HRV"]] input_hsaf_cronjob.py

## remove result files older than 1 hour
#echo "*** Remove all result files older than 1 hour"
#find /data/cinesat/out/* -type f -mmin +60 -exec rm {} \;
