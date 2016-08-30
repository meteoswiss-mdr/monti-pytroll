#!/usr/bin/python

# small programm to loop the plot_msg function 
# until all desired RGB images are processed

from time import time, sleep
import os.path
from os import remove

if __name__ == '__main__':

    from get_input_msg import get_input_msg
    from plot_msg import plot_msg, print_usage
    #from postprocessing import postprocessing, print_usage
    import sys

    print len(sys.argv), "arguments given"

    if len(sys.argv) < 2:
        print_usage()
    else:
        # read input file 
        input_file=sys.argv[1]
        if input_file[-3:] == '.py': 
            input_file=input_file[:-3]
        in_msg = get_input_msg(input_file)

        # check for more arguments 
        if len(sys.argv) > 2:
            if len(sys.argv) < 7:
                print_usage()
            else:
                year   = int(sys.argv[2])
                month  = int(sys.argv[3])
                day    = int(sys.argv[4])
                hour   = int(sys.argv[5])
                minute = int(sys.argv[6])
            # update time slot in in_msg class
            in_msg.update_datetime(year, month, day, hour, minute)
            print "... specified date: ", str(in_msg.datetime)
            if len(sys.argv) > 7:
                if type(sys.argv[7]) is str:
                    in_msg.RGBs = [sys.argv[7]]
                else:
                    in_msg.RGBs = sys.argv[7]
            if len(sys.argv) > 8:
                if type(sys.argv[8]) is str:
                    in_msg.area = [sys.argv[8]]
                else:
                    in_msg.area = sys.argv[8]
        else:
            # chose last SEVIRI date
            in_msg.get_last_SEVIRI_date()

    delta_time =  10             # time in seconds to wait between the tries
    total_time = 600             # maximum total time in seconds trying to get images
#    delta_time =  1             # time in seconds to wait between the tries
#    total_time = 6             # maximum total time in seconds trying to get images

    end_time = time()+total_time   # total time add time to try in seconds
    event_time=time()
    i=1
    print " "

    ## in case that the last time no RSS was available, do a non-RSS image at once
    #if os.path.isfile("/tmp/NO_RSS_INPUT.txt") and in_msg.RSS == True:
    #    print "... RSS failure check: We know that no RSS was available last time -> make a MSG-3 image before normal processing..."
    #    sat_nr_org=in_msg.sat_nr
    #    datetime_org=in_msg.datetime
    #    in_msg.RSS    = False
    #    in_msg.sat_nr = 10                 # use prime satellite
    #    in_msg.get_last_SEVIRI_date()      # get last full scan time
    #    RGBs_done__ = plot_msg(in_msg)     # try to produce MSG-3 image as replacement 
    #    in_msg.RSS      = True                 # reset original input
    #    in_msg.sat_nr   = sat_nr_org           # reset original input
    #    in_msg.datetime = datetime_org       # reset original input

    while event_time < end_time:
        print "... try to get SEVIRI images, try number ", i
        i=i+1
        # call of the plot function
        RGBs_done = plot_msg(in_msg)
        # remove the processed RGBs from the list of RGBs to do 
        for rgb in RGBs_done:
            in_msg.RGBs.remove(rgb)
            if os.path.isfile("/tmp/NO_RSS_INPUT.txt"):
                print "A) remove NO_RSS_INPUT.txt"
                remove("/tmp/NO_RSS_INPUT.txt")
        # exit loop, if no more images need to be processed 
        if len(in_msg.RGBs) == 0:
            break
        else:
            print "processing not complete, still need to process: ", in_msg.RGBs
        # sleep before next try
        sleep(delta_time)
        event_time=time()

    # last try without checking the completeness of the input
    if len(in_msg.RGBs) > 0:
        print "*** WARNING, SEGMENTS NOT COMPLETE, TRY TO MAKE IMAGES WITHOUT ALL SEGMENTS "
        in_msg.check_input = False  # but at least prolog, epilog and one segment are necessary
        RGBs_done = plot_msg(in_msg)
        for rgb in RGBs_done:
            in_msg.RGBs.remove(rgb)
            if os.path.isfile("/tmp/NO_RSS_INPUT.txt"):
                print "B) remove NO_RSS_INPUT.txt"
                remove("/tmp/NO_RSS_INPUT.txt")
        if len(in_msg.RGBs) > 0:
            print "*** SEVERE WARNING, MISSING CHANNELS "

        # if still images are missing and RSS is activated -> try to produce normal scan images
        if len(in_msg.RGBs) > 0 and in_msg.RSS == True:
            if not os.path.isfile("/tmp/NO_RSS_INPUT.txt"):
                print "*** TRY TO PRODUCE NORMAL SCAN IMAGES (INSTEAD OF RAPID SCAN)"
                in_msg.RSS = False                 # switch rapid scan off
                in_msg.sat_nr = 10                 # use prime satellite
                in_msg.get_last_SEVIRI_date()      # get last full scan time
                RGBs_done = plot_msg(in_msg)
            print "*** Create/Update file recording missing RSS data"
            f1 = open("/tmp/NO_RSS_INPUT.txt",'a')   # mode append 
            f1.write("... no RSS input: "+str(in_msg.datetime))
            f1.close()

    else:
        print '*** All images processed, tutto bene!'
        print '    Ciao, ciao!'
        print ' '

