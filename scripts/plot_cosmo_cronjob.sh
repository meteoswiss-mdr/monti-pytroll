#!/bin/bash

# go to operational pytroll folder  
echo '***'
echo '*** start plot_msg_cosmo_cronjob.sh'
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python
#which python

day=`date --utc '+%d'`
month=`date --utc '+%m'`
year=`date --utc '+%Y'`
hour=`date --utc '+%H'`
minute=`date --utc '+%M'`

echo "current time: " $year $month $day $hour $minute

echo "*** Start to make seviri pictures (loop until all data is there)"
echo "************************************************************"
echo 
cd $PYTROLLHOME/scripts
echo " "
echo "--------------------------------------------------------"
echo "    python loop_msg.py input_cosmo_cronjob    (by COSMO simulated 10.8 SEVIRI image)"
python loop_msg.py input_cosmo_cronjob.py $year $month $day $hour 0
echo " "
echo "    python plot_msg_minus_cosmo.py input_msg_cosmo_cronjob.py    (difference COSMO-MSG)"
python plot_msg_minus_cosmo.py input_msg_cosmo_cronjob.py $year $month $day $hour 0
echo " "



## remove uncompressed data older than 10min
#export mm=60
#echo "*** Remove uncompressed data files older than " ${mm} "min"
#find /tmp/SEVIRI_DECOMPRESSED_$LOGNAME/?-000-MSG?__-MSG?_???____-*_-*___-*-__ -type f -mmin +${mm} -delete
#find /tmp/SEVIRI_DECOMPRESSED/?-000-MSG?__-MSG?_???____-*_-*___-*-__          -type f -mmin +${mm} -delete
