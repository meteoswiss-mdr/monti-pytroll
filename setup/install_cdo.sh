#!/bin/bash
#
# This script does the following:
# * install basemap package
#
# The script will install the m4 library in 
# /opt/users/common/packages
# following the instruction of
# https://code.zmaw.de/projects/cdo/wiki/Cdo#Documentation
# click on "Installation from source code"
# 
#
# author: Ulrich Hamann
# version 0.1: 19-07-2016 U. Hamann

export INSTALL_DIR=/opt/users/common/packages
cd $INSTALL_DIR

## check for new packages here:
# https://code.zmaw.de/projects/cdo/files
# copy package and unzip
export version=cdo-1.7.2
wget https://code.zmaw.de/attachments/download/12760/$version.tar.gz
gunzip $version.tar.gz
tar xf $version.tar
rm $version.tar

## configure, make and install 
cd $version
export PREFIX=/opt/users/common/ 
# using the python options, the grib_api library is not installed in PREFIX but insite python
#./configure --prefix=${PREFIX} CFLAGS="-fPIC -m64" --with-netcdf=${PREFIX}  --with-jasper=${PREFIX} --with-hdf5=${PREFIX} --with-grib_api=${PREFIX}
# so this is the correct grib_api directory
./configure --prefix=${PREFIX} CFLAGS="-fPIC -m64" --with-netcdf=${PREFIX}  --with-jasper=${PREFIX} --with-hdf5=${PREFIX} --with-grib_api=/opt/users/common/lib/python3.5/site-packages/grib_api

make; make check; make install;