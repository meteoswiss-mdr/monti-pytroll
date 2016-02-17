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

echo "Switch off SSL check for conda installations"
conda config --set ssl_verify false

echo "Update anaconda itself"
conda update conda

echo "install additional conda packages with PyTroll-conda-package-list.txt"
conda create -n PyTroll --file PyTroll-conda-package-list.txt

echo "activate virtual environment"
source activate PyTroll

echo "do pip installation of additional package"
pip install --trusted-host pypi.python.org -r PyTroll-pip-requirements.txt

echo "deactivate virtual environment"
source deactivate