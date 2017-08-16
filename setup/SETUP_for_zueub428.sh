#!/bin/bash
#
# script to install PyTroll 
#
# This script does the following:
# * install anaconda
# * create an virtual envirtual environment
# * and install nessesary pytroll packages
#
# The script will only work on the zueub227 in the folder 
# /opt/users/\$(logname)/PyTroll/setup
# to install PyTroll on another computer, please use
# setup_developer.py
#
# author: Ulrich Hamann
# version 0.1: 16-02-2016 U. Hamann

# installation of Anaconda (not necessary for zueub427, zueub428 and CSCS, as we use a common Anaconda installation)
# (use the ". ./" syntax to remember env variable set inside the bash script)
#. ./setup_anaconda.sh
#echo "press enter to continue"
#read junk

# update Anaconda, create virt. env. "PyTroll_${LOGNAME}", install python packages
. ./setup_virtual_environment.sh
echo "press enter to continue"
read junk

# install PyTroll packages with develop option
. ./setup_submodules.sh
#echo "press enter to continue"
#read junk

