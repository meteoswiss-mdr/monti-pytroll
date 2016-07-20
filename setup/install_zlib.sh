#!/bin/bash
#
# This script does the following:
# * install basemap package
#
# The script will install the netCDF library in 
# /opt/users/common/packages
# following the instruction of
# http://www.zlib.net/
#
# author: Ulrich Hamann
# version 0.1: 19-07-2016 U. Hamann

export INSTALL_DIR=/opt/users/common/packages
cd $INSTALL_DIR

git clone https://github.com/madler/zlib.git
export zlibv=zlib

## check for new packages here:
# http://www.zlib.net/
# copy package and unzip
#export zlibv=zlib-1.2.8
#wget ftp://ftp.unidata.ucar.edu/pub/netcdf/netcdf-4/$zlibv.tar.gz
#unzip $zlibv.tar.gz

## configure, make and install 
cd $zlibv
export PREFIX=/opt/users/common/
export CFLAGS="-fPIC -m64"   # use fPIC and compile for 64bit machine 
./configure --prefix=${PREFIX}
make; make check; make install;