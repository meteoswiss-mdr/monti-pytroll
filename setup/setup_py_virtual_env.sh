pip install --user --trusted-host nexus.meteoswiss.ch --install-option="--prefix=/opt/users/hau/python-packets" virtualenv
#pip install --trusted-host nexus.meteoswiss.ch --install-option="--prefix=/opt/users/hau/python-packets" numexpr

## Sometimes, the previously installed version is cached. 
## We can use --no-cache-dir together with -I to overwrite this
# besser nicht nutzen, es werden alte Version teilweise überschrieben, anstatt die alten ordentlich zu deinstallieren.
# pip install --trusted-host nexus.meteoswiss.ch --install-option="--prefix=/opt/users/hau/python-packets" --no-cache-dir -I matplotlib==1.5.1

export ENV_PATH=/opt/users/hau/C2python2_env
#echo $ENV_PATH
mkdir -p $ENV_PATH

python -m virtualenv $ENV_PATH

source $ENV_PATH/bin/activate

# This does NOT work: 
# pip install --trusted-host nexus.meteoswiss.ch --install-option="--prefix=/opt/users/hau/python-packets" virtualenvwrapper
#   File "/tmp/pip-install-JXHTwV/virtualenv-clone/setup.py", line 9, in <module>
#   with open('README.md') as f:
#   IOError: [Errno 2] No such file or directory: 'README.md'

## Nach Aktivieren vom virtualenv
## NICHT MEHR IN DAS PREFIX ENVIRONMENT SCHREIBEN 
pip install --trusted-host nexus.meteoswiss.ch matplotlib==2.1.2
pip install --trusted-host nexus.meteoswiss.ch scikit-image==0.14.2
pip install --trusted-host nexus.meteoswiss.ch numpy==1.16.0
pip install --trusted-host nexus.meteoswiss.ch statsmodels
pip install --trusted-host nexus.meteoswiss.ch sympy
