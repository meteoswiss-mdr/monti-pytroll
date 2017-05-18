from __future__ import print_function
#import os
#os.chdir("/data/cinesat/in/eumetcast1/")
#from satpy import Scene
#from satpy.scene import Scene
from datetime import datetime
import os
import datetime
import sys
import getpass

## for more debugging information uncomment the two following lines 
from satpy.utils import debug_on
debug_on()

def print_usage():
    print("***           ")
    print("*** Error, not enough command line arguments")
    print("***        please specify at least an input file")
    print("***        possible calls are:")
    print("*** python "+inspect.getfile(inspect.currentframe()))
    print("*** python "+inspect.getfile(inspect.currentframe())+" 2014 07 23 16 10 ")
    print("                                 date and time must be completely given")
    print("***           ")

cwd = os.getcwd()

if len(sys.argv) == 1:
    ## automatic choise of time
    ## either fixed
    time_start = datetime.datetime(2015, 5, 30, 12, 00, 0)
    ## or last time available 
    #RSS=False
    #from my_msg_module import get_last_SEVIRI_date
    #time_start = get_last_SEVIRI_date(RSS, delay=10)
elif len(sys.argv) == 5:
    year   = int(sys.argv[2])
    month  = int(sys.argv[3])
    day    = int(sys.argv[4])
    hour   = int(sys.argv[5])
    minute = int(sys.argv[6])
    time_start = datetime.datetime(year, month, day, hour, minute)
else:
    print_usage()

time_end = time_start + datetime.timedelta(minutes=12)

print("")
print("========================")

import socket
hostname=socket.gethostname()

if "zueub" in hostname:
    data_dir = "/data/COALITION2/database/meteosat/native_test/"
    #data_file="MSG3-SEVI-MSG15-0100-NA-20170326101240.438000000Z-20170326101257-1213498.nat"
    data_file="MSG3-SEVI-MSG15-0100-NA-20170326102740.340000000Z-20170326102757-1213498.nat"
    #data_file="MSG2-SEVI-MSG15-0100-NA-20150531235918.139000000Z-20150531235936-1178986.nat"   # does not work, as number of columns cant be devided by 4 
    filenames=[data_dir+data_file]
elif "kesch" in hostname:
    testfile=False
    if testfile:
        filenames=["/store/mch/msclim/cmsaf/msg/native_test/MSG3-SEVI-MSG15-0100-NA-20170326102740.340000000Z-21213498-1.nat"]
    else:
        ## get archive directoy 
        archive_dir = "/store/mch/msclim/cmsaf/msg/native-fulldisk/"
        #archive_dir = "/store/mch/msclim/cmsaf/msg/native-alps/"    ### does not work, as number of columns cant be devided by 4 

        ## search file
        import glob
        filename_pattern = time_end.strftime( archive_dir + "/%Y/%m/%d/" + '/MSG[1-4]-SEVI-MSG15-0100-NA-%Y%m%d%H%M??.*.nat.bz2' )
        bz2files = glob.glob(filename_pattern)
        if len(bz2files) == 0:
            raise ValueError("... No input file found, searched for:"+filename_pattern)

        ## copy and bunzip2 file
        print("...copy file from archive: "+bz2files[0])
        from subprocess import call
        #data_dir="/scratch/"+getpass.getuser()+"/"   
        data_dir=os.environ['SCRATCH']+"/"
        if not os.path.exists(data_dir):
            print('... create output directory: '+data_dir)
            os.makedirs(data_dir)
        call(["cp", bz2files[0], data_dir])
        os.chdir(data_dir)
        print("...bunzip2 file: "+bz2files[0])
        bz2file=os.path.basename(bz2files[0])
        call(["bunzip2",data_dir+bz2file])
        data_file=bz2file[:-4]
        filenames=[data_dir+data_file]
else:
    raise ValueError("Unknown computer"+hostname+": no example file is provided")


print("========================")
print("... read file:")
print(filenames)

## choose reader
reader="native_msg"
#reader="hrit_msg"

## different ways to define the satellite data object 
from satpy import Scene
global_scene = Scene(platform_name="Meteosat-9", sensor="seviri", reader=reader, filenames=filenames)
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=datetime(2015, 4, 20, 10, 0), base_dir="/home/a001673/data/satellite/Meteosat-10/seviri/lvl1.5/2015/04/20/HRIT") 
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=lastdate, base_dir="/data/cinesat/in/eumetcast1")
#global_scene = Scene(platform_name="Meteosat-10", sensor="seviri", start_time=lastdate, reader="hrit_msg", basedir="/data/cinesat/in/eumetcast1/")  
#global_scene = Scene(platform_name="Meteosat-9", sensor="seviri", reader="hrit_msg", start_time=lastdate)

## get some infos about the satellite data object
print("========================")
print("... dir(global_scene)")
print(dir(global_scene))
print("========================")
print("... global_scene.info")
print(global_scene.info)
print("========================")
#print(global_scene.available_composite_names())  ### currently not all of them work, I have to check with the PyTroll satpy guys
#print(global_scene.all_composite_names())        ### currently not all of them work, I have to check with the PyTroll satpy guys
#print("========================")
print("... all channel names:")
print(global_scene.all_dataset_names())

## tested RGBs 
#RGB='natural'            # IR_016         VIS008         VIS006
#RGB='green_snow'
RGB='overview'
#RGB='overview_sun'

#### RGB in mpop that do not yet work with satpy 
##RGB='airmass'           # WV_062-WV_073  IR_097-IR_108  -WV_062
##RGB='ash'
##RGB='cloudtop'
##RGB='convection'         # WV_062-WV_073  IR_039-IR_108  IR_016-VIS006
##RGB='convection_co2'
##RGB='day_microphysics'   # VIS008         IR_039(solar)  IR_108     # requires the pyspectral modul
##RGB='dust'               # IR_120-IR_108  IR_108-IR_087  IR_108
#RGB='fog'  
##RGB='ir108'
##RGB='night_fog'
##RGB='night_microphysics' # IR_120-IR_108  IR_108-IR_039  IR_108
##RGB='night_overview'
##RGB='red_snow'
##RGB='refl39_chan'        # requires the pyspectral modul
##RGB='snow'               # requires the pyspectral modul
##RGB='vis06'
##RGB='wv_high'
##RGB='wv_low'

## different ways to load channel data into the sat data object 
global_scene.load([RGB])
global_scene.load(["VIS006"])
#global_scene.load([0.6, 0.8, 10.8])
#global_scene.load(['overview'])
#global_scene.load(["VIS006", "VIS008", "IR_108"])

## get information about loaded channels
#print("========================")
#print(global_scene.datasets)

## show satellite pictures directly on the screen 
#global_scene.show(0.6)
#global_scene.show('VIS006')
#global_scene.show('overview')

## save an RGB as png file 
outputfile=time_start.strftime(cwd+'/MSG_'+RGB+'-global'+'_%Y%m%d%H%M.png')

if False:
    print("... save "+outputfile)
    global_scene.save_dataset(RGB, outputfile)


print("========================")
## choose area
area="ccs4"
#area="SeviriDisk00"
#area="cosmo7"
#area="cosmo1"
print("... resample data to another projection") 
local_scene = global_scene.resample(area)
outputfile=time_start.strftime(cwd+'/MSG_'+RGB+'-'+area+'_%Y%m%d%H%M.png')

print("... save "+outputfile)
add_border=True
if add_border:
    if "zueub" in hostname:
        shape_dir='/opt/users/common/shapes/'
    elif "kesch" in hostname:
        shape_dir='/store/msrad/utils/shapes/'
    local_scene.show(RGB, overlay={'coast_dir':shape_dir, 'color':'white', 'width':0.75})
    local_scene.save_dataset(RGB, outputfile, overlay={'coast_dir':shape_dir, 'color':'white', 'width':0.75})
else:
    local_scene.save_dataset(RGB, outputfile)
    #local_scene.save_dataset('overview', time_start.strftime(cwd+'/MSG_'+RGB+'-'+area+'_%Y%m%d%H%M.tiff'), writer='geotiff')


# work with channel data
print("========================")
print(type(local_scene['VIS006'].data))
