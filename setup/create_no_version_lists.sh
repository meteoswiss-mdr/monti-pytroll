#!/bin/bash

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


#meld PyTroll-conda-package-list_${user}_no_version_nr.txt PyTroll-conda-package-list_no_version_nr.txt
#meld PyTroll-pip-requirements_${user}_no_version_nr.txt PyTroll-pip-requirements_no_version_nr.txt
