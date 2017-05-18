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
#. ./setup_anaconda_zueub428.sh

#export packages="aggdraw pygrib pyresample pycoast pyorbital posttroll trollsift pytroll-schedule trollimage mipp mpop trollduction pyspectral pydecorate"
export packages="pyresample pycoast pyorbital posttroll trollsift pytroll-schedule trollimage mipp mpop trollduction pyspectral pydecorate satpy"

declare -A branches
branches=( ["aggdraw"]="master" ["pygrib"]="master" ["pyresample"]="master" ["pycoast"]="master" \
           ["pyorbital"]="master" ["posttroll"]="develop" ["trollsift"]="master" \
           ["pytroll-schedule"]="master" ["trollimage"]="develop" ["mipp"]="master" \
           ["mpop"]="master" ["trollduction"]="develop" ["pyspectral"]="master" ["pydecorate"]="master" ["satpy"]="develop")

source set_paths.sh  # load functions from this script
set_pytroll_paths
cd $PYTROLLHOME


echo ""
echo "*** Synchronize PyTroll modules (git submodule sync)"
echo "===================================================="
git submodule sync
echo "Does this look good? (press enter to continue or CTRL+c to abort)"
read junk


echo ""
echo "*** Update PyTroll modules (git submodule update --remote)"
echo "=========================================================="
git submodule update --remote
echo "Does this look good? (press enter to continue or CTRL+c to abort)"
read junk


echo ""
echo "*** Checkout branches of PyTroll modules (... git checkout $branch, in order to avoid the detached head state)"
echo "=============================================================================================================="
#git submodule foreach -q --recursive 'branch="$(git config -f $toplevel/.gitmodules submodule.$name.branch)"; git checkout $branch'
git submodule foreach -q --recursive git pull 
echo "Does this look good? (press enter to continue or CTRL+c to abort)"
read junk


echo ""
echo "*** Activate virtual environment " PyTroll_$(logname)
echo "============================================= "
source activate PyTroll_$(logname)
echo "Is the virtual environement active? (press enter to continue or CTRL+c to abort)"
read junk

echo ""
echo "*** Install PyTroll packages "
echo "============================ "

for pack in $packages
do 
    echo ""
    echo "*** install"  $pack " with branch " ${branches[$pack]} " from repository " ${repositories[$pack]}
    cd $PYTROLLHOME

    cd packages/$pack

    # For pygrib specify libraries in the setup.cfg
    if [ "$pack" == "pygrib" ]
    then
	echo cp setup.cfg.template setup.cfg
	cp setup.cfg.template setup.cfg

        # specify jasper library folder
        echo sed -i -- 's/\#jasper\_dir\ \=\ \/usr\/local/jasper\_dir\ \=\ \/opt\/users\/common\/lib\/jasper/g' setup.cfg
	sed -i -- 's/\#jasper\_dir\ \=\ \/usr\/local/jasper\_dir\ \=\ \/opt\/users\/common\/lib\/jasper/g' setup.cfg 
        # specify grib_api library folder
        echo sed -i -- 's/\#grib\_api\_dir\ \=\ \/usr\/local/grib\_api\_dir\ \=\ \/opt\/users\/common\/lib\/grib\_api/g' setup.cfg
	sed -i -- 's/\#grib\_api\_dir\ \=\ \/usr\/local/grib\_api\_dir\ \=\ \/opt\/users\/common\/lib\/grib\_api/g' setup.cfg
    fi

    # Install python and PyTroll packages
    if ( [ "$pack" == "aggdraw" ] || [ "$pack" == "aggdraw" ] ) ; then
	# normal installation in the site-package directory
	echo python setup.py install 
	python setup.py install 
    else
	# development installation using the easy-install.pth file
	echo python setup.py develop 
	python setup.py develop 
    fi

done 

echo "*** Deactivate virtual environment"
source deactivate
