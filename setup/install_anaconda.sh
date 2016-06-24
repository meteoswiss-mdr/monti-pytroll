#!/bin/bash
#
# script to install a virtual environment called "PyTroll"
#
# This script does the following:
# * install anaconda
#
# The script is part of setup_user.sh and 
# will only work on the zueub428 in the folder 
# /opt/users/\$(logname)/PyTroll/setup.
# To install PyTroll on another computer, please use
# setup_developer.py
#
# author: Ulrich Hamann
# version 0.1: 16-02-2016 U. Hamann

export PYTROLLHOME=/opt/users/$(logname)/PyTroll/
mkdir -p $PYTROLLHOME/packages
export HOME_ORG=$HOME
export HOME=$PYTROLLHOME/packages
echo ""
echo "... PyTroll installation script starts"
echo ""
echo "You will be asked to read the license agreement."
echo "You have to press ENTER to read them."
echo "Press 'q' to quit the license agreement."
echo ""
echo "When asked: Do you approve the license terms? [yes|no]"
echo "answer with >>> yes"
echo ""
echo "When asked where to install anaconda, the answer should look like this:"
#echo "[/home/lom/users/"$LOGNAME"/anaconda2] >>> /opt/users/"$LOGNAME"/PyTroll/packages/anaconda2"
echo "[/home/lom/users/"$LOGNAME"/anaconda3] >>> /opt/users/"$LOGNAME"/PyTroll/packages/anaconda3"
echo "you have to press enter to approve the installation location"
echo "(this is the default for this installation)"
echo ""
echo "Anaconda will ask to modify your .bashrc"
echo "Type here 'no'. We will take care of this at another place"
echo ""
echo "Did you read the last lines? (Continue with enter)"
echo ""
read junk
#/opt/users/common/packages/Anaconda2-2.4.1-Linux-x86_64.sh
#/opt/users/common/packages/Anaconda2-4.0.0-Linux-x86_64.sh
/opt/users/common/packages/Anaconda3-4.0.0-Linux-x86_64.sh
export HOME=$HOME_ORG


# add anaconda to your path
echo "the script changes your \$PATH and \$PYTHONPATH to avoid conflicts:"
#export PATH=$PYTROLLHOME/packages/anaconda2/bin:$PATH
export PATH=$PYTROLLHOME/packages/anaconda3/bin:$PATH
echo "\$PATH="$PATH
#export PYTHONPATH=$PYTROLLHOME/packages/anaconda2/bin:$PYTROLLHOME/scripts
export PYTHONPATH=$PYTROLLHOME/packages/anaconda3/bin:$PYTROLLHOME/scripts
echo "\$PYTHONPATH="$PYTHONPATH