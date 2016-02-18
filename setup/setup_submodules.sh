#!/bin/bash
#
# script to install a PyTroll packages
#
# This script does the following:
# * install PyTroll packages
#
# The script is part of setup_user.sh and
# will only work on the zueub428 in the folder
# /opt/users/\$(logname)/PyTroll/setup.
# To install PyTroll on another computer, please use
# setup_developer.py
#
# author: Ulrich Hamann
# version 0.1: 16-02-2016 U. Hamann

# set paths for anaconda (again, for security)
export PYTROLLHOME=/opt/users/$LOGNAME/PyTroll/
export PATH=$PYTROLLHOME/packages/anaconda2/bin:$PATH
export PYTHONPATH=$PYTROLLHOME/packages/anaconda2/bin:$PYTROLLHOME/scripts

# git submodule synchronisation 
git submodule sync

echo "*** Activate virtual environment"
source activate PyTroll
cd ..

echo "*** Install aggdraw as submodule"
cd packages/aggdraw
python setup.py install 
cd -

echo "*** Install pygrib as submodule"
cd packages/pygrib
cp setup.cfg.template setup.cfg
# specify jasper library folder
sed -i -- 's/\#jasper\_dir\ \=\ \/usr\/local/jasper\_dir\ \=\ \/opt\/users\/common\/lib\/jasper/g' setup.cfg
# specify grib_api library folder
sed -i -- 's/\#grib\_api\_dir\ \=\ \/usr\/local/grib\_api\_dir\ \=\ \/opt\/users\/common\/lib\/grib\_api/g' setup.cfg
python setup.py install 
cd -

echo "*** Install PyTroll packages"
for package in pyresample pycoast pyorbital posttroll trollsift pytroll-schedule trollimage mipp mpop trollduction pyspectral pydecorate
do
    cd packages/$package
    python setup.py develop
    cd -
done

echo "*** Deactivate virtual environment"
source deactivate
