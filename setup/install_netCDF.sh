#!/bin/bash
#
# This script does the following:
# * install basemap package
#
# The script will install the netCDF library in 
# /opt/users/common/packages
# following the instruction of
# http://www.unidata.ucar.edu/software/netcdf/docs/getting_and_building_netcdf.html
#
# author: Ulrich Hamann
# version 0.1: 19-07-2016 U. Hamann

export INSTALL_DIR=/opt/users/common/packages
cd $INSTALL_DIR

# check for new packages here (use the C version):
# http://www.unidata.ucar.edu/downloads/netcdf/index.jsp
# copy package and unzip
wget ftp://ftp.unidata.ucar.edu/pub/netcdf/netcdf-4.4.1.zip
unzip netcdf-4.4.1.zip

# configure, make and install 
cd netcdf-4.4.1
export PREFIX=/opt/users/common/
export CFLAGS="-fPIC -m64"   # use fPIC and compile for 64bit machine
CPPFLAGS=-I${PREFIX}/include LDFLAGS=-L${PREFIX}/lib ./configure --prefix=${PREFIX} CFLAGS="-fPIC -m64"  
make; make check; make install;