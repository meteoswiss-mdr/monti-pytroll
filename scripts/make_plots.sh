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
month=6
MM="$(printf "%02d" $month)"

export PYTHONPATH=/home/cinesat/python/lib/python2.7/site-packages:$dir_
#export PPP_CONFIG_DIR=$dir_
export PPP_CONFIG_DIR=/data/OWARNA/hau/pytroll/cfg_offline
#export PPP_CONFIG_DIR /data/OWARNA/hau/pytroll/cfg_nrt
export XRIT_DECOMPRESS_PATH=/data/OWARNA/hau/pytroll/bin/xRITDecompress

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
	for (( d = 6; d <= 7; d++ ))
	do 
	    dd="$(printf "%02d" $d)"
	    date=$year-$MM-${dd}
	    dir1=$dir_/$date/
	    #mkdir $dir_/$year-$MM-${dd}/convection-RZC-ccs4
	    #mkdir $dir_/$year-$MM-${dd}/convection-RZC-THX-ccs4
	    for (( h = 0; h <= 23; h=h+1 ))
	    do 
		hh="$(printf "%02d" $h)"
 		for (( m = 0; m <= 55; m=m+5 ))
 		do
		    mm="$(printf "%02d" $m)"
                    echo "*** DATE: " $year $MM $dd $hh $mm # $rgb $area
		    #echo " "
 		    #/usr/bin/python $dir_/plot_lightning.py $year $month $d $h $m 
		    #echo " "
 		    #/usr/bin/python $dir_/plot_hrw.py $year $month $d $h $m 
		    #echo " " /usr/bin/python $dir_/plot_radar.py $year $month $d $h $m 
 		    #/usr/bin/python $dir_/plot_radar.py $year $month $d $h $m 
		    #echo " " /usr/bin/python $dir_/plot_trt.py $year $month $d $h $m 
 		    #/usr/bin/python $dir_/plot_trt.py $year $month $d $h $m 
		    #echo " "python $dir_/plot_msg.py input_nwc $year $month $d $h $m 
 		    #/usr/bin/python $dir_/plot_msg.py input_nwc $year $month $d $h $m 
		    #echo " "
		    echo /usr/bin/python $dir_/plot_msg.py input_thun $year $month $d $h $m $rgb $area
 		    /usr/bin/python $dir_/plot_msg.py input_thun $year $month $d $h $m $rgb $area

		    dir1=$dir0/${year}-${MM}-${dd}

		    #echo "composite RZC + convection -> convection_RZC"
		    #/usr/bin/composite $dir1/${date}_precip-ccs4/RAD_RZC-ccs4_$y2$MM$dd$hh$mm.png $dir1/${date}_convection-ccs4/MSG_convection-ccs4_$y2$MM$dd$hh$mm.png  $dir1/${date}_convection-RZC-ccs4/MSG_convection-RZC-ccs4_$y2$MM$dd$hh$mm.png

		    #echo "composite TRT + convection/RZC -> convection_RZC_TRT"
                    #/usr/bin/composite $dir1/${date}_TRT_ccs4/RAD_TRT-ccs4_$y2$MM$dd$hh${mm}.png $dir1/${date}_convection-RZC_ccs4/MSG_convection_RZC-ccs4_$y2$MM$dd$hh$mm.png $dir1/${date}_convection-RZC-TRT-ccs4/MSG_convection-RZC-TRT-ccs4_$y2$MM$dd$hh$mm.png  
		    #echo /usr/bin/composite $dir1/${date}_TRT_ccs4/RAD_TRT-ccs4_$y2$MM$dd$hh${mm}.png $dir1/${date}_convection-RZC_ccs4/MSG_convection_RZC-ccs4_$y2$MM$dd$hh$mm.png $dir1/${date}_convection-RZC-TRT-ccs4/MSG_convection-RZC-TRT-ccs4_$y2$MM$dd$hh$mm.png  

		    #echo "composite THX + convection/RZC -> convection_RZC_THX"
                    #/usr/bin/composite $dir1/${date}_dens-ccs4/THX_dens-ccs4_$y2$MM$dd$hh${mm}_0005min_005km.png $dir1/${date}_convection-RZC-ccs4/MSG_convection-RZC-ccs4_$y2$MM$dd$hh$mm.png $dir1/${date}_convection-RZC-THX-ccs4/MSG_convection-RZC-THX-ccs4_$y2$MM$dd$hh$mm.png
		    #echo /usr/bin/composite $dir1/${date}_dens-ccs4/THX_dens-ccs4_$y2$MM$dd$hh${mm}_0005min_005km.png $dir1/${date}_convection-RZC-ccs4/MSG_convection-RZC-ccs4_$y2$MM$dd$hh$mm.png $dir1/${date}_convection-RZC-THX-ccs4/MSG_convection-RZC-THX-ccs4_$y2$MM$dd$hh$mm.png

		    # echo "composite RZC + convection -> convection_RZC"
		    #/usr/bin/composite $dir_/$year-$MM-${dd}/radar/RAD_RZC-ccs4_$y2$MM$dd$hh$mm.png $dir_/$year-$MM-${dd}/convection-ccs4/MSG_convection-ccs4_$y2$MM$dd$hh$mm.png  $dir_/$year-$MM-${dd}/convection-RZC-ccs4/MSG_convection-RZC-ccs4_$y2$MM$dd$hh$mm.png

		    #echo "composite RZC + convection -> convection_RZC"
		    #/usr/bin/composite $dir_/$year-$MM-${dd}/radar/RAD_RZC-ccs4_$y2$MM$dd$hh$mm.png $dir2/2014-07-23_convection_ccs4/MSG-2_$year-$MM-${dd}_$hh-${mm}__ccs4_convection.png  $dir_/$year-$MM-${dd}/convection-RZC-ccs4/MSG_convection-RZC-ccs4_$y2$MM$dd$hh$mm.png

                    # echo "composite TRT + convection -> convection_RZC"
		    #echo $dir_/$year-$MM-${dd}/convection-TRT-ccs4/MSG_convection-TRT-ccs4_$y2$MM$dd$hh$mm.png
                    #/usr/bin/composite  $dir_/$year-$MM-${dd}/TRT/TRT_cells-ccs4_$y2$MM$dd$hh${mm}.png  $dir2/2014-07-23_convection_ccs4/MSG-2_$year-$MM-${dd}_$hh-${mm}__ccs4_convection.png  $dir_/$year-$MM-${dd}/convection-TRT-ccs4/MSG_convection-TRT-ccs4_$y2$MM$dd$hh$mm.png

		    #echo "composite THX + convection/RZC -> convection_RZC_THX"
                    #/usr/bin/composite $dir_/$year-$MM-${dd}/THX/THX_dens-ccs4_$y2$MM$dd$hh${mm}_0005min_005km.png $dir_/$year-$MM-${dd}/convection-RZC-ccs4/MSG_convection-RZC-ccs4_$y2$MM$dd$hh$mm.png $dir_/$year-$MM-${dd}/convection-RZC-THX-ccs4/MSG_convection-RZC-THX-ccs4_$y2$MM$dd$hh$mm.png

		    #echo $dir_/$year-$MM-${dd}/convection-RZC-TRT-ccs4/MSG_convection-RZC-TRT-ccs4_$y2$MM$dd$hh${mm}_13000006.png
		    #/usr/bin/composite $dir_/$year-$MM-${dd}/TRT/ID13000006/TRT_cells-ccs4_$y2$MM$dd$hh${mm}_13000006.png $dir2/$year-$MM-${dd}_convection_RZC_ccs4/MSG_convection_RZC-ccs4_$y2$MM$dd$hh$mm.png $dir_/$year-$MM-${dd}/convection-RZC-TRT-ccs4/MSG_convection-RZC-TRT-ccs4_$y2$MM$dd$hh${mm}_13000006.png

		    #echo $dir_/$year-$MM-${dd}/convection-TRT-ccs4/MSG_convection-TRT-ccs4_$y2$MM$dd$hh${mm}_13000006.png
		    #/usr/bin/composite $dir_/$year-$MM-${dd}/TRT/ID13000006/TRT_cells-ccs4_$y2$MM$dd$hh${mm}_13000006.png $dir2/$year-$MM-${dd}_convection/MSG-2_$year-$MM-${dd}_$hh-${mm}__ccs4_convection.png $dir_/$year-$MM-${dd}/convection-TRT-ccs4/MSG_convection-TRT-ccs4_$y2$MM$dd$hh${mm}_13000006.png

		    #echo $dir_/$year-$MM-${dd}/HRoverview-TRT-ccs4/MSG_HRoverview-TRT-ccs4_$y2$MM$dd$hh${mm}_13000006.png
		    #/usr/bin/composite $dir_/$year-$MM-${dd}/TRT/ID13000006/TRT_cells-ccs4_$y2$MM$dd$hh${mm}_13000006.png $dir2/$year-$MM-${dd}_HRoverview/MSG-2_$year-$MM-${dd}_$hh-${mm}__ccs4_HRoverview.png $dir_/$year-$MM-${dd}/HRoverview-TRT-ccs4/MSG_HRoverview-TRT-ccs4_$y2$MM$dd$hh${mm}_13000006.png

                    #echo "composite convection/RZC + TRT -> convection_RZC_THX_TRT"
                    #/usr/bin/composite $dir_/$year-$MM-${dd}/TRT/TRT_cells-ccs4_$y2$MM$dd$hh${mm}.png $dir2/$year-$MM-${dd}_convection_RZC_ccs4/MSG_convection-RZC-ccs4_$y2$MM$dd$hh$mm.png $dir_/$year-$MM-${dd}/convection-RZC-TRT-ccs4/MSG_convection-RZC-TRT-ccs4_$y2$MM$dd$hh$mm.png

                    #echo "composite convection/RZC + TRT -> convection_RZC_THX_TRT"
                    #/usr/bin/composite $dir_/$year-$MM-${dd}/TRT/TRT_cells-ccs4_$y2$MM$dd$hh${mm}.png $dir2/$year-$MM-${dd}_convection_RZC_ccs4/MSG_convection_RZC-ccs4_$y2$MM$dd$hh$mm.png $dir_/$year-$MM-${dd}/convection-RZC-TRT-ccs4/MSG_convection-RZC-TRT-ccs4_$y2$MM$dd$hh$mm.png

		    #echo $dir_/$year-$MM-${dd}/convection-RZC-THX-TRT-ccs4/MSG_convection-RZC-THX-TRT-ccs4_$y2$MM$dd$hh$mm.png
                    #/usr/bin/composite $dir_/$year-$MM-${dd}/TRT/ID13000006/TRT_cells-ccs4_$y2$MM$dd$hh${mm}_13000006.png  $dir2/$year-$MM-${dd}_convection_RZC_light_ccs4/MSG_convection_RZC_light-ccs4_$y2$MM$dd$hh$mm.png  $dir_/$year-$MM-${dd}/convection-RZC-THX-TRT-ccs4/MSG_convection-RZC-THX-TRT-ccs4_$y2$MM$dd$hh$mm.png

 		done
	    done
	done
#    done
#done