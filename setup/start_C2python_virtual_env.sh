#!/bin/bash

# .bashrc

echo bashrc $1

# Source global definitions
if [ -f /etc/bashrc ]; then
    echo 'start /etc/bashrc'
    . /etc/bashrc
fi

#PS1='\[[\u@ \e[1;31m\]\h \e[0;37m\W]\$\[\e[0m\] '

# when using cronjobs a few common shell variables are not set
if ! test -n "${HOSTNAME}"; then
    export HOSTNAME=`/bin/hostname`
    echo '... set HOSTNAME to:' ${HOSTNAME}
fi
if ! test -n "${USER}"; then
    export USER=${LOGNAME}
    echo '... set USER to:' ${LOGNAME}
fi
if ! test -n "${logname}"; then
    export logname=${LOGNAME}
    echo '... set logname to:' ${LOGNAME}
fi

echo ''
echo '*** current SHELL variables'
echo "SHELL "${SHELL}
echo "USER" ${USER}
echo "\$(logname)" $(logname)
echo "\$LOGNAME" $LOGNAME
echo "uname -mrs:" `uname -mrs`
echo "whoami:" `/usr/bin/whoami`

# VENV variable is set in C2python2_env-v0.X/etc/coalition_start.sh

export UTILS_PATH=/opt/users/common/
export SAT_UTILS_PATH=/opt/users/common/

export PYTROLLHOME=$VENV/config_files/
#export XRIT_DECOMPRESS_PATH=/opt/users/common/bin/xRITDecompress
export XRIT_DECOMPRESS_PATH=$VENV/config_files/setup/xRITDecompress
export XRIT_DECOMPRESS_OUTDIR=/tmp/SEVIRI_DECOMPRESSED 
export PSP_CONFIG_FILE=$VENV/lib/python2.7/site-packages/pyspectral/etc/pyspectral.yaml
#export PYGAC_CONFIG_FILE=$PYTROLLHOME/packages/pygac/etc/pygac.cfg

if [ "$1" == "offline" ] ; then
    export PPP_CONFIG_DIR=$PYTROLLHOME/cfg_offline/
else
    export PPP_CONFIG_DIR=$PYTROLLHOME/etc/
fi
echo "... set PPP_CONFIG_DIR to: "$PPP_CONFIG_DIR

echo "... set PYTROLLHOME to: "$PYTROLLHOME
echo "... set XRIT_DECOMPRESS_PATH to: "$XRIT_DECOMPRESS_PATH
echo "... set XRIT_DECOMPRESS_OUTDIR to: "$XRIT_DECOMPRESS_OUTDIR
echo "... set PSP_CONFIG_FILE to: "$PSP_CONFIG_FILE
#echo "... set PYGAC_CONFIG_FILE to: "$PYGAC_CONFIG_FILE

alias tkdiff='echo tkdiff is too old, use \"meld\" instead; echo  meld '
alias ncdump=/usr/bin/ncdump

echo "... open proxy ports 8080"
export http_proxy=http://proxy.meteoswiss.ch:8080
export https_proxy=https://proxy.meteoswiss.ch:8080

#echo "*** change XAUTHORITY"
#export XAUTHORITY=/home/lom/users/$LOGNAME/.Xauthority

echo '... configure host dependent settings, HOSTNAME='$HOSTNAME
export FULLNAME=`getent passwd $LOGNAME | cut -d ":" -f 5 | cut -d "," -f 1`
export FIRSTNAME=`echo $FULLNAME | cut -d " " -f 1`
export LASTNAME=`echo $FULLNAME | cut -d " " -f 2`
export EMAIL=${FIRSTNAME}.${LASTNAME}@meteoswiss.ch
echo "... set FULLNAME to: "$FULLNAME
echo "... set FIRSTNAME to: "$FIRSTNAME
echo "... set LASTNAME to: "$LASTNAME
echo "... set EMAIL to: "$EMAIL

#echo '... set PYTHONPATH to:':$PYTROLLHOME/scripts
#export PYTHONPATH=$PYTROLLHOME/scripts

echo "*** activate virtual environment: source "$VENV"/bin/activate"
##### source activate PyTroll_$LOGNAME  
source $VENV/bin/activate

# some useful alias commands
alias ll='ls --color=auto -alh'
alias ls='ls --color=auto'
