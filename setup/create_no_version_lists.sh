#!/bin/bash

# possibilities to list packages
# pip freeze > PyTroll-pip-requirements.txt
# conda list --export > PyTroll-conda-package-list.txt
# conda env export > PyTroll_conda_and_pip.yml # difficult to use with ssl error!
### pip   list for human readable list
### conda list for human readable list
### conda list --json


export user=sam
# installation of following packages did not work:
# glymur
# openjpeg
awk 'BEGIN { FS="=" }{ if ($1!="glymur") if ($1!="openjpeg") print $1}' PyTroll-conda-package-list_${user}.txt > PyTroll-conda-package-list_${user}_no_version_nr.txt

# installation does not work with pip install for following packages
# all pytroll packages (start with "-e" in the list
# basemap (as it need a GEOS library)
# pygrib (as it need as library too)
# trollimage is installed as submodule
awk 'BEGIN { FS="=" } { if (substr($1,0,3) != "-e") if ($1!="basemap") if ($1!="pygrib") if ($1!="trollimage") if ($1!="aggdraw") print $1 }' PyTroll-pip-requirements_${user}.txt > PyTroll-pip-requirements_${user}_no_version_nr.txt


# try later
# pip list --disable-pip-version-check
# pip list --disable-pip-version-check | grep -E "^ruamel\.yaml "

#meld PyTroll-conda-package-list_${user}_no_version_nr.txt PyTroll-conda-package-list_no_version_nr.txt
#meld PyTroll-pip-requirements_${user}_no_version_nr.txt PyTroll-pip-requirements_no_version_nr.txt
