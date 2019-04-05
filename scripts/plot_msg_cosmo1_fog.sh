#!/bin/bash

echo ""
echo "$LOGNAME" $LOGNAME
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc no_virtual_environment
#export python=$CONDA_PATH/envs/PyTroll_$LOGNAME/bin/python
echo "which python"
which python
echo $PYTROLLHOME

cd $PYTROLLHOME/scripts # necessary to specify input file without path

echo ""
echo "************************************************************"
echo "    python" $PYTROLLHOME/scripts/loop_msg.py input_msg_cosmo1_fog_cronjob.py  
python $PYTROLLHOME/scripts/loop_msg.py input_msg_cosmo1_fog_cronjob.py

echo ""
echo "************************************************************"

echo ""
