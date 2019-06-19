
echo "cleanup of input/output data directories for "$HOSTNAME
find /data/cinesat/in/safnwc/*h5       -type f -mmin +300 | xargs /bin/rm -f
find /data/cinesat/in/safnwc/*gz       -type f -mmin +300 | xargs /bin/rm -f
find /data/cinesat/in/safnwc/*buf      -type f -mmin +300 | xargs /bin/rm -f
find /data/cinesat/in/safnwc/*csi      -type f -mmin +300 | xargs /bin/rm -f
find /data/cinesat/in/safnwc_v2016/*nc -type f -mmin +300 | xargs /bin/rm -f
find /data/cinesat/in/radar/*gif       -type f -mmin +300 | xargs /bin/rm -f
find /data/cinesat/in/radar/*hdf5      -type f -mmin +300 | xargs /bin/rm -f
find /data/cinesat/in/cosmo/*nc        -type f -mmin +300 | xargs /bin/rm -f
###  find /data/cinesat/in/cpp/*nc     -type f -mmin +300 | xargs /bin/rm -f
find /data/cinesat/out/labels/Label*   -type f -mmin +80  | xargs /bin/rm -f
find /data/cinesat/out/20*p            -type f -mmin +90  | xargs /bin/rm -f
/data/cinesat/out/C2-BT-forecasts/20*p -type f -mmin +90  | xargs /bin/rm -f
find /data/cinesat/out/*png            -type f -mmin +100 | xargs /bin/rm -f
find /data/cinesat/out/*tif            -type f -mmin +100 | xargs /bin/rm -f
find /data/cinesat/out/ninjo/*tif      -type f -mmin +100 | xargs /bin/rm -f

find /tmp/SEVIRI_DECOMPRESSED_hau/H-000-MSG* -type f -mmin +55 | xargs /bin/rm -f
find /tmp/SEVIRI_DECOMPRESSED/H-000-MSG*     -type f -mmin +55 | xargs /bin/rm -f
