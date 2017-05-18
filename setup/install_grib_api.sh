#!/bin/bash
#
# This script does the following:
# * install basemap package
#
# The script will install jasper in 
# /opt/users/common/packages
# following the instruction of
# https://software.ecmwf.int/wiki/display/GRIB/GRIB+API+Autotools+installation
# and (installation with python interphase)
# https://software.ecmwf.int/wiki/display/GRIB/Python+package+gribapi#_details 
#
# author: Ulrich Hamann
# version 0.1: 19-07-2016 U. Hamann

source set_paths.sh  # load functions from this script
set_utils_path

export version=grib_api-1.15.0-Source
#export version=grib_api-1.16.0-Source

if [ -d $UTILS_PATH/packages/$version ]
then

    cd $UTILS_PATH/packages/

    #export INSTALL_DIR=/opt/users/common/packages
    #cd $INSTALL_DIR

    # check for new versions here: https://software.ecmwf.int/wiki/display/GRIB/Releases !!!
    # !!! dont use 1.16.0, make ends with !!!
    #libgrib_tools.la ../src/libgrib_api.la -lm -ljasper
    #libtool: link: gcc -pedantic -Wall -DYYDEBUG -fPIC -m64 -I/opt/users/common//include -I/opt/users/common//include -o .libs/grib_keys grib_keys.o  -L/opt/users/common//lib ./.libs/libgrib_tools.a ../src/.libs/libgrib_api.so -lm -ljasper -Wl,-rpath -Wl,/opt/users/common/lib
    #../src/.libs/libgrib_api.so: undefined reference to `grib_md5_add'
    #../src/.libs/libgrib_api.so: undefined reference to `grib_md5_init'
    #../src/.libs/libgrib_api.so: undefined reference to `grib_md5_end'

    wget https://software.ecmwf.int/wiki/download/attachments/3473437/$version.tar.gz
    gunzip $version.tar.gz
    tar xf $version.tar
    rm $version.tar

else
    echo "... grib_api already downloaded "
    echo "    continue with installation"
fi



# configure, make and install 
cd $version/
export PREFIX=$UTILS_PATH
case $HOSTNAME in
"zueub"[2-4][0-9][0-9])
    export NETCDF=$UTILS_PATH ;;
"keschln-"[0-9][0-9][0-9][0-9])
    #export NETCDF=/usr/lib64 ;; 
    module load netCDF/4.3.3.1-gmvolf-15.11
    export NETCDF=$LD_LIBRARY_PATH 
    export JASPER=$UTILS_PATH/lib/jasper
    ;;
*)
    echo "ERROR in bashrc: unknown computer "$HOSTNAME
    return
    ;;
esac


case $HOSTNAME in
"zueub"[2-4][0-9][0-9])
    ## configure 
    #./configure --prefix=$PREFIX CFLAGS="-fPIC -m64"  --with-netcdf=$PREFIX --with-jasper=$PREFIX --disable-shared    
    ## configure with python interphase
    #./configure --prefix=$PREFIX CFLAGS="-fPIC -m64"  --with-netcdf=$PREFIX --with-jasper=$PREFIX --disable-shared --enable-python --disable-numpy
    ./configure --prefix=$PREFIX CFLAGS="-fPIC"  --with-netcdf=$NETCDF --with-jasper=$JASPER --enable-python 
"keschln-"[0-9][0-9][0-9][0-9])
    ./configure --prefix=$PREFIX CFLAGS="-fPIC"  --with-netcdf=$NETCDF --with-jasper=$JASPER ## --enable-python (FIXME: does not find python library...)
    ;;
*)
    echo "ERROR in bashrc: unknown computer "$HOSTNAME
    return
    ;;
esac


# using the python options, grib_api will be installed here:
# /opt/users/common/lib/python3.5/site-packages/grib_api

# make and make install
make
#make check
make install
