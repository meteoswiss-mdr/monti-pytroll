
cd /opt/users/hau/monti-pytroll/

# pip-3 install --user --trusted-host nexus.meteoswiss.ch --install-option="--prefix=/opt/users/hau/python-packets" virtualenv  #does not work
# python -m pip install --user --trusted-host nexus.meteoswiss.ch --install-option="--prefix=/opt/users/hau/python-packets" virtualenv # does not work
#pip-3 install --trusted-host nexus.meteoswiss.ch --install-option="--prefix=/opt/users/hau/python-packets" numexpr

## Sometimes, the previously installed version is cached.
## We can use --no-cache-dir together with -I to overwrite this
# besser nicht nutzen, es werden alte Version teilweise überschrieben, anstatt die alten ordentlich zu deinstallieren.
# pip install --trusted-host nexus.meteoswiss.ch --install-option="--prefix=/opt/users/hau/python-packets" --no-cache-dir -I matplotlib==1.5.1

# we call the venv mp for monty pytroll
export ENV_PATH=/opt/users/hau/monti-pytroll/mp
#echo $ENV_PATH
mkdir -p $ENV_PATH

#python -m virtualenv $ENV_PATH
cd /opt/users/hau/monti-pytroll/
python -m venv mp

source $ENV_PATH/bin/activate

export USE_CYTHON=True

# This does NOT work:
# pip install --trusted-host nexus.meteoswiss.ch --install-option="--prefix=/opt/users/hau/python-packets" virtualenvwrapper
#   File "/tmp/pip-install-JXHTwV/virtualenv-clone/setup.py", line 9, in <module>
#   with open('README.md') as f:
#   IOError: [Errno 2] No such file or directory: 'README.md'

## Nach Aktivieren vom virtualenv
## NICHT MEHR IN DAS PREFIX ENVIRONMENT SCHREIBEN
export trusted_hosts="--trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host nexus.meteoswiss.ch --cert /etc/pki/ca-trust/source/anchors/MCHProxy.pem"
pip install $trusted_hosts --upgrade pip   # !!! very important !!!
# pip install $trusted_hosts zlib  #does not work !!!
#pip install --trusted-host nexus.meteoswiss.ch matplotlib==2.1.2
pip install $trusted_hosts matplotlib 
#pip install --trusted-host nexus.meteoswiss.ch scikit-image==0.14.2
pip install $trusted_hosts scikit-image
#pip install --trusted-host nexus.meteoswiss.ch numpy==1.16.0
# pip install $trusted_hosts numpy # already satisfied 

pip install $trusted_hosts statsmodels
pip install $trusted_hosts sympy

pip install $trusted_hosts h5py
# pip install $trusted_hosts hdf5 # does not work
pip install $trusted_hosts netcdf4 # works but needs to cached cftime
pip install $trusted_hosts basemap
pip install $trusted_hosts pygrib 
