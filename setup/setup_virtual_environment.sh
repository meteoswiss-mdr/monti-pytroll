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

# set paths for anaconda (again, for security)
. ./setup_anaconda_zueub428.sh

#echo "*** Switch off SSL check for conda installations"
conda config --set ssl_verify false

#echo "*** Update anaconda itself"
#conda update conda

echo "*** Create virtual environement and install python packages according to PyTroll-conda-package-list.txt"
echo "======================================================================================================="
conda create -n PyTroll_$(logname) --copy --file PyTroll-conda-package-list_no_version_nr.txt
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
pip install --trusted-host pypi.python.org -r PyTroll-pip-requirements_no_version_nr2.txt
echo "Does the installation look fine? (press enter to continue or CTRL+c to abort)"
read junk

export INSTALL_DIR=/opt/users/common/packages
cd $INSTALL_DIR

echo ""
echo "*** Install basemap (inside the virtual env)"
echo "============================================"
cd $INSTALL_DIR/basemap
# specify preinstalled GEOS_DIR library directory
export GEOS_DIR=$INSTALL_DIR/basemap/GEOS-3.3.3
# install basemap
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
echo ""
echo "*** All installations done"
echo "=========================="
echo "    You can now use your virtual environent with"
echo "    source activate "PyTroll_$(logname)
echo "    and deactivate it with"
echo "    source deactivate"
echo ""
echo "    Please do some test, if you can import packages:"
echo ""
echo "source activate "PyTroll_$(logname)
echo "python"
echo "import matplotlib._path"
echo "import h5py"
echo "import netCDF4"
echo "from mpl_toolkits.basemap import Basemap"
echo "import aggdraw"
echo "import pygrib"
echo "import scipy"
echo "import numpy"
echo "import PIL"
echo "from __future__ import print_function"
echo "import skimage"
echo ""
