#!/bin/bash

rgbs="[VIS006 VIS008 IR_016 IR_039 WV_062 WV_073 IR_087 IR_097 IR_108 IR_120 IR_134 HRV]"

#areas="ccs4 EuropeCanary MSGHRVN mesanX mesanE baws eurotv eurotv4n eurol euron1 nsea ssea euro euro_north "
#areas="ccs4"

echo ""

echo "*** create dates"
if [ 1 -eq 1 ]; then
    # check old dates from archive (offline modus)
    date_start="2015-07-07 00:00"
    date_start_s=$(/bin/date --date "$date_start" +"%s")
    date_end="2015-07-07 23:55"
    date_end_s=$(/bin/date --date "$date_end" +"%s")
    . /opt/users/cinesat/monti-pytroll/setup/bashrc_offline no_virtual_environment
    # check satellite in the input file (MSG2 or MSG3) depending on start/end time in line 105/106 and 109/110 
else
    # check near real time dates for the last "check_time" seconds (nrt modus)
    date_end=$(/bin/date  +$"%Y-%m-%d %H:%M")  # now (current date)
    date_end_s=$(/bin/date --date "$date_end" +"%s") 
    #check_time=$(expr 6 \* 60 \* 60 \-50 )          # check for the last 6 hours 
    check_time=21550         # check for the last 6 hours 
    #date_start_s=$(echo "$date_end_s - $check_time" | bc)
    date_start_s=$(expr $date_end_s - $check_time )
    date_start=$(/bin/date -d @$date_start_s +"%Y-%m-%d %H:%M")
    . /opt/users/cinesat/monti-pytroll/setup/bashrc_offline no_virtual_environment
    # check satellite in the input file (MSG2 or MSG3) depending on start/end time in line 105/106 and 109/110 
fi
#export python=/usr/bin/python
#export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python


# round start date to 5 min (begin of MSG RSS scans)
date_start_s=$(awk "BEGIN {printf \"%i\n\", $date_start_s - ($date_start_s % 300 ) }") # round by 5 min = 300 s
date_start=$(date -d @$date_start_s +"%Y-%m-%d %H:%M")
#echo $date_start_s
#echo $date_end_s

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
#i_max=$(echo " ($date_end_s - $date_start_s) / 300 + 1 " | bc) # 5 min = 300 s
i_max=$(awk "BEGIN {printf \"%i\n\", ($date_end_s - $date_start_s) / 300 + 1 }") # round by 5 min = 300 s

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
    if [ $# -eq 0 ]; then
	rad_dir=/data/COALITION2/database/meteosat/ccs4/$year/$month/$day/
	radfile_wildcard=MSG?_ccs4_$year$month$day$hour${minute}_rad.nc
	radfile=$(find $rad_dir -name $radfile_wildcard -print)
    elif [[ "$1" = "PLAX" ]]; then
	rad_dir=/data/COALITION2/database/meteosat/ccs4_PLAX/$year/$month/$day/
	radfile_wildcard=MSG?_ccs4_$year$month$day$hour${minute}_rad_PLAX.nc
	radfile=$(find $rad_dir -name $radfile_wildcard -print)
    else
	echo "unknown command line arguemnt" $1
    fi	
    
    if test -n "$radfile" 
    then
	echo "*** MSG SEVIRI radiance file exits for date: " $year $month $day $hour $minute # $rgb $area
	echo "    " $radfile
	file_size_kb=`du -k $radfile | cut -f1`
	echo "    filesize" $file_size_kb
	if [ $file_size_kb -lt 1250 ]; then 
	    echo "*** filesize "$radfile" too small"
	    calculate_radfile=1
	fi
    else
	echo "*** no MSG SEVIRI radiance file exists for date: " $year $month $day $hour $minute # $rgb $area
	calculate_radfile=1
    fi
    
    if [ $calculate_radfile -eq 1 ]; then 
	echo '    calculate MSG SEVIRI radiance file'
	cd $PYTROLLHOME/scripts # necessary to specify input file without path
	if [ $# -eq 0 ]; then
	    echo "    "python $PYTROLLHOME/scripts/plot_msg.py input_rad_ncfiles.py $year $month $day $hour $minute 
 	    #python $PYTROLLHOME/scripts/plot_msg.py input_rad_ncfiles.py $year $month $day $hour $minute
 	    python $PYTROLLHOME/scripts/plot_msg.py input_rad_ncfiles_MSG2.py $year $month $day $hour $minute
	elif [[ "$1" = "PLAX" ]]; then
	    echo "    "python $PYTROLLHOME/scripts/plot_msg.py input_rad_ncfiles_PLAX.py $year $month $day $hour $minute 
 	    python $PYTROLLHOME/scripts/plot_msg.py input_rad_ncfiles_PLAX.py $year $month $day $hour $minute
 	    python $PYTROLLHOME/scripts/plot_msg.py input_rad_ncfiles_PLAX_MSG2.py $year $month $day $hour $minute
	else
	    echo "unknown command line arguemnt" $1
	fi		    
    fi

    # clean temporary files
    find /tmp/SEVIRI_DECOMPRESSED/H-000-MSG* -type f -mmin +5 -delete 2>&1
    
    # add 5min (dtime) to current date 
    currentdate_s=$(/bin/date --date "$currentdate $dtime" +"%s") 

    # i=$(echo $i+1 | /usr/bin/bc)
    i=$(expr $i + 1 )
    if [ $i -gt $i_max ]; then break; fi
done

echo ""
