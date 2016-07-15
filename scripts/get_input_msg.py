
def get_input_msg(input_file=None):

   from datetime import datetime, timedelta
   from os import getcwd
   import scp_settings

   print "... read input file from :", getcwd()

   class input_msg_class:

      def __init__(self):
         self.datetime = None
         self.delay = 0
         self.RGBs = []
         self.areas = []
         #self.sat = "meteosat"
         self.sat = "Meteosat-"
         self.sat_nr = None  # rapid scan service
         self.RSS = True
         self.check_input = False
         self.reader_level = None
         self.parallax_correction = False
         self.parallax_gapfilling = 'False'
         self.save_reprojected_data = []
         self.save_statistics = False
         self.HRV_enhancement = False
         self.make_plots = True
         self.fill_value = None          # black (0,0,0) / white (1,1,1) / transparent None  
         self.nwcsaf_calibrate = False   # False -> dont scale to real values, plot with palette
         self.outputFile = 'MSG_%(rgb)s-%(area)s_%y%m%d%H%M.png'
         self.outputDir = "./%Y-%m-%d/%(rgb)s-%(area)s/"
         self.compress_to_8bit=False
         self.scpOutput = False
         self.scpOutputDir = scp_settings.scpOutputDir
         self.scpID = scp_settings.scpID
         self.mapDir = ""
         self.mapResolution = None
         self.indicate_mask = True
         self.add_title = True
         self.add_borders = True
         self.border_color = 'red'
         self.add_rivers = False
         self.river_color = 'blue'
         self.add_logos = True
         self.add_colorscale = True
         self.fixed_minmax = True
         self.rad_min = {'VIS006':   0, 'VIS008':   0, 'IR_016':   0, 'IR_039': 210, 'WV_062': 210, 'WV_073': 190,\
                         'IR_087': 205, 'IR_097': 210, 'IR_108': 205, 'IR_120': 205, 'IR_134': 205, 'HRV': 0,\
                         'VIS006c':   0, 'VIS008c':   0, 'IR_016c':   0, 'IR_039c': 210, 'WV_062c': 210, 'WV_073c': 190,\
                         'IR_087c': 205, 'IR_097c': 210, 'IR_108c': 205, 'IR_120c': 205, 'IR_134c': 205, 'HRVc': 0,\
                         'CMa': 1, 'CT': 0, 'CT_PHASE': 0, 'CTH': 0, 'CTP':  100.,'CTT': 210., 'PC':0, 'CRR':0, 'clouddepth':0,\
                         'WV_062-WV_073': -25, 'WV_062-IR_108': -70, 'WV_073-IR_134':-15, 'IR_087-IR_108':-4.0, 'IR_087-IR_120':-4,'IR_120-IR_108':-6,\
                         'sphr_bl': 0, 'sphr_cape': 150, 'sphr_diffbl': -1.5, 'sphr_diffhl': -0.75, 'sphr_diffki': -7, 'sphr_diffli': -2.5,\
                         'sphr_diffml': -2.5, 'sphr_diffshw': -2.5, 'sphr_difftpw': -3, 'sphr_hl': 0, 'sphr_ki': 0, 'sphr_li': -15, \
                         'sphr_ml': 0, 'sphr_quality': 0, 'sphr_sflag': 0, 'sphr_shw': -15, 'sphr_tpw': 0, 'h03': 0, \
                         'azidiff':0,'cth':0,'cldmask':0,'cot':0,'cph':0,'ctt':210.,'cwp':0,\
                         'dcld':0,'dcot':0,'dcwp':0,'dndv':0,'dreff':0,\
                         'precip':0,'precip_ir':0,'qa':0,'reff':0,'satz':0,'sds':0,'sds_cs':0,'sds_diff':0,'sds_diff_cs':0,\
                         'sunz':0,'lat':-80,'lon':-80,'time_offset':0}
         self.rad_max = {'VIS006':  85, 'VIS008':  90, 'IR_016':  80, 'IR_039': 340, 'WV_062': 260, 'WV_073': 280,\
                         'IR_087': 320, 'IR_097': 285, 'IR_108': 320, 'IR_120': 320, 'IR_134': 290, 'HRV': 100,\
                         'VIS006c':  85, 'VIS008c':  90, 'IR_016c':  80, 'IR_039c': 340, 'WV_062c': 260, 'WV_073c': 280,\
                         'IR_087c': 320, 'IR_097c': 285, 'IR_108c': 320, 'IR_120c': 320, 'IR_134c': 290, 'HRVc': 100,\
                         'CMa': 4, 'CT': 21, 'CT_PHASE': 3, 'CTH': 12, 'CTP': 1000.,'CTT': 320., 'PC':100, 'CRR':10, 'clouddepth':6,\
                         'WV_062-WV_073':   5,'WV_062-IR_108':    5, 'WV_073-IR_134':  5, 'IR_087-IR_108': 1.5, 'IR_087-IR_120': 4,'IR_120-IR_108': 2,\
                         'sphr_bl': 35, 'sphr_cape': 200, 'sphr_diffbl': 1.5, 'sphr_diffhl': 0.75, 'sphr_diffki': 7, 'sphr_diffli': 2.5,\
                         'sphr_diffml': 2.5, 'sphr_diffshw': 2.5, 'sphr_difftpw': 3, 'sphr_hl': 8, 'sphr_ki': 60, 'sphr_li': 25, \
                         'sphr_ml': 45, 'sphr_quality': 5000, 'sphr_sflag': 20, 'sphr_shw': 25, 'sphr_tpw': 70, 'h03': 30, \
                         'azidiff':180,'cth':12,'cldmask':3,'cot':256,'cph':2,'ctt':320.,'cwp':10,\
                         'dcld':4,'dcot':50,'dcwp':10,'dndv':4,'dreff':20,\
                         'precip':256,'precip_ir':256,'qa':50,'reff':50,'satz':90,'sds':1200,'sds_cs':1200,'sds_diff':800,'sds_diff_cs':800,\
                         'sunz':90,'lat':80,'lon':80,'time_offset':750}
         self.tick_marks= {'VIS006': 20, 'VIS008': 20, 'IR_016': 20, 'IR_039': 20, 'WV_062': 20, 'WV_073': 20,\
                           'IR_087': 20, 'IR_097': 20, 'IR_108': 20, 'IR_120': 20, 'IR_134': 20, 'HRV': 20,\
                           'vza': 5, 'vaa': 5, 'lat': 5, 'lon': 5,\
                           'CTH': 4, 'CTP':  100,'CTT': 20, 'CT': 1, 'CT_PHASE': 1, 'CMa': 1, 'CMa_DUST':  1, 'CMa_TEST': 1, 'CMa_VOLCANIC': 1, 'clouddepth':1,\
                           'sphr_bl': 5, 'sphr_cape': 10, 'sphr_diffbl': 0.5, 'sphr_diffhl': 0.5, 'sphr_diffki': 2, 'sphr_diffli': 0.5,\
                           'sphr_diffml': 1, 'sphr_diffshw': 0.5, 'sphr_difftpw': 1, 'sphr_hl': 1, 'sphr_ki': 5, 'sphr_li': 1, \
                           'sphr_ml': 5, 'sphr_quality': 500, 'sphr_sflag': 1, 'sphr_shw': 1, 'sphr_tpw': 5, 'h03': 10, \
                           'azidiff':10,'cth':1,'cldmask':1,'cot':10,'cph':1,'ctt':10.,'cwp':2,\
                           'dcld':1,'dcot':10,'dcwp':2,'dndv':1,'dreff':20,\
                           'precip':10,'precip_ir':10,'qa':10,'reff':10,'satz':10,'sds':100,'sds_cs':100,'sds_diff':100,'sds_diff_cs':100,\
                           'sunz':10,'lat':10,'lon':10,'time_offset':100}
         self.minor_tick_marks = {'VIS006': 5, 'VIS008': 5, 'IR_016': 5, 'IR_039': 5, 'WV_062': 5, 'WV_073': 5,\
                           'IR_087': 5, 'IR_097': 5, 'IR_108': 5, 'IR_120': 5, 'IR_134': 5, 'HRV': 5,\
                           'vza': 1, 'vaa': 1, 'lat': 1, 'lon': 1,\
                           'CTH': 1, 'CTP':  50,'CTT': 5, 'CT': 1, 'CT_PHASE': 1, 'CMa': 1, 'CMa_DUST':  1, 'CMa_TEST': 1, 'CMa_VOLCANIC': 1, 'clouddepth':1,
                           'sphr_bl': 1, 'sphr_cape': 5, 'sphr_diffbl': 0.1, 'sphr_diffhl': 0.05, 'sphr_diffki': 0.5, 'sphr_diffli': 0.1,
                           'sphr_diffml': 0.5, 'sphr_diffshw': 0.1, 'sphr_difftpw': 0.5, 'sphr_hl': 0.5, 'sphr_ki': 1, 'sphr_li': 0.5, 
                           'sphr_ml': 1, 'sphr_quality': 100, 'sphr_sflag': 1, 'sphr_shw': 0.2, 'sphr_tpw': 1, 'h03': 5, \
                           'azidiff':2,'cth':0.2,'cldmask':1,'cot':2,'cph':1,'ctt':5.,'cwp':1,\
                           'dcld':1,'dcot':5,'dcwp':1,'dndv':1,'dreff':5,\
                           'precip':5,'precip_ir':5,'qa':2,'reff':2,'satz':2,'sds':10,'sds_cs':10,'sds_diff':10,'sds_diff_cs':10,\
                           'sunz':2,'lat':2,'lon':2,'time_offset':10 }

         self.postprocessing_areas     = []
         self.postprocessing_composite = []
         self.postprocessing_montage   = [[]]

         self.verbose = True
         

      def add_rgb(self, rgb):
         self.RGBs.append(rgb)
      def add_area(self, area):
         self.areas.append(area)
      def update_datetime(self, year, month, day, hour, minute):
         if year != None and month != None and day != None and hour != None and minute != None: 
            self.datetime=datetime(year, month, day, hour, minute, 0)
         else:
            print "*** WARNING: cannot update time!"
      def get_last_SEVIRI_date(self):
         from my_msg_module import get_last_SEVIRI_date
         self.datetime = get_last_SEVIRI_date(self.RSS, delay=self.delay)
         #print "... use time delay of ", self.delay, " minutes"
         #if self.delay != 0:
         #   self.datetime -= timedelta(minutes=self.delay)

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
            print "*** Error in sat_nr_str (get_input_msg.py)"
            print "    unknown type of sat_nr", type(self.sat_nr)
            quit()

         #return sat_nr_str
         return ""

      def sat_str(self, layout="%(sat)s-%(sat_nr)s"):
         if self.sat[0:8].lower() == "meteosat":
            return "Meteosat-"+str(int(self.sat_nr))
         else:
            return self.sat+str(int(self.sat_nr))
         
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
         if self.sat[0:8]=="meteosat" or self.sat[0:8]=="Meteosat":
            
            if 8 <= self.sat_nr and self.sat_nr <=11:
               d={'msg':'MSG', 'msg_nr':str(int(self.sat_nr)-7), 'sat':self.sat, 'sat_nr':str(self.sat_nr),'0sat_nr':str(self.sat_nr).zfill(2)}
               msg_str = layout % d
            else:
               print "*** Error in msg_str (get_input_msg.py)"
               print "    try to get msg_string for sat number", self.sat_nr, " which is not meteosat SECOND generation "
               quit()

         else:
            print "*** Error in msg_str (get_input_msg.py)"
            print "    try to get msg_string for sat ", self.sat, " which is not Meteosat/meteosat"
            quit()
         return msg_str

   # define input class
   in_msg = input_msg_class()

   # get input from (user specified) file 
   input_module = __import__(input_file)
   input_module.input(in_msg)

   return in_msg
