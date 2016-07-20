#!/bin/bash
#
# script to install packages needed for PyTroll
# note:
# this script has only to be run once per computer!
# It can be done by an experienced person (Lorenzo or Ulrich)
#
# This script will install following packages:
# * anaconda3
# * zlib
# * 
# 
#
# The script is part of setup_user.sh and 
# will only work on the zueub428 in the folder 
# /opt/users/\$(logname)/PyTroll/setup.
# To install PyTroll on another computer, please use
# setup_developer.py
#
# author: Ulrich Hamann
# version 0.1: 16-02-2016 U. Hamann

./install_zlib.sh
./install_hdf5.sh
./install_m4.sh
./install_netCDF.sh
./install_jasper.sh
./install_grip_api.sh
./install_anaconda.sh

#./install_cdo.sh better ask IT to install this
./install_tkdiff.sh
