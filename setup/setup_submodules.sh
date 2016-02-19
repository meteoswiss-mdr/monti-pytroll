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

export packages="aggdraw pygrib pyresample pycoast pyorbital posttroll trollsift pytroll-schedule trollimage mipp mpop trollduction pyspectral pydecorate"

declare -A branches
branches=( ["aggdraw"]="master" ["pygrib"]="master" ["pyresample"]="master" ["pycoast"]="master" \
           ["pyorbital"]="master" ["posttroll"]="develop" ["trollsift"]="master" \
           ["pytroll-schedule"]="master" ["trollimage"]="develop" ["mipp"]="master" \
           ["mpop"]="master" ["trollduction"]="develop" ["pyspectral"]="master" ["pydecorate"]="master" )

# git submodule synchronisation 
git submodule sync


echo "*** Activate virtual environment"
source activate PyTroll

for pack in $packages
do 
    echo install  $pack " with branch " ${branches[$pack]} " from repository " ${repositories[$pack]}
    cd $PYTROLLHOME

    cd packages/$pack

    # For pygrib specify libraries in the setup.cfg
    if [ "$pack" == "pygrib" ]
    then
	echo cp setup.cfg.template setup.cfg
        # specify jasper library folder
        echo sed -i -- 's/\#jasper\_dir\ \=\ \/usr\/local/jasper\_dir\ \=\ \/opt\/users\/common\/lib\/jasper/g' setup.cfg
        # specify grib_api library folder
        echo sed -i -- 's/\#grib\_api\_dir\ \=\ \/usr\/local/grib\_api\_dir\ \=\ \/opt\/users\/common\/lib\/grib\_api/g' setup.cfg
    fi

    # Install python and PyTroll packages
    if ( [ "$pack" == "aggdraw" ] || [ "$pack" == "aggdraw" ] ) ; then
	# normal installation in the site-package directory
	echo python setup.py install 
    else
	# development installation using the easy-install.pth file
	echo python setup.py develop 
    fi

done 

echo "*** Deactivate virtual environment"
source deactivate
