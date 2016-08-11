#### 
### ### #!/bin/bash

# go to operational pytroll folder  
#export PYTHONPATH=/opt/users/common/packages/anaconda2/bin:/opt/users/hau/PyTroll//scripts
#export XRIT_DECOMPRESS_PATH=/opt/users/common/bin/xRITDecompress
#export PPP_CONFIG_DIR=/opt/users/hau/PyTroll//etc/
echo '***'
echo '*** start produce_forecast_nrt.sh'
. /opt/users/hau/PyTroll/setup/bashrc
#export python=/usr/bin/python
export python=/opt/users/common/packages/anaconda3/envs/PyTroll_hau/bin/python

export dir1=/opt/users/hau/PyTroll/scripts
cd ${dir1}

$python ${dir1}/produce_forecasts_nrt.py
#$python ${dir1}/produce_forecasts_nrt.py > /tmp/produce_forecasts_nrt.txt 2>&1

# remove uncompressed data older than 10min
echo "*** Remove forecast data files older than 45min"
#find /tmp/?-000-MSG?__-MSG?_???____-*_-*___-*-__ -type f -mmin +15 -exec rm {} \;
find /data/cinesat/out/????????_????_??????_t??.p -type f -mmin +45 -delete \;
