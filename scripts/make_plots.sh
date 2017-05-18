#rgbs="HRoverview convection airmass day_microphysics night_microphysics fog ash"
#rgbs="WV_062-WV_073 WV_062-IR_108 IR_120-IR_108 IR_087-IR_108"
#rgbs="WV_062-IR_108"
#for rgb in $rgbs
#do
#    echo $rgb
#done

#areas="ccs4 EuropeCanary MSGHRVN mesanX mesanE baws eurotv eurotv4n eurol euron1 nsea ssea euro euro_north "
#areas="ccs4"

dir_=${PWD}
dir0=/data/COALITION2/PicturesSatellite/
dir3=/data/COALITION2/PicturesSatellite/2015-05-13/2015-05-13_convection
dir4=/data/COALITION2/PicturesSatellite/2014-07-23/2014-07-23_convection_RZC_ccs4

year=2015
y2=$(echo "$year-2000" | bc)
month=7
MM="$(printf "%02d" $month)"

export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python
#export python=/usr/bin/python

. /opt/users/$LOGNAME/PyTroll/setup/bashrc_offline

if [ -z "$rgbs" ]; then 
    if [ -n "$areas" ]; then 
	echo "*** ERROR, rgbs not set but areas", $areas
	echo "    rgbs need not set, in order to use areas"
        echo "    usage: python plot_msg.py input_MSG $year $month $d $h $m $rgb $area"
        echo ""
	exit
    fi
fi

#for area in $areas
#do
#    for rgb in $rgbs
#    do
	for (( d = 7; d <= 7; d++ ))
	do 
	    dd="$(printf "%02d" $d)"
	    date=$year-$MM-${dd}
	    dir1=$dir_/$date/
	    #mkdir $dir_/$year-$MM-${dd}/convection-RZC-ccs4
	    #mkdir $dir_/$year-$MM-${dd}/convection-RZC-THX-ccs4
	    for (( h = 6; h <= 7; h=h+1 ))
	    do 
		hh="$(printf "%02d" $h)"
 		for (( m = 0; m <= 55; m=m+5 ))
 		do
		    mm="$(printf "%02d" $m)"
                    echo "*** DATE: " $year $MM $dd $hh $mm # $rgb $area
		    #echo " "
 		    #${python} $dir_/plot_lightning.py $year $month $d $h $m 
		    #echo " "
 		    #${python} $dir_/plot_hrw.py $year $month $d $h $m 
		    #echo " " ${python} $dir_/plot_radar.py $year $month $d $h $m 
 		    #${python} $dir_/plot_radar.py $year $month $d $h $m 
		    echo ${python} $dir_/plot_msg.py input_MSG $year $month $d $h $m $rgb $area
 		    ${python} $dir_/plot_msg.py input_MSG $year $month $d $h $m $rgb $area
		    #echo ${python} $dir_/plot_coalition2.py input_coalition2 $year $month $d $h $m 
 		    #${python} $dir_/plot_coalition2.py input_coalition2 $year $month $d $h $m 
		    #echo " " ${python} $dir_/plot_trt.py $year $month $d $h $m 
 		    #${python} $dir_/plot_trt.py $year $month $d $h $m 
		    #echo " "python $dir_/plot_msg.py input_nwc $year $month $d $h $m 
 		    #${python} $dir_/plot_msg.py input_nwc $year $month $d $h $m 
		    #echo " "
		    #echo ${python} $dir_/plot_msg.py input_thun $year $month $d $h $m $rgb $area
 		    #${python} $dir_/plot_msg.py input_thun $year $month $d $h $m $rgb $area
		    dir1=$dir0/${year}-${MM}-${dd}
 		done
	    done
	done
#    done
#done