
from my_msg_module import format_name
from os.path import isfile, join, exists, dirname
from os import makedirs
import subprocess

def get_THX_filename(in_msg, time_slot, area):
    print "    get_THX_filename THX"
    from ConfigParser import ConfigParser
    from mpop import CONFIG_PATH
    conf = ConfigParser()
    conf.read(join(CONFIG_PATH, "lightning.cfg"))
    dx = int(conf.get("thx-level2", "dx"))
    dt = int(conf.get("thx-level2", "dt"))
    dt_str = ("%04d" % dt) + "min"
    dx_str = ("%03d" % dx) + "km"
    #outputDir = format_name('./%Y-%m-%d/THX/',  time_slot, area=area)
    #outputDir = "/data/cinesat/out/"
    outputDir = format_name(in_msg.outputDir,  time_slot, area=area, rgb="THX")
    rgb='dens'
    filename =  format_name('THX_'+rgb+'-ccs4_%y%m%d%H%M_'+dt_str+'_'+dx_str+'.png', time_slot, area=area, rgb="THX")
    return outputDir+filename

def get_radar_filename(in_msg, time_slot, area):
    print "    get_radar_filename radar"
    #outputDir = format_name('./%Y-%m-%d/radar/',  time_slot, area=area)
    #outputDir = "/data/cinesat/out/"
    outputDir = format_name(in_msg.outputDir,  time_slot, area=area, rgb="radar")
    filename =  format_name('RAD_RZC-ccs4_%y%m%d%H%M.png', time_slot, area=area)
    return outputDir+filename

def get_odyssey_filename(in_msg, time_slot, area):
    print "    get_odyssey_filename radar"
    #outputDir = format_name('./%Y-%m-%d/radar/',  time_slot, area=area)
    #outputDir = "/data/cinesat/out/"
    outputDir = format_name(in_msg.outputDir,  time_slot, area=area, rgb="radar")
    filename =  format_name('ODY_RATE-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
    return outputDir+filename

def get_TRT_filename(in_msg, time_slot, area):
    print "    get_TRT_filename TRT" 
    #outputDir = format_name('./%Y-%m-%d/radar/',  time_slot, area=area)
    #outputDir = "/data/cinesat/out/"
    outputDir = format_name(in_msg.outputDir,  time_slot, area=area, rgb="TRT")
    filename =  format_name('RAD_TRT-ccs4_%y%m%d%H%M.png', time_slot, area=area)
    return outputDir+filename
    
def get_OT_filename(in_msg, rgb, time_slot, area):
    print "    get_OT_filename" 
    #outputDir = format_name('./%Y-%m-%d/radar/',  time_slot, area=area)
    #outputDir = "/data/cinesat/out/"
    outputDir = format_name(in_msg.outputDir,  time_slot, area=area, rgb=rgb, sat=sat, sat_nr=sat_nr)
    filename  = format_name(in_msg.outputFile, time_slot, area=area, rgb=rgb, sat=sat, sat_nr=sat_nr)
    return outputDir+filename

def get_sat_filename(in_msg, rgb, sat, sat_nr, time_slot, area):
    print "    get_sat_filename ", rgb
    #outputDir = "/data/cinesat/out/"
    outputDir = format_name(in_msg.outputDir,  time_slot, area=area, rgb=rgb, sat=sat, sat_nr=sat_nr)
    filename  = format_name(in_msg.outputFile, time_slot, area=area, rgb=rgb, sat=sat, sat_nr=sat_nr)
    return outputDir+filename

def get_comp_filename(in_msg, comp_str, sat_nr, time_slot, area):
    print "    get_comp_filename ", comp_str
    #outputDir = format_name('./%Y-%m-%d/'+prop_str+'-ccs4/', time_slot, area=area)
    #outputDir = "/data/cinesat/out/"
    outputDir = format_name(in_msg.outputDir,  time_slot, area=area, rgb=comp_str.replace("_","-"), sat_nr=sat_nr)
    if not exists(outputDir):
        if in_msg.verbose:
            print '... create output directory: ' + outputDir
        from os import makedirs
        makedirs(outputDir)
    filename  = format_name('/MSG_'+comp_str.replace("_","-")+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area, sat_nr=sat_nr) 
    return outputDir+'/'+filename

# ---
def get_file_list(composite, in_msg, sat, sat_nr, time_slot, area, n=None):

    import products 
    if n==None:
        rgb_list  = composite.split("-")
    else:
        rgb_list  = composite.split("-",n-1)
    file_list = []

    for rgb in rgb_list:
        if rgb == 'THX':
            file_list.append (get_THX_filename(in_msg, time_slot, area))
        elif rgb == 'TRT':
            file_list.append (get_TRT_filename(in_msg, time_slot, area))
        elif rgb in products.MSG_all:
            file_list.append (get_sat_filename(in_msg, rgb, 'MSG', sat_nr, time_slot, area))
        elif (rgb == 'radar' or rgb in products.Radar) and in_msg.sat != 'cpp':
            file_list.append (get_radar_filename(in_msg, time_slot, area))
        elif rgb == 'RATE':
            file_list.append (get_odyssey_filename(in_msg, time_slot, area))
        else:
            file_list.append (get_sat_filename(in_msg, rgb, sat, sat_nr, time_slot, area))

        if not isfile(file_list[-1]):
            print "*** ERROR, can not find "+rgb+" file: "+file_list[-1]
            print "    skip composite: "+composite
            return None 
    return file_list

# ---
def n_file_composite(composite, in_msg, sat_nr, time_slot, area, bits_per_pixel=8, composites_done=[]):

    n_rgb = composite.count('-') + 1

    # create smaller required composites 
    if n_rgb-1 >= 2:
        rgb_list  = composite.split("-",n_rgb-2)
        n_file_composite(rgb_list[-1], in_msg, sat_nr, time_slot, area)

    print "    create ", n_rgb ," file composite ", composite

    if in_msg.sat == "meteosat":
        sat = 'MSG'
    else:
        sat = in_msg.sat

    # get the filename of the last two files to compose  
    file_list = get_file_list(composite, in_msg, sat, sat_nr, time_slot, area, n=2)
    if file_list == None:  # if not all files are found 
        return composites_done   # return [] as error marker 

    # get result filename 
    comp_file = get_sat_filename(in_msg, composite, sat, sat_nr, time_slot, area) 
    comp_dir = dirname(comp_file)
    if not exists(comp_dir):
        if in_msg.verbose:
            print '... create output directory: ' + comp_dir
        makedirs(comp_dir)

    command="/usr/bin/composite -depth "+str(bits_per_pixel)+" "+file_list[0]+" "+file_list[1]+" "+comp_file
    if in_msg.verbose:
        print "    "+command
    subprocess.call(command, shell=True) #+" 2>&1 &"
    # check if file is produced
    if isfile(comp_file):
        composites_done.append(composite)

    if in_msg.scpOutput and composite in in_msg.postprocessing_composite:
        if in_msg.verbose:
            print "... secure copy "+comp_file+ " to "+in_msg.scpOutputDir
            subprocess.call("/usr/bin/scp "+in_msg.scpID+" "+comp_file+" "+in_msg.scpOutputDir+" 2>&1 &", shell=True)


    return composites_done

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------


def postprocessing (in_msg, time_slot, sat_nr, area):

    if in_msg.verbose:
        print ""
        print "*** start post processing for area: ", area, ', time: ', str(time_slot)
        print "... desired composites: ", in_msg.postprocessing_composite
        print "... desired montages: ", in_msg.postprocessing_montage
        print ""

    ## search for lightning file 
    #yearS  = str(in_msg.datetime.year)
    #monthS = "%02d" % in_msg.datetime.month
    #dayS   = "%02d" % in_msg.datetime.day
    #hourS  = "%02d" % in_msg.datetime.hour 
    #minS   = "%02d" % in_msg.datetime.minute

    #products_needed=set()
    #for comp in in_msg.postprocessing_composite:
    #    products_needed = products_needed |  set(comp.split("-"))  # | == union of two sets
    ##print products_needed

    composites_done = []
    if hasattr(in_msg, 'postprocessing_composite'):
        for composite in in_msg.postprocessing_composite:

            print "... creating composite: ", composite
            composites_done = n_file_composite(composite, in_msg, sat_nr, time_slot, area, composites_done=composites_done)

        if in_msg.verbose:
            if len(composites_done) > 0:
                print "... produced composites: "
                for comp in composites_done:
                    print "   ", comp
            else:
                print "*** Warning, no composites produced "

    # ----------------------------------------------
    if in_msg.verbose:
        print ""
        print "*** start montage_pictures for area: ", area
    
    montage_done = []
    if hasattr(in_msg, 'postprocessing_montage'):

        for montage in in_msg.postprocessing_montage:
            if len(montage) == 0:
                continue

            print "... creating montage: ", montage
            # sleep_str = " && sleep 1 "
            sleep_str = " "

            n_pics = len(montage)
            if n_pics == 2:
                tile = "2x1"
            if n_pics == 3:
                tile = "3x1"
            if n_pics == 4:
                tile = "2x2"
            if n_pics == 5:
                tile = "5x1"
            if n_pics == 6:
                tile = "3x2"
            if n_pics == 8:
                tile = "4x2"
            if n_pics == 9:
                tile = "3x3"
            if n_pics == 10:
                tile = "5x2"
            if n_pics == 12:
                tile = "4x3"

            files = ""
            outfile = ""
            files_exist=True
            files_complete=True
            
            for mfile in montage:
            
                rgb = mfile.split("_")[1]
                outputDir = format_name(in_msg.outputDir,  time_slot, rgb=rgb, area=area)
                
                next_file = outputDir+"/"+format_name(mfile+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
                if not isfile(next_file):
                    files_complete=False
                    print "*** Warning, can not find "+mfile+" file: "+next_file
                    if area == "ccs4" or area == 'EuropeCanaryS95':
                        # produce image with placeholder for missing product
                        files += " "+"/opt/users/common/logos/missing_product_textbox_"+area+".png"
                        outfile += mfile[mfile.index("_")+1:]+"-"
                    else:
                        print "*** ERROR, can not find "+mfile+" file: "+next_file
                        print "*** skip montage: ", montage
                        files_exist=False
                else:
                    files += " "+outputDir+"/"+format_name(mfile+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
                    outfile += mfile[mfile.index("_")+1:]+"-"

            outputDir = format_name(in_msg.outputDir,  time_slot, rgb=outfile[:-1], area=area)
            if not exists(outputDir):
               if in_msg.verbose:
                  print '... create output directory: ' + outputDir
               makedirs(outputDir)
            outfile = outputDir+"/"+format_name( "MSG_"+ outfile[:-1] + '-'+area + '_%y%m%d%H%M.png', time_slot, area=area)

            #filename1 = format_name(mfile+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
            #file1 = outputDir + filename1
            #filename2 =  format_name(montage[1]+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
            #file2 = outputDir + filename2

            #m1 =  montage[1][montage[1].index("_")+1:]  # get rid all strings before "_" (filename convection of SAT live)
            #outfilename = format_name(montage[0]+'-'+m1+"-"+area+'_%y%m%d%H%M.png', time_slot, area=area)
            #outfile = outputDir + outfilename

            if files_exist:
                if in_msg.verbose:
                    print "/usr/bin/montage -tile "+tile+" -geometry +0+0 "+files + " " + outfile  +" 2>&1 "+sleep_str
                subprocess.call("/usr/bin/montage -tile "+tile+" -geometry +0+0 "+files + " " + outfile  +" 2>&1 "+sleep_str, shell=True)

                if hasattr(in_msg, 'resize_montage'):
                    if in_msg.resize_montage != 100:
                        if in_msg.verbose:
                            print "/usr/bin/convert -resize "+str(in_msg.resize_montage)+"% " + outfile  +" tmp.png 2>&1 "+sleep_str
                        subprocess.call("/usr/bin/convert -resize "+str(in_msg.resize_montage)+"% " + outfile  +" tmp.png; mv tmp.png "+ outfile+" 2>&1 ", shell=True)

                # check if file is produced
                if isfile(outfile) and files_complete:
                    montage_done.append(montage)

                if in_msg.scpOutput:
                    if in_msg.verbose:
                        print "... secure copy "+outfile+ " to "+in_msg.scpOutputDir
                    subprocess.call("/usr/bin/scp "+in_msg.scpID+" "+outfile+" "+in_msg.scpOutputDir+" 2>&1 &", shell=True)

        if in_msg.verbose:
            if len(montage_done) > 0:
                print "... produced montages: "
                for montage in montage_done:
                    print "   ", montage
            else:
                print "*** Warning, no montages produced "

    return composites_done, montage_done

#------- ----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------

def print_usage():
         print "***           "
         print "*** Error, not enough command line arguments"
         print "***        please specify at least an input file"
         print "***        possible calls are:"
         print "*** python "+inspect.getfile(inspect.currentframe())+" input_MSG "
         print "*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 "
         print "                                 date and time must be completely given"
         print "*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 'h03-ir108' (use this as postprocessing_composite, not those written in the input file)"
         print "*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 'h03-ir108' 'ccs4' (use this as postprocessing_areas, not those written in the input file)"
         print "*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 ['h03-ir108','h03-airmass'] ['ccs4','euro4'] (several composites and areas)"
         print "***           "
         quit() # quit at this point
#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

   import sys
   from get_input_msg import get_date_and_inputfile_from_commandline
   in_msg = get_date_and_inputfile_from_commandline(print_usage=print_usage)

   if len(sys.argv) > 7:
       in_msg.postprocessing_composite = sys.argv[7]
       print in_msg.postprocessing_composite
       print in_msg.postprocessing_composite[0]
       print "bbb"
       if in_msg.postprocessing_composite[0] != '[':  #type(sys.argv[7]) is str
           print '[[[[['
           in_msg.postprocessing_composite = [sys.argv[7]]
       else:
           # convert (string representation of list) into a list
           import re
           junkers = re.compile('[[" \]]')
           in_msg.postprocessing_composite = junkers.sub('', sys.argv[7]).split(',')
       print "... produce composite: ", in_msg.postprocessing_composite, type(in_msg.postprocessing_composite)
       print type(in_msg.postprocessing_composite)
       if len(sys.argv) > 8:
           if type(sys.argv[8]) is str:
               in_msg.postprocessing_areas = [sys.argv[8]]
           else:
               in_msg.postprocessing_areas = sys.argv[8]
 
   print "*** start postprocessing for: "
   print "    area: ", in_msg.postprocessing_areas
   print "    composite: ", in_msg.postprocessing_composite
   print "    montage: ", in_msg.postprocessing_montage
              
   # loop over all postprocessing areas
   for area in in_msg.postprocessing_areas:
       postprocessing(in_msg, in_msg.datetime, int(in_msg.sat_nr), area)

   if in_msg.verbose:
      print " "

   #RGBs_done = plot_msg(in_msg)
   #print "*** Satellite pictures produced for ", RGBs_done 
   #print " "
