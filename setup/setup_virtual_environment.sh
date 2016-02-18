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
export PYTROLLHOME=/opt/users/$LOGNAME/PyTroll/
export PATH=$PYTROLLHOME/packages/anaconda2/bin:$PATH
export PYTHONPATH=$PYTROLLHOME/packages/anaconda2/bin:$PYTROLLHOME/scripts

echo "*** Switch off SSL check for conda installations"
conda config --set ssl_verify false

echo "*** Update anaconda itself"
conda update conda

echo "*** Install additional conda packages with PyTroll-conda-package-list.txt"
conda create -n PyTroll --file PyTroll-conda-package-list.txt

echo "*** Activate virtual environment"
source activate PyTroll

echo "*** Pip installation of additional package"
pip install --trusted-host pypi.python.org -r PyTroll-pip-requirements.txt

echo "*** Deactivate virtual environment"
source deactivate