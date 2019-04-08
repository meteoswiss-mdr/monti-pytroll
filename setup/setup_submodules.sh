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

# ATTENTION: The order of the packages needs to be optimized!!!
#            when installing with setup.py develop, requirements with be installed without develop option
#            even other Pytroll packages (and this we dont link!) 
#            SO CHECK THE EASY-INSTALL file after installation   
#export packages="aggdraw pygrib pyresample pycoast pyorbital posttroll trollsift pytroll-schedule trollimage mipp mpop trollduction pyspectral pydecorate"
#export packages="pyresample pycoast pyorbital posttroll trollsift pytroll-schedule trollimage mipp mpop trollduction pyspectral pydecorate satpy"
# PYGRIB IS ALREADY INSTALLED BY ANACONDA
# PYTROLL-DB is not recommended by Martin R.
export packages='aggdraw trollimage pykdtree pyresample pycoast pyorbital posttroll trollsift pytroll-schedule mipp mpop trollduction pyspectral pydecorate satpy pytroll-collectors trollflow-sat trollflow trollbufr trollmoves pytroll-examples pytroll-cspp-runner pytroll-pps-runner pytroll-aapp-runner pygac pyninjotiff pytroll-product-filter pytroll-modis-runner pytroll-osisaf-runner python-bufr pygranule'

## !!!USE BRANCHES FROM THE .gitmodule FILE INSTEAD OF HARD CODED BRANCHES!!!
#declare -A branches
#branches=( ["aggdraw"]="master" ["pygrib"]="master" ["pykdtree"]="master" ["pyresample"]="master" ["pycoast"]="master"  \
#           ["pyorbital"]="master" ["posttroll"]="develop" ["trollsift"]="master" \
#           ["pytroll-schedule"]="master" ["trollimage"]="develop" ["mipp"]="master" \
#           ["mpop"]="master" ["trollduction"]="develop" ["pyspectral"]="master" ["pydecorate"]="master" \
#	   ["satpy"]="develop" ["pytroll-collectors"]="develop" ["trollflow-sat"]="develop" \
#	   ["trollflow"]="develop" ["trollbufr"]="develop" ["trollmoves"]="develop" ["pytroll-examples"]="master" \
#	   ["pytroll-cspp-runner"]="master" ["pytroll-pps-runner"]="master" ["pytroll-aapp-runner"]="master" ["pygac"]="master" \
#	   ["pyninjotiff"]="master" ["pytroll-product-filter"]="master" ["pytroll-modis-runner"]="master" \
#	   ["pytroll-osisaf-runner"]="master" ["python-bufr"]="master" ["pytroll-db"]="master" ["pygranule"]="master" \
#	 )

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
# use this line for the first time to specify the branch
git submodule foreach -q --recursive 'branch="$(git config -f $toplevel/.gitmodules submodule.$name.branch)"; path="$(git config -f $toplevel/.gitmodules submodule.$name.path)"; echo $path; git checkout $branch'
#git submodule foreach -q --recursive 'path="$(git config -f $toplevel/.gitmodules submodule.$name.path)"; echo $path; git pull'
echo "Does this look good? (press enter to continue or CTRL+c to abort)"
read junk

case $HOSTNAME in
    "zueub"[2-4][0-9][0-9]|"keschln-"[0-9][0-9][0-9][0-9]|"ela"[0-9])
	# check conda installation 
	which conda
	echo "Is the correct anaconda activated? (press enter to continue or CTRL+c to abort)"
	read junk

	echo ""
	echo "*** Activate virtual environment " PyTroll_$LOGNAME
	echo "============================================= "
	#source activate PyTroll_$(logname) -> logname points to hau, even when using cinesat
	source activate PyTroll_${LOGNAME}
	;;
    "zuerh"[2-4][0-9][0-9])
	echo ""
	echo "*** Activate python virtualenv "
	echo "============================================= "
	export ENV_PATH=/opt/users/hau/C2python2_env
	source $ENV_PATH/bin/activate
	;;
esac
echo "Is the virtual environement active? (press enter to continue or CTRL+c to abort)"
read junk

# enable the use of cython
export USE_CYTHON=True

##
## maybe better use
# pip install (python setup install) and
# pip install -e (python setup.py develop)


echo ""
echo "*** Install PyTroll packages "
echo "============================ "

for pack in $packages
do 
    echo ""
    echo ""
    echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    echo "*** install PyTroll package:"  $pack 
    echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    cd $PYTROLLHOME
    
    cd packages/$pack
    export USE_CYTHON=True
    
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

    # ALSO AGGDRAW IS INSTALLED AS SUBMODULE
    ## Install python and PyTroll packages
    #if ( [ "$pack" == "aggdraw" ] || [ "$pack" == "aggdraw" ] ) ; then
    #	# normal installation in the site-package directory
    #	echo python setup.py install 
    #	python setup.py install 
    #else
	# development installation using the easy-install.pth file
    echo python setup.py develop 
    python setup.py develop 
    #fi

done 

echo "*** check your easy-install file, if all packages are installed with develop option"
echo "    all PyTroll packages shoud look like this:"
echo "trollimage (1.5.0, /opt/users/"$LOGNAME"/PyTroll/packages/trollimage)"
echo "    if this is not the case, deinstall and reinstall as develop version"
echo "pip uninstall package_name"
echo "cd packages/package_name"
echo "python setup.py develop"
echo "==============================================="
echo "more $CONDA_PATH/envs/PyTroll_$LOGNAME/lib/python2.7/site-packages/easy-install.pth"
more $CONDA_PATH/envs/PyTroll_$LOGNAME/lib/python2.7/site-packages/easy-install.pth


echo "*** Deactivate virtual environment"
source deactivate
