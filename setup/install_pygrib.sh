#!/bin/bash
#
# This script does the following:
# * install pygrib package
#
# Please note that you have to install
# the jasper and grib_api library before
# you install pygrib.
#
# author: Ulrich Hamann
# version 0.1: 15-04-2016 U. Hamann

case $HOSTNAME in
"zueub"[2-4][0-9][0-9])
    export INSTALL_DIR=/opt/users/common/packages
"keschln-0002")
    export INSTALL_DIR=/store/msrad/utils
*)
    echo "ERROR in check_hostname: unknown computer: "$HOSTNAME
    exit 1
    ;;
esac

cd $INSTALL_DIR

git clone https://github.com/jswhit/pygrib.git

cd $INSTALL_DIR/pygrib

echo cp setup.cfg.template setup.cfg
cp setup.cfg.template setup.cfg

# !!! check if jasper and grip_api are already installed !!! 
# specify jasper library folder
echo sed -i -- 's/\#jasper\_dir\ \=\ \/usr\/local/jasper\_dir\ \=\ \/opt\/users\/common\/lib\/jasper/g' setup.cfg
sed -i -- 's/\#jasper\_dir\ \=\ \/usr\/local/jasper\_dir\ \=\ \/opt\/users\/common\/lib\/jasper/g' setup.cfg 
# specify grib_api library folder
echo sed -i -- 's/\#grib\_api\_dir\ \=\ \/usr\/local/grib\_api\_dir\ \=\ \/opt\/users\/common\/lib\/grib\_api/g' setup.cfg
sed -i -- 's/\#grib\_api\_dir\ \=\ \/usr\/local/grib\_api\_dir\ \=\ \/opt\/users\/common\/lib\/grib\_api/g' setup.cfg


# THIS HAS TO BE DONE BEFORE THE VIRTUAL ENVIRONMENT IS ACTIVATED
# OTHERWISE WE GET FOLLOWING ERRORs:
#gcc -pthread -shared -B /opt/users/common/packages/anaconda2_cinesat/envs/PyTroll_cinesat/compiler_compat -L/opt/users/common/packages/anaconda2_cinesat/envs/PyTroll_cinesat/lib -Wl,-rpath=/opt/users/common/packages/anaconda2_cinesat/envs/PyTroll_cinesat/lib,--no-as-needed build/temp.linux-x86_64-2.7/pygrib.o -L/opt/users/common/lib/grib_api/lib -L/opt/users/common/lib/grib_api/lib64 -L/opt/users/common/lib/jasper/lib -L/opt/users/common/lib/jasper/lib64 -L/opt/users/common/packages/anaconda2_cinesat/envs/PyTroll_cinesat/lib -R/opt/users/common/lib/grib_api/lib -R/opt/users/common/lib/grib_api/lib64 -R/opt/users/common/lib/jasper/lib -R/opt/users/common/lib/jasper/lib64 -lgrib_api -ljasper -lpython2.7 -o build/lib.linux-x86_64-2.7/pygrib.so
#gcc: error: unrecognized command line option ‘-R’
#gcc: error: unrecognized command line option ‘-R’
#gcc: error: unrecognized command line option ‘-R’
#gcc: error: unrecognized command line option ‘-R’
#error: command 'gcc' failed with exit status 1
python setup.py build
echo "Does the buiding process looks ok? (press enter to continue or CTRL+c to abort)"
read junk

echo "*** Activate virtual environment " PyTroll_${LOGNAME}
echo "================================ "
source activate PyTroll_${LOGNAME}

cd $INSTALL_DIR/pygrib/
python setup.py install

echo "*** Deactivate virtual environment"
source deactivate
