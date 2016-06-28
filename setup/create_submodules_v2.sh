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
# version 0.1: 16.02.2016 U. Hamann
#              initial version
# version 0.2: 19.02.2016 U. Hamann 
#              implementing a loop and arrays to have consistent 
#              branch information everywhere
#              Not tested! remove all "echo" to run the script

# set paths for anaconda (again, for security)
export PYTROLLHOME=/opt/users/$LOGNAME/PyTroll/
#export PATH=$PYTROLLHOME/packages/anaconda2/bin:$PATH
#export PYTHONPATH=$PYTROLLHOME/packages/anaconda2/bin:$PYTROLLHOME/scripts
export PATH=$PYTROLLHOME/packages/anaconda3/bin:$PATH
export PYTHONPATH=$PYTROLLHOME/packages/anaconda3/bin:$PYTROLLHOME/scripts

# activate virtual environment
source activate PyTroll
cd ..

export packages="aggdraw pygrib pyresample pycoast pyorbital posttroll trollsift pytroll-schedule trollimage mipp mpop trollduction pyspectral pydecorate"

declare -A branches
branches=( ["aggdraw"]="master" ["pygrib"]="master" ["pyresample"]="master" ["pycoast"]="master" \
           ["pyorbital"]="master" ["posttroll"]="develop" ["trollsift"]="master" \
           ["pytroll-schedule"]="master" ["trollimage"]="develop" ["mipp"]="master" \
           ["mpop"]="master" ["trollduction"]="develop" ["pyspectral"]="master" ["pydecorate"]="master" )

declare -A repositories
repositories=( ["aggdraw"]="https://github.com/jakul/aggdraw.git packages/aggdraw" \
             ["pygrib"]="https://github.com/jswhit/pygrib.git" \
             ["pyresample"]="https://github.com/pytroll/pyresample.git" \
             ["pycoast"]="https://github.com/pytroll/pycoast.git" \
             ["pyorbital"]="https://github.com/pytroll/pyorbital.git" \
             ["posttroll"]="https://github.com/pytroll/posttroll.git" \
             ["trollsift"]="https://github.com/pytroll/trollsift.git" \
             ["pytroll-schedule"]="https://github.com/pytroll/pytroll-schedule.git" \
             ["trollimage"]="https://github.com/pytroll/trollimage.git" \
             ["mipp"]="https://github.com/pytroll/mipp.git" \
             ["mpop"]="https://github.com/pytroll/mpop.git" \
             ["trollduction"]="https://github.com/pytroll/trollduction.git" \
             ["pyspectral"]="https://github.com/adybbroe/pyspectral.git" \
             ["pydecorate"]="https://code.google.com/p/pydecorate/")

for pack in $packages
do 
    echo install  $pack " with branch " ${branches[$pack]} " from repository " ${repositories[$pack]}
    cd $PYTROLLHOME

    # Add package as git submodule to git superproject and download source code 
    echo git submodule add -b ${branches[$pack]} ${repositories[$pack]}  packages/$pack

    # Specify branch information in the .gitmodules file for new git users
    echo git config --file=.gitmodules submodule.packages/$pack.branch ${branches[$pack]}

    # specify branch information for the upstream repository with -u (upstream) option insite the submodules folders
    cd packages/$pack
    echo git branch -u origin ${branches[$pack]}

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

