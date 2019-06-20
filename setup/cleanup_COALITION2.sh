
echo "cleanup of input/output data directories for "$HOSTNAME
echo "cleanup safnwc input"
find /data/cinesat/in/safnwc/*h5            -type f -mmin +180 -delete
find /data/cinesat/in/safnwc/*gz            -type f -mmin +180 -delete
find /data/cinesat/in/safnwc/*buf           -type f -mmin +180 -delete
find /data/cinesat/in/safnwc/*csi           -type f -mmin +180 -delete
find /data/cinesat/in/safnwc_v2016/*nc      -type f -mmin +180 -delete
echo "cleanup radar input"
find /data/cinesat/in/radar/*gif            -type f -mmin +180 -delete
find /data/cinesat/in/radar/*hdf5           -type f -mmin +180 -delete
echo "cleanup cosmo input"
find /data/cinesat/in/cosmo/*nc             -type f -mmin +180 -delete
### echo "cleanup cpp input"
### find /data/cinesat/in/cpp/*nc           -type f -mmin +180 -delete

echo "cleanup COALITION2 output"
find /data/cinesat/out/labels/Label*        -type f -mmin +80 -delete
find /data/cinesat/out/20*p                 -type f -mmin +90 -delete
find /data/cinesat/out/C2-BT-forecasts/20*p -type f -mmin +90 -delete
find /data/cinesat/out/C2-BT-forecasts/20*p -type f -mmin +80 -delete
echo "cleanup PYTROLL output"
find /data/cinesat/out/*png                 -type f -mmin +100 -delete
find /data/cinesat/out/*tif                 -type f -mmin +100 -delete
find /data/cinesat/out/ninjo/*tif           -type f -mmin +100 -delete

echo "cleanup decompressed MSG/SEVIRI HRIT files"
find /tmp/SEVIRI_DECOMPRESSED_${LOGNAME}/H-000-MSG* -type f -mmin +55 -delete
find /tmp/SEVIRI_DECOMPRESSED/H-000-MSG*            -type f -mmin +55 -delete
echo "cleanup of decompressed HSAF files"
find /tmp/h03_*_rom.grb                             -type f -mmin +55 -delete
find /tmp/h03B_*_fdk.grb                            -type f -mmin +55 -delete
