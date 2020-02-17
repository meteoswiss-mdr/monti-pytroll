#### 
### ### #!/bin/bash

# go to operational pytroll folder  
echo '***'
echo '*** start plot_daymicro_cronjob.sh'
. /opt/users/hau/PyTroll/setup/bashrc
#export python=/usr/bin/python
export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

export dir1=/opt/users/$LOGNAME/PyTroll/scripts
cd ${dir1}

echo "*** Start to make seviri pictures (loop until all data is there)"
echo 
$python ${dir1}/loop_msg.py input_daymicrophysics # > /tmp/loop_msg.txt 2>&1
$python ${dir1}/loop_msg.py input_daymicrophysics_fulldisk # > /tmp/loop_msg.txt 2>&1


# remove result files older than 45min
echo "*** Remove all result files older than 45min"
find /data/cinesat/out/*png -type f -mmin +45 -exec rm {} \;

# remove uncompressed data older than 30min
export mm=50
echo "*** Remove uncompressed data files older than "${mm}"min"
#find /tmp/?-000-MSG?__-MSG?_???____-*_-*___-*-__ -type f -mmin ${mm} -exec rm {} \;
find /tmp/?-000-MSG?__-MSG?_???____-*_-*___-*-__  -type f -mmin ${mm} -delete \;
