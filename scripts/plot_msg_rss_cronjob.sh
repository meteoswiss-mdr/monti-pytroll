#!/bin/bash

# go to operational pytroll folder  
echo '***'
echo '*** start plot_msg_rss_cronjob.sh'
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python
which python

echo "*** Start to make seviri pictures (loop until all data is there)"
echo "************************************************************"
echo 
cd $PYTROLLHOME/scripts
echo "    python plot_msg.py input_rad_pngfiles"
python plot_msg.py input_rad_pngfiles
echo "    python plot_msg.py input_msg_rss_blackwhite"
python plot_msg.py input_msg_rss_blackwhite      #> /tmp/plot_msg_input_msg2_blackwhite.txt 2>&1

# remove uncompressed data older than 10min
export mm=60
echo "*** Remove uncompressed data files older than " ${mm} "min"
find /tmp/SEVIRI_DECOMPRESSED_$LOGNAME/?-000-MSG?__-MSG?_???____-*_-*___-*-__ -type f -mmin +${mm} -delete
find /tmp/SEVIRI_DECOMPRESSED/?-000-MSG?__-MSG?_???____-*_-*___-*-__          -type f -mmin +${mm} -delete
