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
