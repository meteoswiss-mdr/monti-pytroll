

from get_input_msg import parse_commandline_and_read_inputfile
#from get_input_msg import parse_commandline
#from get_input_msg import get_input_msg

in_msg = parse_commandline_and_read_inputfile()

#(options, args) = parse_commandline()
#
#if options.date is None:
#    timeslot=None
#else:
#    print options.date
#    from datetime import datetime
#    timeslot=datetime(options.date[0],options.date[1],options.date[2],options.date[3],options.date[4])
#    
#input_file = args[0]
#if input_file[-3:] == '.py': 
#    input_file=input_file[:-3]
#         
## read input file and initialize in_msg
#in_msg = get_input_msg(input_file, timeslot=timeslot)
#
#print '*** overwrite input from input file with command line arguments'
#for opt, value in options.__dict__.items():
#    if value is not None:
#        print '   ', opt, ' = ', value
#        setattr(in_msg, opt, value)
        
print ""
print in_msg.datetime
print ""
