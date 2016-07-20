#!/bin/bash
#
# This script does the following:
# * install basemap package
#
# The script will install the hdf5 library in 
# /opt/users/common/packages
# following the instruction of
# https://www.hdfgroup.org/HDF5/release/obtainsrc.html#src
# https://www.hdfgroup.org/ftp/HDF5/current/src/unpacked/release_docs/INSTALL
#
# author: Ulrich Hamann
# version 0.1: 19-07-2016 U. Hamann

export INSTALL_DIR=/opt/users/common/packages
cd $INSTALL_DIR

## check for new packages here:
# https://www.hdfgroup.org/ftp/HDF5/releases/
# copy package and unzip
export hdf5v=hdf5-1.8.9
wget ftp://ftp.unidata.ucar.edu/pub/netcdf/netcdf-4/$hdf5v.tar.gz
gunzip $hdf5v.tar.gz
tar xf $hdf5v.tar
rm $hdf5v.tar

## configure, make and install 
cd $hdf5v
export PREFIX=/opt/users/common/ 
./configure --with-zlib=$PREFIX --prefix=$PREFIX CFLAGS=-fPIC
make; make check; make install;