#!/bin/bash

set_utils_path() {
#function set_utils_path {  # function syntax is not supported by crontab
    case $HOSTNAME in
    "zue"[ur][bh][2-4][0-9][0-9])
	export UTILS_PATH=/opt/users/common/
	export SAT_UTILS_PATH=/opt/users/common/ ;;
    "keschln-"[0-9][0-9][0-9][0-9]|"ela"[0-9])
	export UTILS_PATH=/store/msrad/utils/
	export SAT_UTILS_PATH=/store/msrad/sat/pytroll/ ;;
    *)
	echo "ERROR in set_util_path: unknown computer "$HOSTNAME 
	return ;;
	#exit 1 ;;
    esac
    echo "... set UTILS_PATH to: "$UTILS_PATH
    echo "... set SAT_UTILS_PATH to: "$SAT_UTILS_PATH
}

set_conda_path() {
#function set_conda_path {  # function syntax is not supported by crontab
    echo "set_conda_path" $1
    case $HOSTNAME in
    "zue"[ur][bh][2-4][0-9][0-9])
	#if [[ $# -eq 0 ]]; then 
	if [ $# -eq 0 ]; then 
	    export CONDA_PATH="/opt/users/common/packages/anaconda2_$LOGNAME/"
	else
	    if [ "$1" == "python3" ] || [ "$1" == "py3" ] || [ "$1" == "3" ] ; then
		echo "set_conda_path python3"
		export CONDA_PATH="/opt/users/common/packages/anaconda3_${LOGNAME}/"
		#export CONDA_PATH="/opt/users/common/packages/anaconda351/"
		#export CONDA_PATH="/opt/users/common/packages/anaconda3/"
	    else
		echo "unknown command line option: set_conda_path" $1
		export CONDA_PATH=""
		return
	    fi
	fi ;;
    "keschln-"[0-9][0-9][0-9][0-9]|"ela"[0-9])
        export CONDA_PATH="/store/msrad/utils/anaconda3/" ;;
    *)
	echo "ERROR in set_conda_path: unknown computer "$HOSTNAME
	return ;;
	#exit 1 ;;
    esac
    if [ ! -d "$CONDA_PATH" ]; then
	echo "ERROR, CONDA PATH " $CONDA_PATH "does not exists"
	echo "       probably conda is not installed on this server"
	echo "       please contact Ulrich Hamann"
	return
    fi
    export PATH=$CONDA_PATH"/bin:$PATH"
    echo "... set CONDA_PATH to: "$CONDA_PATH
    # echo conda version and conda & python path
    conda -V
    which conda
    which python

    # easy access to the easy-install file
    alias easy-install.pth='emacs '$CONDA_PATH'/envs/PyTroll_$LOGNAME/lib/python2.7/site-packages/easy-install.pth &'
    alias easy-install='emacs '$CONDA_PATH'/envs/PyTroll_$LOGNAME/lib/python2.7/site-packages/easy-install.pth &'
    alias easy-install3='emacs '$CONDA_PATH'/envs/PyTroll_$LOGNAME/lib/python3.8/site-packages/easy-install.pth &'
    alias site-packages='cd '$CONDA_PATH'/envs/PyTroll_$LOGNAME/lib/python2.7/site-packages/ '

    # easier activation and deactivation of the virtual environment PyTroll
    alias activate='source activate PyTroll_$LOGNAME'
    alias deactivate='source deactivate'

    echo "*** Switch off SSL check for conda installations"
    conda config --set ssl_verify false

    conda -V >/dev/null 2>&1 || { echo "Setup of virtual environment requires conda, but it's not installed. Contact Ulrich. Aborting." >&2; exit 1; }

    ## echo "... List of available environments"
    #conda info --envs
}




set_pytroll_paths() {
# function set_pytroll_paths {   # function syntax is not supported by crontab
case $HOSTNAME in
    "zue"[ur][bh][2-4][0-9][0-9])
        if [ -d /opt/users/$LOGNAME/monti-pytroll/ ]
        then
            export PYTROLLHOME=/opt/users/$LOGNAME/monti-pytroll/
        else
            export PYTROLLHOME=/opt/users/$LOGNAME/PyTroll/	
        fi
        export XRIT_DECOMPRESS_PATH=/opt/users/common/bin/xRITDecompress
        #export XRIT_DECOMPRESS_OUTDIR=/tmp/SEVIRI_DECOMPRESSED_$LOGNAME ;;
        export XRIT_DECOMPRESS_OUTDIR=/tmp/SEVIRI_DECOMPRESSED ;;
        #export XRIT_DECOMPRESS_OUTDIR=/data/COALITION2/tmp/SEVIRI_DECOMPRESSED ;;
    "keschln-"[0-9][0-9][0-9][0-9]|"ela"[0-9])
        export PYTROLLHOME=$HOME/monti-pytroll/
        export XRIT_DECOMPRESS_PATH=/store/mch/msrad/sat/pytroll/xRITDecompress
        export XRIT_DECOMPRESS_OUTDIR=/scratch/$LOGNAME ;;
    *)
        echo "ERROR in set_pytroll_paths: unknown computer "$HOSTNAME
	return ;;
	#exit 1 ;;
    esac
    #export PSP_CONFIG_FILE=${UTILS_PATH}/packages/pyspectral_aux_files/pyspectral.cfg
    export PSP_CONFIG_FILE=${UTILS_PATH}/packages/pyspectral_aux_files/pyspectral.yaml
    #unset PSP_CONFIG_FILE   # should not be needed any more ...
    export PYGAC_CONFIG_FILE=$PYTROLLHOME/packages/pygac/etc/pygac.cfg
    echo "... set PYTROLLHOME to: "$PYTROLLHOME
    echo "... set PSP_CONFIG_FILE to: "$PSP_CONFIG_FILE
    echo "... set XRIT_DECOMPRESS_PATH to: "$XRIT_DECOMPRESS_PATH
    echo "... set XRIT_DECOMPRESS_OUTDIR to: "$XRIT_DECOMPRESS_OUTDIR
    echo "... set PYGAC_CONFIG_FILE to: "$PYGAC_CONFIG_FILE
    export METRANETLIB_PATH=$PYTROLLHOME/packages/mpop/mpop/satin/metranet
    echo "... set METRANETLIB_PATH to:" $METRANETLIB_PATH
}
