#!/bin/bash
#
# This script does the following:
# * install basemap package
#
# The script will install the m4 library in 
# /opt/users/common/packages
# following the instruction of
# http://www.gnu.org/software/m4/m4.html
# http://savannah.gnu.org/projects/m4/
# http://www.gnu.org/software/m4/manual/m4.pdf
# https://geeksww.com/tutorials/libraries/m4/installation/installing_m4_macro_processor_ubuntu_linux.php
#
# author: Ulrich Hamann
# version 0.1: 19-07-2016 U. Hamann

export INSTALL_DIR=/opt/users/common/packages
cd $INSTALL_DIR

#git clone git clone http://git.savannah.gnu.org/r/m4.git
#export m4v=m4

## check for new packages here:
# http://ftp.gnu.org/gnu/m4/
# copy package and unzip
export m4v=m4-1.4.17
wget http://ftp.gnu.org/gnu/m4/$m4v.tar.gz
gunzip $m4v.tar.gz
tar xf $m4v.tar
rm $m4v.tar

## configure, make and install 
cd $m4v
export PREFIX=/opt/users/common/ 
./configure --prefix=${PREFIX} CFLAGS="-fPIC -m64" 
make; make check; make install;