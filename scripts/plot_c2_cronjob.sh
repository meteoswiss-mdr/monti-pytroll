#!/bin/bash

# go to operational pytroll folder  
echo '***'
echo '*** start plot_c2_cronjob.sh'
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

echo "*** Start to make seviri pictures (loop until all data is there)"
echo 
cd $PYTROLLHOME/scripts
python plot_coalition2.py input_coalition2_cronjob #> /tmp/plot_coalition2.txt 2>&1

python postprocessing.py --parea ccs4 -c "" -m [["MSG_C2rgb-IR-108","MSG_CT","MSG_HRoverview","MSG_TRT-radar-convection","MSG_radar-convection","MSG_THX-HRVir108"]] --delay 24 input_coalition2_cronjob
python postprocessing.py --parea ccs4 -c "" -m [["MSG_C2rgb-IR-108","MSG_CT","MSG_HRoverview","MSG_TRT-radar-convection","MSG_radar-convection","MSG_THX-HRVir108"]] --delay 34 input_coalition2_cronjob

# remove uncompressed data older than 10min
export mm=60
echo "*** Remove uncompressed data files older than " ${mm} "min"
find /tmp/SEVIRI_DECOMPRESSED_$LOGNAME/?-000-MSG?__-MSG?_???____-*_-*___-*-__ -type f -mmin +${mm} -delete
find /tmp/SEVIRI_DECOMPRESSED/?-000-MSG?__-MSG?_???____-*_-*___-*-__          -type f -mmin +${mm} -delete
