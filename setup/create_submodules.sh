#!/bin/bash
#
# script to create submodules for the PyTroll superproject
#
# This script does the following:
# * adding submodules to the PyTroll superproject
#
# The script is part of SETUP_DEVELOPER.sh.
# !!! DONT USE THIS SCRIPT ON A GIT REPOSITORY !!!
# !!! THAT ALREADY HAVE THE SUBMODULES BELOW !!! 
# Please read the whole script before execution!
#
# author: Ulrich Hamann
# version 0.1: 16-02-2016 U. Hamann

# set paths for anaconda (again, for security)
export PYTROLLHOME=/opt/users/$LOGNAME/PyTroll/
export PATH=$PYTROLLHOME/packages/anaconda2/bin:$PATH
export PYTHONPATH=$PYTROLLHOME/packages/anaconda2/bin:$PYTROLLHOME/scripts

# activate virtual environment
source activate PyTroll
cd ..

# Install aggdraw as submodule
git submodule add -b master https://github.com/jakul/aggdraw.git packages/aggdraw packages/aggdraw
cd packages/aggdraw
python setup.py install 
cd -

# Install pygrib as submodule
git submodule add -b master https://github.com/jswhit/pygrib.git  packages/pygrib
cd packages/pygrib
cp setup.cfg.template setup.cfg
# specify jasper library folder
sed -i -- 's/\#jasper\_dir\ \=\ \/usr\/local/jasper\_dir\ \=\ \/opt\/users\/common\/lib\/jasper/g' setup.cfg
# specify grib_api library folder
sed -i -- 's/\#grib\_api\_dir\ \=\ \/usr\/local/grib\_api\_dir\ \=\ \/opt\/users\/common\/lib\/grib\_api/g' setup.cfg
python setup.py install 
cd -

# Add PyTroll packages as submodules to the git super-project
git submodule add -b master      https://github.com/pytroll/pyresample.git        packages/pyresample
git submodule add -b master      https://github.com/pytroll/pycoast.git           packages/pycoast
git submodule add -b master      https://github.com/pytroll/pyorbital.git         packages/pyorbital
git submodule add -b develop     https://github.com/pytroll/posttroll.git         packages/posttroll
git submodule add -b master      https://github.com/pytroll/trollsift.git         packages/trollsift
git submodule add -b develop     https://github.com/pytroll/pytroll-schedule.git  packages/pytroll-schedule
git submodule add -b develop     https://github.com/pytroll/trollimage.git        packages/trollimage
git submodule add -b master      https://github.com/pytroll/mipp.git              packages/mipp
git submodule add -b pre-master  https://github.com/pytroll/mpop.git              packages/mpop
git submodule add -b develop     https://github.com/pytroll/trollduction.git      packages/trollduction
git submodule add -b develop     https://github.com/adybbroe/pyspectral.git       packages/pyspectral 
git submodule add -b master      https://code.google.com/p/pydecorate/            packages/pydecorate       

# save branch information in the .gitmodules file
git config --file=.gitmodules submodule.packages/aggdraw.branch master
git config --file=.gitmodules submodule.packages/pygrib.branch master

git config --file=.gitmodules submodule.packages/pyresample.branch master
git config --file=.gitmodules submodule.packages/pycoast.branch master
git config --file=.gitmodules submodule.packages/pyorbital.branch master
git config --file=.gitmodules submodule.packages/posttroll.branch develop
git config --file=.gitmodules submodule.packages/trollsift.branch master
git config --file=.gitmodules submodule.packages/pytroll-schedule.branch develop
git config --file=.gitmodules submodule.packages/trollimage.branch develop
git config --file=.gitmodules submodule.packages/mipp.branch master
git config --file=.gitmodules submodule.packages/mpop.branch pre-master
git config --file=.gitmodules submodule.packages/trollduction.branch develop
git config --file=.gitmodules submodule.packages/pyspectral.branch develop
git config --file=.gitmodules submodule.packages/pydecorate.branch master

# Install PyTroll packages
for package in pyresample pycoast pyorbital posttroll trollsift pytroll-schedule trollimage mipp mpop trollduction pyspectral pydecorate
do
    cd packages/$package
    python setup.py develop
    cd -
done


