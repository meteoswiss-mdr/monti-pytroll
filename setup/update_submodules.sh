#!/bin/bash
#
# A small script to install a update PyTroll submodules
#
# author: Ulrich Hamann
# version 0.1: 23-02-2016 U. Hamann

export PYTROLLHOME=/opt/users/$(logname)/PyTroll/
cd $PYTROLLHOME

# get the latest info from the MCH gitlab for the superproject
git pull origin master

## this updates the submodule to the current state of the superproject
#git submodule update

# this updates the submodule to the current state of the submodule's git repository
git submodule update --remote 

# here we take care of the deheaded state of the submodules:
# in each submodule, a checkout is performed with the branch specified in the .gitmodule file
git submodule foreach -q --recursive 'branch="$(git config -f $toplevel/.gitmodules submodule.$name.branch)"; git checkout $branch'

cd -