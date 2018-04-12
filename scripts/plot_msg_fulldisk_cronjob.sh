#!/bin/bash

echo ""
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
#export python=$CONDA_PATH/envs/PyTroll_$LOGNAME/bin/python
echo "which python"
which python

cd $PYTROLLHOME/scripts # necessary to specify input file without path

echo ""
echo "************************************************************"
echo "    python" $PYTROLLHOME/scripts/loop_msg.py input_msg_fulldisk_color_cronjob.py 
python $PYTROLLHOME/scripts/loop_msg.py input_msg_fulldisk_color_cronjob.py

echo ""
echo "************************************************************"
echo "    python" $PYTROLLHOME/scripts/loop_msg.py input_msg_fulldisk_blackwhite_cronjob.py  
python $PYTROLLHOME/scripts/loop_msg.py input_msg_fulldisk_blackwhite_cronjob.py
echo "    python" $PYTROLLHOME/scripts/loop_msg.py input_msg_fulldisk_blackwhite_cronjob2.py  
python $PYTROLLHOME/scripts/loop_msg.py input_msg_fulldisk_blackwhite_cronjob2.py

echo ""
