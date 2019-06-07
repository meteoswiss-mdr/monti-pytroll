'''
input: a data object 
 as returned by GeostationaryFactory.create_scene(sat, str(sat_nr).zfill(2), "seviri", time_slot)
 or by global_data.project(area, precompute=True)
output:
  image function according to the input string
'''

import products 
import inspect
import logging
import datetime
from mpop.projector import get_area_def
from copy import deepcopy 

LOG = logging.getLogger(__name__)
LOG.setLevel(40)
#CRITICAL 50 #ERROR 40 #WARNING 30 #INFO 20 #DEBUG 10 #NOTSET 0

'''
input: RSS 
  logical variable True or False 
  specifies if you like get 
  (RSS=True)  the last rapid scan observation date (every 5  min) 
  (RSS=False) the last full disk  observation date (every 15 min)
  (delay=INT) number of minutes to substract before finding the date (good if data needs a few min before arriving)
  (time_slot) If not given, take last time
              otherwise search scanning time of SEVIRI before given time_slot
output:
  date structure with the date of the last SEVIRI observation
'''

def get_last_SEVIRI_date(RSS, delay=0, time_slot=None):

    from time import gmtime

    LOG.info("*** start get_last_SEVIRI_date ("+inspect.getfile(inspect.currentframe())+")")

    # if rapid scan service than 5min otherwise 15
    if RSS:
        nmin = 5 
    else:
        nmin = 15

    if (time_slot is None):
        # get the current time
        gmt = gmtime()
        #print "GMT time: "+ str(gmt)
        # or alternatively 
        # utc = datetime.datetime.utcnow()
        # convert to datetime format
        t0 = datetime.datetime(gmt.tm_year, gmt.tm_mon, gmt.tm_mday, gmt.tm_hour, gmt.tm_min, 0) 
        LOG.debug("    current time = "+str(t0))
    else:
        t0 = time_slot + datetime.timedelta(seconds=nmin*60)  # we substract one scanning time later, so we can add it here
        LOG.debug("    reference time = "+str(t0))

    # apply delay (if it usually takes 5 min for the data to arrive, use delay 5min)
    if delay != 0:
       t0 -= datetime.timedelta(minutes=delay)
    LOG.debug("    applying delay "+str(delay)+" min delay, time = "+ str(t0))

    LOG.debug("    round by scanning time "+str(nmin)+" min, RSS = "+str(RSS))
    #tm_min2 = gmt.tm_min - (gmt.tm_min % nmin)
    minute1 = t0.minute - (t0.minute % nmin)

    # define current date rounded by one scan time 
    #date1 = datetime.datetime(gmt.tm_year, gmt.tm_mon, gmt.tm_mday, gmt.tm_hour, tm_min2 , 0) 
    t1 = datetime.datetime(t0.year, t0.month, t0.day, t0.hour, minute1, 0) 
    LOG.debug("    end time of last scan: "+str(t1))

    # substracting one scan time (as the start time of scan is returned) 
    t1 -= datetime.timedelta(seconds=nmin*60)
    LOG.info("    start time of last scan: "+str(t1))

    return t1


def check_near_real_time(time_slot, minutes):

    """
    purpose: checks if specified time is within a certain time window with respect to the current time 
    input:
    * minutes [int]: number of minutes, that the input data is there 
    output:
    * nrt_flag [boolean]:
      True, if specified time is not older than "minutes" minutes (with respect to current time)
      False, if older
    """ 

    LOG.info("*** start check_near_real_time ("+inspect.getfile(inspect.currentframe())+")")

    # check if specified time is older than 2 hours 
    from time import gmtime

    # get the current time
    gmt = gmtime()
    t0 = datetime.datetime(gmt.tm_year, gmt.tm_mon, gmt.tm_mday, gmt.tm_hour, gmt.tm_min, 0) 
    #print "    current time ", str(t0)
    #print "    time of interest ", str(time_slot)

    # if specified time is older than current time 'minutes' min 
    if time_slot < (t0 - datetime.timedelta(seconds=minutes*60)):
        LOG.info("    near_real_time = False")
        return False
    else:
        LOG.info("    near_real_time = True")
        return True

'''
input:  
  rgb  -> rgb  you want to check for the existence of the input files
  verbose -> logical (True == print verbose output, False == quiet)
output:
  date structure with the date of the last SEVIRI observation
'''

def rgb_prerequisites(rgb, sat="meteosat", sat_nr="10", verbose=True):

    # import glob
    from mpop.satellites import GeostationaryFactory
    from my_composites import get_image

    LOG.debug("*** start rgb_prerequisites ("+inspect.getfile(inspect.currentframe())+")")

    # create an arbitrary data container
    date = datetime.datetime(2000, 12, 24, 18, 0, 0) # like christmas eve :-)
    global_data = GeostationaryFactory.create_scene(sat, sat_nr, "seviri", date)

    if type(rgb) is str:
        rgb=[rgb]

    all_channels_needed=set()
    rgb_to_do=[]

    for this_rgb in rgb:

        LOG.debug("... get prerequisite for "+this_rgb)

        if this_rgb in products.RGBs_buildin or this_rgb in products.RGBs_user:
            LOG.debug("    add prerequsites by function ")
            obj_image = get_image(global_data, this_rgb) 
            channels_needed = obj_image.prerequisites
            all_channels_needed = all_channels_needed.union(channels_needed)

        if this_rgb in products.MSG or this_rgb in products.MSG_color: 
            LOG.debug("    add prerequsites by name ")
            for channel in products.MSG:
                if this_rgb.find(channel) != -1: 
                    all_channels_needed = all_channels_needed.union(set([channel]))

    all_channels_needed = channel_num2str(all_channels_needed)

    return all_channels_needed


'''
input:  
  channels -> set of SEVIRI channels (strings or numbers) 
output:
  channels -> set of SEVIRI channels (strings only, unique entries)
'''

def channel_num2str(channels):

    i=0 
    channels=list(channels)
    for channel in channels:
        if type(channel) is float:
            if channel == 0.635:
                channels[i] = 'VIS006'
            elif channel == 0.8:         # sometimes this number is used
                channels[i] = 'VIS008'
            elif channel == 0.85:        # but most of the times this 
                channels[i] = 'VIS008'
            elif channel == 1.63:
                channels[i] = 'IR_016'
            elif channel == 3.75:        # sometimes this number is used
                channels[i] = 'IR_039'
            elif channel == 3.9:         # and sometimes this
                channels[i] = 'IR_039'
            elif channel == 6.7:
                channels[i] = 'WV_062'
            elif channel == 7.3:
                channels[i] = 'WV_073'
            elif channel == 8.7:
                channels[i] = 'IR_087'
            elif channel == 9.7:
                channels[i] = 'IR_097'
            elif channel == 10.8:
                channels[i] = 'IR_108'
            elif channel == 12.0:
                channels[i] = 'IR_120'
            elif channel == 13.4:
                channels[i] = 'IR_134'
            else:
                LOG.critical("*** ERROR (A) in channel_num2str ("+inspect.getfile(inspect.currentframe())+"), channel = "+channel)
                LOG.critical("*** This should not happen, please contact the developers (Ulrich H., Lorenzo C., Marco S.)")
                quit()
        elif type(channel) is str:
            # nothing to do
            LOG.debug("    channel is already a string, do nothing ")
        else:
            LOG.critical("*** ERROR (B) in channel_num2str ("+inspect.getfile(inspect.currentframe())+"), channel = "+channel)
            LOG.critical("*** This should not happen, please contact the developers (Ulrich H., Lorenzo C., Marco S.)")
            quit()
        i=i+1

    return set(channels)

'''
input:  
  channels -> SEVIRI channel (strings) 
output:
  indices -> index according to order
             VIS006, VIS008, IR_016... 
'''

def channel_str2ind(channel):

    if channel == 'VIS006':
        index=0
    elif channel == 'VIS008':
        index=1
    elif channel == 'IR_016':
        index=2
    elif channel == 'IR_039':
        index=3
    elif channel == 'WV_062':
        index=4
    elif channel == 'WV_073':
        index=5
    elif channel == 'IR_087':
        index=6
    elif channel == 'IR_097':
        index=7
    elif channel == 'IR_108':
        index=8
    elif channel == 'IR_120':
        index=9
    elif channel == 'IR_134':
        index=10
    elif channel == 'HRV':
        index=11
    else:
        LOG.critical("*** ERROR in channel_str2ind ("+inspect.getfile(inspect.currentframe())+"), channel = "+ channel)
        LOG.critical("*** This should not happen, please contact the developers (Ulrich H., Lorenzo C., Marco S.)")
        quit()

    return index

'''
input:
  date -> date you want to chosse msg satellite
          (output of datetime.datetime)
  RSS  -> Rapid Scan Service desired (True or False)
output:
  MSG number
'''

def choose_msg(date, RSS=True):

    # automatic choise of the Meteosat satellite (depending on RSS mode)
    if date <  datetime.datetime(2008, 5, 13, 0, 0):   # before 13.05.2008 only nominal MSG1 (meteosat8), no Rapid Scan Service yet
        if RSS:
            print "*** Error in choose_msg (my_msg_module.py)"
            print "    no RSS available yet for ", str(date)
            quit()
        else:
            sat_nr = 8 
    elif date <  datetime.datetime(2013, 2, 27, 9, 0): # 13.05.2008 ...  27.02.2013 
        if RSS:                       # MSG-2  (meteosat9) became nominal satellite, MSG-1 (meteosat8) started RSS
            sat_nr = 8  
        else:                       # MSG-2  (meteosat9) became nominal satellite, MSG-1 (meteosat8) started RSS
            sat_nr = 9 
      # 01.-26.02.2013 no RSS observations
    else:                                     # 27.02.2013 9:00UTC                                     
        if RSS:                      # MSG-3 (meteosat10) became nominal satellite, MSG-2 started RSS (MSG1 is backup for MSG2)
            sat_nr = 9  
        else:
            sat_nr = 10 

    return sat_nr

'''
input:
  date -> date you want to chosse msg satellite
          (output of datetime.datetime)
  RSS  -> Rapid Scan Service desired (True or False)
output:
  MSG number
'''
def choose_area_loaded_msg(sat, sat_nr, date_time):
    
   if sat=="Meteosat" or sat=="meteosat":
     if date_time > datetime.datetime(2018, 3, 1):
        # MSG4 prime satellite, MSG3 RSS, MSG2 backup, MSG1 Indian Ocean Data Coverage
        if sat_nr == 8:
           area_loaded = get_area_def("IODC")
        elif sat_nr ==  9: # rapid scan service satellite
           area_loaded = get_area_def("EuropeCanary35")  
        elif sat_nr == 10: # default satellite
           area_loaded = get_area_def("EuropeCanary95")  # full disk service, like EUMETSATs NWC-SAF products
        elif sat_nr == 11: # fake satellite for reprojected ccs4 data in netCDF
           area_loaded = get_area_def("SeviriDiskFull00")  # full disk service, like EUMETSATs NWC-SAF products        
        elif sat_nr == 0: # fake satellite for reprojected ccs4 data in netCDF
           area_loaded = get_area_def("ccs4")  # 
           #area_loaded = get_area_def("EuropeCanary")
           #area_loaded = get_area_def("alps")  # new projection of SAM
        else:
          print "*** Error (A), unknown satellite number ", sat_nr, "in plot_msg (plot_msg.py)"
          area_loaded = get_area_def("hsaf")  # 
     elif date_time.year > 2012:
        if sat_nr == 8:
           area_loaded = get_area_def("EuropeCanary35")
        elif sat_nr ==  9: # rapid scan service satellite
           area_loaded = get_area_def("EuropeCanary95")  
        elif sat_nr == 10: # default satellite
           area_loaded = get_area_def("SeviriDiskFull00")  # full disk service, like EUMETSATs NWC-SAF products
        elif sat_nr == 0: # fake satellite for reprojected ccs4 data in netCDF
           area_loaded = get_area_def("ccs4")  # 
           #area_loaded = get_area_def("EuropeCanary")
           #area_loaded = get_area_def("alps")  # new projection of SAM
        else:
           print "*** Error (B), unknown satellite number ", sat_nr, "in plot_msg (plot_msg.py)"
           area_loaded = get_area_def("hsaf")  # 
     else:
        if sat_nr == 8:
           area_loaded = get_area_def("EuropeCanary95") 
        elif sat_nr ==  9: # default satellite
           area_loaded = get_area_def("EuropeCanary")
   elif sat=="cosmo":
     area_loaded = get_area_def("ccs4") # might be different, depending on product
   elif sat=="swissradar":
     area_loaded = get_area_def("ccs4") # might be different, depending on product
   else:
     area_loaded = None

   return area_loaded
     
'''
input:
  MSG number 
  date -> date you want to chosse msg satellite
          (output of datetime.datetime)
output:
  Rapid Scan Service (True or False)
'''

def check_RSS(sat_nr, date):

    LOG.info("*** start check_RSS ("+inspect.getfile(inspect.currentframe())+")")
    LOG.info("    automatic check if Metesat"+str(sat_nr)+" works in Rapid Scan Service (RSS) mode at this time: "+str(date))

    # check if Meteosat satellite was in RSS mode
    if date <  datetime.datetime(2008, 5, 13, 0, 0):   # before 13.05.2008 only nominal MSG1 (meteosat8), no Rapid Scan Service yet
        if int(sat_nr) == 8:
            RSS = False  
        else:
            RSS = None 
    elif date <  datetime.datetime(2013, 2, 27, 9, 0): # 13.05.2008 ...  27.02.2013 
        if int(sat_nr) == 9:                       # MSG-2  (meteosat9) became nominal satellite, MSG-1 (meteosat8) started RSS
            RSS = False 
        elif int(sat_nr) == 8:
            RSS = True 
        else:                       # MSG-2  (meteosat9) became nominal satellite, MSG-1 (meteosat8) started RSS
            RSS = None 
      # 01.-26.02.2013 no RSS observations
    elif date <  datetime.datetime(2018, 3, 9, 0, 0): # 27.02.2013 ... 09.03.2013
        if int(sat_nr) == 10:                       # MSG-2  (meteosat9) became nominal satellite, MSG-1 (meteosat8) started RSS
            RSS = False 
        elif int(sat_nr) == 8 or int(sat_nr) == 9:
            RSS = True 
        else:                       # MSG-2  (meteosat9) became nominal satellite, MSG-1 (meteosat8) started RSS
            RSS = None 
      # 01.-26.02.2013 no RSS observations      
    else:                                     # 09.03.2013 ...                                    
        if int(sat_nr) == 11:                      # MSG-3 (meteosat10) became nominal satellite, MSG-2 started RSS (MSG1 is backup for MSG2)
            RSS = False
        elif int(sat_nr) == 9 or int(sat_nr) == 10:
            RSS = True 
        elif int(sat_nr) == 8:
            print "*** Attention!!!: This is Indian Ocean Data Coverage ***"
            print "*** Attention!!!: This is Indian Ocean Data Coverage ***"
            RSS = True 
        else:
            RSS = None 

    LOG.info("... Rapid Scan Service (RSS) mode = "+str(RSS))

    return RSS


'''
input:
  directory or filename including placeholders
output:
  directory or filename with replaced placeholders
'''

def format_name (folder, time_slot, rgb=None, sat=None, sat_nr=None, RSS=None, area=None, product=None ):

    # replace time placeholders like %Y%m%d%H%M
    new_folder = time_slot.strftime(folder)

    if rgb is not None:
        #new_folder = (new_folder % {"rgb": rgb.replace("_","-")})
        new_folder = new_folder.replace("%(rgb)s",rgb.replace("_","-"))

    if area is not None:
        #new_folder = (new_folder % {"area": area})
        new_folder = new_folder.replace("%(area)s", area)

    if sat is not None:
        #new_folder = (new_folder % {"msg": "MSG"+str(int(sat_nr)-7)})
        new_folder = new_folder.replace("%(sat)s", sat )

    if (sat_nr is not None) and sat_nr != "":
        #print "... replace sat_nr", sat_nr
        #new_folder = (new_folder % {"msg": "MSG"+str(int(sat_nr)-7)})
        new_folder = new_folder.replace("%(msg)s", "MSG-"+str(int(sat_nr)-7))
        new_folder = new_folder.replace("%(sat_nr)s", str(int(sat_nr)) )  # get rid of leading 0
    else:
        new_folder = new_folder.replace("%(msg)s", "MSG")
    
    if RSS == True:
        new_folder = new_folder.replace("%(RSS)s", "RSS")
    else:
        new_folder = new_folder.replace("%(RSS)s", "___")

    if product is not None:
        #new_folder = (new_folder % {"product": product})
        new_folder = new_folder.replace("%(product)s", str(product))

    new_folder = new_folder.replace("IR10.8", "IR-108")
        
    return new_folder

'''
input:
  rgb [string] or [string array]  -> rgb (or array of rgb) you want to check for the existence of the input files
  data -> satellite scene created by GeostationaryFactory.create_scene
output:
  True -> if all prerequisits are loaded  
  False otherwise  
'''

def check_loaded_channels(rgbs, data):

    from my_composites import get_image

    print "... check if all needed channels are loaded for ", rgbs

    # check if all prerequisites are loaded
    all_loaded = True
    loaded_channels = [chn.name for chn in data.loaded_channels()]

    # replace string with one element string array
    if isinstance(rgbs, str):
        rgbs = [rgbs]

    if (type(rgbs) is not list):
        print "*** Error in check_loaded_channels" 
        print "    unknown type for rgbs ", type(rgbs), rgbs
        quit()

    for rgb in rgbs:
 
        if rgb in products.RGBs_buildin or rgb in products.RGBs_user:
            obj_image = get_image(data, rgb)
            for pre in channel_num2str(obj_image.prerequisites):
                if pre not in loaded_channels:
                    print "*** Warning: missing channel ", pre, ", skip ", rgb
                    all_loaded = False
        elif rgb in products.MSG_color:
            if rgb.replace("c","") not in loaded_channels:
                print "*** Warning: missing channel ", rgb.replace("c",""), ", skip ", rgb
                all_loaded = False
        else:
            if rgb not in loaded_channels:
                print "*** Warning: missing channel ", rgb, ", skip ", rgb
                all_loaded = False

    return all_loaded


'''
input:
  rgb  -> rgb  you want to check for the existence of the input files
  RSS  -> logical (True == rapid scan service, False full disk service)
          default True
  date -> date you want to check for the existence of the input files
          (output of datetime.datetime)
          default last MSG image
  sat_nr -> number of the meteosat satellite (8, 9 or 10)
          default according to date and RSS
  segments   -> specify numbers of segments you need
  HRsegments -> specify numbers of HRV segments you need
  verbose -> logical (True == more output on the sceen, False == Quiet)  
output:
  rgb  -> rgbs where all segments are available 
'''

def check_input(in_msg, fullname, time_slot, RGBs=None, segments=[6,7,8], HRsegments=[20,21,22,23]):
                #rgb, RSS=True, date=None, sat_nr=None, segments=[6,7,8], HRsegments=[18,19,20,21,22,23,24],verbose=True):

    from time import strftime
    from my_msg_module import get_last_SEVIRI_date, choose_msg, channel_str2ind
    from ConfigParser import ConfigParser
    import os
    from mpop import CONFIG_PATH
    #from fnmatch import filter
    #from os import listdir  # , path, access, R_OK
    import glob

    # get date of the last SEVIRI observation
    if in_msg.datetime is None:
        in_msg.datetime = get_last_SEVIRI_date(in_msg.RSS)

    yearS   = str(in_msg.datetime.year)
    monthS  = "%02d" % in_msg.datetime.month
    dayS    = "%02d" % in_msg.datetime.day
    hourS   = "%02d" % in_msg.datetime.hour 
    minuteS = "%02d" % in_msg.datetime.minute
    
    sat="MSG"
    #if in_msg.RSS:
    #    RSSS='RSS'
    #else:
    #    RSSS='___'
    RSSS='???'

    print in_msg.check_input

    # choose MSG satellite
    if in_msg.sat_nr is None:
        in_msg.sat_nr = choose_msg(in_msg.datetime, RSS=in_msg.RSS)

    ## currently no check for hdf data
    if in_msg.reader_level == "seviri-level4":
       return in_msg.RGBs
    ## currently no check for viewing geometry   
    if in_msg.reader_level == "seviri-level6":
       return in_msg.RGBs
    ## currently no check for netCDF data   
    if in_msg.reader_level == "seviri-level8":
       return in_msg.RGBs
    ## currently no check for (parallax corrected) netCDF data   
    if in_msg.reader_level == "seviri-level9":
       return in_msg.RGBs
    ## currently no check for cpp
    if in_msg.sat == "cpp":
       return in_msg.RGBs
    ## currently no check for overshooting tops
    if in_msg.sat == "msg-ot":
       return in_msg.RGBs
       ## currently no check for cosmo data
    if in_msg.sat == "cosmo":
       return in_msg.RGBs

    ## check all RGBs, if not some are defined explecitly
    if RGBs is None:
        RGBs = in_msg.RGBs

    # convert str to array, if only one string is given
    if type(RGBs) is str:
        RGBs = [RGBs]

    needed_input=deepcopy(RGBs)
    if in_msg.parallax_correction:
        needed_input.append('CTH')
        
    rgb_complete=[]
    channels_complete=[False,False,False,False,False,False,False,False,False,False,False,False]
    pro_file_checked=False

    print "... read config file ", os.path.join(CONFIG_PATH, fullname + ".cfg")
    print "... use satellite "+in_msg.sat_str()

    for rgb in needed_input:

        if in_msg.verbose:
            print "... check input for ", rgb

        if rgb in products.MSG or rgb in products.MSG_color or rgb in products.RGBs_buildin or rgb in products.RGBs_user:

            conf = ConfigParser()
            conf.read(os.path.join(CONFIG_PATH, fullname + ".cfg"))
            inputDirectory = time_slot.strftime(conf.get("seviri-level1", "dir"))
            #inputDirectory='/data/OWARNA/hau/database/meteosat/radiance/2014/11/04/'
            #inputDirectory="/data/cinesat/in/eumetcast1/"

            if in_msg.verbose:
                print '... check input in directory '+inputDirectory

            if not pro_file_checked:

                #check prologues file 
                pro_file_checked=True
                sat_nr_org = deepcopy(in_msg.sat_nr)
                there_is_no_backup_satellite = False

                while in_msg.sat_nr > 7:

                    # update pro_file with new sat_nr and search for prolog files
                    MSG = in_msg.msg_str(layout="%(msg)s%(msg_nr)s")
                    if in_msg.verbose:
                        print "... check input files for ", MSG, str(in_msg.datetime), in_msg.RGBs
                    #pro_file = "?-000-"+MSG+"__-"+MSG+"_"+RSSS+"_???-_________-PRO______-"+yearS+monthS+dayS+hourS+minuteS+"-__"
                    inputDirectory = time_slot.strftime(conf.get("seviri-level1", "dir"))
                    pro_file = time_slot.strftime(conf.get("seviri-level1", "filename_pro"))
                    #if len(filter(listdir(inputDirectory), pro_file)) == 0:
                    pro_filename = glob.glob(inputDirectory+'/'+pro_file)

                    if len(pro_filename) > 0:
                        print "    found prologue file ", pro_filename
                        break  # prologue file found, break this loop and check if epilog is there
                    else:
                        if there_is_no_backup_satellite:
                            # reset sat_nr and return empty rgb_complete
                            in_msg.sat_nr = sat_nr_org 
                            if in_msg.verbose:
                                print "*** Warning, no prolog file found, cannot process anything"
                            return []  # rgb_complete is empty 
                        else:
                            # try backup satellite
                            if in_msg.verbose:
                                print "*** Warning, no prologue file found for Meteosat ",in_msg.sat_nr ," : "+inputDirectory+'/'+pro_file
                            # before July 2016: Meteosat 8 is RSS backup for Meteosat 9, but also try Meteosat 10 if possible
                            if in_msg.datetime < datetime.datetime(2016, 7, 1, 0, 0): 
                                if in_msg.sat_nr == 9:
                                    in_msg.sat_nr = 8
                                    fullname = in_msg.sat_str(layout="%(sat)s")+in_msg.sat_nr_str()
                                    conf.read(os.path.join(CONFIG_PATH, fullname + ".cfg"))
                                    if in_msg.verbose:
                                        print "... try backup satellite ", in_msg.sat_nr
                                elif in_msg.sat_nr == 8:
                                    in_msg.sat_nr = 10
                                    fullname = in_msg.sat_str(layout="%(sat)s")+in_msg.sat_nr_str()
                                    conf.read(os.path.join(CONFIG_PATH, fullname + ".cfg"))
                                    if in_msg.verbose:
                                        print "... try backup satellite ", in_msg.sat_nr
                                elif in_msg.sat_nr == 10:
                                    there_is_no_backup_satellite = True  
                                else:
                                    LOG.error("*** ERROR (A), unknown Meteosat satellite number", in_msg.sat_nr, "in check_input (my_msg_module)" )
                            # after July 2016 there is no RSS backup, try if there is Meteosat 10 instead (available every 15min)
                            if in_msg.datetime < datetime.datetime(2018, 3, 3, 0, 0):
                                if in_msg.sat_nr == 9:
                                    in_msg.sat_nr = 10
                                    fullname = in_msg.sat_str(layout="%(sat)s")+in_msg.sat_nr_str()
                                    conf.read(os.path.join(CONFIG_PATH, fullname + ".cfg"))
                                    if in_msg.verbose:
                                        print "... try backup satellite ", in_msg.sat_nr
                                elif in_msg.sat_nr == 8:   # indian ocean data coverage, no backup
                                    LOG.info("*** Warning, Meteosat satellite number", in_msg.sat_nr, " is Indian Ocean Data Coverage")
                                    there_is_no_backup_satellite = True  
                                elif in_msg.sat_nr == 10:  # full disk service, no backup
                                    there_is_no_backup_satellite = True  
                                else:
                                    LOG.error("*** ERROR (B), unknown Meteosat satellite number", in_msg.sat_nr, "in check_input (my_msg_module)" )
                            #    after March 2018 MSG4 is prime, MSG3 is RSS, MSG2 is backup RSS
                            else:
                                if in_msg.sat_nr == 10:
                                    in_msg.sat_nr = 9
                                    fullname = in_msg.sat_str(layout="%(sat)s")+in_msg.sat_nr_str()
                                    conf.read(os.path.join(CONFIG_PATH, fullname + ".cfg"))
                                    if in_msg.verbose:
                                        print "... try backup satellite ", in_msg.sat_nr
                                elif in_msg.sat_nr == 9:
                                    in_msg.sat_nr = 11
                                    # change RSS
                                    # change processing time 
                                    fullname = in_msg.sat_str(layout="%(sat)s")+in_msg.sat_nr_str()
                                    conf.read(os.path.join(CONFIG_PATH, fullname + ".cfg"))
                                    if in_msg.verbose:
                                        print "... try backup satellite ", in_msg.sat_nr
                                elif in_msg.sat_nr == 11:
                                    there_is_no_backup_satellite = True  
                                elif in_msg.sat_nr == 8:
                                    LOG.info("*** Warning, Meteosat satellite number", in_msg.sat_nr, " is Indian Ocean Data Coverage")
                                    there_is_no_backup_satellite = True  
                                else:
                                    LOG.error("*** ERROR (C), unknown Meteosat satellite number", in_msg.sat_nr, "in check_input (my_msg_module)" )
                
                #check epilogues file
                #epi_file = "?-000-"+MSG+"__-"+MSG+"_???_???-_________-EPI______-"+yearS+monthS+dayS+hourS+minuteS+"-__"
                epi_file = time_slot.strftime(conf.get("seviri-level1", "filename_epi"))
                epi_filename = glob.glob(inputDirectory+'/'+epi_file)
                #if len(filter(listdir(inputDirectory), epi_file)) == 0:
                if len(epi_filename) == 0:
                    if in_msg.verbose:
                        print "*** Warning, no epilogue file found: "+inputDirectory+'/'+epi_file
                    return rgb_complete
                else:
                    print "    found epilogue file", epi_filename

            # retrieve channels needed for specific rgb
            channels_needed = rgb_prerequisites(rgb, sat=in_msg.sat_str(), sat_nr=in_msg.sat_nr_str(), verbose=False)
        
            if in_msg.verbose:
                print "    check input files for "+ rgb+ ', channels needed: ', list(channels_needed)
        
            fname1= "?-000-"+MSG+"__-"+MSG+"_???_???-"
            # channel
            fname2= "___-"
            # segements
            fname3= "___-"+yearS+monthS+dayS+hourS+minuteS+"-C_"
        
            input_complete = True
            input_any = False
            for channel in channels_needed:
                if not channels_complete[channel_str2ind(channel)]:
                    # print "... search input files of ", channel
                    if channel != "HRV":
                        all_segments=''
                        for seg in segments:
                            all_segments=all_segments+str(seg)
                        all_segments='['+all_segments+']'
                        search_pattern=fname1+channel+fname2+"00000"+all_segments+fname3
                        #print "    search pattern: ", search_pattern
                        #for this_file in filter(listdir(inputDirectory), search_pattern):
                        #    print this_file
                        #    print path.isfile(inputDirectory+this_file), access(inputDirectory+this_file, R_OK)
                        #n_files = len(filter(listdir(inputDirectory), search_pattern))
                        n_files = len(glob.glob(inputDirectory+'/'+search_pattern))
        
                        if in_msg.check_input:
                            if n_files != len(segments):     # we like to have all segments
                                input_complete=False
                        else:
                            if n_files < 1:                  # we are happy with at least one segment
                                input_complete=False
        
                        if in_msg.verbose:
                            if input_complete==False:
                                print "*** Warning, input not complete for "+channel+ ' ('+rgb+')'
                                print "***          found only "+str(n_files)+" input segments (expected "+str(len(segments))+ " segments)"
                            #else:
                            #   print '    input complete for '+channel+ ' ('+rgb+')'+' '+search_pattern
                    else:

                        for seg in HRsegments:
                            segS = "%02d" % seg
                            search_pattern=fname1+"HRV___"+fname2+"0000"+segS+fname3
                            #n_files = len(filter(listdir(inputDirectory), search_pattern))
                            n_files = len(glob.glob(inputDirectory+'/'+search_pattern))
                            if n_files == 0:
                                input_complete=False
                                if in_msg.verbose:
                                    print "*** Warning, missing file: " + search_pattern
    
                            elif n_files == 1:
                                input_any = True
                            #    if in_msg.verbose:
                            #        print "    found file: ", fname1+"HRV___"+fname2+"0000"+segS+fname3
                
                            if n_files != 0 and n_files != 1:
                                print "*** ERROR in check_input (my_msg_module.py)"
                                print "*** ERROR this should not happen, please contact the developers (Uli, Lorenzo)"
                            search_pattern=''

                        # if we are not checking (for all segments)
                        if not in_msg.check_input:         # ... we are happy with at least one segment
                            if input_any == True:
                                input_complete=True

                #else:
                #    if in_msg.verbose:
                #        print "    input for channel "+channel+" is already checked and complete"
        
                # remember channels that are complete
                if input_complete:
                    channels_complete[channel_str2ind(channel)]=True
        
                if in_msg.verbose:
                    if input_complete:
                        print '    input complete for '+channel+ ' ('+rgb+')' #+' '+search_pattern
                    else:
                        print "*** Warning, input not complete for "+channel+ ' ('+rgb+')'
        
                if input_complete == False:
                    break
        
            if input_complete:
                rgb_complete.append(rgb)

        elif rgb in products.NWCSAF:

            conf = ConfigParser()
            conf.read(os.path.join(CONFIG_PATH, fullname + ".cfg"))
            inputDirectory = time_slot.strftime(conf.get("seviri-level3", "dir"))

            filename = time_slot.strftime(conf.get("seviri-level3", "filename", raw=True))
            #    #e.g. SAFNWC_MSG?_%(product)s%Y%m%d%H%M_FES_*
            pathname = os.path.join(inputDirectory, filename)

            if rgb in products.CMa:
                filename = (pathname % {"number": "01", "product": "CMa__"})
            elif rgb in products.CT:
                filename = (pathname % {"number": "02", "product": "CT___"})
            elif rgb in products.CTTH:
                filename = (pathname % {"number": "03", "product": "CTTH_"})
            elif rgb in products.PC:
                filename = (pathname % {"number": "04", "product": "PC___"})
            elif rgb in products.CRR:
                filename = (pathname % {"number": "05", "product": "CRR__"})
            elif rgb in products.SPhR:
                filename = (pathname % {"number": "13", "product": "SPhR_"})
            elif rgb == 'PCPh':
                filename = (pathname % {"number": "14", "product": "PCPh_"})
            elif rgb == 'CRPh':
                filename = (pathname % {"number": "14", "product": "CRPh_"})
            else:
                print "*** ERROR in check_input (my_msg_module.py)"
                print "    unknown NWC-SAF product ", rgb
                quit()

            print "... search for ", filename

            if len(glob.glob(filename)) == 0:
                if in_msg.verbose:
                    print "*** Warning, no NWC SAF file found: "+filename

                # if parallax correction is desired and there is not CTH,
                # tell main program that no images can be produced
                if in_msg.parallax_correction and rgb=='CTH':
                    return []
            else:
                print "    NWC SAF file found: "+glob.glob(filename)[0]
                rgb_complete.append(rgb)

        elif rgb in products.HSAF:
            
            from mpop.satin.hsaf_h03 import find_hsaf_files
            filenames = find_hsaf_files(time_slot, fullname)
            
            if len(filenames) == 0:
                LOG.info("*** Warning, no HSAF input file found")
            else:
                LOG.info("    HSAF file found: "+filenames[0])
                rgb_complete.append(rgb)
                
        else:
           # currently no check, just append rgb and try to process it
           rgb_complete.append(rgb)

    return rgb_complete


''' returns the Nowcasting SAF product generation element (pge) name '''
def get_NWC_pge_name(rgb):

    if rgb in products.CMa:
        pge = "CloudMask"
    elif rgb in products.CT:
        pge = "CloudType"
    elif rgb in products.CTTH:
        pge = "CTTH"
    elif rgb in products.PC:
        pge = "PC"
    elif rgb in products.CRR:
        pge = "CRR_"
    elif rgb in products.SPhR:
        pge = "SPhR"
    elif rgb == "PCPh":
        pge = "PCPh_"
    elif rgb == "CRPh":
        pge = "CRPh_"

    else:
        print "*** Error in get_NWC_pge_name (my_msg_module.py)"
        print "    unknown NWC-SAF product", rgb
        quit()

    return pge

'''
input:
  rgb  -> rgb  you want to check for the existence of the input files
  RSS  -> logical (True == rapid scan service, False full disk service)
          default True
  date -> date you want to check for the existence of the input files
          (output of datetime.datetime)
          default last MSG image
  sat_nr -> number of the meteosat satellite (8, 9 or 10)
          default according to date and RSS
  segments   -> specify numbers of segments you need
  HRsegments -> specify numbers of HRV segments you need
  verbose -> logical (True == more output on the sceen, False == Quiet)  
output:
  rgb  -> rgbs where all segments are available 
'''

def convert_NWCSAF_to_radiance_format(satscene, area, rgb, nwcsaf_calibrate, IS_PYRESAMPLE_LOADED):

    import numpy.ma as ma
    from numpy import ndarray
    from mpop.channel import Channel

    print "    convert ", rgb, " to the normal format of a radiance/brightness temperature data set"

    pge = get_NWC_pge_name(rgb)

    palette = None
    no_data = 0
    if rgb == 'CMa':
        prop = satscene[pge].CMa
        units= '0 Non-processed, 1 Cloud-free, 2 Cloud contaminated, 3 Cloud filled, 4 Snow/Ice contaminated, 5 Undefined'
        palette = satscene[pge].CMa_palette
    elif rgb == 'CMa_DUST':
        prop = satscene[pge].CMa_DUST
        units= '(no units)'
        palette = satscene[pge].CMa_DUST_palette
    elif rgb == 'CMa_QUALITY':
        prop = satscene[pge].CMa_QUALITY
        units= '(no units)'
    elif rgb == 'CMa_TEST':
        prop = satscene[pge].CMa_TEST
        units= '(no units)'
    elif rgb == 'CMa_VOLCANIC':
        prop = satscene[pge].CMa_VOLCANIC
        units= '(no units)'
        palette = satscene[pge].CMa_VOLCANIC_palette
    elif rgb == 'CT':
        prop = satscene[pge].cloudtype
        palette = satscene[pge].cloudtype_palette
        units= '(no units)'
    elif rgb == 'CT_PHASE':
        prop = satscene[pge].cloudphase
        palette = satscene[pge].cloudphase_palette
        units= '(no units)'
    elif rgb == 'CT_QUALITY':
        prop = satscene[pge].processing_flags
        units= '(no units)'
    elif rgb == 'CTT':
        prop = satscene["CTTH"].temperature    # <class 'numpy.ma.core.MaskedArray'>
        palette = satscene["CTTH"].temperature_palette
        units='K'
        if nwcsaf_calibrate:
           no_data = 150.0
    elif rgb == 'CTP':
        prop = satscene[pge].pressure       # <class 'numpy.ma.core.MaskedArray'>
        palette = satscene[pge].pressure_palette
        units='hPa'
    elif rgb == 'CTH':
        prop = satscene[pge].height         # <class 'numpy.ma.core.MaskedArray'>
        palette = satscene[pge].height_palette
        units= 'm'
        no_data = -2000.0
    elif rgb == 'PC':
        prop    = satscene[pge].probability_1.data
        palette = satscene[pge].probability_1_palette
        units= '%'
    elif rgb == 'CRR':
        prop = satscene[pge].crr         # <class 'numpy.ma.core.MaskedArray'>
        palette = satscene[pge].crr_palette
        units= 'l / (m2 h)'
    elif rgb == 'CRR_ACCUM':
        prop = satscene[pge].crr_accum         # <class 'numpy.ma.core.MaskedArray'>
        palette = satscene[pge].crr_accum_palette
        units= 'l / (m2 h)'
    elif rgb == 'crr_intensity':
        prop = satscene[pge].crr_intensity         # <class 'numpy.ma.core.MaskedArray'>
        palette = satscene[pge].crr_intensity_palette
        units= 'unknown'
    elif rgb in products.SPhR:
#        from mpop.satin.nwcsaf_msg import MsgSPhRData
        prop = getattr(satscene[pge], rgb)
        if hasattr(satscene[pge], rgb+"_palette"):
            palette = getattr(satscene[pge], rgb+"_palette")
        if products.old_sphr_format:
            SPhR_units={'SPhR_BL':'kg/m2', 'SPhR_CAPE':'J/kg', 'SPhR_HL':'kg/m2', 'SPhR_KI':'K', 'SPhR_LI':'K',
                        'SPhR_ML':'kg/m2', 'SPhR_QUALITY':'(no units)', 'SPhR_SHW':'K', 'SPhR_TPW':'kg/m2'}
        else:
            SPhR_units={'sphr_bl':'kg/m2', 'sphr_cape':'J/kg', 'sphr_diffbl':'kg/m2','sphr_diffhl':'kg/m2','sphr_diffki':'K','sphr_diffli':'K','sphr_diffml':'kg/m2',\
                        'sphr_diffshw':'K','sphr_difftpw':'kg/m2','sphr_hl':'kg/m2','sphr_ki':'K','sphr_li':'K','sphr_ml':'kg/m2','sphr_quality':'(no units)',\
                        'sphr_sflag':'(no units)','sphr_shw':'K','sphr_tpw':'kg/m2'}
        units=SPhR_units[rgb]
    elif rgb == "PCPh":
        prop = satscene[pge].pcph_pc         # <class 'numpy.ma.core.MaskedArray'>
        palette = satscene[pge].pcph_pc_palette
        units= '%'
    elif rgb == "CRPh":
        prop = satscene[pge].crph_crr         # <class 'numpy.ma.core.MaskedArray'>
        palette = satscene[pge].crph_pc_palette
        units= 'l / (m2 h)'
    else:
        print "*** ERROR in my_msg_module, unknown rgb: ", rgb
        quit()
  

    #print "    prop.shape: ", prop.shape
    #print "    dir(satscene[pge])", dir(satscene[pge])
    #print "    satscene[pge].num_of_columns", satscene[pge].num_of_columns
    #print "    satscene[pge].num_of_lines", satscene[pge].num_of_lines
    #print "    satscene[pge].area", satscene[pge].area
    #print "    satscene[pge].area_def", satscene[pge].area_def
    #print "    satscene[pge].shape", satscene[pge].shape
    #print "    dir(satscene[pge].info)", dir(satscene[pge].info)
    #print "    satscene[pge].is_loaded", satscene[pge].is_loaded
    #print "    satscene[pge].product_name", satscene[pge].product_name

    if isinstance(prop, ndarray): # normal array as CT
        data = ma.asarray(prop)
        print "(my_msg_module) Mask NWCSAF array (org: unmasked numpy array), min/max = ", prop.min(), prop.max(), ', no_data = ', no_data 
        data.mask = (data == no_data) # create mask 
    elif isinstance(prop, ma.core.MaskedArray):
        data = ma.asarray(prop.data)  # already a masked array
        print "(my_msg_module) Mask NWCSAF array (org: masked array), min/max:", prop.data.min(), prop.data.max(), ', no_data = ', no_data 
        data.mask = (data == no_data) # create mask 
#    elif isinstance(prop, MsgSPhRData):
#        data = ma.asarray(prop.data)  # already a masked array
#        print "(my_msg_module) min/max B2", prop.data.min(), prop.data.max()
#        data.mask = (data == no_data) # create mask         
    else:
        print "*** ERROR, unknown data format", type(prop)
        quit()

    print "... append ", rgb, satscene[pge].resolution, data.min(), data.max() 
    if units is None:
        satscene.channels.append(Channel(name=rgb,
                                         wavelength_range=[0.,0.,0.],
                                         resolution=satscene[pge].resolution, 
                                         data=data))
    else:
        satscene.channels.append(Channel(name=rgb,
                                         wavelength_range=[0.,0.,0.],
                                         resolution=satscene[pge].resolution, 
                                         data=data,
                                         calibration_unit=units))

    #print rgb
    print '(my_msg_module) min/max: ', satscene[rgb].data.min(), satscene[rgb].data.max()

    # satscene[rgb].data = data
    satscene[rgb].info['satname'] = satscene.satname
    satscene[rgb].info['satnumber'] = satscene.number
    satscene[rgb].info['instrument_name'] = satscene.instrument_name
    satscene[rgb].info['time'] = satscene.time_slot
    satscene[rgb].info['units'] = units
    #for key, value in satscene[rgb].info.items():
    #    print (key), satscene[rgb].info[key]

    #quit()

    satscene[rgb].area = satscene[pge].area
    satscene[rgb].area_def = satscene[pge].area_def
    
    if palette is not None:
        if palette.size > 0:
            print "(my_msg_module) copy palette for ", rgb
            satscene[rgb].palette = palette
            #print "(my_msg_module) palette ", palette
        else:
            print "*** Warning, empty palette"

    #if IS_PYRESAMPLE_LOADED:
    #
    #    from pyresample import geometry
    #
    #    # Build an area on the fly from the mipp metadata
    #    proj_params = area.proj4_string.split(" ")
    #    proj_dict = {}
    #    for param in proj_params:
    #        key, val = param.split("=")
    #        proj_dict[key.replace("+","")] = val
    #        #print key.replace("+",""), val
    #        # Build area_def on-the-fly
    #    satscene[rgb].area = geometry.AreaDefinition(
    #        satscene.satname + satscene.instrument_name +
    #        str(area.area_extent).replace("(","[").replace(")","]") +
    #        str(prop.shape),
    #        "On-the-fly area",
    #        proj_dict["proj"],
    #        proj_dict,
    #        prop.shape[1],
    #        prop.shape[0],
    #        area.area_extent)
    #    print "(plot_msg.py) satscene[rgb].area: ", satscene[rgb].area
    #    #Area ID: meteosatseviri[-4823148.08905083  1969764.67835886  4178061.40840017  5570248.47733926](1200, 3000)
    #    #Name: On-the-fly area
    #    #Projection ID: geos
    #    #Projection: {'a': '6378169.00', 'b': '6356583.80', 'h': '35785831.00', 'lat_0': '0.00', 'lon_0': '9.50', 'proj': 'geos'}
    #    #Number of columns: 3000
    #    #Number of rows: 1200
    #    #Area extent: (-4823148.0890508275, 1969764.6783588605, 4178061.4084001728, 5570248.4773392612)
    #
    #else:
    #    LOGGER.warning("pyresample missing. Can only work in satellite projection")
    #    print "*** Error, pyresample missing"


"""
returns SEVIRI viewing geometry 
vza: viewing zenith  angle 
vaa: viewing azimuth angle """

def read_SEVIRI_viewing_geometry(lon0, folder):

    ### the Scientific Python netCDF 3 interface
    ### http://dirac.cnrs-orleans.fr/ScientificPython/
    from Scientific.IO.NetCDF import NetCDFFile as Dataset 

    # the 'classic' version of the netCDF4 python interface
    # http://code.google.com/p/netcdf4-python/
    # from netCDF4_classic import Dataset
    from numpy import arange # array module from http://numpy.scipy.org
    from numpy.testing import assert_array_equal, assert_array_almost_equal

    lon0_str = '{0:02d}'.format(int(10*lon0))
    ncfile_str = folder+'/MSG_SEVIRI_lon'+lon0_str+'_geometry.nc'
    print ncfile_str

    ncfile = Dataset(ncfile_str,'r') 
    # ncfile = Dataset('/data/COALITION2/database/meteosat/SEVIRI/MSG_SEVIRI_lon00_geometry.nc','r') 

    # read the data in variable named 'vza'.
    vza = ncfile.variables['vza'][:]
    vaa = ncfile.variables['vaa'][:]

    print type(vza)
    print vza.shape

    ## check the data.
    #for data in vza: # [vza, vaa]
    #    nx,ny = data.shape
    #    vza_check = arange(nx*ny) # 1d array
    #    vza_check.shape = (nx,ny) # reshape to 2d array
    #    try:
    #        assert_array_equal(data, data_check)
    #        print '*** SUCCESS reading example file '+ncfile
    #    except:
    #        print '*** FAILURE reading example file '+ncfile

    # close the file.
    ncfile.close()
    
    from numpy.ma import masked_array
    import matplotlib.pyplot as plt

    mvza = masked_array(vza)
    mvza.mask = (mvza == 999.0)
    #plt.imshow(mvza)
    #plt.colorbar()
    #plt.show()

    mvaa = masked_array(vaa)
    mvaa.mask = (mvaa == 999.0)
    plt.imshow(mvaa)
    plt.colorbar()
    plt.show()

    from trollimage.colormap import rainbow
    colormap = rainbow
    min_data = mvaa.min()
    max_data = mvaa.max()
    colormap.set_range(min_data, max_data)

    from trollimage.image import Image as trollimage
    img = trollimage(mvaa, mode="L", fill_value=[0,0,0])
    img.colorize(colormap)
    img.show()
    #img.save("test_vaa.png")
    #print "display test_vaa.png &"

    return [vza, vaa] 

# ------------------------------------------
# copied from http://stackoverflow.com/questions/3662361/fill-in-missing-values-with-nearest-neighbour-in-python-numpy-masked-arrays

def fill_with_closest_pixel(data, invalid=None):
    """
    Replace the value of invalid 'data' cells (indicated by 'invalid') 
    by the value of the nearest valid data cell

    Input:
        data:    numpy array of any dimension
        invalid: a binary array of same shape as 'data'. True cells set where data
                 value should be replaced.
                 If None (default), use: invalid  = np.isnan(data)

    Output: 
        Return a filled array. 
    """

    from numpy import isnan 
    from scipy.ndimage import distance_transform_edt

    if invalid is None: invalid = isnan(data)

    ind = distance_transform_edt(invalid, return_distances=False, return_indices=True)

    return data[tuple(ind)]

# ------------------------------------------
def ContourImage(prop, area, clevels=[0.0], vmin=None, vmax=None, alpha=None, linewidths=2.0, colormap=None):

    """
    make a contour plot of the data and return a PIL image
    
    Input: 
       prop:   numpy masked array of 2 dimensions
       area:   area object
       clevel: contour levels that should be drawn
       vmin:   minimum value for colormap
       vmax:   maximum value for colormap
       alpha:  transparency (0.0 transparent, 1.0 opaque)
    """

    import matplotlib.pyplot as plt
    from numpy import arange
    from mpop.imageo.HRWimage import prepare_figure
    from mpop.imageo.TRTimage import fig2img

    import numpy as np

    (ny,nx)=prop.shape
    X, Y = np.meshgrid(range(nx), np.arange(ny-1, -1, -1))

    fig, ax = prepare_figure(area)

    prop_filled = prop.filled()

    if vmin is None:
      vmin=prop_filled.min()
    if vmax is None:
      vmax=prop_filled.max()

    if colormap is None: 
      import matplotlib.cm as cm
      colormap=cm.autumn_r

    print "... CountourImage with clevels = ", clevels, ", (vmin/vmax) =", vmin, vmax, ', alpha=', alpha

    if alpha is None: 
      CS = plt.contour(X, Y, prop.filled(), clevels, linewidths=linewidths, cmap=colormap, vmin=vmin, vmax=vmax) # , linestyles='solid'
    else:
      print "    half transparent plotting with alpha = ", alpha
      CS = plt.contour(X, Y, prop.filled(), clevels, linewidths=linewidths, cmap=colormap, vmin=vmin, vmax=vmax, alpha=alpha) 

    ## opaque higher levels 
    #clevels=[-1.6,-0.9,-0.2]
    #

    PIL_image = fig2img ( fig )

    return PIL_image

# ------------------------------------------
