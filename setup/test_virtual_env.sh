function test_virtual_env {
    echo ""
    echo ""
    echo "    Please do some test, if you can import packages:"
    echo ""
    ## echo "source activate "PyTroll_$(logname) # this is hau even for cinesat
    echo "source activate "PyTroll_$LOGNAME
    echo "python"
    echo "import matplotlib._path"
    echo "import h5py"
    echo "import netCDF4"
    echo "from mpl_toolkits.basemap import Basemap"
    echo "import aggdraw"
    echo "import pygrib"
    echo "import scipy"
    echo "import numpy"
    echo "import PIL"
    echo "from __future__ import print_function"
    echo "import skimage"
    echo ""
}

test_virtual_env
