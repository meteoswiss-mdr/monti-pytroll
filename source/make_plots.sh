#!/bin/bash


currentdate=2023-03-24
loopenddate=$(/bin/date --date "2023-03-24 1 day" +%Y-%m-%d)


dir_=${PWD}
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python
#export python=/opt/users/common/packages/anaconda3_hau/envs/PyTroll_hau/bin/python
##### export python=/opt/users/common/packages/anaconda2_hau//envs/PyTroll_hau//bin/python
#export python=/store/msrad/utils/anaconda3/envs/PyTroll_hamann/bin/python
##export python=/usr/bin/python

. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc3 no_virtual_environment
export python=/opt/users/common/packages/anaconda3_hau/envs/PyTroll_hau/bin/python
cd /opt/users/hau/monti-pytroll/source

# MeteoSwiss
#. /opt/users/$LOGNAME/PyTroll/setup/bashrc_offline
#. /opt/users/$LOGNAME/monti-pytroll/setup/bashrc3_offline
# CSCS
#. /users/$LOGNAME/monti-pytroll/setup/bashrc_offline
 
#rgbs="HRoverview convection airmass day_microphysics night_microphysics fog ash"
#rgbs="WV_062-WV_073 WV_062-IR_108 IR_120-IR_108 IR_087-IR_108"
#rgbs="WV_062-IR_108"
#for rgb in $rgbs
#do
#    echo $rgb
#done

#areas="ccs4 EuropeCanary MSGHRVN mesanX mesanE baws eurotv eurotv4n eurol euron1 nsea ssea euro euro_north "
#areas="ccs4"

#if [ -z "$rgbs" ]; then 
#    if [ -n "$areas" ]; then 
#	echo "*** ERROR, rgbs not set but areas", $areas
#	echo "    rgbs need not set, in order to use areas"
#        echo "    usage: python plot_msg.py input_MSG $year $month $d $h $m $rgb $area"
#        echo ""
#	exit
#    fi
#fi



until [ "$currentdate" == "$loopenddate" ]
do
    ##echo $currentdate
    year=$(/bin/date --date "$currentdate " +%Y)
    month=$(/bin/date --date "$currentdate " +%m)
    d=$(/bin/date --date "$currentdate " +%d)

    echo $year $month $day

    for (( h = 0; h <= 14; h=h+1 ))
    do 
	hh="$(printf "%02d" $h)"
 	for (( m = 0; m <= 45; m=m+15 ))
 	do
	    mm="$(printf "%02d" $m)"
            echo "*** DATE: year" $year "month" $month "day" $d "hour" $hh "min" $m # $rgb $area
	    #echo " "
 	    #${python} $dir_/plot_lightning.py $year $month $d $h $m 
	    #echo " "
 	    #${python} $dir_/plot_hrw.py $year $month $d $h $m 
	    #echo " " ${python} $dir_/plot_radar.py $year $month $d $h $m 
 	    #${python} $dir_/plot_radar.py $year $month $d $h $m 
	    #echo ${python} $dir_/plot_msg.cscs.py input_MSG $year $month $d $h $mm $rgb $area
 	    #${python} $dir_/plot_msg.cscs.py input_MSG $year $month $d $h $mm $rgb $area
	    #echo ${python} $dir_/plot_coalition2.py input_coalition2 $year $month $d $h $m 
 	    #${python} $dir_/plot_coalition2.py input_coalition2 $year $month $d $h $m 
	    #echo " " ${python} $dir_/plot_trt.py $year $month $d $h $m 
 	    #${python} $dir_/plot_trt.py $year $month $d $h $m 
	    #echo " "python $dir_/plot_msg.py input_nwc $year $month $d $h $m 
 	    #${python} $dir_/plot_msg.py input_nwc $year $month $d $h $m 
	    #echo " "python $dir_/demo_satpy_nwcsaf.py $year $month $d $h $m 
 	    #${python} $dir_/demo_satpy_nwcsaf.py $year $month $d $h $m 
	    echo " "python $dir_/fog_crontab.py $year $month $d $h $m 
 	    ${python} $dir_/fog_crontab.py $year $month $d $h $m
	    #echo " "python $dir_/satlive_geo.py input_satlive_ccs4_EuropeCenter.py --date $year $month $d $h $m
	    #${python} $dir_/satlive_geo.py input_satlive_ccs4_EuropeCenter.py --date $year $month $d $h $m
	    #echo " "
	    ###echo ${python} $dir_/plot_msg.py input_MSG $year $month $d $h $m $rgb $area
 	    ###${python} $dir_/plot_msg.py input_MSG $year $month $d $h $m $rgb $area
	    ## clean up temporary files 
	    #rm /scratch/hamann/?-000-MSG?__-MSG?___*
	    #rm /tmp/SEVIRI_DECOMPRESSED/*202011*
	    #find /tmp/SEVIRI_DECOMPRESSED/H-000-MSG* -type f -mmin +3 -delete
	    #find /tmp/H-000-MSG* -type f -mmin +3 -delete	    
 	done
    done
    
    # add one day to current date
    currentdate=$(/bin/date --date "$currentdate 1 day" +%Y-%m-%d)
    
done
