#!/bin/bash
#
# script to install a virtual environment called "PyTroll"
#
# This script does the following:
# * install anaconda
#
# The script is part of SETUP_for_zueub428.sh and 
# will only work on the zueub428 in the folder 
# /opt/users/\$(logname)/PyTroll/setup.
# To install PyTroll on another computer, please use
# setup_developer.py
#
# author: Ulrich Hamann
# version 0.1: 16-02-2016 U. Hamann

# create PYTROLL home directory 
export PYTROLLHOME=/opt/users/$(logname)/PyTroll/
mkdir -p $PYTROLLHOME/packages

# add anaconda to your path
echo "the script changes your \$PATH and \$PYTHONPATH to avoid conflicts:"
export PATH=/opt/users/common/packages/anaconda2/bin:$PATH
echo "\$PATH="$PATH

#export PYTHONPATH=/opt/users/common/packages/anaconda2/bin:$PYTROLLHOME/scripts
export PYTHONPATH=$PYTROLLHOME/scripts
echo "\$PYTHONPATH="$PYTHONPATH