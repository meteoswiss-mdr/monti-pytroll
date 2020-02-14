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

python postprocessing.py --scp --parea EuropeCanaryS95  -c ["h03b-ir108","h03b-HRV","h03b-VIS006ir108"] input_hsaf_cronjob.py
python postprocessing.py --scp --parea odysseyS25       -c ["h03b-ir108","h03b-HRV","h03b-VIS006ir108","RATE-ir108","RATE-HRV","RATE-VIS006ir108"] input_hsaf_cronjob.py
python postprocessing.py --scp --parea odysseyS25       -c '' -m [["MSG_RATE-ir108","MSG_h03b-ir108"],["MSG_RATE-HRV","MSG_h03b-HRV"],["MSG_RATE-VIS006ir108","MSG_h03b-VIS006ir108"]] input_hsaf_cronjob.py

echo ""
