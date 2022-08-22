from __future__ import division
from __future__ import print_function

from my_msg_module_py3 import format_name
from os.path import isfile, join, exists, dirname
from os import makedirs
import subprocess
import inspect
from copy import deepcopy

def get_THX_filename(time_slot, area, outDir, outFile):
    print("    get_THX_filename THX for ", area)
    from ConfigParser import ConfigParser
    from mpop import CONFIG_PATH
    conf = ConfigParser()
    conf.read(join(CONFIG_PATH, "swisslightning.cfg"))
    dx = int(conf.get("thx-level2", "dx"))
    dt = int(conf.get("thx-level2", "dt"))
    dt_str = ("%04d" % dt) + "min"
    dx_str = ("%03d" % dx) + "km"
    outputDir = format_name(outDir, time_slot, area=area, rgb="THX")
    rgb='dens'
    filename =  format_name('THX_'+rgb+'-'+area+'_%y%m%d%H%M_'+dt_str+'_'+dx_str+'.png', time_slot, area=area, rgb="THX")
    return outputDir+filename

def get_radar_filename(rgb, time_slot, area, outDir, outFile):
    print("    get_radar_filename radar for ", area)

    if rgb=='radar':
        # backward comparbility (old convention for file names of radar products, not that good)
        outputDir = format_name(outDir, time_slot, area=area, rgb="radar")
        filename = format_name('RAD_RZC-'+area+'_%y%m%d%H%M.png', time_slot, area=area)   
    else:
        # new better file naming 
        outputDir = format_name(outDir, time_slot, area=area, rgb=rgb)
        filename = format_name('RAD_'+rgb+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)   

    if not exists(outputDir):
        print('... create output directory: ' + outputDir)
        from os import makedirs
        makedirs(outputDir)
        
    return outputDir+filename

def get_odyssey_filename(time_slot, area, outDir, outFile):
    print("    get_odyssey_filename radar for ", area)
    outputDir = format_name(outDir, time_slot, area=area, rgb="radar")
    if not exists(outputDir):
        print('... create output directory: ' + outputDir)
        from os import makedirs
        makedirs(outputDir)
    filename =  format_name('ODY_RATE-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
    return outputDir+filename

def get_TRT_filename(time_slot, area, outDir, outFile):
    print("    get_TRT_filename TRT for ", area) 
    outputDir = format_name(outDir, time_slot, area=area, rgb="TRT")
    if not exists(outputDir):
        print('... create output directory: ' + outputDir)
        from os import makedirs
        makedirs(outputDir)
    filename =  format_name('RAD_TRT-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
    return outputDir+filename

def get_cosmo_filename(rgb, time_slot, area, outDir, outFile):
    print("    get_cosmo_filename radar for ", area)

    outputDir = format_name(outDir, time_slot, area=area, rgb=rgb)
    filename = format_name('COSMO_'+rgb+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)   
    if not exists(outputDir):
        print('... create output directory: ' + outputDir)
        from os import makedirs
        makedirs(outputDir)
        
    return outputDir+filename

def get_OT_filename(rgb, time_slot, area, outDir, outFile):
    print("    get_OT_filename (overshooting top) for ", area) 
    outputDir = format_name(outDir, time_slot, area=area, rgb=rgb, sat=sat, sat_nr=sat_nr)
    if not exists(outputDir):
        print('... create output directory: ' + outputDir)
        from os import makedirs
        makedirs(outputDir)
    filename  = format_name(outFile, time_slot, area=area, rgb=rgb, sat=sat, sat_nr=sat_nr)
    return outputDir+filename

def get_sat_filename(rgb, sat, sat_nr, time_slot, area, outDir, outFile):
    print("    get_sat_filename for ", rgb, area)
    #outputDir = "/data/cinesat/out/"
    outputDir = format_name(outDir, time_slot, area=area, rgb=rgb, sat=sat, sat_nr=sat_nr)
    if not exists(outputDir):
        print('... create output directory: ' + outputDir)
        from os import makedirs
        makedirs(outputDir)
    filename  = format_name(outFile, time_slot, area=area, rgb=rgb, sat=sat, sat_nr=sat_nr)
    return outputDir+filename

def get_comp_filename(comp_str, sat_nr, time_slot, area, outDir, outFile):
    print("    get_comp_filename ", comp_str)
    outputDir = format_name(outDir, time_slot, area=area, rgb=comp_str.replace("_","-"), sat_nr=sat_nr)
    if not exists(outputDir):
        print('... create output directory: ' + outputDir)
        from os import makedirs
        makedirs(outputDir)
    filename  = format_name('MSG_'+comp_str.replace("_","-")+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area, sat_nr=sat_nr) 
    return outputDir+'/'+filename

# ---
def get_file_list(composite, sat, sat_nr, time_slot, area, outDir, outFile, n=None):

    import products 
    if n is None:
        rgb_list  = composite.split("-")
    else:
        rgb_list  = composite.split("-",n-1)
    file_list = []

    
    for rgb in rgb_list:
        if rgb == 'THX':
            file_list.append (get_THX_filename(time_slot, area, outDir, outFile))
        elif rgb == 'TRT':
            file_list.append (get_TRT_filename(time_slot, area, outDir, outFile))
        elif rgb.replace("pc","") in products.MSG_all:  # also the parallax corrected products (marked as pc)
            file_list.append (get_sat_filename(rgb, 'MSG', sat_nr, time_slot, area, outDir, 'MSG_%(rgb)s-%(area)s_%y%m%d%H%M.png'))
        elif (rgb == 'radar' or rgb in products.swissradar) and sat != 'cpp':
            file_list.append (get_radar_filename(rgb, time_slot, area, outDir, outFile))
        elif (rgb in products.cosmo):
            file_list.append (get_cosmo_filename(rgb, time_slot, area, outDir, outFile))
        elif rgb == 'RATE':
            file_list.append (get_odyssey_filename(time_slot, area, outDir, outFile))
        else:
            file_list.append (get_comp_filename(rgb, sat_nr, time_slot, area, outDir, outFile))

        print(file_list)
            
        if not isfile(file_list[-1]):
            print("*** ERROR, can not find "+rgb+" file: "+file_list[-1])
            print("    skip composite: "+composite)
            return None
    return file_list

# ---
def n_file_composite(composite, satellite, sat_nr, time_slot, area, outDir, outFile,
                     scpOutput=False, scpOutDir="/tmp/", scpID=None, scpProducts=[],
                     scpOutDir2="/tmp/", scpID2=None, scpProducts2=[], 
                     ftpUpload=False, ftpProducts=[], ftpServer=None, ftpUser=None, ftpPassword=None, 
                     bits_per_pixel=8, compress_to_8bit=False, composites_done=[], verbose=True):
    
    n_rgb = composite.count('-') + 1

    # create smaller required composites 
    if n_rgb-1 >= 2:
        rgb_list  = composite.split("-",n_rgb-2)
        n_file_composite(rgb_list[-1], satellite, sat_nr, time_slot, area, outDir, outFile,
                         scpOutput=scpOutput, scpOutDir=scpOutDir, scpID=scpID, scpProducts=scpProducts,
                         scpOutDir2=scpOutDir2, scpID2=scpID2, scpProducts2=scpProducts2, 
                         bits_per_pixel=bits_per_pixel, compress_to_8bit=compress_to_8bit, verbose=verbose)

    print("    create ", n_rgb ," file composite ", composite)

    if satellite == "meteosat":
        sat = 'MSG'
    else:
        sat = satellite
    
    # get the filename of the last two files to compose  
    file_list = get_file_list(composite, sat, sat_nr, time_slot, area, outDir, outFile, n=2)
    if file_list is None:  # if not all files are found 
        return composites_done   # return [] as error marker 

    # get result filename 
    comp_file = get_comp_filename(composite, sat_nr, time_slot, area, outDir, outFile)
    comp_dir = dirname(comp_file)
    if not exists(comp_dir):
        if verbose:
            print('... create output directory: ' + comp_dir)
        makedirs(comp_dir)

    command="/usr/bin/composite -depth "+str(bits_per_pixel)+" "+file_list[0]+" "+file_list[1]+" "+comp_file
    if verbose:
        print("    "+command)
    subprocess.call(command, shell=True) #+" 2>&1 &"
    # check if file is produced
    if isfile(comp_file):
        composites_done.append(composite)

    if scpOutput:
        if (composite in scpProducts) or ('all' in [x.lower() for x in scpProducts if type(x)==str]):
            scpOutputDir = format_name (scpOutDir, time_slot, area=area, rgb=composite, sat=sat, sat_nr=sat_nr )
            if verbose:
                print("/usr/bin/scp "+scpID+" "+comp_file+" "+scpOutputDir+" 2>&1 &")
            subprocess.call("/usr/bin/scp "+scpID+" "+comp_file+" "+scpOutputDir+" 2>&1 &", shell=True)
            
    if scpOutput and (scpID2 is not None) and (scpOutDir2 is not None):
        if (composite in scpProducts2) or ('all' in [x.lower() for x in scpProducts2 if type(x)==str]):
            scpOutputDir2 = format_name (scpOutDir2, time_slot, area=area, rgb=composite, sat=sat, sat_nr=sat_nr )
            if compress_to_8bit:
                if verbose:
                    print("... secure copy "+comp_file.replace(".png","-fs8.png")+ " to "+scpOutputDir2)
                subprocess.call("scp "+scpID2+" "+comp_file.replace(".png","-fs8.png")+" "+scpOutputDir2+" 2>&1 &", shell=True)
            else:
                if verbose:
                    print("... secure copy "+comp_file+ " to "+scpOutputDir2)
                subprocess.call("scp "+scpID2+" "+comp_file+" "+scpOutputDir2+" 2>&1 &", shell=True)

    if ftpUpload:
        print("... ftpUpload requested")
        if ftpServer==None or ftpUser==None or ftpPassword==None:
            print("*** ERROR, ftp input is not complete")
            print("ftp_server=", ftpServer)
            print("ftp_user=", ftpUser)
            print("ftp_password=", ftpPassword)
        else:
            if (composite in ftpProducts):
                command_line = "curl -T "+comp_file+" "+ftpServer+" --user "+ftpUser+":"+ftpPassword
                print (command_line)
                subprocess.call(command_line, shell=True)
            
    return composites_done

#-----------------------------------------------------------------------------------------

## simplyfied wrapper to call inside a program
#
#def postprocessing_function (time_slot, sat, sat_nr, areas, composite, montage, input_file='input_template.py'):
#
#    # define an instant of the class 'input_msg_class'
#    from get_input_msg import input_msg_class
#    in_msg = input_msg_class()
#
#    # define satellite (pass arguements to the in_msg instant)
#    in_msg.sat = sat
#    in_msg.sat_nr = sat_nr
#    in_msg.init_datetime(timeslot=timeslot)
#    from my_msg_module import check_RSS
#    in_msg.RSS = check_RSS(sat_nr, date)
#
#    # define postprocessing (pass arguements to the in_msg instant)
#    in_msg.postprocessing_areas=areas
#    in_msg.postprocessing_composite=composite
#    in_msg.postprocessing_montage=montage
#    print "*** start postprocessing for: "
#    print "    area: ", in_msg.postprocessing_areas
#    print "    composite: ", in_msg.postprocessing_composite
#    print "    montage: ", in_msg.postprocessing_montage
#
#    # loop over all postprocessing areas
#    for area in in_msg.postprocessing_areas:
#        postprocessing(in_msg, in_msg.datetime, int(in_msg.sat_nr), area)
    
#-----------------------------------------------------------------------------------------

def postprocessing (in_msg, time_slot, sat_nr, area):

    if hasattr(in_msg, 'postprocessing_composite'):
        if isinstance(in_msg.postprocessing_composite, dict):
            if area in in_msg.postprocessing_composite:
                postprocessing_composite=in_msg.postprocessing_composite[area]
            else:
                postprocessing_composite=[]
        else:
            postprocessing_composite=in_msg.postprocessing_composite
    
        if in_msg.verbose:
            print("==================================")
            print("*** start post processing for area: ", area, ', time: ', str(time_slot))
            print("... desired composites: ", postprocessing_composite)

        composites_done = []

        for composite in postprocessing_composite:

            print("... creating composite: ", composite)
            composites_done = n_file_composite(composite, in_msg.sat, sat_nr, time_slot, area, in_msg.outputDir, in_msg.outputFile,
                                               scpOutput=in_msg.scpOutput, scpOutDir=in_msg.scpOutputDir, scpID=in_msg.scpID, scpProducts=in_msg.scpProducts,
                                               scpOutDir2=in_msg.scpOutputDir2, scpID2=in_msg.scpID2, scpProducts2=in_msg.scpProducts2,
                                               ftpUpload=in_msg.ftpUpload, ftpProducts=in_msg.ftpProducts, ftpServer=in_msg.ftpServer, ftpUser=in_msg.ftpUser, ftpPassword=in_msg.ftpPassword,
                                               composites_done=composites_done, verbose=in_msg.verbose)

        if in_msg.verbose:
            if len(composites_done) > 0:
                print("... produced composites: ")
                for comp in composites_done:
                    print("   ", comp)
            else:
                print("*** Warning, no composites produced ")

    # ----------------------------------------------
    if in_msg.verbose:
        print("*** start montage_pictures for area: ", area)
    
    montage_done = []
    if hasattr(in_msg, 'postprocessing_montage'):

        if isinstance(in_msg.postprocessing_montage, dict):
            if area in in_msg.postprocessing_montage:
                postprocessing_montage=in_msg.postprocessing_montage[area]
            else:
                postprocessing_montage=[]
        else:
            postprocessing_montage=in_msg.postprocessing_montage
    
        if in_msg.verbose:
            print("")
            print("*** start post processing for area: ", area, ', time: ', str(time_slot))
            print("... desired montages: ", postprocessing_montage)
            
        for montage in postprocessing_montage:
            if len(montage) == 0:
                continue

            print("... creating montage: ", montage)
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
            nr_files_exist=0
            files_complete=True
            
            for mfile in montage:

                print('    analyse first filename', mfile)
                rgb = mfile.split("_")[1]
                outputDir = format_name(in_msg.outputDir,  time_slot, rgb=rgb, area=area)
                
                next_file = outputDir+"/"+format_name(mfile+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
                if not isfile(next_file):
                    files_complete=False
                    print("*** Warning, can not find "+mfile+" file: "+next_file)
                    if area in ["ccs4","EuropeCanaryS95","odysseyS25","euroHDready","SeviriDiskFull00S4"]:
                        # produce image with placeholder for missing product
                        files += " "+"/opt/users/common/logos/missing_product_textbox_"+area+".png"
                        outfile += mfile[mfile.index("_")+1:]+"-"
                    else:
                        print("*** ERROR, can not find "+mfile+" file: "+next_file)
                        print("*** skip montage: ", montage)
                        files_exist=False
                else:
                    files += " "+outputDir+"/"+format_name(mfile+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
                    nr_files_exist+=1
                    outfile += mfile[mfile.index("_")+1:]+"-"

            outputDir = format_name(in_msg.outputDir,  time_slot, rgb=outfile[:-1], area=area)
            if not exists(outputDir):
               if in_msg.verbose:
                  print('... create output directory: ' + outputDir)
               makedirs(outputDir)

            montage_name=deepcopy(outfile[:-1])
            outfile = outputDir+"/"+format_name( "MSG_"+ outfile[:-1] + '-'+area + '_%y%m%d%H%M.png', time_slot, area=area)

            #filename1 = format_name(mfile+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
            #file1 = outputDir + filename1
            #filename2 =  format_name(montage[1]+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
            #file2 = outputDir + filename2

            #m1 =  montage[1][montage[1].index("_")+1:]  # get rid all strings before "_" (filename convection of SAT live)
            #outfilename = format_name(montage[0]+'-'+m1+"-"+area+'_%y%m%d%H%M.png', time_slot, area=area)
            #outfile = outputDir + outfilename

            if files_exist and nr_files_exist>0:
                if in_msg.verbose:
                    print("/usr/bin/montage -tile "+tile+" -geometry +0+0 "+files + " " + outfile  +" 2>&1 "+sleep_str)
                subprocess.call("/usr/bin/montage -tile "+tile+" -geometry +0+0 "+files + " " + outfile  +" 2>&1 "+sleep_str, shell=True)

                if hasattr(in_msg, 'resize_montage'):
                    if in_msg.resize_montage != 100:
                        if in_msg.verbose:
                            print("/usr/bin/convert -resize "+str(in_msg.resize_montage)+"% " + outfile  +" tmp.png 2>&1 "+sleep_str)
                        subprocess.call("/usr/bin/convert -resize "+str(in_msg.resize_montage)+"% " + outfile  +" tmp.png; mv tmp.png "+ outfile+" 2>&1 ", shell=True)

                # check if file is produced
                if isfile(outfile) and files_complete:
                    montage_done.append(montage)
                    
                if in_msg.scpOutput:
                    if (montage in in_msg.scpProducts) or ('all' in [x.lower() for x in in_msg.scpProducts if type(x)==str]):
                        scpOutputDir = format_name (in_msg.scpOutputDir, time_slot, area=area, rgb=montage_name, sat=in_msg.sat, sat_nr=sat_nr )
                        if in_msg.verbose:
                            print("    /usr/bin/scp "+in_msg.scpID+" "+outfile+" "+scpOutputDir+" 2>&1 &")
                        subprocess.call("/usr/bin/scp "+in_msg.scpID+" "+outfile+" "+scpOutputDir+" 2>&1 &", shell=True)

                if in_msg.scpOutput and (in_msg.scpID2 is not None) and (in_msg.scpOutputDir2 is not None):
                    if (montage in in_msg.scpProducts2) or ('all' in [x.lower() for x in in_msg.scpProducts2 if type(x)==str]):
                        scpOutputDir2 = format_name (in_msg.scpOutputDir2, time_slot, area=area, rgb=montage_name, sat=in_msg.sat, sat_nr=sat_nr )
                        if in_msg.compress_to_8bit:
                            if in_msg.verbose:
                                print("    scp "+in_msg.scpID2+" "+outfile.replace(".png","-fs8.png")+" "+scpOutputDir2+" 2>&1 &")
                            subprocess.call("scp "+in_msg.scpID2+" "+outfile.replace(".png","-fs8.png")+" "+scpOutputDir2+" 2>&1 &", shell=True)
                        else:
                            if in_msg.verbose:
                                print("    scp "+in_msg.scpID2+" "+outfile+" "+scpOutputDir2+" 2>&1 &")
                            subprocess.call("scp "+in_msg.scpID2+" "+outfile+" "+scpOutputDir2+" 2>&1 &", shell=True)
                        
        if in_msg.verbose:
            if len(montage_done) > 0:
                print("... produced montages: ")
                for montage in montage_done:
                    print("   ", montage)
            else:
                if len(postprocessing_montage) > 0:
                    if len(postprocessing_montage[0]) > 0:
                        print("*** Warning, no montages produced (requested ",postprocessing_montage,")")

    return composites_done, montage_done

#------- ----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------

def print_usage():
         print("***           ")
         print("*** Error, not enough command line arguments")
         print("***        please specify at least an input file")
         print("***        possible calls are:")
         print("*** python "+inspect.getfile(inspect.currentframe())+" input_MSG ")
         print("*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 ")
         print("                                 date and time must be completely given")
         print("*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 'ccs4'           (overwrite in_msg.postprocessing_areas)")
         print("*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 ['ccs4','euro4'] (overwrite in_msg.postprocessing_areas)")
         print("*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 'ccs4' 'h03b-ir108'                 (overwrite postprocessing_composite)")
         print("*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 'ccs4' ['h03b-ir108','h03b-airmass'] (overwrite postprocessing_composite)")
         print("*** python "+inspect.getfile(inspect.currentframe())+" input_MSG 2014 07 23 16 10 ['ccs4','euro4'] ['h03b-ir108','h03b-airmass'] (several composites and areas)")
         print("***           ")
         quit() # quit at this point
#-----------------------------------------------------------------------------------------

# call by command line
if __name__ == '__main__':

#   import sys
#   import re
#   from get_input_msg import get_date_and_inputfile_from_commandline
#   in_msg = get_date_and_inputfile_from_commandline(print_usage=print_usage)
#
#   # interpret 7th argument as area/areas 
#   if len(sys.argv) > 7:
#       area= sys.argv[7]
#       if area[0] != '[':  # user wants a list
#           in_msg.postprocessing_areas = [sys.argv[7]]
#       else:
#           # convert (string representation of list) into a list
#           junkers = re.compile('[[" \]]')
#           in_msg.postprocessing_areas = junkers.sub('', sys.argv[7]).split(',')
#           
#       if len(sys.argv) > 8:
#           composite = sys.argv[8]
#           if composite[0] != '[':  # user wants a list
#               in_msg.postprocessing_composite = [sys.argv[8]]
#           else:
#               # convert (string representation of list) into a list
#               junkers = re.compile('[[" \]]')
#               in_msg.postprocessing_composite = junkers.sub('', sys.argv[8]).split(',')
# 
#           #print "... produce composite: ", in_msg.postprocessing_composite, type(in_msg.postprocessing_composite)
#           #print type(in_msg.postprocessing_composite)
#
#           if len(sys.argv) > 9:
#               montage = sys.argv[9]
#               if montage[0] != '[':  # user wants a list
#                   in_msg.postprocessing_montage = [sys.argv[9]]
#               else:
#                   # convert (string representation of list) into a list
#                   junkers = re.compile('[[" \]]')
#                   in_msg.postprocessing_montage = junkers.sub('', sys.argv[9]).split(',')

   from get_input_msg_py3 import parse_commandline_and_read_inputfile
   in_msg = parse_commandline_and_read_inputfile()
    
   print("*** start postprocessing for: ")
   print("    areas: ", in_msg.postprocessing_areas)
   print("    date: ", in_msg.datetime)
   print("    composite: ", in_msg.postprocessing_composite)
   print("    montage: ", in_msg.postprocessing_montage)
              
   # loop over all postprocessing areas
   for area in in_msg.postprocessing_areas:
       postprocessing(in_msg, in_msg.datetime, in_msg.sat_nr, area)

   if in_msg.verbose:
      print(" ")

   #RGBs_done = plot_msg(in_msg)
   #print "*** Satellite pictures produced for ", RGBs_done 
   #print " "

   
