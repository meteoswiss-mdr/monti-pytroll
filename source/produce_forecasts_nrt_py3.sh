#!/bin/bash

echo '***'
echo '*** start produce_forecast_nrt.sh'
date

case $HOSTNAME in
    "zueub"[2-4][0-9][0-9])
	. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc3 no_virtual_environment
	;;
    "zuerh"[2-4][0-9][0-9])
	. /opt/users/$LOGNAME/monti-pytroll/setup/start_py_virtual_env.sh
	;;
esac

#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

cd $PYTROLLHOME/scripts
python $PYTROLLHOME/source/produce_forecasts_nrt_py3.py input_coalition2_cronjob
#$python $PYTROLLHOME/scripts/produce_forecasts_nrt.py > /tmp/produce_forecasts_nrt.txt 2>&1

# remove uncompressed data older than 10min
export mm=60
echo "*** Remove forecast data files older than "${mm}"min"
#find /tmp/?-000-MSG?__-MSG?_???____-*_-*___-*-__ -type f -mmin +${mm} -exec rm {} \;
find /data/cinesat/out/????????_????_??????_t??.p                  -type f -mmin +${mm} -delete \;
find /data/cinesat/out/C2-BT-forecasts/????????_????_??????_t??.p  -type f -mmin +${mm} -delete \;
