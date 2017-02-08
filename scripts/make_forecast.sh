#!/bin/bash

dir_=${PWD}

year=2015
y2=$(echo "$year-2000" | bc)
month=7
MM="$(printf "%02d" $month)"

export python=/opt/users/common/packages/anaconda3/envs/PyTroll_$LOGNAME/bin/python
#export python=/usr/bin/python

. /opt/users/$LOGNAME/PyTroll/setup/bashrc_offline

for (( d = 7; d <= 7; d++ ))
do 
    dd="$(printf "%02d" $d)"
    for (( h = 0; h <= 23; h=h+1 ))
    do 
	hh="$(printf "%02d" $h)"
 	for (( m = 0; m <= 55; m=m+5 ))
 	do
	    mm="$(printf "%02d" $m)"
	    echo ""
            echo "*** DATE: " $year $MM $dd $hh $mm # $rgb $area
 	    ${python} $dir_/produce_forecasts_nrt.py $year $month $d $h $m 
 	done
    done
done
