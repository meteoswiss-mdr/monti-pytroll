#!/bin/bash

echo '***'
echo '*** start plot_lightning.sh'
. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc3 no_virtual_environment
#. /opt/users/$LOGNAME/PyTroll/setup/bashrc3 no_virtual_environment
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python

cd $PYTROLLHOME/source

echo "*** Start to produce Low-stratus-confidence-level images+netCDF"
## execute plot_lightning pytroll script 
python  nwcsaf_crontab.py CRR    > /tmp/demo_satpy_nwcsaf_py3_crontab_CRR.txt     2>&1  &
python  nwcsaf_crontab.py CRRPh  > /tmp/demo_satpy_nwcsaf_py3_crontab_CRR-Ph.txt  2>&1  &
python  nwcsaf_crontab.py CT     > /tmp/demo_satpy_nwcsaf_py3_crontab_CT.txt      2>&1  & 

# try to create composites and montage pictures with NWCSAF CRR and CRRPh 
python postprocessing_py3.py --parea ccs4 -c ["CRR-HRVir108","CRPh-HRVir108"] -m [["MSG_radar-HRVir108","MSG_CRR-HRVir108","MSG_CRPh-HRVir108"]] input_satlive_ccs4_EuropeCenter.py 

# update COALITION-2 composite
python postprocessing_py3.py --parea ccs4 -c ["C2rgb-IR_108"] -m [["MSG_C2rgb-IR-108","MSG_CT","MSG_HRoverview","MSG_TRT-radar-convection","MSG_radar-convection","MSG_THX-HRVir108"]] --delay 19 input_coalition2_cronjob
python postprocessing_py3.py --parea ccs4 -c ["C2rgb-IR_108"] -m [["MSG_C2rgb-IR-108","MSG_CT","MSG_HRoverview","MSG_TRT-radar-convection","MSG_radar-convection","MSG_THX-HRVir108"]] --delay 24 input_coalition2_cronjob
python postprocessing_py3.py --parea ccs4 -c ["C2rgb-IR_108"] -m [["MSG_C2rgb-IR-108","MSG_CT","MSG_HRoverview","MSG_TRT-radar-convection","MSG_radar-convection","MSG_THX-HRVir108"]] --delay 34 input_coalition2_cronjob

python postprocessing_py3.py --parea ccs4 -c ["C2rgb-HRVir108"] -m [["MSG_C2rgb-HRVir108","MSG_CT","MSG_DayLSConvectionNightMicrophysics","MSG_TRT-radar-HRVir108","MSG_radar-HRVir108","MSG_THX-HRVir108"]] --delay 19 input_coalition2_cronjob
python postprocessing_py3.py --parea ccs4 -c ["C2rgb-HRVir108"] -m [["MSG_C2rgb-HRVir108","MSG_CT","MSG_DayLSConvectionNightMicrophysics","MSG_TRT-radar-HRVir108","MSG_radar-HRVir108","MSG_THX-HRVir108"]] --delay 24 input_coalition2_cronjob
python postprocessing_py3.py --parea ccs4 -c ["C2rgb-HRVir108"] -m [["MSG_C2rgb-HRVir108","MSG_CT","MSG_DayLSConvectionNightMicrophysics","MSG_TRT-radar-HRVir108","MSG_radar-HRVir108","MSG_THX-HRVir108"]] --delay 34 input_coalition2_cronjob

## remove result files older than 1 hour (done in plot_ms.sh)
echo "*** Remove all result files older than 1 hour"
find /data/cinesat/out/* -user hau -type f -mmin +60 -exec rm {} \;
find /tmp/demo_satpy*    -user hau -type f -mmin +60 -exec rm {} \;
