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
conda create -n PyTroll_$(logname) --file PyTroll-conda-package-list_no_version_nr.txt

echo "*** Activate virtual environment" PyTroll_$(logname)
source activate PyTroll_$(logname)

echo ""
echo "*** Pip installation of additional package (inside the virtual env)"
echo "==================================================================="
echo ""
pip install --trusted-host pypi.python.org -r PyTroll-pip-requirements_no_version_nr2.txt
echo ""
echo "*** Deactivate virtual environment"
echo ""
source deactivate