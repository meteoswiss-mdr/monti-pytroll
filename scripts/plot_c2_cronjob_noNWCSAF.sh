#### 
### ### #!/bin/bash

# go to operational pytroll folder  
echo '***'
echo '*** start plot_c2_cronjob2.sh'
. /opt/users/$LOGNAME/PyTroll/setup/bashrc
#export python=/usr/bin/python
export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

export dir1=/opt/users/$LOGNAME/PyTroll/scripts
cd ${dir1}

echo "*** Start to make seviri pictures (loop until all data is there)"
echo 
$python ${dir1}/plot_coalition2.py input_coalition2_noNWCSAF.py > /tmp/plot_coalition2_noNWCSAF.txt 2>&1

# remove uncompressed data older than mm min
export mm=50
echo "*** Remove uncompressed data files older than "$mm"min"
#find /tmp/?-000-MSG?__-MSG?_???____-*_-*___-*-__ -type f -mmin +${mm} -exec rm {} \;
find /tmp/?-000-MSG?__-MSG?_???____-*_-*___-*-__  -type f -mmin +${mm} -delete \;

find /tmp/SEVIRI_DECOMPRESSED_$LOGNAME/?-000-MSG?__-MSG?_???____-*_-*___-*-__ -type f -mmin +${mm} -delete