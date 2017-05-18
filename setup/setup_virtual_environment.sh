#!/bin/bash
#
# script to install a virtual environment called "PyTroll"
#
# This script does the following:
# * create an virtual envirtual environment
#
# The script is part of setup_user.sh and 
# will only work on the zueub428 in the folder 
# /opt/users/\$(logname)/PyTroll/setup.
# To install PyTroll on another computer, please use
# setup_developer.py
#
# author: Ulrich Hamann
# version 0.1: 16-02-2016 U. Hamann

# open proxy ports
export http_proxy=http://proxy.meteoswiss.ch:8080
export https_proxy=https://proxy.meteoswiss.ch:8080

# This is now only done once for all users
## set paths for anaconda (again, for security)
#. ./setup_anaconda_zueub428.sh

# add Anaconda directory to the path and check, if it is installed
source set_paths.sh  # load functions from this script
set_conda_path

#echo "*** Update anaconda itself"
#conda update conda

echo "*** Create virtual environement and install python packages according to PyTroll-conda-package-list.txt"
echo "======================================================================================================="
conda create -n PyTroll_$(logname) python=2.7 --copy --file PyTroll-conda-package-list_no_version_nr.txt  # _$(logname)
### !!! without copy conda does not create shaired library files !!!
echo "Could you create the virtual environment? (press enter to continue or CTRL+c to abort)"
read junk

echo ""
echo "*** Activate virtual environment" PyTroll_$(logname)
source activate PyTroll_$(logname)
echo "Is the virtual environment active? (press enter to continue or CTRL+c to abort)"
read junk
echo ""
echo "*** Installation of additional packages with pip (inside the virtual env)"
echo "========================================================================="
echo ""
pip install --trusted-host pypi.python.org -r PyTroll-pip-requirements_no_version_nr.txt  #_$(logname)
echo "Does the installation look fine? (press enter to continue or CTRL+c to abort)"
read junk

source set_paths.sh  # load functions from this script
set_utils_path
export INSTALL_DIR=$UTILS_PATH/packages/

#echo ""
#echo "*** Install basemap (inside the virtual env)"
#echo "============================================"
cd $INSTALL_DIR/basemap
## specify preinstalled GEOS_DIR library directory
export GEOS_DIR=$INSTALL_DIR/basemap/GEOS-3.3.3
## install basemap
python setup.py install
echo "did the installation of basemap work fine? (press enter to continue or CTRL+c to abort)"
read junk
 

echo ""
echo "*** Install pygrib (inside the virtual env)"
echo "============================================"
cd $INSTALL_DIR/pygrib
# install pygrib (note jasper and grib_api libraries were already installed
#                 and setup.cfg was modified accordingly on zueub428)
python setup.py install
##### works now automatically and also installs the package: ecmwf_grib
####conda install -c conda-forge pygrib   ## very unfortunately in conflict with PIL
echo "Did the installation of pygrib work fine? (press enter to continue or CTRL+c to abort)"
read junk

echo ""
echo "*** Install aggdraw (inside the virtual env)"
echo "============================================"
cd $INSTALL_DIR/aggdraw
python setup.py install
echo "Did the installation of aggdraw work fine? (press enter to continue or CTRL+c to abort)"
read junk

echo ""
echo "*** Deactivate virtual environment"
echo ""
source deactivate
echo ""

echo "*** All installations done"
echo "=========================="
echo "    You can now use your virtual environent with"
echo "    source activate "PyTroll_$(logname)
echo "    and deactivate it with"
echo "    source deactivate"

alias activate='source activate PyTroll_$LOGNAME'
alias deactivate='source deactivate'

source test_virtual_env.sh
