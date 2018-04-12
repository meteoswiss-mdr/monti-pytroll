#!/bin/bash

# go to operational pytroll folder  
echo ''
echo ". /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment"
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python
which python

echo 'cd $PYTROLLHOME/scripts'
cd $PYTROLLHOME/scripts

echo "*** Start to make odyssey images (loop until all data is there)"
echo

export i=0
while [ $i -lt 60 ]
do
   # Odyssey composite
   python plot_odyssey_cronjob.py # > /tmp/plot_msg.txt 2>&1

   i=$[$i+1]
   n_files=$(find /data/cinesat/out/ODY_RATE* -mmin -2 | wc -l)
   echo $n_files " files produced"$(find /data/cinesat/out/ODY_RATE* -mmin -2)
   echo $n_files " files produced"
   echo $n_files " files produced"
   echo $n_files " files produced"
   if [[ "$n_files" -gt 0 ]]
   then
      echo "break while"
      break
   fi
   sleep 10
done

## remove result files older than 1 hour
#echo "*** Remove all result files older than 1 hour"
#find /data/cinesat/out/* -type f -mmin +60 -exec rm {} \;
