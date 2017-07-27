#### #!/bin/bash

echo '***'
echo '*** start produce_forecast_nrt.sh'
. /opt/users/$LOGNAME/PyTroll/setup/bashrc
#export python=/usr/bin/python
export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

export dir1=/opt/users/$LOGNAME/PyTroll/scripts
cd ${dir1}

$python ${dir1}/produce_forecasts_nrt.py
#$python ${dir1}/produce_forecasts_nrt.py > /tmp/produce_forecasts_nrt.txt 2>&1

# remove uncompressed data older than 10min
export mm=60
echo "*** Remove forecast data files older than "${mm}"min"
#find /tmp/?-000-MSG?__-MSG?_???____-*_-*___-*-__ -type f -mmin +${mm} -exec rm {} \;
find /data/cinesat/out/????????_????_??????_t??.p -type f -mmin +${mm} -delete \;
