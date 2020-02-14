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
#python postprocessing.py       --parea ccs4       -c ["h03b-HRVir108","radar-HRVir108"]                                                      input_hsaf_cronjob.py
#python postprocessing.py --scp --parea ccs4       -c []                -m [["MSG_radar-HRVir108","MSG_h03b-HRVir108"]]                       input_hsaf_cronjob.py
python postprocessing.py       --parea odysseyS25 -c ['h03b-HRVir108',"RATE-HRVir108"]                                                       input_hsaf_cronjob.py
python postprocessing.py --scp --parea odysseyS25 -c []                -m [["MSG_rrMlp-HRVir108","MSG_RATE-HRVir108","MSG_h03b-HRVir108"]]   input_hsaf_cronjob.py

## remove result files older than 1 hour
#echo "*** Remove all result files older than 1 hour"
#find /data/cinesat/out/* -type f -mmin +60 -exec rm {} \;
