#!/bin/bash
#
# This script does the following:
# * install basemap package
#
# The script is part of setup_user.sh and
# will only work on the zueub428 in the folder
# /opt/users/\$(logname)/PyTroll/setup.
# To install PyTroll on another computer, please 
# read the administration part in the manual.
#
# author: Ulrich Hamann
# version 0.1: 15-04-2016 U. Hamann

export INSTALL_DIR=/opt/users/common/packages
cd $INSTALL_DIR

## problems when cloning basemap
#
#git clone https://github.com/matplotlib/basemap.git
#
##fatal: The remote end hung up unexpectedly
##fatal: early EOF
##fatal: index-pack failed
## hence do some git settings before cloning
git config --global core.compression 0
git clone --depth 1 https://github.com/matplotlib/basemap.git
cd $INSTALL_DIR/basemap/basemap
git fetch --unshallow
git pull --all

## install geos library
mkdir -p $INSTALL_DIR/basemap/GEOS-3.3.3
export GEOS_DIR=$INSTALL_DIR/basemap/GEOS-3.3.3
cd $INSTALL_DIR/basemap/geos-3.3.3
# python bindung would require installation of SWIG  http://www.swig.org/exec.html
# with --enable-python error while make: -lpython library not found 
./configure --prefix=$GEOS_DIR  # --enable-python --enable-swig
make; make install

#echo "*** Activate virtual environment " PyTroll_$(logname)
#echo "================================ "
#source activate PyTroll_$(logname)

cd $INSTALL_DIR/basemap/
python setup.py install

#echo "*** Deactivate virtual environment"
#source deactivate
