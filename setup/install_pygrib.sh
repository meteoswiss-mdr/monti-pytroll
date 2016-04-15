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

git clone https://github.com/jswhit/pygrib.git

cd $INSTALL_DIR/pygrib

echo cp setup.cfg.template setup.cfg
cp setup.cfg.template setup.cfg

# specify jasper library folder
echo sed -i -- 's/\#jasper\_dir\ \=\ \/usr\/local/jasper\_dir\ \=\ \/opt\/users\/common\/lib\/jasper/g' setup.cfg
sed -i -- 's/\#jasper\_dir\ \=\ \/usr\/local/jasper\_dir\ \=\ \/opt\/users\/common\/lib\/jasper/g' setup.cfg 
# specify grib_api library folder
echo sed -i -- 's/\#grib\_api\_dir\ \=\ \/usr\/local/grib\_api\_dir\ \=\ \/opt\/users\/common\/lib\/grib\_api/g' setup.cfg
sed -i -- 's/\#grib\_api\_dir\ \=\ \/usr\/local/grib\_api\_dir\ \=\ \/opt\/users\/common\/lib\/grib\_api/g' setup.cfg

#echo "*** Activate virtual environment " PyTroll_$(logname)
#echo "================================ "
#source activate PyTroll_$(logname)

cd $INSTALL_DIR/pygrib/
python setup.py install

#echo "*** Deactivate virtual environment"
#source deactivate
