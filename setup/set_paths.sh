#!/bin/bash

set_utils_path() {
#function set_utils_path {  # function syntax is not supported crontab
    case $HOSTNAME in
    "zueub"[2-4][0-9][0-9])
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
#function set_conda_path {  # function syntax is not supported crontab
    case $HOSTNAME in
    "zueub"[2-4][0-9][0-9])
	export CONDA_PATH="/opt/users/common/packages/anaconda3/" ;;
    "keschln-"[0-9][0-9][0-9][0-9]|"ela"[0-9])
	export CONDA_PATH="/store/msrad/utils/anaconda3/" ;;
    *)
	echo "ERROR in set_conda_path: unknown computer "$HOSTNAME
	return ;;
	#exit 1 ;;
    esac
    export PATH=$CONDA_PATH"/bin:$PATH"
    echo "... set CONDA_PATH to: "$CONDA_PATH
    # echo conda version and conda & python path
    conda -V
    which conda
    which python

    # easy access to the easy-install file
    alias easy-install.pth='emacs '$CONDA_PATH'/envs/PyTroll_$LOGNAME/lib/python2.7/site-packages/easy-install.pth &'
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
# function set_pytroll_paths {   # function syntax is not supported crontab
case $HOSTNAME in
    "zueub"[2-4][0-9][0-9])
        if [ -d /opt/users/$LOGNAME/monti-pytroll/ ]
        then
            export PYTROLLHOME=/opt/users/$LOGNAME/monti-pytroll/
        else
            export PYTROLLHOME=/opt/users/$LOGNAME/PyTroll/	
        fi
        export XRIT_DECOMPRESS_PATH=/opt/users/common/bin/xRITDecompress
        #export XRIT_DECOMPRESS_OUTDIR=/tmp/SEVIRI_DECOMPRESSED_$LOGNAME ;;
        export XRIT_DECOMPRESS_OUTDIR=/tmp/SEVIRI_DECOMPRESSED ;;
    "keschln-"[0-9][0-9][0-9][0-9]|"ela"[0-9])
        export PYTROLLHOME=$HOME/monti-pytroll/
        export XRIT_DECOMPRESS_PATH=/store/mch/msrad/sat/pytroll/xRITDecompress
        export XRIT_DECOMPRESS_OUTDIR=/scratch/$LOGNAME ;;
    *)
        echo "ERROR in set_pytroll_paths: unknown computer "$HOSTNAME
	return ;;
	#exit 1 ;;
    esac
    export PSP_CONFIG_FILE=${UTILS_PATH}/packages/pyspectral_aux_files/pyspectral.cfg
    #unset PSP_CONFIG_FILE   # should not be needed any more ... 
    echo "... set PYTROLLHOME to: "$PYTROLLHOME
    echo "... set PSP_CONFIG_FILE to: "$PSP_CONFIG_FILE
    echo "... set XRIT_DECOMPRESS_PATH to: "$XRIT_DECOMPRESS_PATH
    echo "... set XRIT_DECOMPRESS_OUTDIR to: "$XRIT_DECOMPRESS_OUTDIR
}
