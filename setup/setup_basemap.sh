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
# version 0.1: 08-03-2016 U. Hamann

# set paths for anaconda (again, for security)
export PYTROLLHOME=/opt/users/$LOGNAME/PyTroll/
export PATH=$PYTROLLHOME/packages/anaconda2/bin:$PATH
export PYTHONPATH=$PYTROLLHOME/packages/anaconda2/bin:$PYTROLLHOME/scripts

## add basemap package as submodule
# cd $PYTROLLHOME
# git submodule add -b master https://github.com/matplotlib/basemap.git packages/basemap
## git config --file=.gitmodules submodule.packages/basemap.branch master

## tell basemap to update on master branch
cd $PYTROLLHOME/packages/basemap/
git branch -u origin master

## git submodule synchronisation 
cd $PYTROLLHOME
git submodule sync
## update the git submodule to the latest stage of the official repositories 
git submodule update --remote
## checkout all repositories, to avoid the detached head state
git submodule foreach -q --recursive 'branch="$(git config -f $toplevel/.gitmodules submodule.$name.branch)"; git checkout $branch'

## install geos library
mkdir -p $PYTROLLHOME/packages/basemap/GEOS-3.3.3
export GEOS_DIR=$PYTROLLHOME/packages/basemap/GEOS-3.3.3
cd $PYTROLLHOME/packages/basemap/geos-3.3.3
# python bindung would require installation of SWIG  http://www.swig.org/exec.html
./configure --prefix=$GEOS_DIR  # --enable-python --enable-swig
make; make install

#echo "*** Activate virtual environment"
#source activate PyTroll

cd $PYTROLLHOME/packages/basemap/
python setup.py install

#echo "*** Deactivate virtual environment"
#source deactivate
