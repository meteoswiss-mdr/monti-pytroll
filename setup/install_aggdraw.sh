#!/bin/bash
#
# This script does the following:
# * install basemap package
#
# The script is part of setup_user.sh and
# will only work on the zueub428 in the folder
# /opt/users/\$(logname)/PyTroll/setup.
# To install PyTroll on another computer, please 
# read the administration part in the manual.
#
# author: Ulrich Hamann
# version 0.1: 15-04-2016 U. Hamann

source set_paths.sh  # load functions from this script
set_utils_path
export INSTALL_DIR=$UTILS_PATH/packages/
cd $INSTALL_DIR

git clone https://github.com/jakul/aggdraw.git

#echo "*** Activate virtual environment " PyTroll_$(logname)
#echo "================================ "
#source activate PyTroll_$(logname)

#cd $INSTALL_DIR/aggdraw
#python setup.py install

#echo "*** Deactivate virtual environment"
#source deactivate
