#### 
### ### #!/bin/bash

# go to operational pytroll folder  
#export PYTHONPATH=/opt/users/common/packages/anaconda2/bin:/opt/users/hau/PyTroll//scripts
#export XRIT_DECOMPRESS_PATH=/opt/users/common/bin/xRITDecompress
#export PPP_CONFIG_DIR=/opt/users/hau/PyTroll//etc/
echo '***'
echo '*** start plot_hsaf_cronjob.sh'
. /opt/users/$LOGNAME/PyTroll/setup/bashrc
#export python=/usr/bin/python
export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

export dir1=/opt/users/$LOGNAME/PyTroll/scripts
cd ${dir1}

echo "*** Start to make seviri pictures (loop until all data is there)"
echo
$python ${dir1}/loop_msg.py input_hsaf_cronjob # > /tmp/loop_msg.txt 2>&1
