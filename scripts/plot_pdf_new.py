import numpy as np
from datetime import datetime, timedelta
from produce_forecasts_develop import string_date
from scipy.misc import imread
import matplotlib.pyplot as plt
import pickle
import sys
from mpop.satellites import GeostationaryFactory
from mpop.projector import get_area_def
from plot_msg import load_products
import seaborn
from copy import deepcopy


if __name__=="__main__":
    from get_input_msg import get_input_msg
    
    input_file = sys.argv[1]
    if input_file[-3:] == '.py': 
        input_file=input_file[:-3]
    in_msg = get_input_msg(input_file)    
    
    rgb = ["CTP"]
    
    time_slot = datetime(2015,10,15,5,0)
    
    global_data = GeostationaryFactory.create_scene(in_msg.sat_str(),in_msg.sat_nr_str(), "seviri",  time_slot)
    area_loaded = get_area_def("EuropeCanary95")  #(in_windshift.areaExtraction)  
    area_loaded = load_products(global_data, ['CTP'], in_msg, area_loaded)
    data = global_data.project("ccs4")           
    
    data_flat = data[rgb[0]].data.flatten()
    
    num_bins = 100
    
    fig = plt.figure()
    n, bins, patches = plt.hist(data_flat[data_flat>0], num_bins, normed=1, facecolor='blue', align='mid')
    
    plt.xlabel("pressure")
    
    plt.ylabel("pdf")
    
    plt.savefig("CTP.png")
    plt.close()

