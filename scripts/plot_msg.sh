#### 
### ### #!/bin/bash

# go to operational pytroll folder  
#echo ''
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

cd $PYTROLLHOME/scripts

echo "*** Start to make seviri pictures (loop until all data is there)"
echo 
python loop_msg.py input_rad_pngfiles 
python loop_msg.py input_msg2_blackwhite
python loop_msg.py input_c2_background  
