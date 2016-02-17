#rgbs="HRoverview convection airmass day_microphysics night_microphysics fog ash"
#rgbs="WV_062-WV_073 WV_062-IR_108 IR_120-IR_108 IR_087-IR_108"
#rgbs="WV_062-IR_108"
#for rgb in $rgbs
#do
#    echo $rgb
#done

rgbs="[VIS006 VIS008 IR_016 IR_039 WV_062 WV_073 IR_087 IR_097 IR_108 IR_120 IR_134 HRV]"

#areas="ccs4 EuropeCanary MSGHRVN mesanX mesanE baws eurotv eurotv4n eurol euron1 nsea ssea euro euro_north "
#areas="ccs4"

dir_=/data/OWARNA/hau/pytroll/test2/
dir2=/data/COALITION2/PicturesSatellite/2015-05-13/
dir3=/data/COALITION2/PicturesSatellite/2015-05-13/2015-05-13_convection

year=2015
y2=$(echo "$year-2000" | bc)
month=07
MM="$(printf "%02d" $month)"

./set_python_paths.sh

if [ -z "$rgbs" ]; then 
    if [ -n "$areas" ]; then 
	echo "*** ERROR, rgbs not set but areas", $areas
	echo "    rgbs need not set, in order to use areas"
        echo "    usage: python plot_msg.py input_MSG $year $month $d $h $m $rgb $area"
        echo ""
	exit
    fi
fi


for (( d = 7; d <= 7; d++ ))
do 
    dd="$(printf "%02d" $d)"
    date=$year-$MM-${dd}
    dir1=$dir_/$date/
    #mkdir $dir_/$year-$MM-${dd}/convection-RZC-ccs4
    #mkdir $dir_/$year-$MM-${dd}/convection-RZC-THX-ccs4
    for (( h = 10; h <= 12; h++ ))
    do 
	hh="$(printf "%02d" $h)"
 	for (( m = 0; m <= 55; m=m+5 ))
 	do 	    
	    mm="$(printf "%02d" $m)"	
    
	    echo " "
	    calculate_radfile=0
	    rad_dir=/data/COALITION2/database/meteosat/ccs4/$year/$MM/$dd/
	    radfile_wildcard=MSG?_ccs4_$year$MM$dd$hh${mm}_rad.nc
	    radfile=$(find $rad_dir -name $radfile_wildcard -print)

	    if test -n "$radfile" 
	    then
		echo "*** rad file exits for date: " $year $MM $dd $hh $mm # $rgb $area
		echo "    " $radfile
		file_size_kb=`du -k $radfile | cut -f1`
		echo "    filesize" $file_size_kb
		if [ $file_size_kb -lt 1000 ]; then 
		    echo "*** filesize too small"
		    calculate_radfile=1
		fi
	    else
		echo "*** no rad file exists for date: " $year $MM $dd $hh $mm # $rgb $area
		calculate_radfile=1
	    fi

	    if [ $calculate_radfile -eq 1 ]; then 
		echo '    calculate rad file'
		echo "    /usr/bin/python" $dir_/plot_msg.py input_radfile.py $year $month $d $h $m 
 		/usr/bin/python $dir_/plot_msg.py input_radfile.py $year $month $d $h $m 
	    fi

 	done
    done
done
