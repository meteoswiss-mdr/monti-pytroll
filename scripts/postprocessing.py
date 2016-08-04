
from my_msg_module import format_name
from os.path import isfile, join, exists
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
    outputDir = format_name(in_msg.outputDir,  time_slot, area=area)
    rgb='dens'
    filename =  format_name('THX_'+rgb+'-ccs4_%y%m%d%H%M_'+dt_str+'_'+dx_str+'.png', time_slot, area=area)
    return outputDir+filename

def get_radar_filename(in_msg, time_slot, area):
    print "    get_radar_filename radar"
    #outputDir = format_name('./%Y-%m-%d/radar/',  time_slot, area=area)
    #outputDir = "/data/cinesat/out/"
    outputDir = format_name(in_msg.outputDir,  time_slot, area=area)
    filename =  format_name('RAD_RZC-ccs4_%y%m%d%H%M.png', time_slot, area=area)
    return outputDir+filename

def get_odyssey_filename(in_msg, time_slot, area):
    print "    get_odyssey_filename radar"
    #outputDir = format_name('./%Y-%m-%d/radar/',  time_slot, area=area)
    #outputDir = "/data/cinesat/out/"
    outputDir = format_name(in_msg.outputDir,  time_slot, area=area)
    filename =  format_name('ODY_RATE-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
    return outputDir+filename

def get_TRT_filename(in_msg, time_slot, area):
    print "    get_TRT_filename TRT" 
    #outputDir = format_name('./%Y-%m-%d/radar/',  time_slot, area=area)
    #outputDir = "/data/cinesat/out/"
    outputDir = format_name(in_msg.outputDir,  time_slot, area=area)
    filename =  format_name('RAD_TRT-ccs4_%y%m%d%H%M.png', time_slot, area=area)
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
    filename  = format_name('/MSG_'+comp_str.replace("_","-")+'-ccs4_%y%m%d%H%M.png', time_slot, area=area, sat_nr=sat_nr) 
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
def n_file_composite(composite, in_msg, sat_nr, time_slot, area):

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
        return None        # return None as error marker 

    # get result filename 
    comp_file = get_sat_filename(in_msg, composite, sat, sat_nr, time_slot, area) 

    if in_msg.verbose:
        print "    composite "+file_list[0]+" "+file_list[1]+" "+comp_file
    subprocess.call("/usr/bin/composite "+file_list[0]+" "+file_list[1]+" "+comp_file, shell=True) #+" 2>&1 &"

    if in_msg.scpOutput and composite in in_msg.postprocessing_composite:
        if in_msg.verbose:
            print "... secure copy "+comp_file+ " to "+in_msg.scpOutputDir
            subprocess.call("/usr/bin/scp "+in_msg.scpID+" "+comp_file+" "+in_msg.scpOutputDir+" 2>&1 &", shell=True)

    return True

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------


def postprocessing (in_msg, time_slot, sat_nr, area):

    print ""
    print "*** start post processing for area: ", area

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

    if hasattr(in_msg, 'postprocessing_composite'):
        for composite in in_msg.postprocessing_composite:

            print "... creating composite: ", composite

            n_file_composite(composite, in_msg, sat_nr, time_slot, area)

    # ----------------------------------------------

    print ""
    print "*** start montage_pictures for area: ", area

    if hasattr(in_msg, 'postprocessing_montage'):

        for montage in in_msg.postprocessing_montage:
            if len(montage) == 0:
                continue

            print "... creating montage: ", montage
            # sleep_str = " && sleep 1 "
            sleep_str = " "

            outputDir = format_name(in_msg.outputDir,  time_slot, area=area)

            n_pics = len(montage)
            if n_pics == 2:
                tile = "2x1"
            if n_pics == 3:
                tile = "3x1"
            if n_pics == 4:
                tile = "2x2"
            if n_pics == 4:
                tile = "5x1"
            if n_pics == 6:
                tile = "3x2"

            files = ""
            outfile = ""
            files_exist=True
            for mfile in montage:
                next_file = outputDir+"/"+format_name(mfile+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
                if not isfile(next_file):
                    print "*** ERROR, can not find "+mfile+" file: "+next_file
                    print "*** skip montage: ", montage
                    files_exist=False
                files += " "+outputDir+"/"+format_name(mfile+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
                outfile += mfile[mfile.index("_")+1:]+"-"

            outfile = outputDir+"/"+format_name( "MSG_"+ outfile[:-1] + '-'+area + '_%y%m%d%H%M.png', time_slot, area=area)

            #filename1 = format_name(mfile+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
            #file1 = outputDir + filename1
            #filename2 =  format_name(montage[1]+'-'+area+'_%y%m%d%H%M.png', time_slot, area=area)
            #file2 = outputDir + filename2

            #m1 =  montage[1][montage[1].index("_")+1:]  # get rid all strings before "_" (filename convection of SAT live)
            #outfilename = format_name(montage[0]+'-'+m1+"-"+area+'_%y%m%d%H%M.png', time_slot, area=area)
            #outfile = outputDir + outfilename

            if files_exist:
                print "/usr/bin/montage -tile "+tile+" -geometry +0+0 "+files + " " + outfile  +" 2>&1 "+sleep_str
                subprocess.call("/usr/bin/montage -tile "+tile+" -geometry +0+0 "+files + " " + outfile  +" 2>&1 "+sleep_str, shell=True)

                if in_msg.scpOutput:
                    if in_msg.verbose:
                        print "... secure copy "+outfile+ " to "+in_msg.scpOutputDir
                        subprocess.call("/usr/bin/scp "+in_msg.scpID+" "+outfile+" "+in_msg.scpOutputDir+" 2>&1 &", shell=True)

