pip install --user --trusted-host nexus.meteoswiss.ch --install-option="--prefix=/opt/users/hau/python-packets" virtualenv
pip install --trusted-host nexus.meteoswiss.ch --install-option="--prefix=/opt/users/hau/python-packets" numexpr

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
