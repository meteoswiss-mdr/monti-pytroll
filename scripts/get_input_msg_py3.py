from __future__ import division
from __future__ import print_function

#from __future__ import print_function

from datetime import datetime, timedelta
from my_msg_module_py3 import check_near_real_time
import sys
import inspect
import socket
from os import environ, getenv

class input_msg_class:

   def __init__(self):
      import scp_settings

      self.delay = 0
      self.datetime = None
      self.RGBs = []
      self.areas = []
      #self.sat = "meteosat"     # using the old config file: meteosat09.cfg
      self.sat = "Meteosat"      # using the new config file: Meteosat-9.cfg 
      #self.sat = "Meteosat-"      # using the new config file: Meteosat-9.cfg 
      self.sat_nr = None  # rapid scan service
      self.instrument = "seviri"
      self.fullname = ""
      self.RSS = True
      self.check_input = False
      self.reader_level = None
      self.parallax_correction = False
      self.estimate_cth=False
      self.parallax_gapfilling = 'False'
      self.save_reprojected_data = []
      self.save_statistics = False
      self.HRV_enhancement = False
      self.load_data = True
      self.make_plots = True
      self.overwrite = True           # usually overwrite existing products
      self.fill_value = None          # black (0,0,0) / white (1,1,1) / transparent None  
      self.nwcsaf_calibrate = False   # False -> dont scale to real values, plot with palette
      self.outputFormats = ['png']
      self.outputFile = 'MSG_%(rgb)s-%(area)s_%y%m%d%H%M.png'
      self.outputDir = "./%Y-%m-%d/%(rgb)s-%(area)s/"
      self.compress_to_8bit=False
      self.scpOutput = False
      self.scpOutputDir = scp_settings.scpOutputDir
      self.scpID = scp_settings.scpID
      self.scpProducts = ['all']
      self.scpOutputDir2 = None
      self.scpID2 = None
      self.scpProducts2 = []
      self.ninjotifFilename = 'MET-%(sat_nr)s_%(RSS)s_%(rgb)s_%(area)s_%Y%m%d%H%M.tif'
      self.upload_ninjotif = False  
      self.socupload = False  
      self.socuploadFilename = 'r0305n.%Y%m%d%H%M.png' 
      self.socuploadCommand = '/tools/ext/wman/custom/bin/socupload -s zuegts3,zuegts4 -f '+self.socuploadFilename+' -c LSSX'
      self.ftpUpload=False
      self.ftpProducts=[]
      self.ftpServer=None
      self.ftpUser=None
      self.ftpPassword=None
      self.mapDir = "" 
      if socket.gethostname()[0:5] == 'zueub':
         self.mapDir = "/data/OWARNA/hau/maps_pytroll/"
      elif socket.gethostname()[0:5] == 'zuerh':
         if environ.get('VENV') is not None:
            self.mapDir = getenv('VENV')+"/share/shapes/" 
            print("... use shape directory ", self.mapDir)
         else:
            self.mapDir = "/data/OWARNA/hau/maps_pytroll/"
      elif socket.gethostname()[0:7] == 'keschln' or socket.gethostname()[0:7]=="eschaln":
         self.mapDir = "/store/msrad/sat/pytroll/shapes/"
         print("... use shape directory ", self.mapDir)
      if self.mapDir == "": 
         print("*** Warning, unknown location of the shape file for unknown computer "+socket.gethostname())
         print("    please specify in the input file or produce satellite images without national borders")
      self.mapResolution = None
      self.indicate_mask = True
      self.add_title = True
      #self.title = None
      self.title = None               # ' %(sat)s, %Y-%m-%d %H:%MUTC, %(area)s, %(rgb)s'
      if socket.gethostname()[0:5] == 'zueub':
         self.font_file = "/usr/openv/java/jre/lib/fonts/LucidaTypewriterBold.ttf"
      elif socket.gethostname()[0:6] == 'zuerh4':
         self.font_file = "/usr/java/jdk1.8.0_121/jre/lib/fonts/LucidaTypewriterBold.ttf" 
      elif socket.gethostname()[0:5] == 'zuerh':
         if environ.get('VENV') is not None:
            self.font_file = getenv('VENV')+"/config_files/setup/LucidaTypewriterBold.ttf" 
            print("... use font file ", self.font_file)
         else:
            print("*** ERROR, unknown location of the ttf-file, environment variable VENV required")
            quit()
      elif socket.gethostname()[0:7] == 'keschln' or socket.gethostname()[0:7]=="eschaln":
         self.font_file = "/usr/share/fonts/dejavu/DejaVuSansMono.ttf"
      else:
         print("*** ERROR, unknown computer "+socket.gethostname()+", unknown location of the ttf-file")
         quit()
      self.title_color = None
      self.title_y_line_nr = 1        # at which line should the title be written
      self.title_color='white'
      self.add_borders = True
      self.border_color = None  # default red  for RGB images, and white for BW images
      self.add_rivers = False
      self.river_color = None   # default blue for RGB images, and white for BW images
      self.add_logos = True
      self.logos_dir = "/data/OWARNA/hau/logos/"
      if environ.get('VENV') is not None:
         self.logos_dir = getenv('VENV')+"/share/logos/"
      print("... use logo images in  ", self.logos_dir)
      self.add_colorscale = True
      self.fixed_minmax = True
      self.rad_min = {'VIS006':   0, 'VIS008':   0, 'IR_016':   0, 'IR_039': 210, 'WV_062': 210, 'WV_073': 190,\
                      'IR_087': 205, 'IR_097': 210, 'IR_108': 205, 'IR_120': 205, 'IR_134': 205, 'HRV': 0,\
                      'VIS006c':   0, 'VIS008c':   0, 'IR_016c':   0, 'IR_039c': 210, 'WV_062c': 210, 'WV_073c': 190,\
                      'IR_087c': 205, 'IR_097c': 210, 'IR_108c': 255, 'IR_120c': 205, 'IR_134c': 205, 'HRVc': 0,\
                      'CMa': 1, 'CT': 0, 'CT_PHASE': 0, 'CTH': 0, 'CTP':  100.,'CTT': 210., 'PC':0, 'CRR':0, 'clouddepth':0, 'fls':0,\
                      'WV_062-WV_073': -25, 'WV_062-IR_108': -70, 'WV_073-IR_134':-15, 'IR_087-IR_108':-4.0, 'IR_087-IR_120':-4,'IR_120-IR_108':-6,\
                      'sphr_bl': 0, 'sphr_cape': 150, 'sphr_diffbl': -1.5, 'sphr_diffhl': -0.75, 'sphr_diffki': -7, 'sphr_diffli': -2.5,\
                      'sphr_diffml': -2.5, 'sphr_diffshw': -2.5, 'sphr_difftpw': -3, 'sphr_hl': 0, 'sphr_ki': 0, 'sphr_li': -15, \
                      'sphr_ml': 0, 'sphr_quality': 0, 'sphr_sflag': 0, 'sphr_shw': -15, 'sphr_tpw': 0, 'h03': 0, 'h03b': 0, \
                      'azidiff':0,'cth':0,'cldmask':0,'cot':0,'cph':0,'ctt':210.,'cwp':0,\
                      'dcld':0,'dcot':0,'dcwp':0,'dndv':0,'dreff':0,\
                      'precip':0,'precip_ir':0,'qa':0,'reff':0,'satz':0,'sds':0,'sds_cs':0,'sds_diff':0,'sds_diff_cs':0,\
                      'vza':0,'vaa':0,'sunz':0,'sza':0,'lat':-80,'lon':-80,'time_offset':0,\
                      'ot_anvilmean_brightness_temperature_difference':0,\
                      'SYNMSG_BT_CL_IR10.8': 205,'IR_108-COSMO-minus-MSG':-40,\
                      'POH':0,'MESHS':2,'VIL':0,'MaxEcho':-32,'EchoTOP15':0,'EchoTOP20':0,'EchoTOP45':0,'EchoTOP50':0,'TRT':0}      
      self.rad_max = {'VIS006':  85, 'VIS008':  90, 'IR_016':  80, 'IR_039': 340, 'WV_062': 260, 'WV_073': 280,\
                      'IR_087': 320, 'IR_097': 285, 'IR_108': 320, 'IR_120': 320, 'IR_134': 290, 'HRV': 100,\
                      'VIS006c':  85, 'VIS008c':  90, 'IR_016c':  80, 'IR_039c': 340, 'WV_062c': 260, 'WV_073c': 280,\
                      'IR_087c': 320, 'IR_097c': 285, 'IR_108c': 295, 'IR_120c': 320, 'IR_134c': 290, 'HRVc': 100,\
                      'CMa': 4, 'CT': 21, 'CT_PHASE': 3, 'CTH': 12, 'CTP': 1000.,'CTT': 320., 'PC':100, 'CRR':10, 'clouddepth':6, 'fls':1,\
                      'WV_062-WV_073':   5,'WV_062-IR_108':    5, 'WV_073-IR_134':  5, 'IR_087-IR_108': 1.5, 'IR_087-IR_120': 4,'IR_120-IR_108': 2,\
                      'sphr_bl': 35, 'sphr_cape': 200, 'sphr_diffbl': 1.5, 'sphr_diffhl': 0.75, 'sphr_diffki': 7, 'sphr_diffli': 2.5,\
                      'sphr_diffml': 2.5, 'sphr_diffshw': 2.5, 'sphr_difftpw': 3, 'sphr_hl': 8, 'sphr_ki': 60, 'sphr_li': 25, \
                      'sphr_ml': 45, 'sphr_quality': 5000, 'sphr_sflag': 20, 'sphr_shw': 25, 'sphr_tpw': 70, 'h03': 30, 'h03b': 30, \
                      'azidiff':180,'cth':12,'cldmask':3,'cot':256,'cph':2,'ctt':320.,'cwp':10,\
                      'dcld':4,'dcot':50,'dcwp':10,'dndv':4,'dreff':20,\
                      'precip':256,'precip_ir':256,'qa':50,'reff':50,'satz':90,'sds':1200,'sds_cs':1200,'sds_diff':800,'sds_diff_cs':800,\
                      'vza':90,'vaa':360,'sunz':90,'sza':90,'lat':80,'lon':80,'time_offset':750,
                      'ot_anvilmean_brightness_temperature_difference':6,\
                      'SYNMSG_BT_CL_IR10.8': 320,'IR_108-COSMO-minus-MSG':40,\
                      'POH':100,'MESHS':6,'VIL':75,'MaxEcho':95,'EchoTOP15':16,'EchoTOP20':16,'EchoTOP45':16,'EchoTOP50':16,'TRT':3}
      self.tick_marks= {'VIS006': 20, 'VIS008': 20, 'IR_016': 20, 'IR_039': 20, 'WV_062': 20, 'WV_073': 20,\
                        'IR_087': 20, 'IR_097': 20, 'IR_108': 20, 'IR_120': 20, 'IR_134': 20, 'HRV': 20,\
                        'vza': 5, 'vaa': 5, 'lat': 5, 'lon': 5,\
                        'CTH': 4, 'CTP':  100,'CTT': 20, 'CT': 1, 'CT_PHASE': 1, 'CMa': 1, 'CMa_DUST':  1, 'CMa_TEST': 1, 'CMa_VOLCANIC': 1,\
                        'clouddepth':1, 'fls':0.5,\
                        'sphr_bl': 5, 'sphr_cape': 10, 'sphr_diffbl': 0.5, 'sphr_diffhl': 0.5, 'sphr_diffki': 2, 'sphr_diffli': 0.5,\
                        'sphr_diffml': 1, 'sphr_diffshw': 0.5, 'sphr_difftpw': 1, 'sphr_hl': 1, 'sphr_ki': 5, 'sphr_li': 1, \
                        'sphr_ml': 5, 'sphr_quality': 500, 'sphr_sflag': 1, 'sphr_shw': 1, 'sphr_tpw': 5, 'h03': 10, 'h03b': 10, \
                        'azidiff':10,'cth':1,'cldmask':1,'cot':10,'cph':1,'ctt':10.,'cwp':2,\
                        'dcld':1,'dcot':10,'dcwp':2,'dndv':1,'dreff':20,\
                        'precip':10,'precip_ir':10,'qa':10,'reff':10,'satz':10,'sds':100,'sds_cs':100,'sds_diff':100,'sds_diff_cs':100,\
                        'sunz':10,'sza':10,'lat':10,'lon':10,'time_offset':100,
                        'ot_anvilmean_brightness_temperature_difference':1,\
                        'SYNMSG_BT_CL_IR10.8': 20,'MESHS':1,\
                        'POH':10,'MESHS':0.5,'VIL':5,'MaxEcho':10,'EchoTOP15':2,'EchoTOP20':2,'EchoTOP45':2,'EchoTOP50':2,'TRT':1,
                        "TWATER":5, "tropopause_height":1000, "tropopause_temperature":5, "tropopause_pressure":20, 
                        "FF_10M":5, "VMAX_10M":5, "CAPE_MU":50, "CAPE_ML":50, "CAPE_3KM":50, "CIN_MU":20, "CIN_ML":20, 
                        "SLI":2, "LCL_ML":500, "LFC_ML":1000, "T_SO":10, "T_2M":10, "TD_2M":10, "GLOB":100, "PS":10000, 
                        "PMSL":10000, "PMSLr":50, "HZEROCL":1000, "WSHEAR_0-3km":5, "WSHEAR_0-6km":5, "SYNMSG_BT_CL_IR10.8": 20,
                        "SDI_2":0.0001, "SWISS12":5, "OMEGA":10,"W_SO":1, "SOILTYP":2}
      self.minor_tick_marks = {'VIS006': 5, 'VIS008': 5, 'IR_016': 5, 'IR_039': 5, 'WV_062': 5, 'WV_073': 5,\
                        'IR_087': 5, 'IR_097': 5, 'IR_108': 5, 'IR_120': 5, 'IR_134': 5, 'HRV': 5,\
                        'vza': 1, 'vaa': 1, 'lat': 1, 'lon': 1,\
                        'CTH': 1, 'CTP':  50,'CTT': 5, 'CT': 1, 'CT_PHASE': 1, 'CMa': 1, 'CMa_DUST':  1, 'CMa_TEST': 1, 'CMa_VOLCANIC': 1,\
                        'clouddepth':1, 'fls':0.1,\
                        'sphr_bl': 1, 'sphr_cape': 5, 'sphr_diffbl': 0.1, 'sphr_diffhl': 0.05, 'sphr_diffki': 0.5, 'sphr_diffli': 0.1,\
                        'sphr_diffml': 0.5, 'sphr_diffshw': 0.1, 'sphr_difftpw': 0.5, 'sphr_hl': 0.5, 'sphr_ki': 1, 'sphr_li': 0.5,\
                        'sphr_ml': 1, 'sphr_quality': 100, 'sphr_sflag': 1, 'sphr_shw': 0.2, 'sphr_tpw': 1, 'h03': 5, 'h03b': 5, \
                        'azidiff':2,'cth':0.2,'cldmask':1,'cot':2,'cph':1,'ctt':5.,'cwp':1,\
                        'dcld':1,'dcot':5,'dcwp':1,'dndv':1,'dreff':5,\
                        'precip':5,'precip_ir':5,'qa':2,'reff':2,'satz':2,'sds':10,'sds_cs':10,'sds_diff':10,'sds_diff_cs':10,\
                        'sunz':2,'sza':2,'lat':2,'lon':2,'time_offset':10,
                        'ot_anvilmean_brightness_temperature_difference':0.5,\
                        'SYNMSG_BT_CL_IR10.8': 5,'MESHS':0.5,\
                        'POH':5,'MESHS':0.1,'VIL':1,'MaxEcho':5,'EchoTOP15':1,'EchoTOP20':1,'EchoTOP45':1,'EchoTOP50':1,'TRT':1,
                        "TWATER":1, "tropopause_height":500, "tropopause_temperature":1, "tropopause_pressure":5, 
                        "FF_10M":1, "VMAX_10M":1, "CAPE_MU":10, "CAPE_ML":10, "CAPE_3KM":10, "CIN_MU":5, "CIN_ML":5, 
                        "SLI":0.5, "LCL_ML":100, "LFC_ML":100, "T_SO":2, "T_2M":2, "TD_2M":2, "GLOB":20, "PS":2000, 
                        "PMSL":2000, "PMSLr":10, "HZEROCL":200, "WSHEAR_0-3km":1, "WSHEAR_0-6km":1, "SYNMSG_BT_CL_IR10.8": 5,
                        "SDI_2":0.00002, "SWISS12":1, "OMEGA":2,"W_SO":0.2, "SOILTYP":1}

      self.postprocessing_areas     = []
      self.postprocessing_composite = []
      self.postprocessing_montage   = [[]]
      self.resize_composite = 100
      self.resize_montage   = 100

      self.verbose = True

      import getpass
      self.user = getpass.getuser()
      print(("*** working with username \'"+self.user+"\'"))


   def add_rgb(self, rgb):
      self.RGBs.append(rgb)

   def add_area(self, area):
      self.areas.append(area)

   def init_datetime(self, timeslot=None):
      # choose self.datetime (timeslot of the image to process)
      if timeslot==None:
         # get last possible SEVIRI observation
         self.get_last_SEVIRI_date()
      elif type(timeslot) is datetime:
         # overwrite the input file by optional argument timeslot
         self.update_datetime(timeslot.year, timeslot.month, timeslot.day, timeslot.hour, timeslot.minute)
      else:
         print(("*** ERROR in input_msg_class.init_datetime ("+inspect.getfile(inspect.currentframe())+")"))
         print(('    timeslot must be a datetime.date, not a %s' % type(timeslot)))
         raise TypeError('*** ERROR timeslot must be a datetime.date, not a %s' % type(timeslot))
         quit()

   def update_datetime(self, year, month, day, hour, minute):
      if (year is not None) and (month is not None) and (day is not None) and (hour is not None) and (minute is not None): 
         self.datetime = datetime(year, month, day, hour, minute, 0)
      else:
         print ("*** WARNING: cannot update time!")
      # first 120min are saved in the near real time archive
      self.nrt = check_near_real_time(self.datetime, 120)
      return self.datetime

   def get_last_SEVIRI_date(self):
      from my_msg_module_py3 import get_last_SEVIRI_date
      print(("... initialize date: RSS mode = ", self.RSS, ", delay = ", self.delay))
      self.datetime = get_last_SEVIRI_date(self.RSS, delay=self.delay)
      # first 120min are saved in the near real time archive
      self.nrt = check_near_real_time(self.datetime, 120)
      return self.datetime

   def check_RSS_coverage(self):
      # Warning, if large areas are wanted and RSS is specified
      if self.RSS and (('fullearth' in self.areas) or ('met09globe' in self.areas) or ('met09globeFull' in self.areas)): 
         print(("*** WARNING, large areas are requested: ", self.areas))
         print  ("    as well as rapid scan service is selected, which covers only the uppermost 1/3 of the disk")
         print  ("    (1) continue with enter")
         junk = eval(input("    (2) abort with Ctrl+c"))

   def sat_nr_str(self):
      # returns a string for the satellite number according to the convection of the satellite name
      # old convention: satellite name "meteosat", satellite numbers as string "08" and "09"
      # new convection: satellite name "Meteosat", satellite numbers as string  "8" and  "9"

      # if self.sat_nr is an integer, convert it with most appropriate rule to string
      if type(self.sat_nr) is int:
         if self.sat[0:8]=="meteosat":
            sat_nr_str = str(self.sat_nr).zfill(2)
         elif self.sat[0:8]=="Meteosat":
            sat_nr_str = str(self.sat_nr)
         else:
            sat_nr_str = str(self.sat_nr) # for unknown satellite names new convection
      # if self.sat_nr is a string, that force name convention for meteosat/Meteosat, or copy otherwise
      elif type(self.sat_nr) is str:
         if self.sat[0:8]=="meteosat":
            sat_nr_str = str(int(self.sat_nr)).zfill(2)
         elif self.sat[0:8]=="Meteosat":
            sat_nr_str = str(int(self.sat_nr)) # get rid of leading zeros (0) 
         else:
            sat_nr_str = self.sat_nr          # for unknown satellite names just copy the string
      else:
         print(("*** Error in sat_nr_str ("+inspect.getfile(inspect.currentframe())+")"))
         print(("    unknown type of sat_nr", type(self.sat_nr)))
         quit()

      if self.sat[0:8] == "Meteosat" or self.sat[0:4] == "Hsaf":
         return ""
      else:
         return sat_nr_str

   def sat_str(self, layout="%(sat)s-%(sat_nr)s"):

      """
         layout only for other satellites than meteosat
         for meteosat return "meteosat"   as needed by geostationary factory
         for Meteosat return "Meteosat-9" as needed by geostationary factory
         for others, return according to layout
      """

      if self.sat[0:8] == "meteosat":
         #print ("sat_str meteosat")
         return "meteosat"
      elif self.sat[0:8].lower() == "meteosat":
         #print ("sat_str "+"Meteosat-"+str(int(self.sat_nr)))
         return "Meteosat-"+str(int(self.sat_nr))
      elif self.sat[0:4].lower() == "hsaf":
         #print ("sat_str "+"Meteosat-"+str(int(self.sat_nr)))
         return "Hsaf-"+str(int(self.sat_nr))
      elif self.sat[0:6].lower() == "msg-ot":
         #print ("sat_str "+"Meteosat-"+str(int(self.sat_nr)))
         if layout=="%(sat)s-%(sat_nr)s":
           return "msg-ot"
         else:
           return ""
      elif self.sat[0:5].lower() == "cosmo":
         return "cosmo"
      elif self.sat == "swissradar":
         return "swissradar"
      elif self.sat == "swisstrt":
         return "swisstrt"
      else:
         if self.sat_nr != "":
           d={'sat':self.sat, 'sat_nr':str(int(self.sat_nr)), '0sat_nr':str(self.sat_nr).zfill(2)}
         else:
           d={'sat':self.sat, 'sat_nr':"", '0sat_nr':""}
         #print ("sat_str "+self.sat+str(int(self.sat_nr)))
         return layout % d

   def msg_str(self, layout="%(msg)s-%(msg_nr)s"):
      """
      general purpuse
      returns a string representing the meteosat satellite"
      optinonal input:
      layout (string) specifying the format/layout of the returned string
      possible inputs: 
          layout="%(msg)s-%(msg_nr)s"   (default)
          layout="%(msg)s-%(0msg_nr)s"  (with leading zero in for MSG numbers smaller than 10)
      """
      if self.sat[0:8]=="meteosat" or self.sat[0:8]=="Meteosat" or self.sat[0:8]=="hsaf":

         if 8 <= self.sat_nr and self.sat_nr <=11:
            d={'msg':'MSG', 'msg_nr':str(int(self.sat_nr)-7), 'sat':self.sat, 'sat_nr':str(self.sat_nr),'0sat_nr':str(self.sat_nr).zfill(2)}
            msg_str = layout % d
         else:
            print(("*** Error in msg_str ("+inspect.getfile(inspect.currentframe())+")"))
            print(("    try to get msg_string for sat number", self.sat_nr, " which is not meteosat SECOND generation "))
            quit()

      else:
         print(("*** Error in msg_str ("+inspect.getfile(inspect.currentframe())+")"))
         print(("    try to get msg_string for sat ", self.sat, " which is not Meteosat/meteosat"))
         quit()
      return msg_str

   def choose_forecast_times(self):
      if self.forecasts_in_rapid_scan_mode == False:
         self.dt_forecast1 = 15
         self.dt_forecast2 = 30
      else:
         self.dt_forecast1 = 5
         self.dt_forecast2 = 10 
      return 0

   def choose_coalistion2_settings(self, area):

      from plot_coalition2 import check_area
      from copy import deepcopy
      scale = check_area(area)

      # Settings for Switzerland (assuming that we have COSMO and NWC-SAF data as well as Rapid Scan Observation from MSG/SEVIRI
      local_settings={}
      if self.no_NWCSAF:      # (without NWC-SAF CTTH) or (without COSMO wind) no T_B forecast possible !!!
         local_settings['use_TB_forecast']        = False                   
      else:
         local_settings['use_TB_forecast']        = True
      local_settings['mode_downscaling']       = 'gaussian_225_125'
      local_settings['mask_labelsSmall_lowUS'] = True
      local_settings['clean_mask']             = 'skimage' 
      local_settings['rapid_scan_mode']        = False                 # always use 15min and 30min hindcast, as updraft is better visible
      #local_settings['forth_mask']             = 'no_mask'
      #local_settings['forth_mask']             = 'IR_039_minus_IR_108'
      #local_settings['forth_mask']             = 'IR_039_minus_IR_108_day_only'
      #local_settings['forth_mask']             = 'CloudType'
      local_settings['forth_mask']             = 'NWCSAF'
      #local_settings['forth_mask']             = 'combined'
      local_settings['forced_mask']            = 'no_mask'
      local_settings['mask_cirrus']            = True
      #local_settings['reader_level']           = "seviri-level4"
      #local_settings['reader_level']           = "seviri-level2"

      # Settings for Switzerland (assuming that we dont have COSMO and NWC-SAF data, checks if Rapid Scan Observations are available
      global_settings={}
      global_settings['use_TB_forecast']        = False                   # no NWC-SAF CTTH and COSMO wind, hence no T_B forecast possible
      global_settings['mode_downscaling']       = 'no_downscaling'
      global_settings['mask_labelsSmall_lowUS'] = False
      global_settings['clean_mask']             = 'no_cleaning'
      #global_settings['clean_mask'] = 'skimage'   # !!!  test !!!
      if self.RSS and self.sat_nr != 10:
         global_settings['rapid_scan_mode']     = True                    # use 5min and 10min forecast to minimize the bias from movement (which is not taken into account)
      else:
         global_settings['rapid_scan_mode']     = False                   # no RSS available, so chose 15min, 30min forecasts
      global_settings['forth_mask']             = 'no_mask'
      #global_settings['forth_mask']             = 'IR_039_minus_IR_108_day_only'
      #global_settings['forth_mask']             = 'CloudType'
      #global_settings['forth_mask']             = 'combined'
      global_settings['forced_mask']            = 'no_mask'
      global_settings['mask_cirrus']            = True    
      #global_settings['reader_level            = "seviri-level2"

      # FIXME: this is used in produce_forecasts_develop.py -> might be not consistent with local settings above
      self.settingsLocal={}
      self.settingsLocal['mode_downscaling'] = 'gaussian_225_125'
      
      if self.settings == "default":
         if scale == "local":
            chosen_settings  = deepcopy(local_settings)
            default_settings = deepcopy(local_settings)
         else:
            chosen_settings  = deepcopy(global_settings)
            default_settings = deepcopy(global_settings)
      else:
         chosen_settings = deepcopy(self.chosen_settings)
         if scale == "local":
            default_settings = local_settings
         else:
            default_settings = global_settings

         for key, value in chosen_settings.items():
            if value is None:
               chosen_settings[key] = deepcopy(default_settings[key])

      if scale == "broad":
         if chosen_settings['use_TB_forecast'] == True:
            print(("The area you chose ", area," is larger than the available forecast (ccs4).\n Suggestion: use only observation (set use_TB_forecast to False or None)"))
            quit()

      for key, value in chosen_settings.items():
         if value != default_settings[key]:
            print(("    WARNING: not reccomended choice: ", key, " set to ", value,". Reccomended: ", default_settings[key]))

      # switch off Rapid scan, if large areas are wanted ess' in self.aux_results
      if area in self.areasNoRapidScan and self.rapid_scan_mode==True: 
         print(("Over the area you chose ", area," there is no Rapid Scan available.\n Suggestion: set rapid_scan_mode to False"))
         quit()

      if chosen_settings['rapid_scan_mode']==True:
         chosen_settings['dt_forecast1'] = 5
         chosen_settings['dt_forecast2'] = 10
      else:
         chosen_settings['dt_forecast1'] = 15
         chosen_settings['dt_forecast2'] = 30

      chosen_settings['scale'] = scale

      #self.upload_ninjotif = True  
      #print ("set upload_ninjotif = True")
      self.modify_day_color = True
      self.indicate_sza = True

      return chosen_settings

# =====================================================================================================================


def get_input_msg(input_file):

   from os import getcwd
   from os import path

   print(("... read input file from directory:", getcwd()))

   # define input class
   in_msg = input_msg_class()
   
   # check if input file exists
   try:
      if path.getsize(input_file+".py") > 0:
         # Non empty file exists
         # get input from (user specified) file 
         input_module = __import__(input_file)
         input_module.input(in_msg)
            
         return in_msg
      else:
         # Empty file exists
         print(("*** ERROR in get_input_msg ("+inspect.getfile(inspect.currentframe())+")"))
         print(('    input file %s.py is empty' % input_file))
         quit()
   except OSError as e:
      # File does not exists or is non accessible
      print(("*** ERROR in get_input_msg ("+inspect.getfile(inspect.currentframe())+")"))
      print(('    input file %s.py does not exist' % input_file))
      quit()
      
   

# =====================================================================================================================

def get_date_and_inputfile_from_commandline(print_usage=None):

   # get command line arguments, e.g. 
   # $: python plot_msg.py input_MSG or
   # $: python plot_msg.py input_MSG 2014 07 23 16 10 or
   # $: python plot_msg.py input_MSG 2014 07 23 16 10 'IR_108' 'ccs4' or
   # $: python plot_msg.py input_MSG 2014 07 23 16 10 ['HRoverview','fog'] ['ccs4','euro4']
   # and overwrite arguments given in the initialization in get_input_msg

   if len(sys.argv) < 2:
      print_usage()
   else:
      # get input filename 
      input_file=sys.argv[1]
      if input_file[-3:] == '.py': 
         input_file=input_file[:-3]

      timeslot=None
      # check for more arguments 
      if len(sys.argv) > 2:
         if len(sys.argv) < 7:
            if print_usage is None:
                  print ("*** Error, not enough command line arguments")
            else:
               print_usage()
         else:
            year   = int(sys.argv[2])
            month  = int(sys.argv[3])
            day    = int(sys.argv[4])
            hour   = int(sys.argv[5])
            minute = int(sys.argv[6])
            # update time slot in in_msg class
            from datetime import datetime
            timeslot = datetime(year, month, day, hour, minute)

   # read input file and initialize in_msg
   in_msg = get_input_msg(input_file)

   # initialize datetime, if not yet done in the input file 
   if in_msg.datetime is None:
      # choose timeslot of the satellite picture to process
      # datetime according to command line arguments (if given)
      # otherwise the latest possible time of SEVIRI observation (depends on RSS mode and chosen delay)
      # also sets the near real time marker: in_msg.nrt
      # input: in_msg.rss and in_msg.delay 
      in_msg.init_datetime(timeslot=timeslot)
   
   return in_msg

# =====================================================================================================================

def parse_commandline():
   
   from optparse import OptionParser, Option, OptionValueError
   
   class MyOption(Option):

      # extend action to be able to convert input to list and (list of lists)
      ACTIONS              = Option.ACTIONS              + ("extend","extend_list","extend_lists",)
      STORE_ACTIONS        = Option.STORE_ACTIONS        + ("extend","extend_list","extend_lists",)
      TYPED_ACTIONS        = Option.TYPED_ACTIONS        + ("extend","extend_list","extend_lists",)
      ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend","extend_list","extend_lists",)
      
      def take_action(self, action, dest, opt, value, values, parser):
         if action == "extend":
            lvalue = value.split(",")
            values.ensure_value(dest, []).extend(lvalue)
         elif action == "extend_list":
            import re
            # convert (string representation of list) into a list
            junkers = re.compile('[[" \]]')
            lvalue = junkers.sub('', value).split(',')
            values.ensure_value(dest, []).extend(lvalue)
         elif action == "extend_lists":
            strs = value.replace('[','').split('],')
            lvalue = [ s.replace(']','').split(',') for s in strs]
            values.ensure_value(dest, []).extend(lvalue)
         else:
            Option.take_action(
               self, action, dest, opt, value, values, parser)
            
   parser = OptionParser(option_class=MyOption)
   
   #parser.add_option("-i", "--input_file", type="string", action="store")
   parser.add_option("-d", "--date", type="int", nargs=5, dest="date",\
                     help="specify the start date of measurements in following format %Y %m %d %H %M, e.g. '-d 2017 12 31 23 45'" )
   parser.add_option("--delay", type="int", action="store", dest="delay",\
                     help="specify the time difference between now and the date to process in minutes, e.g. '-delay 6'" )
   parser.add_option("-a", "--area", type="string", action="extend", dest="areas",\
                     help="specify projection of shown data, e.g. ccs4, see monti-pytroll/etc/area.def")
   parser.add_option("--parea", "--postprocessing_areas", type="string", action="extend", dest="postprocessing_areas",\
                     help="specify projection for postprocessing, e.g. ccs4, see monti-pytroll/etc/area.def")
   parser.add_option("-s", "--satellite", type="string", action="store", dest="sat",\
                     help="specify satellite name; default 'Meteosat'")
   parser.add_option("-v", "--verbose", action="store_true", dest="verbose",\
                     help="switch on verbose output")
   parser.add_option("--rss","--RSS", action="store_true", dest="RSS",\
                     help="switch on processing in rapid scan mode, e.g. search last rss time slot (each 5min); default 'True'")      
   parser.add_option("--fd","--fulldisk", action="store_false", dest="RSS",\
                     help="switch on processing in full disk mode, e.g. search last full disk slot (each 15min)")      
   parser.add_option("--rgb","--RGBs", type="string", action="extend", dest="RGBs",\
                     help="specify RGBs to process, see scripts/input_template.py, e.g. 'IR_108' or ['WV_062c','airmass']; default []")      
   parser.add_option("--scp", action="store_true", dest="scpOutput",\
                     help="switch on secure copy to remote computer")
   parser.add_option("--no_scp", action="store_false", dest="scpOutput",\
                     help="switch off secure copy to remote computer")
   parser.add_option("--add_title", action="store_true",  dest="add_title", help="show title in image")
   parser.add_option("--no_title",  action="store_false", dest="add_title", help="show no title in image")
   parser.add_option("-t", "--title", type="string", action="store", dest="title",\
                     help="specify a title, possible to use wildcards such as %(sat)s or %(msg)s; default title is ' %(sat)s, %Y-%m-%d %H:%MUTC, %(area)s, %(rgb)s\'")
   parser.add_option("-c","--composite",  type="string", action="extend_list", dest="postprocessing_composite",\
                     help="creates an image composite, such as 'THX-IR_108', argument repetition '-c comp1 -c comp2' possible, lists of composite possible '-c [comp1, comp2]'")
   parser.add_option("-m","--montage",    type="string", action="extend_lists", dest="postprocessing_montage",\
                     help="creates a montage (two images side by side), such as [\"MSG_h03b-ir108\",\"MSG_HRV\"], argument repetition  '-m mont1 -m mont2' possible, list of montages possible [[im1,im2],[im3,im4]]")

   (options, args) = parser.parse_args()
   #print (options)
   #print (args)

   if len(args) < 1:
      print((parser.print_help()))
      # error also cause program to exit
      parser.error("\n*** Error, at least the input file is necessary, e.g. input_msg.py\n")
   else:
      print ("")

   return (options, args)

#########################################################################################

def parse_commandline_and_read_inputfile(input_file=None):

   #from get_input_msg import parse_commandline_and_read_inputfile
   #from get_input_msg import parse_commandline
   #from get_input_msg import get_input_msg

   # interpret command line arguments 
   (options, args) = parse_commandline()

   # first obligatory argument is the input file (or as optional argument)
   if input_file is None:
      input_file = args[0]

   # skip the '.py' at the end of the input filename
   if input_file[-3:] == '.py': 
      input_file=input_file[:-3]
   # read input file and initialize 'in_msg'
   in_msg = get_input_msg(input_file)
   
   print ('*** overwrite options of the input_file with command line arguments')
   for opt, value in list(options.__dict__.items()):
      if value is not None:
         if opt!='date':
            print(('...', opt, ' = ', value))
            setattr(in_msg, opt, value)
         else:
            in_msg.update_datetime(options.date[0],options.date[1],options.date[2],options.date[3],options.date[4])
            
   # initialize datetime, if not yet done per command line comment or in the input file 
   if in_msg.datetime is None:
      # choose timeslot of the latest possible satellite picture 
      # depends on RSS mode and chosen delay == input: in_msg.rss and in_msg.delay
      # also sets the near real time marker: in_msg.nrt
      in_msg.init_datetime()

   from datetime import datetime
   if datetime.now() < in_msg.datetime:
      print(("*** ERROR in parse_commandline_and_read_inputfile ("+inspect.getfile(inspect.currentframe())+")"))
      print(('    in_msg.datetime is in the future ', in_msg.datetime))
      raise TypeError('*** ERROR: in_msg.datetime is in the future '+str(in_msg.datetime))
      quit()
      
   print(("  date:", in_msg.datetime))
   print(("  NRT: ", in_msg.nrt))
   #print in_msg.__dict__
   
   return in_msg

#########################################################################################
