#!/bin/bash
#
# This script does the following:
# * install basemap package
#
# The script will install jasper in 
# /opt/users/common/packages
# following the instruction of
# http://www.linuxfromscratch.org/blfs/view/svn/general/jasper.html
#
# author: Ulrich Hamann
# version 0.1: 19-07-2016 U. Hamann

export INSTALL_DIR=/opt/users/common/packages
cd $INSTALL_DIR

# copy and unzip jasper package
wget http://www.ece.uvic.ca/~mdadams/jasper/software/jasper-1.900.1.zip
unzip jasper-1.900.1.zip

# copy security patch
wget http://www.linuxfromscratch.org/patches/blfs/svn/jasper-1.900.1-security_fixes-2.patch

# add security patch 
cd jasper-1.900.1
patch -Np1 -i ../jasper-1.900.1-security_fixes-2.patch

# install 
./configure --prefix=/opt/users/common/lib/jasper --enable-shared --disable-static --mandir=/opt/users/common/lib/jasper/man 
make
make install