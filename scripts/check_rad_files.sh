
rgbs="[VIS006 VIS008 IR_016 IR_039 WV_062 WV_073 IR_087 IR_097 IR_108 IR_120 IR_134 HRV]"

#areas="ccs4 EuropeCanary MSGHRVN mesanX mesanE baws eurotv eurotv4n eurol euron1 nsea ssea euro euro_north "
#areas="ccs4"

echo ""
dir1=/data/OWARNA/hau/pytroll/test
export PYTHONPATH=/home/cinesat/python/lib/python2.7/site-packages:$dir1
export PPP_CONFIG_DIR=/data/OWARNA/hau/pytroll/cfg_offline
export XRIT_DECOMPRESS_PATH=/data/OWARNA/hau/pytroll/bin/xRITDecompress
echo 'PPP_CONFIG_DIR' $PPP_CONFIG_DIR

if [ 1 -eq 1 ]; then
    date_start="2010-06-01 00:00"
    date_end="2010-10-01 00:00"
else
    check_time=$(echo 6*60*60 | bc) # 6 hours 
    date_end=$(/bin/date  +$"%Y-%m-%d %H:%M")
    date_end_s=$(/bin/date --date "$date_end" +"%s")
    date_start_s=$(echo "$date_end_s - $check_time" | bc)
    date_start=$(/bin/date -d @$date_start_s +"%Y-%m-%d %H:%M")
fi 

date_start_s=$(/bin/date --date "$date_start" +"%s")
date_start_s=$(echo "$date_start_s - ($date_start_s % 300)" | bc) # round by 5 min = 300 s
date_start=$(date -d @$date_start_s +"%Y-%m-%d %H:%M")
date_end_s=$(/bin/date --date "$date_end" +"%s")

echo "*** create MSG SEVIRI radiance files from " $date_start " until " $date_end 

if [ -z "$rgbs" ]; then 
    if [ -n "$areas" ]; then 
	echo "*** ERROR, rgbs not set but areas", $areas
	echo "    rgbs need not set, in order to use areas"
        echo "    usage: python plot_msg.py input_MSG $year $month $d $h $m $rgb $area"
        echo ""
	exit
    fi
fi

# check every 5 min == RSS scan time
dtime="5 min"
i=0
i_max=$(echo " ($date_end_s - $date_start_s) / 300 + 1 " | bc) # 5 min = 300 s

currentdate_s=$date_start_s

until [ $currentdate_s -gt $date_end_s ]
do

    currentdate=$(date -d @$currentdate_s +"%Y-%m-%d %H:%M")

    year=$(/bin/date --date "$currentdate " +$"%Y") # year
    month=$(/bin/date --date "$currentdate " +$"%m") # month 
    day=$(/bin/date --date "$currentdate " +$"%d") # day
    hour=$(/bin/date --date "$currentdate " +$"%H") # hour
    minute=$(/bin/date --date "$currentdate " +$"%M") # min 

    echo " "
    calculate_radfile=0
    rad_dir=/data/COALITION2/database/meteosat/ccs4/$year/$month/$day/
    radfile_wildcard=MSG?_ccs4_$year$month$day$hour${minute}_rad.nc
    radfile=$(find $rad_dir -name $radfile_wildcard -print)
    
    if test -n "$radfile" 
    then
	echo "*** MSG SEVIRI radiance file exits for date: " $year $month $day $hour $minute # $rgb $area
	echo "    " $radfile
	file_size_kb=`du -k $radfile | cut -f1`
	echo "    filesize" $file_size_kb
	if [ $file_size_kb -lt 1250 ]; then 
	    echo "*** filesize too small"
	    calculate_radfile=1
	fi
    else
	echo "*** no MSG SEVIRI radiance file exists for date: " $year $month $day $hour $minute # $rgb $area
	calculate_radfile=1
    fi
    
    if [ $calculate_radfile -eq 1 ]; then 
	echo '    calculate MSG SEVIRI radiance file'
	echo "    /usr/bin/python" $dir1/plot_msg.py input_rad_ncfiles.py $year $month $day $hour $minute 
 	/usr/bin/python $dir1/plot_msg.py input_rad_ncfiles.py $year $month $day $hour $minute 
    fi

    # add 5min (dtime) to current date 
    currentdate_s=$(/bin/date --date "$currentdate $dtime" +"%s") 

    i=$(echo $i+1 | /usr/bin/bc)
    if [ $i -gt $i_max ]; then break; fi
done

echo ""
