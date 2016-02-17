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

setup_anaconda.sh
echo "press enter to continue"
read junk

setup_virtual_environment.sh
echo "press enter to continue"
read junk
